# Repo Cleanup Fas B Microtranche-1 Precheck Report (2026-02-17)

## Syfte

Avblockera Fas B genom en första, låg-risk execution-kandidat utan att exekvera destruktiva ändringar i denna tranche.

## Kandidater i fokus

- **B1:** `src/core/strategy/example.py`
- **B2:** `src/core/ml/overfit_detection.py`

## Färsk evidens (sammanfattning)

- Deep analysis listar B1/B2 som `TRULY_DEAD`-kandidater.
- Färsk granskning visar:
  - B1 har huvudsakligen docs-referenser.
  - B2 har omfattande docs-statusankring som "implemented" och config-ankring (`config/validation_config.json`), vilket ökar drift-/kommunikationsrisk vid tidig radering.

## Beslut (precheck)

| Kandidat | Legitimitet för nästa execution-kontrakt | Motivering                                                          |
| -------- | ---------------------------------------- | ------------------------------------------------------------------- |
| B1       | `APPROVED TO PLAN`                       | Låg risk och isolerbar kandidat för mikrotranche.                   |
| B2       | `BLOCKED TO EXECUTE`                     | Kräver separat docs/config-konsekvenspaket före eventuell radering. |

## Preconditions för nästa execution-kontrakt (B1)

1. Scope ska vara strikt: `src/core/strategy/example.py` + exakt lista docs-referenser som uppdateras.
2. Explicit Scope OUT ska inkludera alla andra B-kandidater (inkl. B2-B8).
3. Opus pre-code review måste godkänna kontraktet innan radering.
4. Full gate-stack före/efter enligt governance.

## Gate results (this precheck tranche)

| Gate                                   | Status | Notes                                                                                                                       |
| -------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------- |
| pre-commit/lint för touched docs files | `PASS` | `pre-commit run --files ...` passerade (black/ruff skip för docs, övriga hooks pass).                                       |
| smoke test                             | `PASS` | `python -m pytest -q tests/test_import_smoke_backtest_optuna.py` -> `.` `[100%]`.                                           |
| determinism replay                     | `PASS` | `python -m pytest -q tests/test_backtest_determinism_smoke.py` -> `...` `[100%]`.                                           |
| feature-cache invariance               | `PASS` | `python -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py` -> `......` `[100%]`. |
| pipeline invariant                     | `PASS` | `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` -> `...` `[100%]`.                                             |
| scope check                            | `PASS` | `git diff --name-only` + `git status --porcelain` verifierat; inga kodfiler ändrade i denna tranche.                        |

Kompletterande scope-evidens (porcelain):

- Carry-forward från tidigare docs-trancher:
  - `M docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
  - `?? docs/ops/DOCS_STATUSSYNC_KICKOFF_CONTRACT_2026-02-17.md`
  - `?? docs/ops/DOCS_STATUSSYNC_KICKOFF_REPORT_2026-02-17.md`
  - `?? docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_CONTRACT_2026-02-17.md`
  - `?? docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_REPORT_2026-02-17.md`
- Nya filer i denna tranche:
  - `?? docs/ops/REPO_CLEANUP_B_MICROTRANCHE1_PRECHECK_CONTRACT_2026-02-17.md`
  - `?? docs/ops/REPO_CLEANUP_B_MICROTRANCHE1_PRECHECK_REPORT_2026-02-17.md`

## Status

- Precheck för Fas B mikrotranche-1: `införd` i arbetskopia.
- Execution för B1: `föreslagen` tills separat execution-kontrakt + Opus pre-review.
