# Command Packet — decision_fib_gating split slice 1

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH` from `docs/governance_mode.md`
- **Risk:** `HIGH` — why: touches `src/core/strategy/*`, a high-sensitivity zone, even though intended change is structural only
- **Required Path:** `Full`
- **Objective:** Perform a no-behavior-change first split of `src/core/strategy/decision_fib_gating.py` by extracting only pure helper functions into a new internal helper module while preserving `apply_fib_gating(...)` semantics and public import path.
- **Candidate:** `decision_fib_gating split slice 1`
- **Base SHA:** `798cf9fe`

### Scope

- **Scope IN:**
  - `src/core/strategy/decision_fib_gating.py`
  - `src/core/strategy/decision_fib_gating_helpers.py`
  - `docs/audit/refactor/decision/context_map_decision_fib_gating_split_2026-03-12.md`
  - `docs/audit/refactor/decision/command_packet_decision_fib_gating_split_slice1_2026-03-12.md`
- **Scope OUT:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/decision_gates.py`
  - `src/core/strategy/decision_sizing.py`
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
  - freeze/config-authority paths
- **Expected changed files:** `4`
- **Max files touched:** `4`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- `apply_fib_gating(...)` signature must remain unchanged.
- `core.strategy.decision` import path and call order must remain unchanged.
- `decision_fib_gating_helpers.py` is internal-only in slice 1; no re-exports, no new call sites, and no imports from `decision.py` or other strategy modules are allowed.
- Only pure helper functions may be extracted in slice 1:
  - `_none_result(...)`
  - `_summarize_fib_debug(...)`
  - `_as_float(...)`
  - `_levels_to_lookup(...)`
  - `_level_price(...)`
  - `_is_context_error_reason(...)`
- No changes to branching logic, threshold math, reason labels, or state/debug payload shapes.

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
- Required invariants:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Gate outcomes

- `pre-commit run --all-files` → `PASS`
- `black --check src/core/strategy/decision_fib_gating.py src/core/strategy/decision_fib_gating_helpers.py` → `PASS`
- `ruff check src/core/strategy/decision_fib_gating.py src/core/strategy/decision_fib_gating_helpers.py` → `PASS`
- `pytest tests/utils/test_decision.py tests/utils/test_decision_edge.py tests/backtest/test_run_backtest_decision_rows.py tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic tests/integration/test_golden_trace_runtime_semantics.py -q` → `PASS`
- `pytest tests/backtest/test_backtest_determinism_smoke.py tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/governance/test_import_smoke_backtest_optuna.py -q` → `PASS`

### Stop Conditions

- Scope drift outside the two strategy files plus evidence docs
- Any behavior change or diff in reason/debug payload semantics
- Stop immediately if any extracted helper requires semantic edits beyond mechanical import rewiring (changed defaults, changed exception handling, changed return shape, changed key ordering, or changed debug/reason field construction)
- Determinism replay regression
- Pipeline invariant regression
- Touching unrelated high-sensitivity modules without explicit re-approval

### Planned implementation

1. Create `decision_fib_gating_helpers.py` with exact helper implementations moved verbatim.
2. Update `decision_fib_gating.py` imports to consume those helpers.
3. Keep `apply_fib_gating(...)` body structurally identical except helper references.
4. Run full gate stack.
5. Request Opus post-diff audit before any commit claim.

### Output required

- **Implementation Report** with exact files changed, exact commands run, and pass/fail outcomes
- **PR evidence template** / READY_FOR_REVIEW evidence after post-diff audit

### Residual risks

- Even pure helper extraction can alter stack traces/import order if done sloppily.
- The main parity risk is accidental drift in helper return values or reason/debug payload fields.

### Governance review

- **Pre-review verdict:** `APPROVED_WITH_NOTES`
- **Post-diff verdict:** `APPROVED`
- **Post-diff READY_TO_COMMIT:** `YES`
- **Reviewer:** `Opus 4.6 Governance Reviewer`
