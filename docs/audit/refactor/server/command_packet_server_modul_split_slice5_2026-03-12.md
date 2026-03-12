# Command Packet — server modul split slice 5

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH` from `docs/governance_mode.md`
- **Risk:** `LOW` — why: touches a read-only auth/account endpoint cluster plus local cache wiring only, with no config-authority, paper/live-order, or response-contract changes
- **Required Path:** `Full`
- **Objective:** Continue `feature/server-modul-split` by extracting the read-only auth/account route cluster (`/auth/check`, `/account/wallets`, `/account/positions`, `/account/orders`) from `src/core/server.py` into a dedicated account router module while preserving route contracts, cache behavior, and direct-call compatibility via `core.server`.
- **Candidate:** `server modul split slice 5`
- **Base SHA:** `bd483f31`

### Scope

- **Scope IN:**
  - `src/core/server.py`
  - `src/core/server_account_api.py`
  - `tests/integration/test_ui_endpoints.py`
  - `tests/integration/test_account_endpoints.py`
  - `docs/audit/refactor/server/command_packet_server_modul_split_slice5_2026-03-12.md`
  - `docs/audit/refactor/server/context_map_server_modul_split_slice5_2026-03-12.md`
- **Scope OUT:**
  - `src/core/server_status_api.py`
  - `src/core/server_info_api.py`
  - `src/core/server_strategy_api.py`
  - `src/core/server_models_api.py`
  - `/ui`, `/public/*`, `/paper/*`, `/models/reload` endpoints except import/include wiring needed for the new router
  - `mcp_server/**`
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
- **Expected changed files:** `6`
- **Max files touched:** `6`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- The `/auth/check` and `/account/*` paths, methods, response bodies, and status-code behavior must remain identical.
- `core.server.app` must continue exposing the four routes after extraction.
- Preserve compatibility by keeping `core.server.auth_check`, `core.server.account_wallets`, `core.server.account_positions`, and `core.server.account_orders` bound to the extracted functions.
- Preserve compatibility by keeping `core.server._ACCOUNT_CACHE` and `core.server._ACCOUNT_TTL` bound to the extracted shared cache objects.
- Only router extraction is allowed in this slice; no changes to filtering rules, exception redaction, cache TTL semantics, or unrelated routes.

### Repo-local skill evidence

- Repo-local skill spec `repo_clean_refactor` must be reviewed/applied for scope lock, minimal reversible diff, and no-behavior-change guardrails.
- `feature_parity_check` is not required for this slice because no feature computation logic changes.

### Gates required

- `black --check src/core/server.py src/core/server_account_api.py tests/integration/test_ui_endpoints.py tests/integration/test_account_endpoints.py`
- `ruff check src/core/server.py src/core/server_account_api.py tests/integration/test_ui_endpoints.py tests/integration/test_account_endpoints.py`
- Focused selectors:
  - `tests/integration/test_ui_endpoints.py`
  - `tests/integration/test_account_endpoints.py`
- Determinism replay selector:
  - `tests/backtest/test_backtest_determinism_smoke.py`
- Determinism / invariant selectors:
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Security selector:
  - `bandit -r src -c bandit.yaml`

### Stop Conditions

- Scope drift beyond the auth/account route cluster, packet/context-map docs, and direct compatibility test coverage
- Any `/auth/check` or `/account/*` contract drift
- Cache TTL or exception-redaction semantics drift
- Determinism / pipeline invariant regression

### Output required

- **Implementation Report** with scope, exact gates, and residual risks
- **PR evidence template** after Opus post-diff audit

### Verification notes

- `tests/integration/test_ui_endpoints.py` must keep direct-call compatibility proof for `auth_check()`.
- Focused touched-flow proof must include both direct-call and route-level verification for `/auth/check` under monkeypatched `srv.bfx_read` helpers.
- `tests/integration/test_account_endpoints.py` must keep the existing route-level filtering and exception-redaction proofs green.
- If shared cache objects move to the extracted module, tests must lock `_ACCOUNT_CACHE` identity via `core.server` aliases; matching values alone is insufficient.
- The extracted module must import `core.io.bitfinex.read_helpers` as module alias `bfx_read`; symbol-level imports of `get_wallets`, `get_positions`, or `get_orders` are out of scope for this slice because they would break existing `srv.bfx_read` monkeypatch behavior.

### Gate results

- `python -m black --check src/core/server.py src/core/server_account_api.py tests/integration/test_ui_endpoints.py tests/integration/test_account_endpoints.py` — `PASS`
- `python -m ruff check src/core/server.py src/core/server_account_api.py tests/integration/test_ui_endpoints.py tests/integration/test_account_endpoints.py` — `PASS`
- `python -m pytest tests/integration/test_ui_endpoints.py tests/integration/test_account_endpoints.py tests/backtest/test_backtest_determinism_smoke.py tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q` — `PASS`
- `python -m bandit -r src -c bandit.yaml -q` — `PASS` (warning only: existing `nosec` acknowledgement for `B608`, no failed findings)
