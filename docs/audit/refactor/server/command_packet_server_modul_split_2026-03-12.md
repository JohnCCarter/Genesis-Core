# Command Packet — server modul split

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH` from `docs/governance_mode.md`
- **Risk:** `HIGH` — why: touches runtime server assembly in `src/core/server.py` and public FastAPI route wiring
- **Required Path:** `Full`
- **Objective:** Start `feature/server-modul-split` with a minimal no-behavior-change slice by extracting the `/strategy/evaluate` route from `src/core/server.py` into a dedicated router module while preserving the current HTTP contract and app wiring.
- **Candidate:** `server modul split slice 1`
- **Base SHA:** `d5e61f10`

### Scope

- **Scope IN:**
  - `src/core/server.py`
  - `src/core/server_strategy_api.py`
  - `tests/integration/test_ui_endpoints.py`
  - `docs/audit/refactor/server/command_packet_server_modul_split_2026-03-12.md`
  - `docs/audit/refactor/server/context_map_server_modul_split_2026-03-12.md`
- **Scope OUT:**
  - `src/core/server_config_api.py`
  - all other `/paper/*`, `/account/*`, `/auth/*`, `/health`, `/observability`, `/ui` endpoints except import/include wiring needed for the new router
  - `mcp_server/**`
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
  - **Expected changed files:** `5`
  - **Max files touched:** `5`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- The `/strategy/evaluate` path, request/response payloads, invalid-candles error payload, and `evaluate_pipeline(...)` call semantics must remain identical.
- `core.server.app` must continue to expose the same route through `TestClient(app)`.
- Only router extraction is allowed in this slice; no paper/account/MCP/config-authority refactors.

### Planned gates

- `black --check src/core/server.py src/core/server_strategy_api.py`
- `ruff check src/core/server.py src/core/server_strategy_api.py`
- Focused route selectors:
  - `tests/integration/test_ui_endpoints.py`
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

- Scope drift beyond the two runtime files plus evidence docs
- Any HTTP contract drift for `/strategy/evaluate`
- App assembly breakage that affects `/config/runtime` or `/health`
- Determinism / pipeline invariant regression

### Output required

- **Implementation Report** with scope, exact gates, and residual risks
- **PR evidence template** after Opus post-diff audit

### Verification notes

- `tests/integration/test_ui_endpoints.py` is the direct route-contract verifier for `/strategy/evaluate`.
- `tests/integration/test_config_endpoints.py` and `tests/utils/test_health.py` are app-assembly smoke checks guarding `core.server.app` after router wiring changes.
- Route parity evidence must include:
  - a direct delegation test that monkeypatches `evaluate_pipeline` in the route module
  - an invalid-candles case with mismatched list lengths

### Gate results

- `python -m black --check src/core/server.py src/core/server_strategy_api.py tests/integration/test_ui_endpoints.py` — `PASS`
- `python -m ruff check src/core/server.py src/core/server_strategy_api.py tests/integration/test_ui_endpoints.py` — `PASS`
- `python -m pytest tests/integration/test_ui_endpoints.py tests/integration/test_config_endpoints.py tests/utils/test_health.py tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q` — `PASS`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py` — `PASS`
- `python -m bandit -r src -c bandit.yaml -q` — `PASS` (warning only: existing `nosec` acknowledgement for `B608`, no failed findings)
