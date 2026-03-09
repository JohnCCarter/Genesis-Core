## Context Map — Shard A Refactor Batch 2

### Files to modify first

| File                           | Purpose                         | Change candidate                                                                                                    |
| ------------------------------ | ------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `scripts/train/train_model.py` | Script-layer training utilities | Continue structural dedupe: consolidate repeated metrics-payload and JSON-write scaffolding without behavior change |

### Dependencies (read/verify)

| File                                   | Relationship                       |
| -------------------------------------- | ---------------------------------- |
| `core.utils.data_loader`               | Used by `load_features_and_prices` |
| `core.utils.timeframe_filename_suffix` | Filename mapping dependency        |
| `core.ml.labeling`                     | Label generation/alignment helpers |

### Test files

| Test                                         | Coverage                                          |
| -------------------------------------------- | ------------------------------------------------- |
| `tests/test_train_model.py`                  | Direct coverage for script-level training helpers |
| `tests/test_import_smoke_backtest_optuna.py` | Indirect import/runtime smoke for script stack    |

### Additional high-coupling scripts (defer for later batches)

| File                                          | Why risky                                                   |
| --------------------------------------------- | ----------------------------------------------------------- |
| `scripts/optimize/optimizer.py`               | Heavy integration surface and broad optimizer test coupling |
| `scripts/preflight/preflight_optuna_check.py` | Preflight guards and env/flag behavior checks               |
| `scripts/run/run_backtest.py`                 | Determinism-sensitive runner path                           |
| `scripts/run_skill.py`                        | Governance/tooling execution path with dedicated tests      |

### Reference patterns

| File                                          | Pattern                                                     |
| --------------------------------------------- | ----------------------------------------------------------- |
| `scripts/preflight/preflight_optuna_check.py` | Explicit check decomposition and descriptive error messages |
| `scripts/optimize/optimizer.py`               | Structured result summaries and helper function boundaries  |

### Risks

- [ ] Breaking behavior in script helper outputs
- [ ] Drift in error wording that tests assert on
- [ ] Accidental scope expansion into `tests/**` edits without approval

### Batch 2 target details

- Keep runtime outputs and file payload contracts identical.
- No changes to CLI default behavior, env/config interpretation, or exit codes.
- Preferred changes:
  - helper extraction for repeated metrics dictionary construction
  - helper extraction for repeated JSON dump-to-file paths
