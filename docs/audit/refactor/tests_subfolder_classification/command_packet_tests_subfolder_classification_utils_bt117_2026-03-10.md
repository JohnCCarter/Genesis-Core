# COMMAND PACKET

- **Mode:** `RESEARCH`
- **Risk:** `LOW`
- **Required Path:** `Full`
- **Objective:** Relocate `test_remote_server_fastmcp_sse_alias.py` till `tests/utils/` med no-behavior-change.
- **Candidate:** `tests/test_remote_server_fastmcp_sse_alias.py -> tests/utils/test_remote_server_fastmcp_sse_alias.py`
- **Category:** `tooling`
- **Constraints:** `NO BEHAVIOR CHANGE`

### Scope IN

- `tests/test_remote_server_fastmcp_sse_alias.py`
- `tests/utils/test_remote_server_fastmcp_sse_alias.py`
- `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md`
- `docs/audit/refactor/command_packet_tests_subfolder_classification_utils_bt117_2026-03-10.md`

### Scope OUT

- `src/**`, `mcp_server/**`, `scripts/**`, `config/**`, `.github/workflows/**`

### Gates required

- `python -m pytest -q tests/utils/test_remote_server_fastmcp_sse_alias.py`

### Review + verification evidence

- Gates: **NOT RUN (shell runtime blocked: pwsh.exe unavailable in agent)**
- Implementation: **DONE** (path move applied + plan row updated)
