# Repo Cleanup Fas B8 Precheck Report (2026-02-17)

## Syfte

Fastställa om B8 (`src/core/strategy/fvg_filter.py`) är legitim för isolerad execution-tranche utan att orsaka oavsiktlig beteendedrift.

## Kandidat i fokus

- **B8:** `src/core/strategy/fvg_filter.py` (`ARCHIVE_ONLY` i deep analysis)

## Färsk evidens

- Tracked proof:
  - `git ls-files --error-unmatch src/core/strategy/fvg_filter.py` -> `TRACK_EXIT=0`
- Aktiv referens i scripts (ej archive):
  - `scripts/generate_meta_labels.py:24` importerar `from core.strategy.fvg_filter import generate_fvg_opportunities`
- Runtime/test referensbild i övrigt:
  - inga träffar i `src/**` (förutom `SOURCES.txt`)
  - inga träffar i `tests/**`

## Beslut (precheck)

| Kandidat | Legitimitet för isolerad execution | Motivering                                                                                                      |
| -------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| B8       | `BLOCKED TO EXECUTE`               | `fvg_filter.py` är fortfarande beroende för `scripts/generate_meta_labels.py`; isolerad `git rm` är inte säker. |

## Nästa säkra steg (föreslagen)

1. Antingen skapa separat tranche som hanterar både `src/core/strategy/fvg_filter.py` och `scripts/generate_meta_labels.py` med explicit konsekvensanalys.
2. Eller lämna B8 tills script-arkivering (Fas C) kan göras i ett sammanhållet paket.

## Gate results (this precheck tranche)

| Gate                                   | Status | Notes                                                                                            |
| -------------------------------------- | ------ | ------------------------------------------------------------------------------------------------ |
| pre-commit/lint för touched docs files | `PASS` | `pre-commit run --files ...` passerade.                                                          |
| smoke test                             | `PASS` | `tests/test_import_smoke_backtest_optuna.py` passerade.                                          |
| determinism replay                     | `PASS` | `tests/test_backtest_determinism_smoke.py` passerade.                                            |
| feature-cache invariance               | `PASS` | `tests/test_feature_cache.py` + `tests/test_features_asof_cache_key_deterministic.py` passerade. |
| pipeline invariant                     | `PASS` | `tests/test_pipeline_fast_hash_guard.py` passerade.                                              |
| scope check                            | `PASS` | Endast nya precheck-filer i `docs/ops/` enligt `git status --short`; inga kodfiler ändrade.      |

## Status

- B8 precheck: `införd` i arbetskopia.
- B8 execution: fortsatt `föreslagen`.
