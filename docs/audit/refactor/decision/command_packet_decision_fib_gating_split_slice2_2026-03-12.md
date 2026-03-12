# Command Packet — decision_fib_gating split slice 2

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH` from `docs/governance_mode.md`
- **Risk:** `HIGH` — why: touches `src/core/strategy/*`, a high-sensitivity zone, while extracting override-path logic from a decision hot path
- **Required Path:** `Full`
- **Objective:** Perform a no-behavior-change second split of `src/core/strategy/decision_fib_gating.py` by extracting only the LTF override preparation and HTF-block override application helpers into the internal helper module while preserving `apply_fib_gating(...)` semantics, mutation order, and debug/reason payloads.
- **Candidate:** `decision_fib_gating split slice 2`
- **Base SHA:** `b2f48761`

### Scope

- **Scope IN:**
  - `src/core/strategy/decision_fib_gating.py`
  - `src/core/strategy/decision_fib_gating_helpers.py`
  - `tests/utils/test_decision.py`
  - `docs/audit/refactor/decision/context_map_decision_fib_gating_split_2026-03-12.md`
  - `docs/audit/refactor/decision/command_packet_decision_fib_gating_split_slice2_2026-03-12.md`
- **Scope OUT:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/decision_gates.py`
  - `src/core/strategy/decision_sizing.py`
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
  - freeze/config-authority paths
- **Expected changed files:** `5`
- **Max files touched:** `5`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- `apply_fib_gating(...)` signature must remain unchanged.
- `core.strategy.decision` import path and call order must remain unchanged.
- `decision_fib_gating_helpers.py` remains internal-only; no re-exports, no new call sites, and no new dependencies beyond the existing `decision_gates` utility/type import are allowed.
- Only override-path helpers may be extracted in slice 2:
  - `prepare_override_context(...)`
  - `try_override_htf_block(...)`
  - any new helper introduced must be purely internal to support those two extracted paths and must not own HTF/LTF gate branching outside the current override behavior.
- No changes to threshold math, reason labels, logging payload content, `state_out` key names, or the order in which `override_state`, `state_out`, and `reasons` are mutated.
- `apply_override(...)` semantics must remain identical if lifted out of nested scope.
- Extracted override helpers must be fully argument-threaded and may mutate only the same objects as today: `override_state[history_key]`, `state_out["ltf_override_debug"]`, `state_out["htf_fib_entry_debug"]`, `reasons.append("HTF_OVERRIDE_LTF_CONF")`, plus the same logger call.
- The mutation sequence must remain identical to the current implementation.

### Gates required

- `pre-commit run --all-files`
- `black --check src/core/strategy/decision_fib_gating.py src/core/strategy/decision_fib_gating_helpers.py`
- `ruff check src/core/strategy/decision_fib_gating.py src/core/strategy/decision_fib_gating_helpers.py`
- `pytest tests/governance/test_import_smoke_backtest_optuna.py -q`
- Focused selectors:
  - `tests/utils/test_decision.py`
  - `tests/utils/test_decision_edge.py`
  - `tests/backtest/test_run_backtest_decision_rows.py`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
  - `tests/utils/test_decision.py::test_htf_override_preserves_debug_payload_and_history`
- Required invariants:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Gate outcomes

- `pre-commit run --all-files` → `PASS`
- `black --check src/core/strategy/decision_fib_gating.py src/core/strategy/decision_fib_gating_helpers.py tests/utils/test_decision.py` → `PASS`
- `ruff check src/core/strategy/decision_fib_gating.py src/core/strategy/decision_fib_gating_helpers.py tests/utils/test_decision.py` → `PASS`
- `pytest tests/governance/test_import_smoke_backtest_optuna.py -q` → `PASS`
- `pytest tests/utils/test_decision.py::test_htf_override_preserves_debug_payload_and_history -q` → `PASS`
- `pytest tests/utils/test_decision.py tests/utils/test_decision_edge.py tests/backtest/test_run_backtest_decision_rows.py tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic tests/integration/test_golden_trace_runtime_semantics.py -q` → `PASS`
- `pytest tests/backtest/test_backtest_determinism_smoke.py tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q` → `PASS`

### Stop Conditions

- Scope drift outside the two strategy files plus evidence docs
- Any behavior change or diff in `HTF_OVERRIDE_LTF_CONF`, `ltf_override_debug`, `htf_fib_entry_debug`, or `fib_gate_summary` semantics
- Stop immediately if extraction requires changing defaults, exception handling, return shapes, key ordering, or logger payload content beyond mechanical argument threading
- Determinism replay regression
- Pipeline invariant regression
- Touching unrelated high-sensitivity modules without explicit re-approval

### Planned implementation

1. Update context map to mark slice 1 complete and slice 2 active.
2. Add explicit override helper functions to `decision_fib_gating_helpers.py` with fully threaded arguments/state.
3. Replace the nested override functions in `apply_fib_gating(...)` with helper calls only.
4. Keep HTF/LTF gate branches otherwise structurally unchanged.
5. Run full gate stack.
6. Request Opus post-diff audit before any commit claim.

### Output required

- **Implementation Report** with exact files changed, exact commands run, and pass/fail outcomes
- **PR evidence template** / READY_FOR_REVIEW evidence after post-diff audit

### Residual risks

- Override-path extraction touches the most mutation-heavy inner closures in this module.
- The main parity risks are mutation timing drift and payload-shape drift for override debug fields.

### Governance review

- **Pre-review verdict:** `APPROVED`
- **Post-diff verdict:** `APPROVED`
- **Post-diff READY_TO_COMMIT:** `YES`
- **Reviewer:** `Opus 4.6 Governance Reviewer`
