# Command Packet — server modul split slice 6

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH` from `docs/governance_mode.md`
- **Risk:** `LOW` — why: touches one pure read-only UI endpoint and app wiring only, with no shared runtime state, exchange I/O, config-authority behavior, or response-contract changes
- **Required Path:** `Full`
- **Objective:** Continue `feature/server-modul-split` by extracting the `/ui` route from `src/core/server.py` into a dedicated UI router module while preserving the exact HTML response and route exposure via `core.server.app`.
- **Candidate:** `server modul split slice 6`
- **Base SHA:** `c23e1191`

### Scope

- **Scope IN:**
  - `src/core/server.py`
  - `src/core/server_ui_api.py`
  - `tests/integration/test_ui_endpoints.py`
  - `docs/audit/refactor/server/command_packet_server_modul_split_slice6_2026-03-12.md`
  - `docs/audit/refactor/server/context_map_server_modul_split_slice6_2026-03-12.md`
- **Scope OUT:**
  - `src/core/server_status_api.py`
  - `src/core/server_info_api.py`
  - `src/core/server_strategy_api.py`
  - `src/core/server_models_api.py`
  - `src/core/server_account_api.py`
  - `/public/*`, `/paper/*` endpoints except import/include wiring needed for the new router
  - `mcp_server/**`
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
- **Expected changed files:** `5`
- **Max files touched:** `5`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- The `/ui` path, method, response class, and HTML response body must remain identical.
- `core.server.app` must continue exposing `/ui` after extraction.
- Preserve compatibility by keeping `core.server.ui_page` bound to the extracted function.
- Only router extraction is allowed in this slice; no HTML/JS content edits, no UI behavior changes, and no unrelated route changes.

### Repo-local skill evidence

- Repo-local skill spec `repo_clean_refactor` must be reviewed/applied for scope lock, minimal reversible diff, and no-behavior-change guardrails.
- `feature_parity_check` is not required for this slice because no feature computation logic changes.

### Gates required

- `black --check src/core/server.py src/core/server_ui_api.py tests/integration/test_ui_endpoints.py`
- `ruff check src/core/server.py src/core/server_ui_api.py tests/integration/test_ui_endpoints.py`
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

- Scope drift beyond the `/ui` route, packet/context-map docs, and direct route-compatibility test coverage
- Any `/ui` contract drift or HTML content drift
- App assembly breakage affecting existing extracted routers
- Determinism / pipeline invariant regression

### Output required

- **Implementation Report** with scope, exact gates, and residual risks
- **PR evidence template** after Opus post-diff audit

### Verification notes

- `tests/integration/test_ui_endpoints.py` must continue proving `GET /ui` returns status `200` and contains `"Minimal test"`.
- Because `core.server.ui_page` is preserved as a compatibility alias in this no-behavior-change slice, tests must also lock alias identity and direct-return parity against the extracted handler.
- The extracted route must keep `response_class=HTMLResponse` unchanged.
- `tests/integration/test_ui_endpoints.py` must also prove the response header still starts with `text/html`.
- The HTML/JS payload must be moved byte-for-byte except for surrounding module indentation.

### Gate results

- `python -m black --check src/core/server.py src/core/server_ui_api.py tests/integration/test_ui_endpoints.py` — `PASS`
- `python -m ruff check src/core/server.py src/core/server_ui_api.py tests/integration/test_ui_endpoints.py` — `PASS`
- `python -m pytest tests/integration/test_ui_endpoints.py tests/backtest/test_backtest_determinism_smoke.py tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q` — `PASS` (`26 passed`)
- `python -m bandit -r src -c bandit.yaml -q` — `PASS` (warning only: existing `nosec` acknowledgement for `B608`, no failed findings)
