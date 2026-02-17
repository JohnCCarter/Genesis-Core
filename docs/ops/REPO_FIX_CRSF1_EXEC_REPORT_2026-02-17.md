# REPO_FIX_CRSF1_EXEC_REPORT_2026-02-17

Status: föreslagen
Datum: 2026-02-17
Kategori: api
Kontrakt: `docs/ops/REPO_FIX_CRSF1_EXEC_CONTRACT_2026-02-17.md`

## 1) Legitimitetsverifiering (före implementation)

Verifierad i aktuell branch med kodankare:

- CR-1 (`src/core/strategy/features_asof.py`): duplicerad cache-write
  - `_feature_cache[cache_key] = result` förekommer två gånger (två separata rader nära slutet av `_extract_asof`).
- CR-7 (`src/core/strategy/evaluate.py`): cap_ratio-semantik
  - `ratio = min(ratio, cap_ratio)` följt av `score = ratio` och slutlig clamp till [0,1] gör cap_ratio ineffektiv i normalfall.
- CR-8 (`src/core/strategy/decision.py`): shallow copy-risk
  - `state_out: dict[str, Any] = dict(state_in)`.
- SF-9 (`src/core/optimizer/runner.py`): tyst skip av korrupta filer
  - `except (ValueError, OSError): continue`.
- SF-10 (`src/core/strategy/features_asof.py`): swallow i config-konvertering
  - `_as_config_dict` returnerar `{}` vid broad `except` utan observabilitet.
- SF-12 (`src/core/backtest/engine.py`): swallow vid cache-write
  - broad `except Exception: pass` runt `_np.savez_compressed`.
- SF-13 (`src/core/server.py`): health endpoint rapporterar ok vid fel
  - fallback returnerar `{status: "ok", config_version: None, config_hash: None}` även vid exception.

## 2) BEFORE-gates

- Lint/pre-commit: PASS
  - Kommando: `.venv\\Scripts\\pre-commit.exe run --all-files`
- Obligatoriska pytest-gates: PASS
  - Kommando: `.venv\\Scripts\\python.exe -m pytest tests/test_import_smoke_backtest_optuna.py tests/test_backtest_determinism_smoke.py tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py tests/test_pipeline_fast_hash_guard.py -q`
  - Utfall: `13 passed`

## 3) Opus pre-review

- BLOCKED (första pre-review)
  - Orsak: kontrakt/report saknade explicit acceptans för CR-7/CR-8, exakt API-kontrakt för SF-13 och namngiven test-allowlist.
  - Åtgärd: kontrakt skärpt med acceptanskriterier per finding + explicit test-allowlist; BEFORE-gates dokumenterade ovan.
  - Ny pre-review krävdes efter remediation.
- APPROVED (andra pre-review)
  - Motivering: remediation verifierad (explicit acceptanskriterier, API-kontrakt och test-allowlist).

## 4) Implementation

- Genomförd inom Scope IN:
  - `src/core/strategy/features_asof.py`
    - CR-1: duplicerad slutlig cache-write borttagen.
    - SF-10: `_as_config_dict` loggar warning vid `model_dump`-fel före säker fallback `{}`.
  - `src/core/strategy/evaluate.py`
    - CR-7: `cap_ratio` hardening (`<1` golvas till `1.0`) för att undvika artificiell penalisering av normalvolym.
  - `src/core/strategy/decision.py`
    - CR-8: explicit state-isolering med deep copy av input/output-state.
  - `src/core/optimizer/runner.py`
    - SF-9: korrupta/oläsbara trialfiler ger observerbar warning istället för tyst skip.
  - `src/core/backtest/engine.py`
    - SF-12: cache-write-fel loggas som warning istället för tyst swallow.
  - `src/core/server.py`
    - SF-13: `/health` returnerar HTTP 503 + `status="error"` vid config-läsfel.
- Regressionstester tillagda/uppdaterade:
  - `tests/test_features_asof_cache.py`
  - `tests/test_evaluate_pipeline.py`
  - `tests/test_decision.py`
  - `tests/test_optimizer_runner.py`
  - `tests/test_backtest_engine.py`
  - `tests/test_ui_endpoints.py`

## 5) AFTER-gates

- Lint/pre-commit: PASS
  - Kommando: `.venv\\Scripts\\pre-commit.exe run --all-files`
- Obligatoriska pytest-gates: PASS
  - Kommando: `.venv\\Scripts\\python.exe -m pytest tests/test_import_smoke_backtest_optuna.py tests/test_backtest_determinism_smoke.py tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py tests/test_pipeline_fast_hash_guard.py -q`
  - Utfall: `13 passed`
- Riktade regressionstester: PASS
  - Kommando: `.venv\\Scripts\\python.exe -m pytest tests/test_features_asof_cache.py tests/test_evaluate_pipeline.py tests/test_decision.py tests/test_optimizer_runner.py tests/test_backtest_engine.py tests/test_ui_endpoints.py -q`
  - Utfall: `65 passed`

## 6) Opus post-audit

- APPROVED
  - Guardrail: stagea endast CRSF1 scope-filer.
  - Exkludera pre-existerande/out-of-scope lokala filer:
    - `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md`
    - `docs/ops/WORK_SUMMARY_REPORT_2026-02-17.md`

## 7) Residual risks

- En pre-existerande modifiering utanför denna tranche finns fortsatt i working tree:
  - `docs/ops/REPO_CLEANUP_B2_EXEC_REPORT_2026-02-17.md`
