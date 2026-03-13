# Command Packet — decision_fib_gating split slice 3

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: verified branch `feature/decision-fib-gating-split` via `git status --short --branch`, mapped by `docs/governance_mode.md` (`feature/* -> RESEARCH`)
- **Risk:** `HIGH` — why: touches `src/core/strategy/*`, a high-sensitivity zone, while extracting HTF gate-branch logic from a decision hot path
- **Required Path:** `Full`
- **Objective:** Perform a no-behavior-change third split of `src/core/strategy/decision_fib_gating.py` by extracting only the HTF Fibonacci entry gate handler into the internal helper module while preserving `apply_fib_gating(...)` semantics, override sequencing, mutation order, debug payloads, reason labels, and logging behavior.
- **Candidate:** `decision_fib_gating split slice 3`
- **Base SHA:** `ff572f71`

### Scope

- **Scope IN:**
  - `src/core/strategy/decision_fib_gating.py`
  - `src/core/strategy/decision_fib_gating_helpers.py`
  - `tests/utils/test_decision.py`
  - `docs/audit/refactor/decision/context_map_decision_fib_gating_split_2026-03-12.md`
  - `docs/audit/refactor/decision/command_packet_decision_fib_gating_split_slice3_2026-03-12.md`
- **Scope OUT:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/decision_gates.py`
  - `src/core/strategy/decision_sizing.py`
  - the LTF gate branch in `decision_fib_gating.py`
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
- `decision_fib_gating_helpers.py` remains internal-only; no re-exports, no new call sites, and no new dependencies beyond existing strategy-local utilities/types are allowed.
- Slice 3 may extract only the HTF gate branch, including:
  - HTF unavailable/context-error handling
  - HTF target-level matching and off-target blocking
  - HTF pass/debug payload assembly
  - existing override-path delegation via `try_override_htf_block(...)`
- Slice 3 must not extract or rewrite the LTF gate branch, final `fib_gate_summary` assembly, or override-context preparation.
- No changes to threshold math, reason labels, `state_out` key names, logger message text, payload shapes, or the order in which `state_out["htf_fib_entry_debug"]`, `reasons`, and override-related mutations occur.
- The extracted HTF helper must be fully argument-threaded and preserve the current early-return contract:
  - blocked path returns the same NONE/meta tuple semantics through `_none_result(...)`
  - pass path leaves `apply_fib_gating(...)` positioned exactly where the LTF gate starts today
- Existing semantics for `HTF_FIB_CONTEXT_ERROR`, `HTF_FIB_UNAVAILABLE`, `HTF_FIB_NO_PRICE`, `HTF_FIB_LONG_BLOCK`, `HTF_FIB_SHORT_BLOCK`, `TARGET_MATCH`, `UNAVAILABLE_PASS`, and `PASS` must remain identical.

### Gates required

- `pre-commit run --all-files`
- `black --check src/core/strategy/decision_fib_gating.py src/core/strategy/decision_fib_gating_helpers.py tests/utils/test_decision.py`
- `ruff check src/core/strategy/decision_fib_gating.py src/core/strategy/decision_fib_gating_helpers.py tests/utils/test_decision.py`
- `pytest tests/governance/test_import_smoke_backtest_optuna.py -q`
- Focused selectors:
  - `tests/utils/test_decision.py`
  - `tests/utils/test_decision_edge.py`
  - `tests/backtest/test_run_backtest_decision_rows.py`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
  - `tests/utils/test_decision.py::test_htf_gate_handler_preserves_targets_and_summary`
- Required invariants:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Gate outcomes

- `pre-commit run --all-files` → `PASS`
- `python -m black --check src/core/strategy/decision_fib_gating.py src/core/strategy/decision_fib_gating_helpers.py tests/utils/test_decision.py` → `PASS`
- `python -m ruff check src/core/strategy/decision_fib_gating.py src/core/strategy/decision_fib_gating_helpers.py tests/utils/test_decision.py` → `PASS`
- `python -m pytest tests/governance/test_import_smoke_backtest_optuna.py -q` → `PASS`
- `python -m pytest tests/utils/test_decision.py tests/utils/test_decision_edge.py tests/backtest/test_run_backtest_decision_rows.py tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic tests/integration/test_golden_trace_runtime_semantics.py tests/utils/test_decision.py::test_htf_gate_handler_preserves_targets_and_summary -q` → `PASS`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q` → `PASS`

### Stop Conditions

- Scope drift outside the two strategy files plus evidence docs and the mandatory HTF-focused parity test
- Any behavior change or diff in `htf_fib_entry_debug`, `fib_gate_summary["htf"]`, or HTF reason ordering/labels
- Any change to override behavior or mutation timing for `HTF_OVERRIDE_LTF_CONF`
- Stop immediately if extraction requires changing defaults, exception handling, return shapes, key ordering, or logger payload content beyond mechanical argument threading
- Determinism replay regression
- Pipeline invariant regression
- Touching unrelated high-sensitivity modules without explicit re-approval

### Planned implementation

1. Update context map to mark slice 2 complete and slice 3 active.
2. Add a dedicated HTF gate helper to `decision_fib_gating_helpers.py` with fully threaded inputs and unchanged early-return semantics.
3. Replace the inline HTF branch in `apply_fib_gating(...)` with a single helper call only.
4. Add `tests/utils/test_decision.py::test_htf_gate_handler_preserves_targets_and_summary` to lock a non-override HTF pass path, a non-override HTF block path, exact `targets` payload ordering, reason ordering, and `fib_gate_summary["htf"]` parity.
5. Run the full gate stack.
6. Request Opus post-diff audit before any commit claim.

### Output required

- **Implementation Report** with exact files changed, exact commands run, and pass/fail outcomes
- **PR evidence template** / READY_FOR_REVIEW evidence after post-diff audit

### Residual risks

- The HTF branch owns multiple early returns plus override-aware block/pass behavior.
- The main parity risks are `htf_fib_entry_debug` payload drift, hidden reason-order drift, and accidental movement of override-related mutations.

### Governance review

- **Pre-review verdict:** `APPROVED`
- **Post-diff verdict:** `APPROVED`
- **Post-diff READY_TO_COMMIT:** `YES`
- **Reviewer:** `Opus 4.6 Governance Reviewer`
