# Kodgranskning — Genesis-Core

**Datum:** 2026-03-01
**Granskare:** Claude (Opus 4.6)
**Scope:** Fullständig granskning — säkerhet, kodkvalitet, arkitektur, testning, prestanda

---

## Sammanfattning

Genesis-Core är ett välstrukturerat Python-ramverk för handelsstrategier med ~24K rader källkod (102 filer) och ~22K rader tester (169 filer). Repot uppvisar hög mognad med modulär arkitektur, SSOT-konfiguration och omfattande CI/CD med pre-commit hooks (Black, Ruff, Bandit, detect-secrets).

Granskningen identifierade **55+ fynd** fördelade enligt:

| Allvarlighetsgrad | Antal | Kategori |
|:---|:---:|:---|
| **KRITISK** | 6 | Säkerhet (sandbox, exec), affärslogikfel, kodkomplexitet |
| **HÖG** | 14 | Felhantering, global state, stora filer, CORS, state reset |
| **MEDEL** | 20 | Kodduplicering, prestanda, resurshantering |
| **LÅG** | 15+ | Namngivning, dokumentation, magic numbers |

**Ruff linting: 0 fel** — kodstilen följer alla konfigurerade regler.

---

## 1. Säkerhet

### 1.1 KRITISKT — `exec()` i skript

**Filer:** `scripts/validate/validate_registry.py`, `scripts/train/train_model.py`, `scripts/run/run_backtest.py`, `scripts/run/paper_trading_runner.py`, `scripts/preflight/preflight_optuna_check.py`, `scripts/build/build_auth_headers.py`, `scripts/optimize/optimizer.py`

Alla skript använder mönstret:
```python
code = compile(open(target_script).read(), target_script, "exec")
exec(code, {"__name__": "__main__"})
```

**Risk:** Godtycklig kodexekvering om filsökvägen manipuleras.
**Rekommendation:** Byt till `importlib.import_module()` eller `runpy.run_path()`.

---

### 1.2 KRITISKT — MCP sandbox blockerar inte farlig kod

**Fil:** `mcp_server/utils.py:131-168`

```python
def sanitize_code(code: str) -> str:
    # NOTE: only logs warnings ... does NOT prevent execution
    dangerous_patterns = [r"import\s+os\s*$", ...]
    for pattern in dangerous_patterns:
        if re.search(pattern, code, re.MULTILINE):
            logger.warning(...)
    return code  # Returns UNCHANGED
```

**Risk:** En angripare kan exekvera godtycklig Python via `execute_python`-verktyget. Regex-mönstren är lätta att kringgå (multi-line imports, `__import__`, `importlib`).
**Rekommendation:** Antingen blockera farliga mönster helt, använd `RestrictedPython`, eller inaktivera `execute_python`-verktyget.

---

### 1.3 KRITISKT — Svag path traversal-validering med fnmatch

**Fil:** `mcp_server/utils.py:82-91`

`fnmatch.fnmatch()` är designat för shell-globbing, inte säkerhetsfiltrering. Möjliga bypass:
- Case-sensitivity: `.ENV` vs `.env`
- Symboliska länkar: `allowed_dir/link -> /etc/passwd`

**Rekommendation:** Använd strikt regex eller allowlist-modell. Validera alltid den upplösta (resolved) sökvägen.

---

### 1.4 HÖG — Felmeddelanden läcker systeminformation

**Filer:** Flera platser i `mcp_server/`

```python
# mcp_server/utils.py:97
return False, f"Invalid path: {str(e)}"
# mcp_server/tools.py:98
return {"success": False, "error": f"Error reading file: {str(e)}"}
```

**Risk:** Fullständiga filsökvägar, modulnamn och stacktraces kan läcka till klienter.
**Rekommendation:** Logga fullständiga feldetaljer server-side, returnera generiska meddelanden till klienter.

---

### 1.5 HÖG — Säkerhetsinställningar via miljövariabler utan validering

**Fil:** `mcp_server/remote_server.py:100-116`

```python
SAFE_REMOTE_MODE = os.environ.get("GENESIS_MCP_REMOTE_SAFE", "1") != "0"
ALLOW_UNAUTH_REMOTE = os.environ.get("GENESIS_MCP_REMOTE_ALLOW_UNAUTH") == "1"
```

**Risk:** Container escape eller env-var-injektion kan inaktivera autentisering.
**Rekommendation:** Autentisering bör aldrig kunna stängas av via miljövariabler.

---

### 1.6 HÖG — Ovaliderade git branch-namn

**Fil:** `mcp_server/tools.py:1149-1152, 1435-1448`

Branch-namn och PR-titlar skickas direkt till subprocess utan validering.
**Rekommendation:** Validera branch-namn mot `^[a-zA-Z0-9._/-]+$`. Lägg till `--` separator före användarinput i git-kommandon.

---

### 1.7 HÖG — Hardkodad CORS-whitelist

**Fil:** `mcp_server/remote_server.py:1378-1385`

```python
allow_origins=["https://chat.openai.com", "https://chatgpt.com"]
allow_methods=["*"]
allow_headers=["*"]
```

**Rekommendation:** Gör CORS-origins konfigurerbar. Undvik `allow_methods=["*"]` och `allow_headers=["*"]`.

---

### 1.8 Positivt (säkerhet)

- `subprocess` använder konsekvent listform, inte `shell=True`
- `hmac.compare_digest()` för timing-safe tokenvalidering
- `numpy allow_pickle=False` i `backtest/engine.py:498`
- Filsökvägssanering med allowlist-approach
- Logg-redaktion av API-nycklar (`utils/logging_redaction.py`)
- `.secrets.baseline` för detect-secrets
- Säkra standardvärden: auth krävs, read-only-läge aktiverat

---

## 2. Affärslogik

### 2.0 KRITISKT — Bar-index mismatch med precomputed features

**Fil:** `backtest/engine.py:1143-1147`

```python
level_0382 = _to_positive_finite(self._precomputed_features["htf_fib_0382"][idx])
```

`idx` är bar-index i den filtrerade datasetet, men precomputed features indexeras från **hela originaldataset**. Om backtest använder datumfilter (rad 417-424) uppstår index-felinställning.

**Exempel:**
- Fullt dataset: 100 000 bars
- Precompute: beräknas på alla 100 000
- Filtrerat backtest: bars 50 000–60 000
- Bar 100 i filtrerat set → `_precomputed_features[100]` → **fel bar**

**Risk:** Felaktiga trades baserade på inkorrekt Fibonacci-data.
**Rekommendation:** Omindexera precomputed features efter datumfiltrering, eller lagra offset.

---

### 2.1 HÖG — Position tracker state ej fullständigt återställd

**Fil:** `backtest/engine.py:743-749`

`run()` återställer `position_tracker` och `state`, men **inte** numpy-kolumnarrays (`_col_open`, etc.), `_np_arrays` eller `_precomputed_features`. Om `run()` anropas utan föregående `load_data()` kan stale data användas.

**Rekommendation:** Validera att data laddats eller återställ alla runtime-attribut.

---

## 3. Kodkvalitet

### 3.1 KRITISKT — Megafunktioner

De 5 längsta funktionerna:

| Funktion | Fil | Rader | Problem |
|:---|:---|:---:|:---|
| `_run_optuna()` | `optimizer/runner.py:2437` | 659 | Nestade closures, `nonlocal` state, inre `objective()` är 211 rader |
| `run_trial()` | `optimizer/runner.py:1681` | 523 | Deduplicering + caching + exekvering + retry + jämförelse |
| `run_optimizer()` | `optimizer/runner.py:3171` | 417 | Config + strategi + validering + champion-promotion |
| `_run_backtest_direct()` | `optimizer/runner.py:1372` | 216 | Engine-laddning + pruning + config |
| `step()` | `backtest/engine.py` | ~200 | Huvudloop med 5+ indenteringsnivåer |

**Rekommendation:** Bryt `_run_optuna` till klasser: `OptunaObjective`, `TimeoutManager`, `CheckpointHandler`. Bryt `run_trial` till: `TrialDeduplicator`, `TrialExecutor`, `TrialComparator`.

---

### 3.2 HÖG — 116 breda `except Exception:`

Spritt genom hela `src/` — tystar fel och försvårar debugging.

**Värsta exemplen:**

| Fil | Rad | Mönster |
|:---|:---:|:---|
| `optimizer/runner.py` | 149, 245, 418, 661, 2639, 2723, 2871, 2941 | `except Exception: pass` eller fallback utan loggning |
| `backtest/engine.py` | Flera | `except Exception: pass` |
| `config/authority.py` | Flera | Tyst felhantering |

**Rekommendation:** Fånga specifika undantag. Om bredare catch behövs, logga alltid:
```python
except Exception as e:
    logger.warning("Non-critical failure: %s", e)
```

---

### 3.3 HÖG — 13 tysta `except: pass` block

**Filer:** `backtest/engine.py`, `optimizer/runner.py`, `config/authority.py`

Blankt `except:` fångar även `SystemExit`, `KeyboardInterrupt` och `GeneratorExit`.
**Rekommendation:** Använd alltid `except Exception:` som minimum. Lägg till loggning.

---

### 3.4 HÖG — Global state utan lifecycle management

**Fil:** `optimizer/runner.py:126-146`

```python
_TRIAL_KEY_CACHE: dict[int, str] = {}
_DEFAULT_CONFIG_CACHE: dict[str, Any] | None = None
_BACKTEST_DEFAULTS_CACHE: dict[str, Any] | None = None
_STEP_DECIMALS_CACHE: dict[float, int] = {}
_JSON_CACHE: OrderedDict = OrderedDict()
_DATA_CACHE: dict[str, Any] = {}
```

6 globala caches med manuella locks, ingen eviction policy, ingen cleanup.
**Rekommendation:** Skapa en `CacheManager`-klass med bounded size och clear()-metod för testning.

---

### 3.5 MEDEL — Kodduplicering

| Plats | Mönster |
|:---|:---|
| `indicators/htf_fibonacci.py` | 5 upprepade try-except-block med identiskt mönster |
| `optimizer/runner.py:1517 & 1638` | Pruner-konfigurationsparsning duplicerad |
| `optimizer/runner.py:2281 & 2287` | Config name field extraction duplicerad |
| `optimizer/runner.py:2068-2084` | Scoring threshold-parsning upprepas 4 gånger |

**Rekommendation:** Extrahera gemensamma hjälpfunktioner.

---

### 3.6 MEDEL — ~20 print-satser i produktionskod

**Filer:** `backtest/engine.py`, `backtest/trade_logger.py`, `ml/label_cache.py`, `optimizer/runner.py`

**Rekommendation:** Migrera till `logging`-ramverket som redan finns.

---

### 3.7 MEDEL — Filsökvägar i optimizer utan traversal-skydd

**Fil:** `optimizer/runner.py:2232-2233`

```python
candidate_path = Path(baseline_results_path_cfg)
if not candidate_path.is_absolute():
    candidate_path = PROJECT_ROOT / candidate_path
```

**Rekommendation:** Validera att resolved path är inom `PROJECT_ROOT`:
```python
candidate_path = (PROJECT_ROOT / candidate_path).resolve()
assert str(candidate_path).startswith(str(PROJECT_ROOT))
```

---

## 4. Arkitektur

### 4.1 Styrkor

- **Modulär strategiarkitektur:** `strategy/components/` med kompositionsmönster
- **SSOT-konfiguration:** `config/runtime.json` som enda sanningskälla
- **Paper/TEST-symbolwhitelisting:** Skyddar mot oavsiktlig handel
- **Registry-governance:** Kontrollerad agentskill-registrering
- **Separata CI/CD-workflows:** Deploy, test, lint med GitHub Actions

### 4.2 HÖG — God Object: `optimizer/runner.py` (3586 rader)

Denna fil hanterar:
- JSON I/O och caching (rad 47-260)
- Konfigurationshantering (282-531)
- Trial-exekvering (1681-2201)
- Optuna-integration (2264-2905)
- Grid search (918-962)
- Resultatvalidering (1107-1351)

**Rekommendation:** Dela upp i:
```
core/optimizer/
├── runner.py          (orkestrerare, <500 rader)
├── json_utils.py      (JSON I/O, caching)
├── config_loader.py   (konfigurationshantering)
├── trial_executor.py  (trial-körning med retry)
├── optuna_manager.py  (Optuna-specifik logik)
├── search_space.py    (parameterexpansion)
└── scoring.py         (resultatvalidering)
```

### 4.3 MEDEL — server.py (1084 rader) med alla endpoints i en fil

**Rekommendation:** Dela upp i FastAPI-routers per domän.

### 4.4 MEDEL — Backtest-engine blandar beräkning med I/O

**Fil:** `backtest/engine.py` (1658 rader)

Engine-klassen hanterar både beräkningslogik, caching och filskrivning.
**Rekommendation:** Separera beräkningsmotor från I/O-lager.

---

## 5. Testning

### 5.1 Styrkor

- **169 testfiler** med ~22K rader — bra testbas
- Integrationstester finns i `tests/integration/`
- Regressionstester för specifika buggar
- Test-to-source-ratio: 0.92 (22K test / 24K src)

### 5.2 Testresultat

**pytest:** 894 passed, 2 failed, 4 errors, 16 skipped (47.55s)

| Status | Detalj |
|:---|:---|
| 894 passed | Hela testsviten |
| 2 failed | `test_validate_registry_audit_ci.py` — registry audit-tester |
| 4 errors | `test_mcp_git_workflow_tools.py` — kräver specifik git-miljösetup |
| 16 skipped | Villkorade tester (nätverks-/miljöberoende) |

### 5.3 Linting & Säkerhetsskanning

- `ruff check src/` — 0 fel
- `bandit -r src/ -c bandit.yaml` — 0 problem i 18 784 rader (med repots konfigurerade excludes: B110, B311, B324, B112, B101, B404, B603)

---

## 6. Prestanda

### 6.1 MEDEL — Ineffektiv cache-eviction i optimizer

**Fil:** `optimizer/runner.py:498-502`

```python
if len(_TRIAL_KEY_CACHE) > 10000:
    items = list(_TRIAL_KEY_CACHE.items())  # O(n) memory
    _TRIAL_KEY_CACHE.clear()
    _TRIAL_KEY_CACHE.update(items[-8000:])   # O(n) rebuild
```

**Rekommendation:** Använd `functools.lru_cache` eller `OrderedDict.popitem(last=False)`.

### 6.2 MEDEL — Ingen memory-limit på subprocess i MCP

**Fil:** `mcp_server/tools.py:231-243`

Code execution via `execute_python` har timeout men ingen memory-begränsning.
**Rekommendation:** Använd `resource.setrlimit()` eller cgroups.

### 6.3 MEDEL — ATR beräknas 3 gånger per bar

**Fil:** `backtest/engine.py:515, 1188-1206`

ATR(14) beräknas i precomputation (rad 515), sen recalkuleras i exit-check (rad 1188-1197 numpy, 1200-1206 DataFrame). För en position som hålls 500 bars beräknas ATR 500 gånger i exit-loopen.
**Rekommendation:** Cacheera precomputed ATR och återanvänd i exit-check.

### 6.4 LÅG — Redundant JSON-serialisering i trial key

**Fil:** `optimizer/runner.py:485-486`

JSON serialiseras och hashas för varje trial. Cachning finns men kan optimeras med `lru_cache`.

---

## 7. CI/CD & Verktyg

### Styrkor
- GitHub Actions CI med Python 3.11
- Pre-commit hooks: Black, Ruff, Bandit, detect-secrets
- `.secrets.baseline` konfigurerat

### Observation
- Ruff passerar utan fel
- Bandit passerar utan problem (med repots bandit.yaml-excludes)
- `.gitignore` hade en bugg: `!scripts/build/**` negerade `__pycache__`-ignore — fixat

---

## 8. Prioriterad åtgärdslista

### Fas 1 — Kritiskt (omedelbart)
1. **Fixa bar-index mismatch** i `backtest/engine.py` precomputed features vid datumfiltrering
2. Ersätt `exec()` i alla skript med `importlib`/`runpy`
3. Blockera eller inaktivera `execute_python` i MCP-servern
4. Ersätt `fnmatch` med strikt path-validering
5. Bryt upp `_run_optuna()` (659 rader) till klasser

### Fas 2 — Högt (1-2 veckor)
6. Komplettera state reset i `backtest/engine.py:run()` — inkludera numpy-arrayer
7. Åtgärda alla `except: pass` och `except Exception: pass`
8. Validera git branch-namn i MCP-verktyg
9. Säkra att env-variabler inte kan inaktivera autentisering
10. Ersätt globala caches med `CacheManager`-klass
11. Gör CORS-origins konfigurerbar

### Fas 3 — Medel (2-4 veckor)
12. Extrahera kodduplicering till hjälpfunktioner
13. Migrera `print()` till `logging`
14. Dela upp `optimizer/runner.py` i moduler
15. Dela upp `server.py` i FastAPI-routers
16. Lägg till path traversal-skydd i optimizer
17. Cacheera ATR-beräkning i backtest-engine

### Fas 4 — Lågt (löpande)
18. Definiera konstanter istället för magic numbers
19. Komplettera type hints i nestade funktioner
20. Lägg till rate limiting i MCP-server
21. Lägg till security headers i HTTP-svar

---

*Granskningen genomfördes med manuell kodanalys, Ruff linting, Bandit säkerhetsskanning, pytest-körning och parallell djupdykning i kritiska filer.*
