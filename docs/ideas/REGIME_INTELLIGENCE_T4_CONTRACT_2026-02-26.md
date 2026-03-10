# REGIME INTELLIGENCE T4 CONTRACT (2026-02-26)

## Category

`api`

## Scope IN

- `src/core/config/schema.py`
- `src/core/config/authority.py`
- `src/core/strategy/regime_intelligence.py`
- `src/core/strategy/evaluate.py`
- `tests/test_evaluate_pipeline.py`
- `tests/test_evaluate_regime_precomputed_index.py`
- `tests/test_config_endpoints.py`
- `tests/test_config_ssot.py`
- `tests/test_config_api_e2e.py`
- `tests/test_ui_endpoints.py`
- `docs/ideas/REGIME_INTELLIGENCE_T4_CONTRACT_2026-02-26.md`

## Scope OUT (strict)

- `src/core/strategy/decision.py`
- `src/core/strategy/prob_model.py`
- `src/core/strategy/confidence.py`
- `src/core/strategy/regime_unified.py`
- `src/core/server.py` envelope/shape changes
- `src/core/backtest/*`
- `src/core/optimizer/*`
- `config/runtime.json`
- `config/runtime.seed.json`
- `config/strategy/champions/*`
- `.github/workflows/champion-freeze-guard.yml`

## Constraints

- Default: NO BEHAVIOR CHANGE (OFF parity mandatory).
- ON-path behavior must be explicit and deterministic.
- `/strategy/evaluate` response envelope must remain unchanged: `{ "result": ..., "meta": ... }`.
- `feature_parity_check` STOP/no_steps is expected policy attestation, not a failure.

## Required implementation

1. Add typed nested config under `multi_timeframe.regime_intelligence.authority_mode`.
   - default: `legacy`
   - allowed: `legacy`, `regime_module`
2. Allow this nested config path in ConfigAuthority with strict value validation.
3. Regime authority selection:
   - OFF/absent => existing legacy authority path.
   - ON => explicit `regime_module` authority path.
4. Keep evaluate metadata additive and maintain `decision_input = false`.
5. Add/adjust tests for OFF parity, ON deterministic path, whitelist/schema/e2e, and UI envelope guard.

## Gates (PRE + POST, same commands)

- `pre-commit run --files src/core/config/schema.py src/core/config/authority.py src/core/strategy/regime_intelligence.py src/core/strategy/evaluate.py tests/test_evaluate_pipeline.py tests/test_evaluate_regime_precomputed_index.py tests/test_config_endpoints.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_ui_endpoints.py docs/ideas/REGIME_INTELLIGENCE_T4_CONTRACT_2026-02-26.md`
- `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
- `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`
- `pytest -q tests/test_import_smoke_backtest_optuna.py`
- `pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `pytest -q tests/test_features_asof_cache_key_deterministic.py`
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `pytest -q tests/test_evaluate_pipeline.py tests/test_evaluate_regime_precomputed_index.py tests/test_config_endpoints.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_ui_endpoints.py::test_ui_get_and_evaluate_post`

## Notes

- T4 follows Option A minimal switch with explicit authority gate.
- Default mode remains `legacy` to preserve parity until explicitly enabled.
