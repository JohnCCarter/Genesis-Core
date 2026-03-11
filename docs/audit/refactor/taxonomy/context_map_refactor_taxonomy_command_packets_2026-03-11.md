## Context Map — refactor docs taxonomy (batch-1)

### Files to Modify

| File(s)                                                                 | Purpose                            | Changes Needed                                                |
| ----------------------------------------------------------------------- | ---------------------------------- | ------------------------------------------------------------- |
| `docs/audit/refactor/command_packet_candidate*.md`                      | Candidate-level governance packets | Move to `docs/audit/refactor/candidates/`                     |
| `docs/audit/refactor/command_packet_tests_subfolder_classification*.md` | Test-classification packet family  | Move to `docs/audit/refactor/tests_subfolder_classification/` |
| `docs/audit/refactor/command_packet_archive_audit*.md`                  | Archive-audit packet family        | Move to `docs/audit/refactor/archive_audit/`                  |
| `docs/audit/refactor/command_packet_shard_*.md`                         | Shard packet family                | Move to `docs/audit/refactor/shards/`                         |
| `docs/audit/refactor/command_packet_ci_fix*.md`                         | CI-fix packet                      | Move to `docs/audit/refactor/misc/`                           |
| `docs/audit/refactor/command_packet_merge_*.md`                         | Merge packet                       | Move to `docs/audit/refactor/misc/`                           |
| `docs/audit/refactor/command_packet_refactor_docs*.md`                  | Refactor-doc packet                | Move to `docs/audit/refactor/misc/`                           |
| `docs/audit/refactor/context_map_*.md`                                  | Root-level context maps            | Move to `docs/audit/refactor/misc/`                           |
| `docs/audit/refactor/candidate*_*.md`                                   | Candidate signoff docs             | Move to `docs/audit/refactor/candidates/`                     |

### Dependencies (may need updates)

| File                              | Relationship                                    |
| --------------------------------- | ----------------------------------------------- |
| `docs/audit/refactor/readme.md`   | May need path updates if file lists are present |
| `docs/audit/refactor/README.md`   | Policy entrypoint; keep as root index           |
| `docs/audit/refactor/evidence/**` | Keep untouched                                  |

**Scope guard:** Move only files under main-tree `docs/audit/refactor/`; explicitly exclude `.claude/worktrees/**`.

### Test Files

| Test                                                    | Coverage                                          |
| ------------------------------------------------------- | ------------------------------------------------- |
| `tests/governance/test_import_smoke_backtest_optuna.py` | Smoke import sanity (no runtime changes expected) |

### Reference Patterns

| File                                  | Pattern                                            |
| ------------------------------------- | -------------------------------------------------- |
| `docs/audit/refactor/features_asof/*` | Task-specific docs isolated in dedicated subfolder |
| `docs/audit/cleanup/*`                | Phase-specific segregation by top-level folder     |

### Risk Assessment

- [ ] Breaking changes to public API
- [ ] Database migrations needed
- [ ] Configuration changes required

### Move Manifest (family-level)

- `command_packet_candidate*` -> `candidates/`
- `command_packet_tests_subfolder_classification*` -> `tests_subfolder_classification/`
- `command_packet_archive_audit*` -> `archive_audit/`
- `command_packet_shard_*` -> `shards/`
- `command_packet_ci_fix*`, `command_packet_merge_*`, `command_packet_refactor_docs*` -> `misc/`
- `context_map_*` -> `misc/`
- `candidate*_*.md` -> `candidates/`

### Execution requirement

- Generate and persist a deterministic **1:1 move manifest** (`source -> target`) before moving files.
- Run collision preflight (`no existing target overwrite`, `no duplicate destination basenames`).
