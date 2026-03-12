# Command Packet — server API package move

## COMMAND PACKET

- **Mode:** `STRICT` — source: `docs/governance_mode.md` (`master`)
- **Risk:** `HIGH` — why: multi-file import relocation touching FastAPI router wiring, test imports, and paper-trading API edge modules
- **Required Path:** `Full`
- **Objective:** Move the route-module implementations into a dedicated `src/core/api/` package so API-layer files are no longer scattered at `src/core/` root, while preserving exact behavior and old `core.server_*_api` import paths through semantically identical module aliases.
- **Candidate:** `server API package move`
- **Base SHA:** `798cf9fe`

### Scope

- **Scope IN:**
  - `src/core/server.py`
  - `src/core/api/__init__.py`
  - `src/core/api/account.py`
  - `src/core/api/config.py`
  - `src/core/api/info.py`
  - `src/core/api/models.py`
  - `src/core/api/paper.py`
  - `src/core/api/public.py`
  - `src/core/api/status.py`
  - `src/core/api/strategy.py`
  - `src/core/api/ui.py`
  - `src/core/server_account_api.py`
  - `src/core/server_config_api.py`
  - `src/core/server_info_api.py`
  - `src/core/server_models_api.py`
  - `src/core/server_paper_api.py`
  - `src/core/server_public_api.py`
  - `src/core/server_status_api.py`
  - `src/core/server_strategy_api.py`
  - `src/core/server_ui_api.py`
  - `tests/integration/test_ui_endpoints.py`
  - `tests/integration/test_config_endpoints.py`
  - `tests/utils/test_observability.py`
  - `tests/utils/test_health.py`
  - `tests/integration/test_account_endpoints.py`
  - `src/core/config/validator.py`
  - `docs/architecture/ARCHITECTURE_VISUAL.md`
- **Scope OUT:**
  - runtime strategy/backtest/optimizer logic
  - config authority behavior
  - historical audit packets/context maps under `docs/audit/refactor/server/`
  - `docs/audit/CONFIG_GOVERNANCE_AUDIT.md`
  - `src/genesis_core.egg-info/SOURCES.txt`
  - unrelated untracked files under `.claude/worktrees/` and `docs/audit/refactor/decision/`
- **Expected changed files:** 27
- **Max files touched:** 30

### Gates required

- `python -m black --check src/core/server.py src/core/api tests/integration/test_ui_endpoints.py tests/integration/test_config_endpoints.py tests/utils/test_observability.py src/core/config/validator.py`
- `python -m ruff check src/core/server.py src/core/api tests/integration/test_ui_endpoints.py tests/integration/test_config_endpoints.py tests/utils/test_observability.py src/core/config/validator.py`
- `python -m pytest tests/integration/test_ui_endpoints.py tests/integration/test_config_endpoints.py tests/utils/test_observability.py tests/utils/test_health.py tests/integration/test_account_endpoints.py`
- `python -m pytest tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest tests/governance/test_config_ssot.py::test_regime_unified_alias_only_is_canonicalized_before_persist tests/governance/test_config_ssot.py::test_regime_unified_alias_non_dict_is_rejected tests/governance/test_config_ssot.py::test_regime_unified_alias_extra_key_is_rejected tests/integration/test_config_api_e2e.py::test_runtime_endpoints_e2e_regime_unified_alias_bridge`

### Stop Conditions

- Scope drift outside files above
- Any behavior change in route payloads, registration count, or monkeypatch-sensitive alias behavior
- Hidden import-cycle regressions between `core.server` and moved route modules
- Old `core.server_*_api` import paths stop resolving to the same module objects as `core.api.*`
- Unrelated untracked files get pulled into scope

### Output required

- **Implementation Report**
- **PR evidence template**
