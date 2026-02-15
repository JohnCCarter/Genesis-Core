# Repo Cleanup D7 Minimal Execution Report (2026-02-15)

## Syfte

Verifiera att D6-policyändringen fungerar i praktiken genom en strikt scopead,
git-spårbar move-only pilot för exakt en fil.

## Genomfört

- Move-only execution för en kandidatfil:
  - Från: `results/hparam_search/run_seeds/run_meta.json`
  - Till: `archive/_orphaned/results/hparam_search/run_seeds/run_meta.json`
- Kandidatval:
  - Storlek: 2 bytes (`{}`)
  - Referensscan: inga träffar i docs/kod/test/script för kandidatpath.

## Scope-verifiering

- Endast scopead flyttfil + D7 docs/ledger-filer ändrade.
- Ingen ändring i `src/**`, `tests/**`, `config/**`, `.github/**`.
- Ingen `.gitignore`-ändring i D7.
- Ingen ytterligare `results/**` execution i denna tranche.

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

- Piloten verifierar spårbar execution-path för en minimal artefakt, men säger inte
  i sig något om större volymtrancher. Fortsatt execution utökning kräver separat
  kontrakt, kandidatval och governance-audit.

## Status

- D7 minimal execution pilot: införd.
- Vidare execution utanför scopead one-file pilot: fortsatt föreslagen.
