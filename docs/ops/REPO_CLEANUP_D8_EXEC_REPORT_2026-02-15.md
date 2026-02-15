# Repo Cleanup D8 Minimal Execution Report (2026-02-15)

## Syfte

Verifiera en liten men verklig execution-tranche efter D7 genom att flytta exakt tre
lågriskfiler från `results/**` till allowlistad archive-path.

## Genomfört

Move-only execution för exakt tre filer:

1. Från `results/hparam_search/run_test/run_meta.json`
   till `archive/_orphaned/results/hparam_search/run_test/run_meta.json`
2. Från `results/hparam_search/run_20251227_180204/trial_001.log`
   till `archive/_orphaned/results/hparam_search/run_20251227_180204/trial_001.log`
3. Från `results/hparam_search/run_20251227_180204/trial_002.log`
   till `archive/_orphaned/results/hparam_search/run_20251227_180204/trial_002.log`

Preconditions:

- Destinationerna var frånvarande innan flytt (no-overwrite).
- Referensscan för exakta scopeade paths gav inga träffar.

## Scope-verifiering

- Ingen `.gitignore`-ändring i D8.
- Inga ändringar i `src/**`, `tests/**`, `config/**`, `.github/**`.
- Ingen execution utanför de tre scopeade filerna.

## Required gates (BEFORE + AFTER)

Körda enligt kontrakt:

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_pipeline_fast_hash_guard.py -q`

Gate-status:

- Before-gates: pass
- After-gates: pass

## Residual risk

- Tranche-volymen är liten och risken låg, men större batches behöver fortfarande
  separat kontrakt och audit för att undvika scope-drift.

## Status

- D8 minimal execution tranche: införd.
- Vidare execution utanför scopead tre-filsbatch: fortsatt föreslagen.
