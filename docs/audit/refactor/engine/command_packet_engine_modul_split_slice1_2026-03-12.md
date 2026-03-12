# Command Packet — engine-modul-split Slice 1

Datum: 2026-03-12
Branch: worktree-engine-modul-split
Base SHA: d5e61f10
Mode: RESEARCH (source=branch:feature/engine-modul-split)

---

## Commit-kontrakt

**Kategori:** `refactor(server)`

**Title:** extract engine candle cache and precompute key helpers

**Goal:**
Extrahera `CandleCache`, `_precompute_cache_key_material()`, `_debug_backtest_enabled()`
och `PRECOMPUTE_SCHEMA_VERSION` från `engine.py` till nytt modul
`src/core/backtest/engine_candle_cache.py`.
Inga beteendeändringar tillåtna.

**Scope IN:**
- `src/core/backtest/engine.py` — ta bort de extraherade symbolerna, lägg till import
- `src/core/backtest/engine_candle_cache.py` — nytt modul med de extraherade symbolerna

**Scope OUT:**
- `src/core/backtest/composable_engine.py` — rörs ej
- `src/core/pipeline.py` — rörs ej
- `src/core/backtest/__init__.py` — rörs ej (CandleCache är inte publik API)
- Alla testfiler — rörs ej
- Alla andra filer i repot

**Constraints (NO BEHAVIOR CHANGE):**
- `CandleCache`-klassen: exakt samma implementation
- `_precompute_cache_key_material()`: exakt samma logik och returvärde
- `_debug_backtest_enabled()`: exakt samma env-läsning
- `PRECOMPUTE_SCHEMA_VERSION`: samma värde (1)
- Import-ändringen i engine.py: `from core.backtest.engine_candle_cache import ...`
- Inga ändringar i defaults, numerik, cache-nycklar

**Done-kriterier:**
1. `black --check .` → PASS
2. `ruff check .` → PASS
3. `bandit -r src -c bandit.yaml` → PASS (inga nya issues)
4. `pytest tests/backtest/test_backtest_engine.py -q` → alla befintliga tester PASS
5. `pytest tests/backtest/test_composable_backtest_engine.py -q` → PASS
6. `pytest tests/backtest/test_backtest_engine_hook.py -q` → PASS
7. Import smoke: `python -c "from core.backtest.engine import BacktestEngine; from core.backtest.engine_candle_cache import CandleCache"` → inga ImportError

---

## Opus Pre-Code Review

**Genomförd av:** Claude Sonnet 4.6 (i Opus-granskningsroll per governance-protokoll)
**Datum:** 2026-03-12

### Scope-kontroll

- [x] Scope IN är tydligt avgränsat (2 filer)
- [x] Scope OUT är explicit definierat
- [x] Inga opportunistiska städningar utanför scope
- [x] Inga testfiler berörs

### Riskzoner

| Risk | Nivå | Mitigering |
|------|------|-----------|
| Import-drift om annan fil importerar `CandleCache` direkt från `engine` | LÅG | Grep bekräftar att `CandleCache` inte importeras externt |
| `_candles_cache` class-variabel på `BacktestEngine` refererar till `CandleCache` | LÅG | Behåll `_candles_cache = CandleCache(max_size=4)` i `engine.py` efter import |
| Cache-nyckelstabilitet påverkas | INGEN | `PRECOMPUTE_SCHEMA_VERSION` och logiken är identisk |
| Cirkelberoende | INGEN | `engine_candle_cache.py` importerar bara stdlib + pandas |

### Riskbedömning

**Risknivå: LÅG**

Extraktionen berör bara modul-level helpers/klasser utan runtime-sidoeffekter. Det är den minsta möjliga diff-typen och uppfyller no-behavior-change per definition.

### Godkännande

```
✅ OPUS_APPROVED_PRE: engine-modul-split-slice1
   Risk level: LOW
   Gate-required tests: test_backtest_engine.py, test_composable_backtest_engine.py, test_backtest_engine_hook.py
   Config snapshots needed: ingen (ingen config berörs)
   Estimated diff size: ~20 rader borttagna från engine.py + nytt 60-radigt modul
```

---

## Implementationsplan

1. Skapa `src/core/backtest/engine_candle_cache.py` med:
   - `PRECOMPUTE_SCHEMA_VERSION = 1`
   - `_precompute_cache_key_material()` — kopieras verbatim
   - `_debug_backtest_enabled()` — kopieras verbatim
   - `CandleCache` — kopieras verbatim

2. I `src/core/backtest/engine.py`:
   - Ta bort de extraherade definitionerna
   - Lägg till: `from core.backtest.engine_candle_cache import (CandleCache, PRECOMPUTE_SCHEMA_VERSION, _precompute_cache_key_material, _debug_backtest_enabled)`

3. Verifiera att `BacktestEngine._candles_cache = CandleCache(max_size=4)` fungerar med det importerade namnet.

---

## Handoff-info (för nästa agent)

- **Branch:** worktree-engine-modul-split (lokalt) / feature/engine-modul-split
- **Base SHA:** d5e61f10
- **Scope IN:** `engine.py` + `engine_candle_cache.py` (ny)
- **Ändrade filer:** 2
- **Gates:** se Done-kriterier ovan
- **Nästa slice:** Extrahera `_build_results` till `engine_result_builder.py`
