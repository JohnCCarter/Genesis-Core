# Repo Cleanup Fas B2 Docs/Config Approval (2026-02-17)

## Syfte

Avblocka B2 execution genom ett explicit docs/config-konsekvensbeslut för `src/core/ml/overfit_detection.py`.

## Beslut

- B2 docs/config-konsekvenspaket: `APPROVED TO EXECUTE`.
- Beslutet gäller endast B2-scope i `docs/ops/REPO_CLEANUP_B2_EXEC_CONTRACT_2026-02-17.md`.

## Underlag

- Legitimitetsgranskning finns dokumenterad i:
  - `docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_REPORT_2026-02-17.md`
- Mikrotranche-precheck markerade B2 som blockerad tills separat konsekvenspaket fanns:
  - `docs/ops/REPO_CLEANUP_B_MICROTRANCHE1_PRECHECK_REPORT_2026-02-17.md`
- B2-kontraktet har explicit allowlist för kvarvarande docs/config-referenser:
  - `docs/validation/**`
  - `config/validation_config.json`
  - `CHANGELOG.md`
  - `docs/ops/**`, `docs/audits/**`, `docs/daily_summaries/**`, `scripts/archive/**`

## Konsistensvillkor för execution

1. Inga ändringar utanför B2 Scope IN.
2. Endast följande runtime-/index-drift tillåts:
   - delete `src/core/ml/overfit_detection.py`
   - remove stale rad i `src/genesis_core.egg-info/SOURCES.txt`
   - ta bort `overfit_detection` från `docs/architecture/ARCHITECTURE_VISUAL.md` inklusive konsekventa counts.
3. Full BEFORE/AFTER gate-stack måste vara grön.
4. Opus pre-code + post-code review måste vara `APPROVED`.

## Status

- Docs/config-avblockning för B2: `införd` i arbetskopia.
