# Command Packet — server modul split slice 9

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH` from `docs/governance_mode.md`
- **Risk:** `HIGH` — why: touches the remaining `/paper/*` order-submission endpoint, including whitelist validation, size clamping, optional wallet-cap behavior, upstream signed requests, and error handling on a paper/live-edge-adjacent API surface
- **Required Path:** `Full`
- **Objective:** Continue `feature/server-modul-split` by extracting the `/paper/submit` route from `src/core/server.py` into the existing `src/core/server_paper_api.py` module while preserving route contract, helper/default semantics, wallet-cap behavior, and direct-call compatibility via `core.server`.
- **Candidate:** `server modul split slice 9`
- **Base SHA:** `5f7b78a7`

### Scope

- **Scope IN:**
  - `src/core/server.py`
  - `src/core/server_paper_api.py`
  - `tests/integration/test_ui_endpoints.py`
  - `docs/audit/refactor/server/command_packet_server_modul_split_slice9_2026-03-12.md`
  - `docs/audit/refactor/server/context_map_server_modul_split_slice9_2026-03-12.md`
- **Scope OUT:**
  - `src/core/server_public_api.py`
  - `src/core/server_account_api.py`
  - `src/core/server_ui_api.py`
  - `src/core/server_models_api.py`
  - `src/core/server_status_api.py`
  - `src/core/server_info_api.py`
  - `src/core/server_strategy_api.py`
  - `/paper/estimate` behavior except reuse through the already extracted `server_paper_api.py` module
  - `mcp_server/**`
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
  - unrelated unstaged formatting drift in `docs/audit/refactor/server/context_map_server_modul_split_slice6_2026-03-12.md`
- **Expected changed files:** `5`
- **Max files touched:** `5`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- The `/paper/submit` path, method, request/response contract, whitelist behavior, size-clamp semantics, wallet-cap semantics, and upstream error-shape semantics must remain identical.
- The request contract must remain `payload: dict = Body(...)`, keep TEST symbols in the signed-request body, and preserve `amount` as a sign-correct string for LONG/SHORT orders.
- `core.server.app` must continue exposing `/paper/submit` after extraction.
- Preserve compatibility by keeping `core.server.paper_submit` bound to the extracted function and `core.server.paper_router` bound to the extracted router.
- Preserve the legacy monkeypatch surface for focused tests and hidden Python callers: patching `core.server.get_settings`, `core.server.bfx_read.get_wallets`, `core.server.get_exchange_client`, `core.server.MIN_ORDER_SIZE`, `core.server.MIN_ORDER_MARGIN`, `core.server._real_from_test`, `core.server._base_ccy_from_test`, and `core.server.TEST_SPOT_WHITELIST` must still affect `core.server.paper_submit` behavior after extraction.
- The extracted module must not snapshot compatibility surfaces at import time; lookups for `core.server.get_settings`, `core.server.get_exchange_client`, `core.server.MIN_ORDER_SIZE`, `core.server.MIN_ORDER_MARGIN`, `core.server._real_from_test`, `core.server._base_ccy_from_test`, `core.server.TEST_SPOT_WHITELIST`, and `core.server.bfx_read.get_wallets` must remain late-bound so existing monkeypatches continue to affect behavior.
- Only `/paper/submit` extraction is allowed in this slice; no `/paper/estimate` contract changes, no new wallet-cap behavior, and no UI code changes.

### Repo-local skill evidence

- Repo-local skill spec `repo_clean_refactor` must be reviewed/applied for scope lock, minimal reversible diff, and no-behavior-change guardrails.
- `feature_parity_check` is not required for this slice because no feature computation logic changes.

### Gates required

- `black --check src/core/server.py src/core/server_paper_api.py tests/integration/test_ui_endpoints.py`
- `ruff check src/core/server.py src/core/server_paper_api.py tests/integration/test_ui_endpoints.py`
- Focused selectors:
  - `tests/integration/test_ui_endpoints.py`
- Determinism replay selector:
  - `tests/backtest/test_backtest_determinism_smoke.py`
- Determinism / invariant selectors:
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Security selector:
  - `bandit -r src -c bandit.yaml`

### Stop Conditions

- Scope drift beyond `/paper/submit`, packet/context-map docs, and direct compatibility test coverage
- Any `/paper/submit` contract drift, clamp drift, wallet-cap drift, or upstream error-shape drift
- Loss of compatibility for direct `core.server.paper_submit` callers or monkeypatch behavior through `core.server`
- Determinism / pipeline invariant regression

### Output required

- **Implementation Report** with scope, exact gates, and residual risks
- **PR evidence template** after Opus post-diff audit

### Verification notes

- `tests/integration/test_ui_endpoints.py` must keep route-level proof that `/paper/submit` preserves whitelist rejection, successful signed-request parity, and wallet-cap helper semantics.
- Focused touched-flow proof must show direct-call and route-level parity under monkeypatched `core.server` helper surfaces, including exactly one registered `/paper/submit` route.
- Focused proof must explicitly lock the `invalid_action_or_size` payload shape for both direct-call and route-level access.
- Focused proof must explicitly lock the `HTTPStatusError` branch shape (`ok=False`, `error="bitfinex_http_error"`, `status`, `error_id`) and the generic exception branch shape (`ok=False`, `error="internal_error"`, `error_id`) after extraction.
- Compatibility proof must lock `core.server.paper_submit is core.server_paper_api.paper_submit` and `core.server.paper_router is core.server_paper_api.router` after extraction.

### Gate results

- `python -m black --check src/core/server.py src/core/server_paper_api.py tests/integration/test_ui_endpoints.py` — `PASS`
- `python -m ruff check src/core/server.py src/core/server_paper_api.py tests/integration/test_ui_endpoints.py` — `PASS`
- `python -m pytest tests/integration/test_ui_endpoints.py tests/backtest/test_backtest_determinism_smoke.py tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q` — `PASS` (`33 passed`)
- `python -m bandit -r src -c bandit.yaml -q` — `PASS` (warning only: existing `nosec` acknowledgement for `B608`, no failed findings)
