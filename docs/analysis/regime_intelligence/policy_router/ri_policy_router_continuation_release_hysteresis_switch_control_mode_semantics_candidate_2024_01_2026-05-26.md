# RI policy router continuation_release_hysteresis switch_control_mode semantics candidate 2024-01 — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the landed `2024-01` control-mode-only residual inventory slice.

Question:

> now that the late `2024-01` local residual has been isolated to `switch_control_mode` alone, does that field carry any independent runtime behavior here, or is the widened 2024 tail using the same descriptive router/debug breadcrumb semantics already established for the earlier candidate chain?

This slice is read-only and observational.

It does **not** rerun the carrier, reopen the local execution/economic question, or edit any runtime/config surface.

## Inputs

- residual inventory artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2024_01_2026-05-26.json`
- prior semantics closure: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_switch_control_mode_semantics_candidate_2020_06_2026-05-26.md`
- historical exercising control note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_exercising_subject_2026-05-04.md`

## What changed and what did not

- **Changed:** one new bounded analysis note ties the late `2024-01` residual rows to the already-established in-repo semantics of `switch_control_mode`.
- **Did not change:** no runtime file changed, no new code inspection was needed to redefine the field, and the isolated `2024-01` breadcrumb was not reinterpreted as if it had become execution or P&L divergence.

## Observed

### 1. The late `2024-01` candidate residual is already isolated to `switch_control_mode` alone

From the landed residual inventory artifact:

- candidate-only rows: `3`
- control rows: `0`
- candidate timestamps:
  - `2024-01-19T00:00:00+00:00`
  - `2024-01-19T03:00:00+00:00`
  - `2024-01-19T06:00:00+00:00`
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

So the widened 2024 residual is already narrowed to the semantics of that single field.

### 2. The field/value pattern matches the already-closed local breadcrumb story

The three late `2024-01` rows all show:

- selected policy: `RI_continuation_policy` on both paths
- switch reason: `stable_continuation_state` on both paths
- action/effect: execution-equivalent on both paths
- only the control-mode label differs (`continuation_release` vs `default`)

That is the same structural state as the earlier candidate-only breadcrumb tail:

- continuation routing is already aligned
- the late separation survives only in the control-mode label

### 3. The existing semantics closure already established the meaning of `switch_control_mode`

The earlier `2020-06` semantics note tied repo evidence together as follows:

- `switch_control_mode` is written inside the router’s release-path control helper
- it labels whether the row is still treated as defensive -> continuation release (`continuation_release`) or has normalized to ordinary routing (`default`)
- the field is emitted via router/debug state rather than consumed downstream as an independent action/size driver

Nothing in the new `2024-01` residual inventory contradicts that meaning.

Instead, the widened 2024 tail fits it exactly.

### 4. The older exercising-subject note already describes the same late label behavior

The exercising control note records that on late release rows:

> baseline can still record `switch_control_mode == continuation_release` because it is unwinding the defensive -> continuation release path, while the zero-hysteresis branch has already normalized into ordinary continuation routing.

That wording also fits the new `2024-01` tail:

- both paths already agree on continuation state
- only the label describing how that state is being reached/held still differs

## Inferred

### 1. The late `2024-01` residual is descriptive router state, not a new execution-bearing signal

The smallest honest inference is:

> on the `2024-01` late residual rows, `switch_control_mode` is not introducing a new behavioral branch; it is describing that baseline is still tagged as continuity reached via the release path while `release_zero` has already normalized to the default continuation control mode.

### 2. This closes the remaining local ambiguity for `2024-01`

The bounded local chain for `2024-01` now says:

- stronger packet asymmetry than the fixed control
- exact local envelope economics still flat
- no execution divergence on the exact envelope
- the remaining candidate-only late tail is just `switch_control_mode`
- that field already has an established descriptive/debug-like meaning in repo evidence

So the local `2024-01` separator is best read as a traceability breadcrumb, not as a hidden execution surface.

### 3. The next honest continuation is widening or issue-aligned evidence comparison, not more local breadcrumb shaving

Because the `2024-01` local path now ends at the same semantics closure as the earlier candidate chain, the admissible next move is no longer another microscopic local replay.

It is either:

- widen again to a new candidate surface, or
- compare the current evidence-first chain against the earlier GitHub issue framing and see what still genuinely differs

## Unverified

The following remain open:

1. whether the next widened candidate month also decays to the same descriptive `switch_control_mode` breadcrumb
2. whether any non-local or issue-framed evidence surface still separates 2024 concerns after the exact local packet/envelope/execution/residual chain is exhausted
3. whether the earlier GitHub issue #104 expects a different evidence surface than the one now repeatedly falsified locally

## Verification

- read-only inspection of `results/evaluation/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2024_01_2026-05-26.json`
- read-only cross-check against `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_switch_control_mode_semantics_candidate_2020_06_2026-05-26.md`
- read-only cross-check against `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_exercising_subject_2026-05-04.md`

## Bottom line

This slice closes the local `2024-01` chain without pretending the breadcrumb means more than it does.

What is now supported is:

> after the last locked-size row disappears, the remaining `2024-01` candidate-only residual is just `switch_control_mode`; and the already-established repo semantics for that field say it is a descriptive release-path/debug label, not a separately consumed execution-bearing signal.

So the next honest continuation is to move off the exhausted local `2024-01` path rather than shaving even smaller breadcrumbs from it.
