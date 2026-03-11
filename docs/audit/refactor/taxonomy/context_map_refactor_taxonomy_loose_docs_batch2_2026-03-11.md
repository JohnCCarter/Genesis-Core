## Context Map — refactor docs taxonomy (batch-2 loose docs)

### Files to Modify

| File(s)                                                                 | Purpose                   | Changes Needed                                                |
| ----------------------------------------------------------------------- | ------------------------- | ------------------------------------------------------------- |
| `docs/audit/refactor/*_signoff_*.md`                                    | Candidate signoff docs    | Move to `docs/audit/refactor/candidates/`                     |
| `docs/audit/refactor/test_prototypes_review_2026-03-06.md`              | Candidate review note     | Move to `docs/audit/refactor/candidates/`                     |
| `docs/audit/refactor/shard_a_breadth_audit_report_2026-03-06.md`        | Shard A audit report      | Move to `docs/audit/refactor/reports/`                        |
| `docs/audit/refactor/genesis_refactor_agent_overlay_shard_*.md`         | Shard overlays            | Move to `docs/audit/refactor/overlays/`                       |
| `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md` | Tests classification plan | Move to `docs/audit/refactor/tests_subfolder_classification/` |

### Canonical root anchors (stay in root)

- `docs/audit/refactor/readme.md`
- `docs/audit/refactor/hard_rules_refactor.md`

### Dependencies (may need updates)

| File                                                                     | Relationship                                      |
| ------------------------------------------------------------------------ | ------------------------------------------------- |
| `docs/audit/refactor/misc/context_map_refactor_docs_2026-03-06.md`       | References old overlay root path                  |
| `docs/audit/refactor/overlays/genesis_refactor_agent_overlay_shard_a.md` | References `hard_rules_refactor.md` root baseline |

### Test Files

| Test                                                    | Coverage                    |
| ------------------------------------------------------- | --------------------------- |
| `tests/governance/test_import_smoke_backtest_optuna.py` | smoke selector              |
| `tests/backtest/test_backtest_determinism_smoke.py`     | determinism selector        |
| `tests/utils/test_feature_cache.py`                     | cache invariance selector   |
| `tests/governance/test_pipeline_fast_hash_guard.py`     | pipeline invariant selector |

### Scope guard

- Move only files under main-tree `docs/audit/refactor/`.
- Exclude `.claude/worktrees/**` entirely.

### Execution requirement

- Generate deterministic 1:1 move manifest before moving files.
- Run collision preflight: no duplicate target, no overwrite.
