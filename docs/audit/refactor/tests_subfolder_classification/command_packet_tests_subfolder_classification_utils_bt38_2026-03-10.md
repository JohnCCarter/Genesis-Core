# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`branch: feature/tests-subfolder-classification-bt33`)
- **Risk:** `LOW` — why: single-candidate utility-test relocation utan runtime- eller configpåverkan.
- **Required Path:** `Full`
- **Objective:** Relocate `test_labeling.py` till `tests/utils/` med no-behavior-change.
- **Candidate:** `tests/test_labeling.py -> tests/utils/test_labeling.py`
- **Base SHA:** `f734e34f`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE`

### Scope IN

- `tests/test_labeling.py`
- `tests/utils/test_labeling.py`
- `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md`
- `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt38_2026-03-10.md`

### Scope OUT

- `src/**`, `mcp_server/**`, `scripts/**`, `config/**`, `.github/workflows/**`
- övriga docs/testflyttar

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q tests/utils/test_labeling.py`
- `python -m pytest -q tests/test_import_smoke_backtest_optuna.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/test_features_asof_cache.py tests/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/test_pipeline_fast_hash_guard.py`

### Review + verification evidence

- Opus pre-code review: **PENDING**
- Gates: **PENDING**
- Opus post-diff audit: **PENDING**
