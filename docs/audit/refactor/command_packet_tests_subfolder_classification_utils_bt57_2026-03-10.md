# COMMAND PACKET

- **Mode:** `RESEARCH`
- **Risk:** `LOW` — single-candidate utility-test relocation.
- **Required Path:** `Full`
- **Objective:** Relocate `test_ws_public_min.py` till `tests/utils/` med no-behavior-change.
- **Candidate:** `tests/test_ws_public_min.py -> tests/utils/test_ws_public_min.py`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE`

### Scope IN

- `tests/test_ws_public_min.py`
- `tests/utils/test_ws_public_min.py`
- `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md`
- `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt57_2026-03-10.md`

### Scope OUT

- `src/**`, `mcp_server/**`, `scripts/**`, `config/**`, `.github/workflows/**`

### Gates required

- `python -m pre_commit run --all-files`
- `python -m ruff check .`
- `python -m pytest -q tests/utils/test_ws_public_min.py`

### Review + verification evidence

- Gates: **NOT RUN (shell runtime blocked: pwsh.exe unavailable in agent)**
- Implementation: **DONE** (path move applied + plan row updated)
