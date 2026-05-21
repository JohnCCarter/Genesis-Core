# Optimizer validation payload-carrier surface selection packet

Date: 2026-05-21
Branch: `feature/risk-hardening-wave3`
Status: `decision-recorded / docs-only / non-authorizing`

This packet records the next fresh current-branch `#16` surface after the already-landed first
code-bearing validation → promotion helper extraction. It does not authorize optimizer source
changes, restart the March split queue, or imply that `runner_optuna_orchestration.py` is the
default next locus by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice narrows one future optimizer surface only and changes no
  optimizer runtime behavior, promotion policy, or tests
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice selects one exact next `#16` surface without
  reopening optimizer implementation work
- **Skill usage:** `none required` — bounded docs-only optimizer surface selection
- **Objective:** record the next fresh current-branch `#16` surface after the first
  validation/promotion helper extraction, while narrowing a stale broad reading in the optimizer
  refactor README
- **Related artifacts:**
  `docs/decisions/governance/optimizer_validation_promotion_contract_seam_packet_2026-05-21.md`,
  `docs/audit/refactor/optimizer/README.md`, `handoff.md`, `src/core/optimizer/runner.py`,
  `src/core/optimizer/runner_validation.py`, `src/core/optimizer/runner_trial_results.py`,
  `tests/utils/test_optimizer_runner.py`

### Scope

- **Scope IN:** this packet; one later-branch truthfulness note in
  `docs/audit/refactor/optimizer/README.md`; one live note refresh in `handoff.md`
- **Scope OUT:** all edits under `src/**`, `tests/**`, `scripts/**`, `config/**`, `results/**`, and
  `artifacts/**`; any optimizer code refactor; any score-version/comparability/promotion-policy
  change; any implication that `runner_optuna_orchestration.py` automatically re-enters scope next
- **Expected changed files:**
  `docs/decisions/governance/optimizer_validation_payload_carrier_surface_selection_packet_2026-05-21.md`,
  `docs/audit/refactor/optimizer/README.md`, `handoff.md`
- **Max files touched:** `3`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual wording audit that the slice remains non-authorizing and docs-only
- manual wording audit that the first landed `#16` helper seam is not re-described as still open
- manual wording audit that the next surface is narrower than broad `runner.py` +
  `runner_optuna_orchestration.py` carry-forward language

## Purpose

This packet answers one narrow question only:

- after the first validation → promotion helper extraction landed, what is the next fresh `#16`
  surface on the current branch?

## What changed in this slice

- one new packet selects the next fresh `#16` surface after the first landed helper extraction
- the optimizer refactor README is narrowed so it no longer implies a broad runner/orchestration
  reopen as the default next move
- `handoff.md` is refreshed so wave3 records the new exact `#16` surface instead of leaving the
  family at vague fragmentation language

## What did not change

- no optimizer code changed
- no tests changed
- no promotion behavior changed
- no March optimizer artifacts were reactivated as a live plan

## Governing basis

### Observed

1. `docs/decisions/governance/optimizer_validation_promotion_contract_seam_packet_2026-05-21.md`
   now carries a later-branch note saying the first code-bearing follow-up on the selected
   validation → promotion seam has already landed on `feature/risk-hardening-wave3`.
2. Current `src/core/optimizer/runner.py` now delegates best-candidate scanning to
   `_select_best_candidate_from_results(...)`, but still owns the hand-off from
   `validation_results` to `results_for_promotion`.
3. Current `src/core/optimizer/runner_validation.py::run_validation_stage_impl(...)` still:
   - selects validation candidates
   - runs validation trials
   - mutates dict payloads with `stage="validation"`
   - returns the raw payload list that promotion later consumes
4. Current `src/core/optimizer/runner_trial_results.py::_candidate_from_result(...)` still defines
   the payload fields promotion depends on for candidate eligibility and champion construction.
5. `docs/audit/refactor/optimizer/README.md` still frames the first admissible future subtopic as
   the broad orchestration / validation / promotion boundary across `runner.py` and
   `runner_optuna_orchestration.py`, which is now too coarse as the default next reading after the
   first code-bearing seam already landed in `runner.py` / `runner_validation.py` /
   `runner_trial_results.py`.
6. `tests/utils/test_optimizer_runner.py` already pins the relevant current branch boundary
   behavior for validation-best promotion, missing-data blocking, validation-stage patch surfaces,
   and promotion negative cases.

### Inferred

- the next honest `#16` surface is no longer a broad runner/orchestration pairing by default
- the fresh current opacity is the **validation result-payload carrier** in
  `run_validation_stage_impl(...)`: the point where validation payloads are tagged and returned for
  later promotion consumption
- narrowing the README to this smaller surface better matches the already-landed first helper seam
  and avoids silently widening the next reopen back into `runner_optuna_orchestration.py`

### Unverified

- whether a later code slice is needed at all
- whether a later implementation would keep the payload carrier in `runner_validation.py` or wrap it
  elsewhere
- whether `stage="validation"` should remain documentary only or ever become a stronger contract
  field in a future reopen

## Surface selection conclusion

The next fresh current-branch `#16` surface is:

- the **validation result-payload carrier in `runner_validation.py::run_validation_stage_impl(...)`**,
  not a blanket reopen of `runner.py` + `runner_optuna_orchestration.py`

This selection does **not** approve code work. It records the next honest surface only.

## Bottom line

On wave3, `#16` should no longer be retold as “resume the optimizer split” or “default back to
runner plus orchestration.” After the first landed helper seam, the next fresh surface is the
validation payload carrier that hands results forward for promotion use.
