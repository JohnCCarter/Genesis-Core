# COMMAND PACKET

- **Mode:** `RESEARCH` — source: explicit user request + `docs/governance_mode.md`
- **Risk:** `HIGH` — why: touches authoritative `regime_module` decision-path logic under `src/core/strategy/*` plus canonical runtime config authority
- **Required Path:** `Full`
- **Objective:** Enable one minimal, default-parity, canonical runtime/config surface for `SIGNAL / regime-definition` within the existing RI family by exposing `regime_module` ADX-band classification thresholds via config, without changing defaults, family rules, decision logic, or execution semantics. This packet covers enablement only; execution YAML/search-space work remains out of scope until gates are green.
- **Candidate:** `multi_timeframe.regime_intelligence.regime_definition.{adx_trend_threshold, adx_range_threshold, slope_threshold, volatility_threshold}` with defaults preserved at `25.0 / 20.0 / 0.001 / 0.05`; first runnable research slice will tune only the ADX band once enablement is verified.
- **Base SHA:** `d227be7e6d07c4b389529ee6a0ece228ca9a9b10`

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence_optuna_signal_regime_definition_enablement_command_packet_2026-03-27.md`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `src/core/strategy/regime.py`
  - `src/core/strategy/evaluate.py`
  - `tests/backtest/test_regime.py`
  - `tests/backtest/test_evaluate_pipeline.py`
  - `tests/backtest/test_evaluate_regime_precomputed_index.py`
  - `tests/governance/test_regime_intelligence_cutover_parity.py`
  - `tests/governance/test_config_ssot.py`
  - `tests/integration/test_config_endpoints.py`
- **Scope OUT:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/family_registry.py`
  - `src/core/intelligence/regime/authority.py`
  - optimizer objective/sampler semantics
  - family-admission rules
  - champion/default runtime payloads
  - promotion/readiness/comparison flows
  - any execution packet or Optuna YAML before enablement gates are green
- **Expected changed files:** `10-11`
- **Max files touched:** `11`

## Skill Usage

- **Loaded repo skill/spec:** `.github/skills/optuna_run_guardrails.json`
- **Use in this slice:** preflight/validation guardrails are carried forward as execution prerequisites only.
- **No dedicated repo skill found for:** canonical `regime_module` config-plumbing / runtime-authority enablement.

## Constraints

- **Default mode:** `NO BEHAVIOR CHANGE`
- Preserve current outputs when the new config surface is absent.
- Preserve `strategy_family=ri` contract and `authority_mode=regime_module` requirement.
- No changes to threshold cluster, gates contract, decision reasons, sizing rules, or pipeline order hash.
- New config surface must be canonical under `multi_timeframe.regime_intelligence` and accepted by runtime validation/authority.
- Invalid nested keys under the new surface must remain fail-closed.
- Explicit default-parity proof is required for:
  - `classify_regime(..., config=None)`
  - `detect_regime_from_candles(..., config=None)`
  - `evaluate.py` with `authority_mode=regime_module` and no `regime_definition` override present
- Legacy/precomputed authority paths must remain byte-for-byte behaviorally unchanged.

## Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest tests/backtest/test_regime.py`
- `python -m pytest tests/backtest/test_evaluate_pipeline.py tests/backtest/test_evaluate_regime_precomputed_index.py`
- `python -m pytest tests/governance/test_regime_intelligence_cutover_parity.py tests/governance/test_config_ssot.py`
- `python -m pytest tests/integration/test_config_endpoints.py`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest tests/utils/test_features_asof_cache_key_deterministic.py`
- explicit smoke proof for `authority_mode=regime_module` with no override and with explicit default override set to canonical values; both must match baseline regime outputs
- explicit fail-closed negative tests for malformed `multi_timeframe.regime_intelligence.regime_definition`

## Stop Conditions

- Scope drift
- Behavior change without explicit default-parity proof
- Family/admission drift
- Hash/determinism regression
- Any need to touch forbidden/out-of-scope paths

## Output required

- **Implementation Report**
- **PR evidence template**
- Explicit statement whether enablement is approved to proceed into the first Optuna/backtest slice
