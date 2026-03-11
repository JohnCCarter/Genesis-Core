# Command Packet — decision modul split

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH` from `docs/governance_mode.md`
- **Risk:** `HIGH` — why: touches `src/core/strategy/*` (`decision.py` facade and extracted decision helpers)
- **Required Path:** `Full`
- **Objective:** Verify and evidence a no-behavior-change modular split of `core.strategy.decision` where `decide()` remains the public facade and internal logic is extracted into focused helper modules.
- **Candidate:** `decision modul split`
- **Base SHA:** `8e6c779e`

### Scope

- **Scope IN:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/decision_gates.py`
  - `src/core/strategy/decision_fib_gating.py`
  - `src/core/strategy/decision_sizing.py`
  - `docs/audit/refactor/decision/command_packet_decision_modul_split_2026-03-11.md`
  - `docs/audit/refactor/decision/context_map_decision_modul_split_2026-03-11.md`
- **Scope OUT:**
  - `config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
  - unrelated feature branches/worktrees
  - runtime/config authority and freeze paths
- **Expected changed files:** `6`
- **Max files touched:** `6`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- `decide()` signature and repo-local import path must remain unchanged.
- Gate ordering inside `decide()` must remain semantically identical:
  1. candidate selection / fail-safe / thresholds
  2. fib gating
  3. post-fib gates
  4. sizing
- Existing `state_out`, `reasons`, and override-state mutations must preserve parity.

### Gates required

- `black --check` on the four touched decision files
- `ruff check` on the four touched decision files
- Focused decision selectors:
  - `tests/utils/test_decision.py`
  - `tests/utils/test_decision_edge.py`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
- Determinism / pipeline-path selectors:
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta`
  - `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic`
- Feature cache invariance selector:
  - `tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- Pipeline invariant selector:
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- Supplemental smoke selector:
  - `tests/backtest/test_run_backtest_decision_rows.py`

### Gate outcomes

- `black --check src/core/strategy/decision.py src/core/strategy/decision_gates.py src/core/strategy/decision_fib_gating.py src/core/strategy/decision_sizing.py` → `PASS`
- `ruff check src/core/strategy/decision.py src/core/strategy/decision_gates.py src/core/strategy/decision_fib_gating.py src/core/strategy/decision_sizing.py` → `PASS`
- `pytest tests/utils/test_decision.py tests/utils/test_decision_edge.py tests/integration/test_golden_trace_runtime_semantics.py tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_regime_module_deterministic -q` → `PASS (26 passed)`
- `pytest tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable -q` → `PASS (2 passed)`
- `pytest tests/backtest/test_run_backtest_decision_rows.py -q` → `PASS (3 passed)`

### Governance review

- **Pre-review verdict:** `APPROVED_WITH_NOTES`
- **Reviewer:** `Opus 4.6 Governance Reviewer`
- **Key note:** replace hook-only backtest evidence with real `evaluate_pipeline` selectors for parity proof.

### Stop Conditions

- Scope drift beyond the four decision files plus evidence docs
- Any behavior change without explicit exception
- Determinism or pipeline invariant regression
- Forbidden/high-sensitivity paths outside approved scope touched

### Output required

- **Implementation Report** with scope summary, file summary, exact gates, and residual risks
- **PR evidence template** / READY_FOR_REVIEW evidence after post-diff audit

### Residual risks

- Mutable cross-module state (`state_out`, `reasons`, `override_state`) remains the primary parity risk; current focused + pipeline tests passed.
- No post-diff governance signoff yet in this worktree after evidence docs creation.
