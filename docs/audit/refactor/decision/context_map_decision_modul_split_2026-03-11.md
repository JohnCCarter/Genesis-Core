# Context Map — decision modul split

## Objective

Preserve `core.strategy.decision.decide()` as the public facade while extracting internal responsibilities into smaller modules without changing runtime behavior.

## Scope map

### Facade

- `src/core/strategy/decision.py`
  - owns `Action`
  - keeps `_sanitize_context()` and `_log_decision_event()`
  - deep-copies inbound state
  - orchestrates exact call order:
    1. `select_candidate(...)`
    2. `apply_fib_gating(...)`
    3. `apply_post_fib_gates(...)`
    4. `apply_sizing(...)`

### Extracted modules

- `src/core/strategy/decision_gates.py`
  - `safe_float(...)`
  - `compute_percentile(...)`
  - `select_candidate(...)`
  - `apply_post_fib_gates(...)`

- `src/core/strategy/decision_fib_gating.py`
  - `apply_fib_gating(...)`
  - owns HTF/LTF fib entry gating, override handling, and fib debug summaries

- `src/core/strategy/decision_sizing.py`
  - `apply_sizing(...)`
  - owns risk ladder sizing, scaled confidence, regime multipliers, HTF regime multipliers, volatility sizing, and RI clarity sizing-only path

## Repo-local dependency map

### Direct imports from `decision.py`

- `src/core/strategy/evaluate.py`
- `tests/utils/test_decision.py`
- `tests/utils/test_decision_edge.py`
- `tests/integration/test_golden_trace_runtime_semantics.py`

### Internal dependencies used by extracted modules

- `core.strategy.fib_logging.log_fib_flow`
- `core.strategy.regime_intelligence`
- `core.utils.logging_redaction.get_logger`

## Primary parity risks

1. **Mutable shared state across module boundaries**
   - `state_out`
   - `reasons`
   - `override_state`
2. **Gate-order preservation**
   - candidate selection must happen before fib gating
   - fib gating must happen before confidence/edge/hysteresis/cooldown
   - sizing must only run after all gates pass
3. **Debug/meta field parity**
   - `htf_fib_entry_debug`
   - `ltf_fib_entry_debug`
   - `fib_gate_summary`
   - `zone_debug`
   - sizing / RI debug fields in `state_out`

## Verification selectors

### Direct decision coverage

- `tests/utils/test_decision.py`
  - gate order, fail-safe, cooldown, fib context errors, nested state isolation, clarity-score sizing semantics

- `tests/utils/test_decision_edge.py`
  - min-edge behavior, scaled-confidence sizing, regime-size multipliers, risk-map failure handling

### Pipeline / determinism coverage

- `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta`
- `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`

### Golden trace / invariant coverage

- `tests/integration/test_golden_trace_runtime_semantics.py`
- `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Supplemental smoke

- `tests/backtest/test_run_backtest_decision_rows.py`

## Current assessment

- `decide()` signature appears unchanged.
- Extracted helpers are internal and repo-local consumers still call `decide()`.
- Focused lint + parity/invariant selectors are green in the decision worktree.
- Remaining governance step is post-diff audit before commit/merge claim.
