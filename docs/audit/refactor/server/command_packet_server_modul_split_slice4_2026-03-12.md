# Command Packet — server modul split slice 4

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH` from `docs/governance_mode.md`
- **Risk:** `LOW` — why: touches one small runtime endpoint and app wiring only, with no config-authority, trading-path, or response-contract changes; handler semantics remain limited to `ModelRegistry.clear_cache()` delegation
- **Required Path:** `Full`
- **Objective:** Continue `feature/server-modul-split` with the next smallest no-behavior-change slice by extracting `/models/reload` from `src/core/server.py` into a dedicated models router module while preserving the endpoint contract and compatibility via `core.server.app`.
- **Candidate:** `server modul split slice 4`
- **Base SHA:** `bd04b723`

### Scope

- **Scope IN:**
  - `src/core/server.py`
  - `src/core/server_models_api.py`
  - `tests/integration/test_ui_endpoints.py`
  - `docs/audit/refactor/server/command_packet_server_modul_split_slice4_2026-03-12.md`
  - `docs/audit/refactor/server/context_map_server_modul_split_slice4_2026-03-12.md`
- **Scope OUT:**
  - `src/core/server_status_api.py`
  - `src/core/server_info_api.py`
  - `src/core/server_strategy_api.py`
  - `src/core/server_config_api.py`
  - `/ui`, `/public/*`, `/auth/check`, `/account/*`, `/paper/*` endpoints except import/include wiring needed for the new router
  - `mcp_server/**`
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
- **Expected changed files:** `5`
- **Max files touched:** `5`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- The `/models/reload` path, method, response body, and status code behavior must remain identical.
- `core.server.app` must continue exposing `/models/reload` after extraction.
- Preserve compatibility by keeping `core.server.reload_models` bound to the extracted function.
- Only router extraction is allowed in this slice; no changes to model-registry semantics, cache invalidation logic, or unrelated routes.

### Repo-local skill evidence

- Repo-local skill spec `repo_clean_refactor` reviewed/applied for scope lock, minimal reversible diff, and no-behavior-change guardrails.
- `feature_parity_check` is not required for this slice because no feature computation logic changes.

### Gates required

- `black --check src/core/server.py src/core/server_models_api.py tests/integration/test_ui_endpoints.py`
- `ruff check src/core/server.py src/core/server_models_api.py tests/integration/test_ui_endpoints.py`
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

- Scope drift beyond the reload route, packet/context-map docs, and direct route-compatibility test coverage
- Any `/models/reload` contract drift
- App assembly breakage affecting existing extracted routers
- Determinism / pipeline invariant regression

### Output required

- **Implementation Report** with scope, exact gates, and residual risks
- **PR evidence template** after Opus post-diff audit

### Verification notes

- `tests/integration/test_ui_endpoints.py` must lock `POST /models/reload` to status `200` and exact JSON body `{"ok": True, "message": "Model cache cleared"}`.
- `tests/integration/test_ui_endpoints.py` must patch `ModelRegistry.clear_cache()` and prove the route still delegates exactly once per call.
- Because `core.server.reload_models` is preserved as a compatibility alias in this no-behavior-change slice, tests must lock alias identity or direct-call parity against the extracted handler.
- The extracted module must keep cache-clear semantics identical by delegating to `ModelRegistry.clear_cache()` with no extra side effects.

### Gate results

- `python -m black --check src/core/server.py src/core/server_models_api.py tests/integration/test_ui_endpoints.py` — `PASS`
- `python -m ruff check src/core/server.py src/core/server_models_api.py tests/integration/test_ui_endpoints.py` — `PASS`
- `python -m pytest tests/integration/test_ui_endpoints.py tests/backtest/test_backtest_determinism_smoke.py tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q` — `PASS`
- `python -m bandit -r src -c bandit.yaml -q` — `PASS` (warning only: existing `nosec` acknowledgement for `B608`, no failed findings)
