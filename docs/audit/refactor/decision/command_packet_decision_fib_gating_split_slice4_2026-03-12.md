# Command Packet — decision_fib_gating split slice 4

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: verified branch `feature/decision-fib-gating-split` via `git status --short --branch`, mapped by `docs/governance_mode.md` (`feature/* -> RESEARCH`)
- **Risk:** `HIGH` — why: touches `src/core/strategy/*`, a high-sensitivity zone, while extracting the remaining LTF gate branch from a decision hot path
- **Required Path:** `Full`
- **Objective:** Perform a no-behavior-change fourth split of `src/core/strategy/decision_fib_gating.py` by extracting only the LTF Fibonacci entry gate handler into the internal helper module while preserving `apply_fib_gating(...)` semantics, mutation order, debug payloads, reason labels, and final `fib_gate_summary` assembly.
- **Candidate:** `decision_fib_gating split slice 4`
- **Base SHA:** `32258497`

### Scope

- **Scope IN:**
  - `src/core/strategy/decision_fib_gating.py`
  - `src/core/strategy/decision_fib_gating_helpers.py`
  - `tests/utils/test_decision.py`
  - `docs/audit/refactor/decision/context_map_decision_fib_gating_split_2026-03-12.md`
  - `docs/audit/refactor/decision/command_packet_decision_fib_gating_split_slice4_2026-03-12.md`
- **Scope OUT:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/decision_gates.py`
  - `src/core/strategy/decision_sizing.py`
  - the already-extracted HTF gate helper semantics in `decision_fib_gating_helpers.py`
  - override-context preparation / override helper semantics
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
  - freeze/config-authority paths
- **Expected changed files:** `5`
- **Max files touched:** `5`

### Skill Usage

- `repo_clean_refactor` — governs this no-behavior-change high-sensitivity refactor with locked scope, minimal diff expectations, and mandatory verification evidence.
- `decision_gate_debug` — applies because the slice touches decision gate semantics and debug payloads (`LTF_FIB_BLOCK`, `ltf_fib_entry_debug`), so gate-specific parity and traceability must remain explicit.
- These repo-local skills are invoked for pre-code planning and must be referenced again during post-audit evidence review.

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- `apply_fib_gating(...)` signature must remain unchanged.
- `core.strategy.decision` import path and call order must remain unchanged.
- `decision_fib_gating_helpers.py` remains internal-only; no re-exports, no new call sites, and no new dependencies beyond existing strategy-local utilities/types are allowed.
- Slice 4 may extract only the LTF gate branch, including:
  - LTF unavailable/context-error handling
  - LTF no-price handling
  - LTF level blocking logic for `LONG_ABOVE_LEVEL` and `SHORT_BELOW_LEVEL`
  - LTF pass/debug payload assembly
- Slice 4 must not rewrite HTF helper behavior, override-context preparation, or final `fib_gate_summary` assembly.
- The extracted LTF helper must neither read nor write `state_out["fib_gate_summary"]`; only `apply_fib_gating(...)` may assemble final summary payloads after the helper returns.
- No changes to threshold math, reason labels, `state_out` key names, logger message text, payload shapes, or the order in which `state_out["ltf_fib_entry_debug"]` and `reasons` mutate.
- The extracted LTF helper must be fully argument-threaded and preserve the current early-return contract:
  - blocked path returns the same NONE/meta tuple semantics through `_none_result(...)`
  - pass path returns control to `apply_fib_gating(...)` exactly where final summary assembly happens today
- Existing semantics for `LTF_FIB_CONTEXT_ERROR`, `LTF_FIB_UNAVAILABLE`, `LTF_FIB_NO_PRICE`, `LTF_FIB_LONG_BLOCK`, `LTF_FIB_SHORT_BLOCK`, `UNAVAILABLE_PASS`, and `PASS` must remain identical.

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
  - `tests/utils/test_decision.py::test_ltf_context_error_blocks_even_when_missing_policy_pass`
  - `tests/utils/test_decision.py::test_ltf_unavailable_backcompat_still_passes_with_missing_policy_pass`
  - `tests/utils/test_decision.py::test_ltf_gate_handler_preserves_debug_and_summary`
- Required invariants:
  - `tests/backtest/test_backtest_determinism_smoke.py`
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### Gate outcomes

- `pre-commit run --all-files` → `PASS`
- `python -m black --check src/core/strategy/decision_fib_gating.py src/core/strategy/decision_fib_gating_helpers.py tests/utils/test_decision.py` → `PASS`
- `python -m ruff check src/core/strategy/decision_fib_gating.py src/core/strategy/decision_fib_gating_helpers.py tests/utils/test_decision.py` → `PASS`
- `python -m pytest tests/governance/test_import_smoke_backtest_optuna.py -q` → `PASS`
- `python -m pytest tests/utils/test_decision.py -q` → `PASS`
- `python -m pytest tests/utils/test_decision_edge.py tests/backtest/test_run_backtest_decision_rows.py -q` → `PASS`
- `python -m pytest tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic -q` → `PASS`
- `python -m pytest tests/integration/test_golden_trace_runtime_semantics.py -q` → `PASS`
- `python -m pytest tests/backtest/test_backtest_determinism_smoke.py tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q` → `PASS`

### Stop Conditions

- Scope drift outside the two strategy files plus evidence docs and the mandatory LTF-focused parity test
- Any behavior change or diff in `ltf_fib_entry_debug`, `fib_gate_summary["ltf"]`, or LTF reason ordering/labels
- Any change to HTF helper or override behavior while working this slice
- Any drift in transient-to-final LTF mutation order, including unavailable/debug setup, `NO_PRICE`, block payload writes, and final `PASS` overwrite timing
- Stop immediately if extraction requires changing defaults, exception handling, return shapes, key ordering, or logger payload content beyond mechanical argument threading
- Determinism replay regression
- Pipeline invariant regression
- Touching unrelated high-sensitivity modules without explicit re-approval

### Planned implementation

1. Update context map to mark slice 4 active.
2. Add a dedicated LTF gate helper to `decision_fib_gating_helpers.py` with fully threaded inputs and unchanged early-return semantics.
3. Replace the inline LTF branch in `apply_fib_gating(...)` with a single helper call only.
4. Add `tests/utils/test_decision.py::test_ltf_gate_handler_preserves_debug_and_summary` to lock at minimum three LTF outcomes: pass-path, early-return block-path, and `missing_policy=pass` unavailable-path; the test must verify exact reasons ordering, exact final `ltf_fib_entry_debug["reason"]`, summary presence only on non-early-return paths, and that transient `UNAVAILABLE_PASS` setup does not drift into the wrong final payload.
5. Run the full gate stack.
6. Request Opus post-diff audit before any commit claim.

### Output required

- **Implementation Report** with exact files changed, exact commands run, and pass/fail outcomes
- **PR evidence template** / READY_FOR_REVIEW evidence after post-diff audit

### Residual risks

- The LTF branch still owns multiple early returns and final-stage debug payload construction just before summary assembly.
- The main parity risks are `ltf_fib_entry_debug` payload drift, hidden reason-order drift, and accidental movement of final summary timing.

### Governance review

- **Pre-review verdict:** `APPROVED_WITH_NOTES`
- **Post-diff verdict:** `APPROVED`
- **Post-diff READY_TO_COMMIT:** `YES`
- **Reviewer:** `Opus 4.6 Governance Reviewer`
