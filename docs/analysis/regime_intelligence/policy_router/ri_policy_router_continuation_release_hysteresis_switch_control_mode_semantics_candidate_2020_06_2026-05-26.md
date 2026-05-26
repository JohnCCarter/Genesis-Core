# RI policy router continuation_release_hysteresis switch_control_mode semantics candidate 2020-06 — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed `2020-06` control-mode-only residual inventory slice.

Question:

> now that the late `2020-06` local residual has been isolated to `switch_control_mode` alone, does that field carry any runtime behavior on its own, or is it only a descriptive router/debug breadcrumb for the same release-path state already visible elsewhere?

This slice is read-only and observational.

It does **not** rerun the carrier, reopen the local execution/economic question, or edit any runtime/config surface.

## Inputs

- residual inventory artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2020_06_2026-05-26.json`
- router implementation: `src/core/strategy/ri_policy_router.py`
- router tests: `tests/utils/test_ri_policy_router.py`
- historical exercising control note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_exercising_subject_2026-05-04.md`

## What changed and what did not

- **Changed:** one new bounded analysis note ties the late `2020-06` residual rows to the actual `switch_control_mode` write path in the router and to the existing exercising-subject interpretation already documented in-repo.
- **Did not change:** no runtime file changed, no carrier rerun was introduced, and the isolated breadcrumb was not reinterpreted as if it had become execution or P&L divergence.

## Observed

### 1. The late `2020-06` candidate residual is already isolated to `switch_control_mode` alone

From the landed residual inventory artifact:

- candidate-only rows: `3`
- control rows: `0`
- candidate timestamps:
  - `2020-06-18T12:00:00+00:00`
  - `2020-06-18T15:00:00+00:00`
  - `2020-06-18T18:00:00+00:00`
- all candidate rows occur after the last locked-size row

On all three candidate rows, the following already match between baseline and `release_zero`:

- action
- execution effect
- selected policy
- switch reason
- size
- position context

The sole remaining difference is:

- baseline `switch_control_mode = continuation_release`
- `release_zero` `switch_control_mode = default`

So the current question is genuinely only about the semantics of that one field.

### 2. Inside runtime source, `switch_control_mode` is assigned in exactly one place

Read-only inspection of `src/core/strategy/ri_policy_router.py` shows:

- `_resolve_switch_controls(...)` initializes `switch_control_mode = "default"`
- it flips to `"continuation_release"` only when both are true:
  - previous router state selected `POLICY_DEFENSIVE`
  - the current raw router decision targets `POLICY_CONTINUATION`
- the same helper also swaps in `continuation_release_hysteresis` as the effective hysteresis for that release path

So the field does not independently decide anything.

It labels one already-determined control regime: defensive -> continuation release.

### 3. Inside runtime source, the field is emitted into debug only

The same router file later:

- receives the tuple `(effective_switch_threshold, effective_hysteresis, switch_control_mode)`
- inserts `switch_control_mode` into the `debug` payload
- returns it as part of `PolicyRouterOutcome.debug`

Read-only workspace search within `src/**/*.py` found occurrences only in `src/core/strategy/ri_policy_router.py`:

- assignment to `"default"`
- conditional flip to `"continuation_release"`
- helper return
- local unpacking
- debug emission

No second runtime source file consumes `switch_control_mode` as an input to action, size, state transition, or execution behavior.

### 4. Tests assert the debug label, not downstream behavioral consumption of the label

Read-only inspection of `tests/utils/test_ri_policy_router.py` shows tests such as:

- blocked defensive -> continuation release path -> `debug["switch_control_mode"] == "continuation_release"`
- released path with `continuation_release_hysteresis=0` -> `debug["switch_control_mode"] == "continuation_release"`
- other paths -> `debug["switch_control_mode"] == "default"`

These tests confirm the label is emitted consistently with the release-path branch.

They do **not** demonstrate a second-stage consumer that uses the label itself to change runtime behavior.

### 5. The older exercising-subject note already gives the in-repo meaning of the label

The earlier exercising control note records that on late release rows:

> baseline still records `switch_control_mode == continuation_release` because it is releasing from the defensive state on those rows, while the release-zero branch has already normalized into ordinary continuation state.

That matches the code path above.

So the late `2020-06` residual is not introducing a new semantics story.

It is using the same already-documented release-path label.

## Inferred

### 1. The late `2020-06` residual is descriptive router state, not an independent execution-bearing signal

The smallest honest inference is:

> on the `2020-06` late residual rows, `switch_control_mode` does not carry a separate behavioral decision beyond describing whether the row is still tagged as defensive -> continuation release (`continuation_release`) or has already normalized back to ordinary routing (`default`).

That is consistent with both the router code and the already-landed artifact chain.

### 2. This closes the remaining local ambiguity for `2020-06`

Before this slice, it was still possible to argue that the candidate-only late residual might hide some additional harmless state distinction not yet isolated.

Now the repo evidence says:

- only `switch_control_mode` remains
- that field is assigned only inside the release-path control helper
- the field is emitted into debug
- no downstream runtime consumer appears in `src/**/*.py`

So the surviving `2020-06` local separator is best read as a traceability breadcrumb, not as a hidden execution surface.

### 3. The next honest continuation is widening, not another local 2020-06 micro-slice

Because the last surviving local residual now has a narrow descriptive semantics, the admissible next move is:

> retire `2020-06` on this bounded local path and widen to the next negative-like candidate month rather than extracting still smaller local breadcrumbs from the same envelope.

## Unverified

The following remain open:

1. whether the next widened candidate month also collapses to the same descriptive `switch_control_mode` breadcrumb
2. whether any non-runtime consumer outside `src/**/*.py` gives this field operational meaning beyond debug/analysis traceability
3. whether a wider non-local surface can still separate candidates after the exact local packet/envelope/execution chain has been exhausted

## Verification

- read-only inspection of `results/evaluation/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2020_06_2026-05-26.json`
- read-only inspection of `src/core/strategy/ri_policy_router.py`
- workspace search for `switch_control_mode` within `src/**/*.py`
- read-only inspection of `tests/utils/test_ri_policy_router.py`
- read-only cross-check against `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_exercising_subject_2026-05-04.md`

## Bottom line

This slice closes the local `2020-06` chain without claiming more than the code supports.

What is now supported is:

> after the last locked-size row disappears, the remaining `2020-06` candidate-only residual is just `switch_control_mode`; and inside runtime source that field is a descriptive release-path debug label, not a separately consumed execution-bearing signal.

So the next honest continuation is to widen again, not to keep shaving smaller local breadcrumbs off `2020-06`.
