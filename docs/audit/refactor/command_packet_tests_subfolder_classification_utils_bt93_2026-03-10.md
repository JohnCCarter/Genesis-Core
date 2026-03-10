# COMMAND PACKET

- **Mode:** `RESEARCH`
- **Risk:** `LOW` — single test-file relocation only.
- **Required Path:** `Full`
- **Objective:** Relocate `test_optuna_rdbstorage_engine_kwargs.py` to `tests/utils/` with no behavior change.
- **Candidate:** `tests/test_optuna_rdbstorage_engine_kwargs.py -> tests/utils/test_optuna_rdbstorage_engine_kwargs.py`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE`

### Scope IN

- `tests/test_optuna_rdbstorage_engine_kwargs.py`
- `tests/utils/test_optuna_rdbstorage_engine_kwargs.py`
- `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md`
- `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt93_2026-03-10.md`

### Scope OUT

- `src/**`, `scripts/**`, `config/**`, `.github/workflows/**`

### Gates

- Coordinator gates required (not executed in edit-only mode).

### Gate status

- `NOT RUN (edit-only mode by coordinator instruction)`

`READY_FOR_COORDINATOR_GATES`
