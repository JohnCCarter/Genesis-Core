# Context Map — decision_fib_gating split

## Objective

Split `src/core/strategy/decision_fib_gating.py` into smaller internal helpers while preserving `apply_fib_gating(...)` behavior, mutation order, and emitted debug/meta fields.

## Current state

- `src/core/strategy/decision.py` calls `apply_fib_gating(...)` as the second gate stage after candidate selection.
- `src/core/strategy/decision_fib_gating.py` currently contains:
  - generic result/summary helpers
  - numeric/level conversion helpers
  - LTF override preparation and override application logic
  - HTF Fibonacci entry gating
  - LTF Fibonacci entry gating
  - final debug summary assembly
- The module is semantically centralized in a single large `apply_fib_gating(...)` body.

## Files to modify

| File                                                                                         | Purpose                          | Planned change                                                     |
| -------------------------------------------------------------------------------------------- | -------------------------------- | ------------------------------------------------------------------ |
| `src/core/strategy/decision_fib_gating.py`                                                   | Current fib gating orchestration | Keep public function, delegate only the active LTF helper slice    |
| `src/core/strategy/decision_fib_gating_helpers.py`                                           | New internal helper module       | Hold pure helper functions first, then later gate-specific helpers |
| `docs/audit/refactor/decision/context_map_decision_fib_gating_split_2026-03-12.md`           | Governance evidence              | Capture current map and risks                                      |
| `docs/audit/refactor/decision/command_packet_decision_fib_gating_split_slice4_2026-03-12.md` | Governance packet                | Active slice scope, gates, stop conditions, evidence               |

## Direct dependencies

| File                                  | Relationship                                          |
| ------------------------------------- | ----------------------------------------------------- |
| `src/core/strategy/decision.py`       | Imports and calls `apply_fib_gating(...)`             |
| `src/core/strategy/decision_gates.py` | Provides `Action`, `compute_percentile`, `safe_float` |
| `src/core/strategy/fib_logging.py`    | Supplies `log_fib_flow(...)` callback                 |

## Test files

| Test                                                                                                                      | Coverage                                                                             |
| ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `tests/utils/test_decision.py`                                                                                            | Gate order, fib context error blocking, missing-policy pass-through, state isolation |
| `tests/utils/test_decision_edge.py`                                                                                       | Post-fib path sanity and overall decision semantics                                  |
| `tests/backtest/test_run_backtest_decision_rows.py`                                                                       | Decision rows smoke in backtest flow                                                 |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta`                                           | Pipeline integration returns decision meta                                           |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`             | Deterministic pipeline path                                                          |
| `tests/integration/test_golden_trace_runtime_semantics.py`                                                                | Golden trace / runtime semantics                                                     |
| `tests/utils/test_decision.py::test_htf_override_preserves_debug_payload_and_history`                                     | Override-path parity for history mutation, debug payloads, and reason ordering       |
| `tests/utils/test_decision.py::test_ltf_gate_handler_preserves_debug_and_summary`                                         | Mandatory slice-4 parity proof for LTF pass/block/unavailable summary semantics      |
| `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed` | Required invariant selector in repo governance baseline                              |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`                | Pipeline invariant guard                                                             |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                                       | Determinism replay smoke                                                             |

## Reference patterns

| File                                              | Pattern                                                             |
| ------------------------------------------------- | ------------------------------------------------------------------- |
| `src/core/strategy/decision_gates.py`             | Pure helper extraction with facade preserved in `decision.py`       |
| `src/core/strategy/decision_sizing.py`            | Isolated stage-specific logic with explicit mutation inputs/outputs |
| `src/core/strategy/features_asof_parts/*.py`      | Small helper modules that preserve orchestrator readability         |
| `src/core/backtest/engine_htf_exit_dispatcher.py` | Recent no-behavior-change extraction from a hot path orchestrator   |

## Slice candidate plan

### Slice 1 — pure helper extraction

Extract only helper functions with no branching-policy ownership change:

- `_none_result(...)`
- `_summarize_fib_debug(...)`
- `_as_float(...)`
- `_levels_to_lookup(...)`
- `_level_price(...)`
- `_is_context_error_reason(...)`

Target module: `src/core/strategy/decision_fib_gating_helpers.py`

Status: completed in commit `b2f48761` as a no-behavior-change helper extraction.

### Slice 2 — override preparation/apply helpers

Potential later extraction:

- `prepare_override_context(...)`
- `try_override_htf_block(...)`

Status: completed in commit `ff572f71` as a no-behavior-change override helper extraction.

### Slice 3 — HTF gate handler

Potential later extraction:

- HTF unavailable/context-error handling
- HTF target/level blocking logic
- shared HTF pass/debug payload assembly while preserving override-path sequencing

Status: completed in this slice as a no-behavior-change HTF helper extraction while keeping the LTF branch and final summary assembly inside `apply_fib_gating(...)`.

### Slice 4 — LTF gate handler

Potential later extraction:

- LTF unavailable/context-error handling
- LTF level blocking logic
- LTF pass/debug payload assembly

Status: completed in this slice as a no-behavior-change LTF helper extraction while keeping final `fib_gate_summary` assembly inside `apply_fib_gating(...)`.

## Primary parity risks

- `reasons` mutation order changes
- `state_out` debug payload shape drift
- override-state mutation timing drift
- HTF/LTF missing-policy and `*_CONTEXT_ERROR` semantics drifting
- `fib_gate_summary` being assembled with changed intermediate payloads

## Current recommendation

Slices 1, 2, 3, and 4 are complete. `decision_fib_gating.py` is now split into orchestrator + helper stages with the public `apply_fib_gating(...)` facade preserved and no further slice planned under the current contract.
