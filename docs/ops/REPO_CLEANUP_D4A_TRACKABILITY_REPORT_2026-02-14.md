# Repo Cleanup D4A Trackability Report (2026-02-14)

## Syfte

Dokumentera varför pilotflytt av `results/**` inte kan göras som spårbar git-change under nuvarande ignore-policy.

## Observation

Pilotkandidat:

- `results/hparam_search/phase7b_grid_3months` (10 filer, 0 externa refs i docs/.github/README/CHANGELOG/AGENTS)

Genomförd lokal move-test gav ingen spårbar git-diff. Katalogen återställdes till ursprungspath.

## Evidens för blocker

- `.gitignore:212` innehåller `results/`.
- Detta gör att artefakter i kataloger med namn `results` inte blir spårbara i git.
- Därmed blir en move-only execution för `results/**` icke-verifierbar i commit-diff under nuvarande policy.

## Konsekvens

- D4A i denna tranche markeras som docs-only blocker-dokumentation.
- Ingen destruktiv `results/**`-flytt införs i denna commit.

## Rekommenderade nästa alternativ (föreslagna)

1. **Policyspår:** separat kontrakt för eventuell ignore-policyändring (högre risk, kräver explicit godkännande).
2. **Lokal driftspår:** fortsätt icke-git cleanup av `results/**` via operativ rutin, med tydlig out-of-band loggning.
3. **Fortsatt git-spårbar cleanup:** fokusera endast på spårbara områden utanför `results/**`.

## Required gates (BEFORE + AFTER)

Körda enligt kontrakt:

1. `python -m black --check .`
2. `python -m ruff check .`
3. `python -m pytest tests/test_import_smoke_backtest_optuna.py -q`
4. `python -m pytest tests/test_backtest_determinism_smoke.py -q`
5. `python -m pytest tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py -q`
6. `python -m pytest tests/test_pipeline_fast_hash_guard.py -q`

## Verifiering

- Scope gate: endast docs/AGENTS i diff.
- No-code-drift: inga ändringar i `src/**`, `tests/**`, `config/**`, `.github/**`, `results/**`, `tmp/**`.
- Before-gates: pass.
- After-gates: pass.
- Opus post-code diff-audit: krävs som slutgate.

## Status

- D4A blocker-dokumentation: införd.
- D4 execution för `results/**`: fortsatt föreslagen i separat kontrakt.
