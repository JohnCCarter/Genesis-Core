# Optimizer validation → promotion contract seam packet

Date: 2026-05-21
Branch: `feature/risk-hardening-wave3`
Status: `precode-defined / docs-only / non-authorizing`

Later-branch truthfulness note (2026-05-21): the first code-bearing follow-up on this exact seam
has now been landed on `feature/risk-hardening-wave3`. `src/core/optimizer/runner.py` now
delegates the best-candidate scan to
`src/core/optimizer/runner_trial_results.py::_select_best_candidate_from_results(...)`, while the
runner-level `_candidate_from_result(...)` patch surface remains preserved via callback injection.
Observed behavior of the landed slice remains no-behavior-change for validation-result preference,
candidate eligibility semantics, score-version/comparability policy, and champion write policy.
Observed gate stack for that later branch implementation: touched-file `black --check`; touched-file
`ruff check`; `pytest tests/utils/test_optimizer_runner.py -q`; `pytest`
`tests/governance/test_import_smoke_backtest_optuna.py -q`; `pytest`
`tests/backtest/test_backtest_determinism_smoke.py -q`; `pytest`
`tests/utils/test_features_asof_cache_key_deterministic.py -q`; and `pytest`
`tests/governance/test_pipeline_fast_hash_guard.py -q`. This packet remains a historical pre-code
selection artifact only; the note above records later-branch truthfulness, not new authority.

This document opens one bounded current-branch pre-code packet for `#16` only. It selects the
smallest exact future sub-boundary inside the already-chosen optimizer orchestration /
validation / promotion area: the validation → promotion result-contract seam around
`run_validation_stage_impl()`, `results_for_promotion`, and `_candidate_from_result()`.

The current slice is docs-only and does not approve source changes, test changes, optimizer
behavior changes, March refactor continuation, or queue activation by implication.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice narrows one future optimizer refactor seam in docs only and
  changes no runtime, tests, or optimizer behavior
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice chooses one exact future optimizer reopen seam
  without beginning refactor work
- **Skill usage:** `none required` — bounded docs-only optimizer traceability / candidate-selection
  slice
- **Objective:** define the smallest current-branch exact reopen inside the already-selected
  orchestration / validation / promotion boundary, without reviving the full March optimizer split
  queue
- **Candidate:** `future validation → promotion contract seam around run_validation_stage_impl(),
results_for_promotion, and _candidate_from_result()`
- **Base SHA:** `44ed6b4a`
- **Related artifacts:**
  `docs/decisions/governance/optimizer_refactor_trace_reopen_shape_packet_2026-05-19.md`,
  `docs/audit/refactor/optimizer/README.md`,
  `docs/audit/refactor/optimizer/context_map_runner_split2_optuna_orchestration_validation_promotion_2026-03-13.md`,
  `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`,
  `src/core/optimizer/runner.py`, `src/core/optimizer/runner_validation.py`,
  `src/core/optimizer/runner_trial_results.py`, `tests/utils/test_optimizer_runner.py`

### Scope

- **Scope IN:** this new packet; one matching live-note update in `handoff.md`; explicit future
  scope/gates/stop conditions for the selected contract seam only
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and
  `artifacts/**`; any blanket continuation of the March optimizer split tracks; any selection of a
  second optimizer subtopic; any runtime/promotion/config authority claim; any wording that treats
  the historical optimizer refactor folder as a live approval queue
- **Expected changed files:**
  `docs/decisions/governance/optimizer_validation_promotion_contract_seam_packet_2026-05-21.md`,
  `handoff.md`
- **Max files touched:** `2`

### Gates required

For this docs-only slice:

- targeted docs validation for this packet and `handoff.md`
- manual wording audit that the slice remains docs-only and non-authorizing
- manual wording audit that exactly one `#16` sub-boundary is selected
- manual wording audit that no March optimizer artifact is rewritten as branch-current approval

## Purpose

This packet answers one narrow question only:

- after the retained optimizer refactor folder was reclassified as historical-only, what is the
  smallest honest current-branch `#16` reopen seam?

## What changed in this slice

- one new docs-only packet narrows `#16` to an exact validation → promotion contract seam
- the slice records why blanket optimizer-split retelling is no longer the honest next move
- the handoff live note is aligned so `#16` is grounded to one exact seam rather than a vague hot-file
  complaint

## What did not change

- no optimizer code changed
- no tests changed
- no validation selection behavior changed
- no champion promotion behavior changed
- no score-version or comparability policy changed
- no March optimizer packet was reactivated as a live plan

## Governing basis

### Observed

1. `docs/decisions/governance/optimizer_refactor_trace_reopen_shape_packet_2026-05-19.md` already
   narrowed the first admissible `#16` reopen to the optimizer orchestration / validation /
   promotion boundary, rather than broad continuation of all retained March split artifacts.
2. `src/core/optimizer/runner.py` currently imports `run_validation_stage_impl` from
   `runner_validation.py` and `_candidate_from_result` from `runner_trial_results.py`, keeping
   `run_optimizer(...)` as the facade/orchestrator.
3. In `run_optimizer(...)`, `validation_results = run_validation_stage_impl(...)` is followed by
   `results_for_promotion = validation_results if validation_results is not None else results`, and
   the promotion loop then consumes each payload through `_candidate_from_result(result)`.
4. `src/core/optimizer/runner_validation.py::run_validation_stage_impl(...)` currently preserves
   validation payloads from `run_trial(...)`, adds `stage="validation"`, writes validation metadata,
   and returns the raw payload list without a separately documented promotion-facing contract.
5. `src/core/optimizer/runner_trial_results.py::_candidate_from_result(...)` currently decides
   promotion eligibility from `score.score`, `score.hard_failures`, and `constraints.ok`, while also
   carrying `parameters`, `trial_id`, `results_path`, and `merged_config` into
   `ChampionCandidate`.
6. `tests/utils/test_optimizer_runner.py` already pins branch-current boundary behavior for this
   seam, including validation-best promotion, validation missing-data promotion blocking,
   validation-stage patch-surface preservation, validation fallback from Optuna storage, and
   score-version / comparability guard behavior on adjacent promotion surfaces.

### Inferred

- the smallest current opacity is no longer “where validation happens,” but which result-payload
  contract must remain stable between validation output and promotion candidate extraction
- the first honest `#16` reopen is therefore narrower than the whole orchestration boundary and can
  stay docs-only until a later code slice is explicitly reopened
- because `runner_optuna_orchestration.py` already owns storage fallback and score-version/
  comparability helper surfaces, the first exact reopen can stay tighter than sampler/pruner/study
  orchestration work
- a contract-seam packet is a truer current-branch move than reviving the March split queue as if
  both historical subtracks were still silently active

### Unverified

- whether a later code slice is needed at all once the contract seam is explicit
- whether `_candidate_from_result(...)` should remain owned by `runner_trial_results.py` if a later
  extraction occurs
- whether validation fallback through Optuna storage can remain purely contextual or would need to
  enter a later implementation scope

## Candidate selection

### Current standing conclusion

The next admissible `#16` reopen is:

- a **docs-only pre-code packet for the validation → promotion contract seam** around
  `run_validation_stage_impl()`, `results_for_promotion`, and `_candidate_from_result()`

This is a candidate-selection conclusion only. It is **not** approval to refactor optimizer code.

### Why this seam first

The current branch supports this narrower reading:

- the broader orchestration / validation / promotion boundary is already selected at packet level
- `runner.py` still owns the hand-off from validation outputs into promotion selection
- the contract consumed by `_candidate_from_result(...)` is real, current, and already test-pinned
- this exact seam can be described without reopening study/sampler/pruner, config-sidecar, or March
  split-3 topics

## Likely future implementation scope

If this candidate is later reopened as an implementation-bearing slice, the smallest honest starting
scope is likely:

- `src/core/optimizer/runner.py`
- `src/core/optimizer/runner_validation.py`
- `src/core/optimizer/runner_trial_results.py`
- `tests/utils/test_optimizer_runner.py`

`src/core/optimizer/runner_optuna_orchestration.py` is currently cited as **context only**. It
should remain out of the first implementation slice unless a newly discovered blocker proves that
validation fallback or comparability helpers must move with the contract seam.

### Likely future scope OUT

A later implementation slice for this candidate must keep the following out of scope unless
separately reopened:

- `src/core/optimizer/runner_config.py`
- sampler / pruner / study-creation ownership
- resume-signature policy
- score-version or comparability policy changes
- `ChampionManager` replacement policy or champion file semantics
- config / metadata / parameter-space split concerns
- any `src/core/backtest/**`, `src/core/config/**`, or paper/live execution surfaces

## What a future implementation packet must define

A later implementation-bearing packet for this candidate must define at minimum:

- the exact result-payload fields promotion is allowed to depend on after validation
- whether `stage="validation"` remains purely documentary or becomes part of the contract seam
- the exact ownership boundary between validation payload production and promotion candidate
  extraction
- whether `_candidate_from_result(...)` remains the promotion boundary helper or is only wrapped
- the exact tests proving no drift in validation-best promotion, missing-data blocking, and runner
  patch surfaces

## Minimum future verification stack

If this candidate advances to code later, the later packet must require at minimum:

1. touched-file `black --check`
2. touched-file `ruff check`
3. `pytest tests/utils/test_optimizer_runner.py -q`
4. `pytest tests/governance/test_import_smoke_backtest_optuna.py -q`
5. `pytest tests/backtest/test_backtest_determinism_smoke.py -q`
6. `pytest tests/utils/test_features_asof_cache_key_deterministic.py -q`
7. `pytest tests/governance/test_pipeline_fast_hash_guard.py -q`
8. if `runner_optuna_orchestration.py` enters scope, add the exact relevant Optuna helper/regression
   files such as `tests/utils/test_optuna_resume_signature.py` and
   `tests/utils/test_optimizer_duplicate_fixes.py`

This list is for a later implementation slice only. It is **not** claimed as already satisfied by
the current docs-only packet.

## Hard stop and reopen rule

If a later slice needs any of the following, it must stop and reopen as a separate bounded packet:

- edits in `runner_optuna_orchestration.py`
- score-version or comparability policy changes
- fallback selection semantics from Optuna storage
- broader champion promotion policy changes
- any implication that the full March optimizer split queue is active again

## Bottom line

The next honest `#16` move is not “resume the optimizer split.” It is a **docs-only pre-code
packet for the validation → promotion contract seam** already visible on the current branch. That
keeps the reopen exact, branch-truthful, and small enough to reason about before any optimizer code
is touched again.
