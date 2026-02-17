# Repo Cleanup Legitimacy Review Report (2026-02-17)

## Syfte

Formell legitimitetsgranskning av cleanup-faserna B/C/D/F/G innan någon ny execution startas.

## Governancegrund

- Commit-kontrakt med explicit Scope IN/OUT och default `NO BEHAVIOR CHANGE` krävs.
- Opus pre-review krävs före exekvering.
- Statusdisciplin `föreslagen` vs `införd` måste hållas.

## Evidensbas (ur read-only discovery)

- Working tree var docs-dirty vid granskning:
  - `M docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
  - `?? docs/ops/DOCS_STATUSSYNC_KICKOFF_CONTRACT_2026-02-17.md`
  - `?? docs/ops/DOCS_STATUSSYNC_KICKOFF_REPORT_2026-02-17.md`
- `DEEP_ANALYSIS_REPORT` har as-of `de9f417`, medan senare HEAD finns (`6b5eda4`), vilket innebär delvis stale baslinje.
- Fasnotiser i deep analysis markerar B/C/D/F som kandidatlistor (ej exekveringsklara i bulk).

## Opus 4.6 legitimitetsbeslut per fas

| Fas | Beslut               | Motivering (kort)                                                                   | Minimikriterier innan execution                                                     |
| --- | -------------------- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| B   | `BLOCKED TO EXECUTE` | B8 har aktiv referens; fasen kan inte exekveras som helhet.                         | Dela i mikrotrancher, isolera B8, bevisa noll oönskade referenser per tranche.      |
| C   | `BLOCKED TO PLAN`    | "Deprecated"-listan innehåller scripts med aktiva refs i test/docs/ops.             | Gör dependency-closure per script och klassificera active vs archival innan plan.   |
| D   | `BLOCKED TO PLAN`    | Count/targets i rapporten är delvis stale; flera config-paths har aktiva beroenden. | Re-baseline från aktuell HEAD, klassificera runtime-kritisk vs icke-kritisk config. |
| F   | `BLOCKED TO PLAN`    | Delar av kandidatlistan verkar redan no-op/stale; scope är inte färsk.              | Regenerera kandidatlista mot nuvarande `results/` med tracked/untracked-separation. |
| G   | `APPROVED TO PLAN`   | Konsolidering är legitim, men kräver referensmappning före flytt.                   | Definiera målstruktur och old->new referenslista innan execution-kontrakt.          |

## Operativ slutsats

- Ingen cleanup-fas är legitim för omedelbar exekvering i bulk.
- Nästa säkra steg är **plan-only mikrotrancher** med färsk evidens per fas.
- Rekommenderad start: Fas B utan B8 (först efter separat preconditions-check).

## Gate results (this docs tranche)

| Gate                                   | Status | Notes                                                                                                                        |
| -------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------------------------- |
| pre-commit/lint för touched docs files | `PASS` | `pre-commit run --files ...` passerade (black/ruff skip för docs, övriga hooks pass).                                        |
| smoke test                             | `PASS` | `python -m pytest -q tests/test_import_smoke_backtest_optuna.py` -> `.` `[100%]`.                                            |
| determinism replay                     | `PASS` | `python -m pytest -q tests/test_backtest_determinism_smoke.py` -> `...` `[100%]`.                                            |
| feature-cache invariance               | `PASS` | `python -m pytest -q tests/test_feature_cache.py tests/test_features_asof_cache_key_deterministic.py` -> `......` `[100%]`.  |
| pipeline invariant                     | `PASS` | `python -m pytest -q tests/test_pipeline_fast_hash_guard.py` -> `...` `[100%]`.                                              |
| scope check                            | `PASS` | `git diff --name-only` + `git status --porcelain`; inga nya out-of-scope ändringar utöver dokumenterade carry-forward paths. |

Kompletterande scope-evidens:

- Carry-forward (pre-existing):
  - `M docs/audits/DEEP_ANALYSIS_REPORT_2026-02-15.md`
  - `?? docs/ops/DOCS_STATUSSYNC_KICKOFF_CONTRACT_2026-02-17.md`
  - `?? docs/ops/DOCS_STATUSSYNC_KICKOFF_REPORT_2026-02-17.md`
- Nya paths i denna tranche:
  - `?? docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_CONTRACT_2026-02-17.md`
  - `?? docs/ops/REPO_CLEANUP_LEGITIMACY_REVIEW_REPORT_2026-02-17.md`

## Status

- Legitimitetsgranskning dokumenterad: `införd` i arbetskopia.
- Execution-kontrakt för faser B/C/D/F/G: fortsatt `föreslagen` tills fasvis avblockering och Opus pre-review.
