# Command Packet — server modul split slice 3

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH` from `docs/governance_mode.md`
- **Risk:** `MED` — why: touches runtime server assembly plus config/status route wiring for `/health` and `/debug/auth`, but remains read-only and no-behavior-change
- **Required Path:** `Full`
- **Objective:** Continue `feature/server-modul-split` with a no-behavior-change slice by extracting `/health` and `/debug/auth` from `src/core/server.py` into a dedicated status router module while preserving route contracts, masking behavior, and equivalent exposure through `core.server.app`.
- **Candidate:** `server modul split slice 3`
- **Base SHA:** `56987e3d`

### Scope

- **Scope IN:**
  - `src/core/server.py`
  - `src/core/server_status_api.py`
  - `tests/utils/test_health.py`
  - `tests/integration/test_ui_endpoints.py`
  - `docs/audit/refactor/server/command_packet_server_modul_split_slice3_2026-03-12.md`
  - `docs/audit/refactor/server/context_map_server_modul_split_slice3_2026-03-12.md`
- **Scope OUT:**
  - `src/core/server_info_api.py`
  - `src/core/server_strategy_api.py`
  - all other `/ui`, `/public/*`, `/auth/check`, `/account/*`, `/paper/*`, `/models/reload` endpoints except import/include wiring needed for the new router
  - `mcp_server/**`
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
- **Expected changed files:** `6`
- **Max files touched:** `6`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- The `/health` success and error payloads must remain identical, including `503` on config-read failure.
- The `/debug/auth` response shape and masking semantics (`present`, `length`, `suffix`) must remain identical.
- Route exposure and HTTP contracts through `core.server.app` must remain equivalent; only minimal router import/include wiring may change.
- `core.server._AUTH`, `core.server.health`, and `core.server.debug_auth` must remain available for existing tests and monkeypatches.
- Only router extraction is allowed in this slice; no UI/public/account/paper/MCP/config-authority behavior changes.

### Planned gates

- `black --check src/core/server.py src/core/server_status_api.py tests/utils/test_health.py tests/integration/test_ui_endpoints.py`
- `ruff check src/core/server.py src/core/server_status_api.py tests/utils/test_health.py tests/integration/test_ui_endpoints.py`
- Focused route selectors:
  - `tests/utils/test_health.py`
  - `tests/integration/test_ui_endpoints.py`
  - `tests/integration/test_config_endpoints.py`
- Security selector:
  - `bandit -r src -c bandit.yaml`
- Determinism replay selector:
  - `tests/backtest/test_backtest_determinism_smoke.py`
- Determinism / invariant selectors:
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Stop Conditions

- Scope drift beyond the two runtime files plus evidence docs/test lock
- Any HTTP contract drift for `/health` or `/debug/auth`
- App assembly breakage that affects `/config/runtime` or route availability
- Determinism / pipeline invariant regression

### Output required

- **Implementation Report** with scope, exact gates, and residual risks
- **PR evidence template** after Opus post-diff audit

### Verification notes

- `tests/utils/test_health.py` and `tests/integration/test_ui_endpoints.py` must lock both the healthy path exact payload and the `503` error payload for `/health`.
- `tests/utils/test_health.py` must also lock the legacy `/health` error logger identity (`core.server`) so the extraction does not change observable warning provenance.
- `tests/integration/test_ui_endpoints.py` must lock both direct function compatibility and route-contract parity for `/debug/auth`.
- `_AUTH` must remain a single shared object reachable through `core.server._AUTH` after extraction.
- Focused route selectors must include direct parity proof for `/debug/auth` and explicit healthy-payload proof for `/health`.

### Gate results

- `python -m black --check src/core/server.py src/core/server_status_api.py tests/utils/test_health.py tests/integration/test_ui_endpoints.py` — `PASS`
- `python -m ruff check src/core/server.py src/core/server_status_api.py tests/utils/test_health.py tests/integration/test_ui_endpoints.py` — `PASS`
- `python -m pytest tests/utils/test_health.py tests/integration/test_ui_endpoints.py tests/integration/test_config_endpoints.py tests/backtest/test_backtest_determinism_smoke.py tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q` — `PASS`
- `python -m bandit -r src -c bandit.yaml -q` — `PASS` (warning only: existing `nosec` acknowledgement for `B608`, no failed findings)

### Post-audit remediation

- Fixed the only post-audit blocker by restoring the `/health` warning logger name to `core.server` inside `src/core/server_status_api.py`.
- Added a focused regression test in `tests/utils/test_health.py` to lock the legacy logger identity on the `/health` failure path.
