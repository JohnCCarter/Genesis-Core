# Command Packet — server modul split slice 2

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH` from `docs/governance_mode.md`
- **Risk:** `MED` — why: touches runtime server assembly in `src/core/server.py` and two public FastAPI GET route wirings, but only for simple read-only info endpoints
- **Required Path:** `Full`
- **Objective:** Continue `feature/server-modul-split` with a no-behavior-change slice by extracting `/paper/whitelist` and `/observability/dashboard` from `src/core/server.py` into a dedicated info router module while preserving route contracts and `core.server.app` wiring.
- **Candidate:** `server modul split slice 2`
- **Base SHA:** `042be63b`

### Scope

- **Scope IN:**
  - `src/core/server.py`
  - `src/core/server_info_api.py`
  - `tests/integration/test_ui_endpoints.py`
  - `tests/utils/test_observability.py`
  - `docs/audit/refactor/server/command_packet_server_modul_split_slice2_2026-03-12.md`
  - `docs/audit/refactor/server/context_map_server_modul_split_slice2_2026-03-12.md`
- **Scope OUT:**
  - `src/core/server_strategy_api.py`
  - all other `/health`, `/ui`, `/public/*`, `/auth/*`, `/account/*`, `/paper/submit`, `/paper/estimate`, `/debug/auth`, `/models/reload` endpoints except import/include wiring needed for the new router
  - `mcp_server/**`
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
  - **Expected changed files:** `6`
  - **Max files touched:** `6`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- The `/paper/whitelist` path and sorted `{"symbols": ...}` payload must remain identical.
- The `/observability/dashboard` path and `get_dashboard()` response passthrough must remain identical.
- Route exposure and HTTP contracts through `core.server.app` must remain equivalent; only minimal router import/include wiring may change.
- Only router extraction is allowed in this slice; no health/UI/account/paper-trading/MCP/config-authority refactors.

### Planned gates

- `black --check src/core/server.py src/core/server_info_api.py tests/integration/test_ui_endpoints.py tests/utils/test_observability.py`
- `ruff check src/core/server.py src/core/server_info_api.py tests/integration/test_ui_endpoints.py tests/utils/test_observability.py`
- Focused route selectors:
  - `tests/integration/test_ui_endpoints.py`
  - `tests/utils/test_observability.py`
  - `tests/integration/test_config_endpoints.py`
  - `tests/utils/test_health.py`
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
- Any HTTP contract drift for `/paper/whitelist` or `/observability/dashboard`
- App assembly breakage that affects `/config/runtime` or `/health`
- Determinism / pipeline invariant regression

### Output required

- **Implementation Report** with scope, exact gates, and residual risks
- **PR evidence template** after Opus post-diff audit

### Verification notes

- `tests/integration/test_ui_endpoints.py` will lock the `/paper/whitelist` route contract and sorted whitelist semantics.
- `tests/utils/test_observability.py` must lock both `/observability/dashboard` shape and direct passthrough of the sentinel payload from `core.server_info_api.get_dashboard`.
- `tests/integration/test_config_endpoints.py` and `tests/utils/test_health.py` are app-assembly smoke checks guarding `core.server.app` after router wiring changes.
- `TEST_SPOT_WHITELIST` must have a single source of truth after extraction; do not duplicate the constant to avoid drift.

### Gate results

- `python -m black --check src/core/server.py src/core/server_info_api.py tests/integration/test_ui_endpoints.py tests/utils/test_observability.py` — `PASS`
- `python -m ruff check src/core/server.py src/core/server_info_api.py tests/integration/test_ui_endpoints.py tests/utils/test_observability.py` — `PASS`
- `python -m pytest tests/integration/test_ui_endpoints.py tests/utils/test_observability.py tests/integration/test_config_endpoints.py tests/utils/test_health.py tests/backtest/test_backtest_determinism_smoke.py tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q` — `PASS`
- `python -m bandit -r src -c bandit.yaml -q` — `PASS` (warning only: existing `nosec` acknowledgement for `B608`, no failed findings)
