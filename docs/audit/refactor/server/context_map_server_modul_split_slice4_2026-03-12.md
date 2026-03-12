# Context Map — server modul split slice 4

## Current target

Continue `feature/server-modul-split` with the next smallest safe extraction from `src/core/server.py`.

## Files to modify

| File                                                                                | Purpose                    | Changes needed                                                                      |
| ----------------------------------------------------------------------------------- | -------------------------- | ----------------------------------------------------------------------------------- |
| `src/core/server.py`                                                                | FastAPI app assembly       | Remove inline `/models/reload` implementation and include a dedicated models router |
| `src/core/server_models_api.py`                                                     | New slice-4 router module  | Host `/models/reload` and preserve current cache-clear semantics                    |
| `tests/integration/test_ui_endpoints.py`                                            | Reload route compatibility | Add exact route contract lock, `clear_cache()` delegation proof, and alias parity   |
| `docs/audit/refactor/server/command_packet_server_modul_split_slice4_2026-03-12.md` | Commit contract            | Record slice scope, gates, and constraints                                          |
| `docs/audit/refactor/server/context_map_server_modul_split_slice4_2026-03-12.md`    | Dependency/test map        | Capture affected files, tests, and risks                                            |

## Dependencies

| File                                  | Relationship                                                                    |
| ------------------------------------- | ------------------------------------------------------------------------------- |
| `src/core/strategy/model_registry.py` | `/models/reload` instantiates `ModelRegistry` and calls `clear_cache()`         |
| `src/core/server_config_api.py`       | Existing extracted-router include pattern to mirror                             |
| `src/core/server_status_api.py`       | Existing alias + include pattern for small compatibility-preserving extractions |

## Test files

| Test                                                                                                                      | Coverage                                                                  |
| ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `tests/integration/test_ui_endpoints.py`                                                                                  | App route availability plus new `/models/reload` route/direct parity lock |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Canonical determinism replay required by RESEARCH governance              |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`             | Pipeline determinism guard after server wiring change                     |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Feature cache invariance guard                                            |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant guard                                                  |
| `bandit -r src -c bandit.yaml`                                                                                            | Security scan required by repo-local policy                               |

## Reference patterns

| File                            | Pattern                                                                      |
| ------------------------------- | ---------------------------------------------------------------------------- |
| `src/core/server_config_api.py` | Existing `APIRouter` extraction pattern already included by `core.server`    |
| `src/core/server_info_api.py`   | Slice-2 pattern for router extraction plus symbol rebinding in `core.server` |
| `src/core/server_status_api.py` | Slice-3 pattern for a very small endpoint group with compatibility aliasing  |

## Risk assessment

- [x] Public API/HTTP contract risk: `/models/reload` must preserve its exact response body and route exposure
- [x] App wiring risk: adding another extracted router must not disturb existing router includes
- [x] Compatibility risk: if `core.server.reload_models` remains exported, aliasing must keep direct-call behavior stable
- [ ] Database migrations needed
- [ ] Configuration changes required

## Slice rationale

This slice stays contained because:

1. `/models/reload` is the smallest remaining inline route in `src/core/server.py`.
2. The handler's runtime effect is limited to delegating to `ModelRegistry.clear_cache()`.
3. A small integration test can lock the endpoint response, exact delegation, and direct alias parity.
4. The extraction pattern directly mirrors the already-verified router splits from slices 1-3.

## Repo-local skill evidence

- Repo-local skill spec `repo_clean_refactor` was reviewed for strict scope, minimal reversible diff, and no-behavior-change guardrails before implementation.

## Verification snapshot

- Formatter parity held after extraction: `black --check` passed for `src/core/server.py`, `src/core/server_models_api.py`, and `tests/integration/test_ui_endpoints.py`.
- Lint parity held for the same slice files: `ruff check` passed with no findings.
- `tests/integration/test_ui_endpoints.py` now locks:
	- `POST /models/reload` exact `200` response body
	- `ModelRegistry.clear_cache()` delegation count
	- `core.server.reload_models` alias identity plus route/direct parity
- Governance selectors passed via:
	- `tests/backtest/test_backtest_determinism_smoke.py`
	- `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
	- `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
	- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Security scan passed: `bandit -r src -c bandit.yaml -q` produced only the existing acknowledged `B608` `nosec` warning and no failed findings.
