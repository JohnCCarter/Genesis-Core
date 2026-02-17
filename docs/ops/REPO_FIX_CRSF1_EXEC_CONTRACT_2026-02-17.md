# REPO_FIX_CRSF1_EXEC_CONTRACT_2026-02-17

Status: föreslagen
Datum: 2026-02-17
Kategori: api

## Bakgrund

Användaren har prioriterat följande findings för omedelbar hantering, med krav på legitimitetsverifiering före implementation:

- CR-1
- CR-7
- CR-8
- SF-9
- SF-10
- SF-12
- SF-13

Legitimitetsverifiering (kodankare i aktuell branch) är genomförd före detta kontrakt.

## Scope IN

Endast följande filer får ändras:

- `src/core/strategy/features_asof.py` (CR-1, SF-10)
- `src/core/strategy/evaluate.py` (CR-7)
- `src/core/strategy/decision.py` (CR-8)
- `src/core/optimizer/runner.py` (SF-9)
- `src/core/backtest/engine.py` (SF-12)
- `src/core/server.py` (SF-13)
- Endast följande testfiler under `tests/`:
  - `tests/test_features_asof_cache.py`
  - `tests/test_evaluate_pipeline.py`
  - `tests/test_decision.py`
  - `tests/test_optimizer_runner.py`
  - `tests/test_backtest_engine.py`
  - `tests/test_ui_endpoints.py`
  - samt obligatoriska gate-filer:
    - `tests/test_import_smoke_backtest_optuna.py`
    - `tests/test_backtest_determinism_smoke.py`
    - `tests/test_feature_cache.py`
    - `tests/test_features_asof_cache_key_deterministic.py`
    - `tests/test_pipeline_fast_hash_guard.py`
- Governance artefakt: `docs/ops/REPO_FIX_CRSF1_EXEC_REPORT_2026-02-17.md`

## Scope OUT

- Inga ändringar i andra runtime-zoner, särskilt inte:
  - `src/core/strategy/*` utanför explicit Scope IN-filer
  - `src/core/backtest/*` utanför explicit Scope IN-fil
  - `config/**`, `results/**`, `scripts/**`, `registry/**`
- Inga opportunistiska refactors/formattering utanför berörda kodrader
- Ingen ändring av endpoint-paths/response-shapes utöver explicit SF-13-correction

## Constraints

- Default NO BEHAVIOR CHANGE gäller inte fullt ut för denna tranche.
- Tillåtna beteendeförändringar är strikt begränsade till:
  1. SF-13: `/health` får inte returnera `status=ok` vid config-läsfel.
  2. SF-9/SF-10/SF-12: fel får inte sväljas tyst; observabilitet ska förbättras utan att krascha normalflöde.
  3. CR-1: duplicerad cache-write i `features_asof` tas bort (ingen avsedd semantikändring).
  4. CR-7: `volume_score` får inte sänkas för normalvolym (ratio<=1), och `cap_ratio` får inte skapa straff vid värden <1.
  5. CR-8: state-isolering i `decide` ska vara explicit; muterbar nested state från input får inte delas till output.
- Bevara determinism och canonical jämförbarhet.

## Acceptanskriterier per finding

- CR-1: endast en slutlig write av `_feature_cache[cache_key]` i `_extract_asof`, med bibehållen LRU-begränsning.
- CR-7: tester visar att normal ratio (1.0) ger maximal kvalitet och att `cap_ratio<1` inte orsakar artificiell nedskalning.
- CR-8: tester visar att indata-state inte muteras indirekt via output-state.
- SF-9: korrupt trialfil ger observerbar signal (logg/varning), inte tyst continue utan spår.
- SF-10: `_as_config_dict` ger observerbar signal vid model_dump-fel och fallback är fortsatt säker.
- SF-12: cache write-fel i precompute ger observerbar signal, utan att stoppa backtest.
- SF-13: vid config-fel ska `/health` returnera HTTP 503 och shape `{status, config_version, config_hash}` där `status="error"`.

## Done criteria

1. BEFORE-gates körda och dokumenterade.
2. Opus 4.6 pre-review: APPROVED innan implementation.
3. Minimal implementation inom Scope IN.
4. Regressionstester för ändrade beteenden tillagda/uppdaterade.
5. AFTER-gates gröna:
   - lint/pre-commit
   - `tests/test_import_smoke_backtest_optuna.py`
   - `tests/test_backtest_determinism_smoke.py`
   - `tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py`
   - `tests/test_pipeline_fast_hash_guard.py`
   - riktade tester för Scope IN-filer
6. Opus 4.6 post-audit: APPROVED.
7. Rapport uppdaterad med evidens och residual risk.
