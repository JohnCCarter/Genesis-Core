# Context Map — engine-modul-split

Datum: 2026-03-12
Branch: worktree-engine-modul-split
Base SHA: d5e61f10

## Primära källfiler

| Fil | Rader | Ansvar |
|-----|-------|--------|
| `src/core/backtest/engine.py` | 1655 | Huvud-backtest-engine: datainladdning, bar-replay, exit-logik, resultatbygge |
| `src/core/backtest/composable_engine.py` | 156 | Wrapper runt BacktestEngine för composable strategy (hooks) |
| `src/core/pipeline.py` | 144 | Pipeline-entry point (ej primär target för engine-split) |

## BacktestEngine — ansvarskartering (engine.py)

### Modul-level (rad 1–95)

| Symbol | Typ | Ansvar | Beroenden |
|--------|-----|--------|-----------|
| `PRECOMPUTE_SCHEMA_VERSION` | konstant | Versionsguard för on-disk cache | ingen |
| `_precompute_cache_key_material()` | funktion | Bygger stable hash-input för precompute cache | `hashlib`, `json` |
| `_debug_backtest_enabled()` | funktion | Läser env-flagga `GENESIS_DEBUG_BACKTEST` | `env_flags` |
| `CandleCache` | klass | Enkel LRU-cache (max 4 slots) för candle DataFrames | `pandas` |

### BacktestEngine-metoder

| Metod | Rad | Rader | Ansvar | Extern koppling |
|-------|-----|-------|--------|-----------------|
| `__init__` | 113 | ~80 | Init alla attribut, kalla `_validate_mode_consistency` + `_init_htf_exit_engine` | PositionTracker, ChampionLoader |
| `_validate_mode_consistency` | 192 | 27 | Validera fast_window + env-flaggor | `os.getenv` |
| `_deep_merge` | 220 | 3 | Delegerar till `deep_merge_dicts` | `core.utils.dict_merge` |
| `_config_fingerprint` | 224 | 17 | SHA256-fingerprint av effektiv config | `core.utils.diffing.canonical` |
| `_init_htf_exit_engine` | 242 | 43 | Väljer legacy/ny HTF-exit-motor + default-config | `LegacyExitEngine`, `NewExitEngine` |
| `load_data` | 285 | 330 | Laddar Parquet-data, filter, precompute-features, numpy arrays | pandas, pyarrow, many indicators |
| `_precompute_cache_key` | 617 | 35 | Bygger on-disk cache-nyckel per symbol/timeframe/period | `_precompute_cache_key_material` |
| `_prepare_numpy_arrays` | 653 | 11 | Konverterar candles_df till numpy-dict | pandas/numpy |
| `_build_candles_window` | 665 | 53 | Bygger candles-dict för pipeline (fast/slow path) | `_np_arrays`, `_col_*` |
| `run` | 719 | 363 | Huvud-backtest-loop: config-merge, bar-replay, exit+entry-logic | evaluate_pipeline, position_tracker, hooks |
| `_check_htf_exit_conditions` | 1084 | 373 | HTF Fibonacci exit-kontroll (precomputed + live path, signal-tolkning) | HTFExitEngine, ATR, ExitAction |
| `_check_traditional_exit_conditions` | 1458 | 48 | Fallback SL/TP/confidence/regime exit | position_tracker |
| `_build_results` | 1507 | 86 | Assemblerar backtest-resultat-dict | position_tracker, git subprocess |
| `_initialize_position_exit_context` | 1594 | 62 | Initierar exit-kontext för ny position | calculate_exit_fibonacci_levels |

## Viktiga beroenden

```
engine.py
├── core.backtest.htf_exit_engine (LegacyExitEngine, ExitAction)
├── core.strategy.htf_exit_engine (NewExitEngine — try/except import)
├── core.config.merge_policy (resolve_champion_merge_for_engine)
├── core.utils.dict_merge (deep_merge_dicts)
├── core.utils.env_flags (env_flag_enabled)
├── core.utils.logging_redaction (get_logger)
├── core.backtest.position_tracker (PositionTracker)
├── core.indicators.exit_fibonacci (calculate_exit_fibonacci_levels)
├── core.strategy.champion_loader (ChampionLoader)
├── core.strategy.evaluate (evaluate_pipeline)
├── core.utils.diffing.canonical (scrub_volatile) — lazy import
├── core.indicators.{atr, ema, rsi, bollinger, adx, fibonacci} — lazy imports in load_data
├── core.indicators.htf_fibonacci — lazy import in load_data
```

```
composable_engine.py
└── core.backtest.engine (BacktestEngine) — wrapping via hooks
```

## Testfiler

| Testfil | Vad den testar |
|---------|----------------|
| `tests/backtest/test_backtest_engine.py` | BacktestEngine core funktionalitet |
| `tests/backtest/test_composable_backtest_engine.py` | ComposableBacktestEngine |
| `tests/backtest/test_backtest_engine_hook.py` | evaluation_hook + post_execution_hook |
| `tests/integration/test_new_htf_exit_engine_adapter.py` | HTF exit engine adapter |
| `tests/backtest/test_htf_exit_engine.py` | HTF exit engine logik |
| `tests/backtest/test_htf_exit_engine_selection.py` | HTF engine-val (legacy/ny) |
| `tests/backtest/test_htf_exit_engine_htf_context_schema.py` | HTF context schema |

## Identifierade split-kandidater (prioritetsordning)

### Slice 1 — FÖRESLAGEN (denna session)
**Extrahera `CandleCache` + cache-key helpers till `engine_candle_cache.py`**

- `CandleCache` (rad 75–93) — enkel LRU-klass, inga runtime-sidoeffekter
- `_precompute_cache_key_material()` (rad 47–66) — ren hashfunktion
- `_debug_backtest_enabled()` (rad 69–72) — enkel env-läsare
- `PRECOMPUTE_SCHEMA_VERSION` — konstant

Rationale: Noll beteendeändring möjlig. Alla är oberoende av backtest-loopen. Enkel import-uppdatering.

### Slice 2 — FÖRESLAGEN (nästa session)
**Extrahera `_build_results` till `engine_result_builder.py`**
- Ren data-assembling, ingen sidoeffekt utom git subprocess
- 86 rader

### Slice 3 — FÖRESLAGEN
**Extrahera `_check_traditional_exit_conditions` till `engine_exit_utils.py`**
- Ren logik, inga sidoeffekter, 48 rader

### Slice 4 — FÖRESLAGEN (kräver mer planering)
**Extrahera precompute-blocket i `load_data` till `engine_precompute.py`**
- Större, fler beroenden, kräver interface-design

### Slice 5 — FÖRESLAGEN (kräver mer planering)
**Extrahera `_check_htf_exit_conditions` till `engine_htf_exit_dispatcher.py`**
- 373 rader, komplex adapter-logik, kräver noggrann granskning

## Freeze-zoner (rörs ej)

- Runtime-semantik i `run()` backtest-loopen
- HTF-exit engine-val i `_init_htf_exit_engine`
- Precompute on-disk cache schema (PRECOMPUTE_SCHEMA_VERSION)
- Config-authority paths
- `composable_engine.py` hook-kontrakt
