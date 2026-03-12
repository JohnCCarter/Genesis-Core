# Command Packet — server modul split slice 7

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH` from `docs/governance_mode.md`
- **Risk:** `LOW` — why: touches one read-only public candles endpoint plus its local cache wiring, with no config-authority, paper/live-order, or response-contract changes intended
- **Required Path:** `Full`
- **Objective:** Continue `feature/server-modul-split` by extracting the `/public/candles` route from `src/core/server.py` into a dedicated public router module while preserving route contract, cache behavior, and direct-call compatibility via `core.server`.
- **Candidate:** `server modul split slice 7`
- **Base SHA:** `3efe6f05`

### Scope

- **Scope IN:**
  - `src/core/server.py`
  - `src/core/server_public_api.py`
  - `tests/integration/test_ui_endpoints.py`
  - `docs/audit/refactor/server/command_packet_server_modul_split_slice7_2026-03-12.md`
  - `docs/audit/refactor/server/context_map_server_modul_split_slice7_2026-03-12.md`
- **Scope OUT:**
  - `src/core/server_status_api.py`
  - `src/core/server_info_api.py`
  - `src/core/server_strategy_api.py`
  - `src/core/server_models_api.py`
  - `src/core/server_account_api.py`
  - `src/core/server_ui_api.py`
  - `/paper/*` endpoints except import/include wiring needed for the new router
  - `mcp_server/**`
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
  - unrelated unstaged formatting drift in `docs/audit/refactor/server/context_map_server_modul_split_slice6_2026-03-12.md`
- **Expected changed files:** `5`
- **Max files touched:** `5`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- The `/public/candles` path, method, query parameters, response body shape, and normalization semantics must remain identical.
- `core.server.app` must continue exposing `/public/candles` after extraction.
- Preserve compatibility by keeping `core.server.public_candles` bound to the extracted function.
- Preserve compatibility by keeping `core.server._CANDLES_CACHE` aliased to the extracted shared cache dict and `core.server._CANDLES_TTL` value-equal to the extracted module constant. The preserved behavioral monkeypatch surface for this slice is `core.server.get_exchange_client`.
- Preserve the legacy monkeypatch surface for focused tests and hidden Python callers: patching `core.server.get_exchange_client` must still affect `core.server.public_candles` behavior after extraction.
- Only router extraction is allowed in this slice; no cache TTL changes, no response-body changes, and no unrelated route changes.

### Repo-local skill evidence

- Repo-local skill spec `repo_clean_refactor` must be reviewed/applied for scope lock, minimal reversible diff, and no-behavior-change guardrails.
- `feature_parity_check` is not required for this slice because no feature computation logic changes.

### Gates required

- `black --check src/core/server.py src/core/server_public_api.py tests/integration/test_ui_endpoints.py`
- `ruff check src/core/server.py src/core/server_public_api.py tests/integration/test_ui_endpoints.py`
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

- Scope drift beyond `/public/candles`, its shared cache state, packet/context-map docs, and direct compatibility test coverage
- Any `/public/candles` contract drift or cache semantics drift
- Loss of compatibility for direct `core.server.public_candles` callers or `core.server.get_exchange_client` monkeypatch behavior
- Determinism / pipeline invariant regression

### Output required

- **Implementation Report** with scope, exact gates, and residual risks
- **PR evidence template** after Opus post-diff audit

### Verification notes

- `tests/integration/test_ui_endpoints.py` must keep route-level proof that `/public/candles` returns normalized OHLCV keys.
- Focused touched-flow proof must show that a cache fill via `core.server.public_candles` is observed by the assembled `/public/candles` route under a monkeypatched `core.server.get_exchange_client`, with a single upstream fetch, preserved cache-key semantics `f"{symbol}:{timeframe}:{limit}"` before limit clamping, and exactly one registered `/public/candles` route.
- If shared cache objects move to the extracted module, tests must lock `_CANDLES_CACHE` identity via `core.server` aliases; matching values alone is insufficient.
- The extracted route must remain registered exactly once in the assembled FastAPI app.

### Gate results

- `python -m black --check src/core/server.py src/core/server_public_api.py tests/integration/test_ui_endpoints.py` — `PASS`
- `python -m ruff check src/core/server.py src/core/server_public_api.py tests/integration/test_ui_endpoints.py` — `PASS`
- `python -m pytest tests/integration/test_ui_endpoints.py tests/backtest/test_backtest_determinism_smoke.py tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q` — `PASS` (`26 passed`)
- `python -m bandit -r src -c bandit.yaml -q` — `PASS` (warning only: existing `nosec` acknowledgement for `B608`, no failed findings)
