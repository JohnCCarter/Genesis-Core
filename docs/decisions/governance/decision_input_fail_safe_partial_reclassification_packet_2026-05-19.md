# Decision-input fail-safe partial reclassification packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `decision-recorded / tests-backed / non-authorizing`

This packet records one bounded partial reclassification only for baseline finding `#14`. It does not claim that all decision-input hardening is solved. It records that the exact crash seam described in the baseline is narrower on this branch than the baseline row alone suggests: current decision code already fails safe for several malformed `probas` / `confidence` shapes instead of raising type errors, and focused regression coverage now explicitly locks those non-dict paths. The broader absence of property-based input-shape coverage remains unverified.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `obs`
- **Risk:** `LOW` — why: tests + docs evidence hardening only; no runtime code/config behavior change
- **Required Path:** `Bounded RESEARCH slice / tests + docs only`
- **Lane:** `Research-evidence` — why: this slice narrows current branch-visible interpretation of a strategy-input hardening finding without changing runtime authority surfaces
- **Skill usage:** `none required` — bounded tests/docs truthfulness slice
- **Objective:** record that the exact `#14` crash reading should be narrowed because current decision code already fail-safes several malformed input shapes, and lock that branch-visible behavior with focused regression tests
- **Related artifacts:** `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`, `src/core/strategy/decision.py`, `src/core/strategy/decision_gates.py`, `tests/utils/test_decision.py`, `tests/utils/test_decision_gates_contract.py`

### Scope

- **Scope IN:** one focused test expansion in `tests/utils/test_decision.py`; this packet; one later-branch partial-reclassification note for `#14` in `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Scope OUT:** any edit under `src/core/strategy/**`; any property-based framework introduction; any claim that all malformed decision inputs are now exhaustively covered; any broader strategy/runtime behavior change
- **Expected changed files:** `tests/utils/test_decision.py`, `docs/decisions/governance/decision_input_fail_safe_partial_reclassification_packet_2026-05-19.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`

### Gates required

For this no-behavior-change evidence slice:

- `tests/utils/test_decision.py`
- `tests/utils/test_decision_gates_contract.py`
- manual wording audit that `#14` is narrowed, not closed as a broader input-hardening family
- stop-and-reopen rule if a new test exposes a real runtime defect in `src/core/strategy/**`

## Purpose

This slice answers one narrow question only:

- what is the honest current-branch reading of baseline `#14` after checking the current decision fail-safe guards and adding focused coverage for non-dict input shapes?

## What changed in this slice

- one focused test expansion now proves that non-dict `probas` shapes fail safe instead of raising
- one focused test expansion now proves that non-dict `confidence` shapes fail safe instead of raising
- the baseline now carries a dated later-branch note clarifying that the exact crash seam is narrower on this checkout

## What did not change

- no runtime decision code changed
- no strategy defaults changed
- no claim is made that property-based coverage now exists
- no claim is made that every malformed input shape is covered

## Governing basis

### Observed

1. `src/core/strategy/decision_gates.py::select_candidate(...)` already returns fail-safe `NONE` when `probas` is missing or not a `dict`.
2. `src/core/strategy/decision_gates.py::apply_post_fib_gates(...)` already returns fail-safe `NONE` when `confidence` is missing or not a `dict`.
3. `src/core/strategy/decision_gates.py::safe_float(...)` already coerces non-numeric or overflowing numeric-like values to defaults instead of raising.
4. Existing tests in `tests/utils/test_decision.py` already prove some `None` / string-valued `probas` and non-numeric confidence-value cases do not raise type errors.
5. Existing tests in `tests/utils/test_decision_gates_contract.py` already prove the fail-safe/null candidate path for missing `probas`.
6. This slice adds explicit regression coverage for non-dict `probas` and non-dict `confidence` shapes in `tests/utils/test_decision.py`.

### Inferred

- the exact `#14` reading is narrower than `decide()` still plausibly crashes on basic malformed `None` / string input shapes`
- the honest current residual is broader property-based or more exhaustive shape coverage, not an unchanged branch-visible crash seam for the newly covered malformed inputs
- a tests-backed partial reclassification is truer than either declaring `#14` solved or leaving the baseline wording unchanged

### Unverified

- whether more exotic malformed nested shapes could still expose uncovered fail-safe gaps
- whether Hypothesis/property-based coverage should later be added for broader input-shape exploration
- whether adjacent strategy entry points outside the tracked `decide()` path need similar explicit coverage

## Bottom line

Finding `#14` should be **partially reclassified** on this branch. Current strategy decision code already fail-safes several malformed `probas` / `confidence` inputs, and focused regression coverage now makes those non-dict paths explicit. This slice does **not** claim exhaustive hardening or property-based proof; it only narrows the stale branch-visible crash reading.
