# Repo Cleanup D6 Policy Report (2026-02-15)

## Syfte

Införa en minimal ignore-policy-justering så att endast `archive/_orphaned/results/**` blir
git-spårbart, utan att öppna upp root `results/**`.

## Genomfört

- `.gitignore` uppdaterad med en begränsad allowlist:
  - `!archive/_orphaned/results/`
  - `!archive/_orphaned/results/**`
- Inga övriga `results`-regler togs bort eller omdefinierades.
- Ingen `results/**` move/delete execution genomfördes i denna tranche.

## Policyeffekt

- Root policy för `results/**` kvarstår (fortsatt ignorerat).
- Endast archivets orphaned-subträd (`archive/_orphaned/results/**`) kan nu bli
  spårbart i git-diff för framtida, separat execution-kontrakt.

## Scope-verifiering

- Kod/runtime-zoner (`src/**`, `tests/**`, `config/**`, `.github/**`) är oförändrade.
- D6 består av policy/docs-updatering samt backlog/statusdokumentation.

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

- D6 introducerar endast policyförutsättning; execution av artefaktflytt/radering är fortsatt
  en separat riskpunkt och måste kontrakteras samt granskas i egen tranche.

## Status

- D6 policytranche: införd.
- `results/**` execution: fortsatt föreslagen i separat execution-kontrakt.
