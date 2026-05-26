# RI policy router continuation_release_hysteresis annual 2024 contribution — 2026-05-26

## Scope

Bounded RESEARCH follow-up to the new issue-`#104` comparison note.

Question:

> on the fixed full-year `2024` surface, under the same active router stack, does `continuation_release_hysteresis` show any broader `All ON minus X` contribution or harm when baseline is compared against the same carrier with `continuation_release_hysteresis = 0`?

This slice is observational only.

It does **not** change runtime/config surfaces, promote the seam, or reinterpret row-level diffs as automatically meaningful without the ledger and execution surfaces agreeing.

## Inputs

- script: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_annual_2024_contribution_20260526.py`
- artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_annual_2024_contribution_2026-05-26.json`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- issue comparison reference: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_issue_104_evidence_first_comparison_2026-05-26.md`

## What changed and what did not

- **Changed:** one new bounded yearly seam-contribution artifact and note compare full-year `2024` baseline vs `release_zero` under the same active stack.
- **Did not change:** no runtime/config/default changed, no new carrier was introduced, and the slice does not claim broader policy authority beyond this fixed annual surface.

## Observed

### 1. On full-year `2024`, the seam is top-line invariant

Packet summary status:

- `annual_2024_topline_mixed_or_flat_between_baseline_and_release_zero`

Key deltas (`release_zero - baseline`):

- total return diff: `0.0`
- final capital diff: `0.0`
- profit factor diff: `0.0`
- max drawdown diff: `0.0`
- net position PnL diff: `0.0`

So on the fixed annual `2024` stack surface, removing `continuation_release_hysteresis` does **not** improve or worsen the top line at all.

### 2. The seam still changes a huge number of rows — just not the action ledger

Annual comparison counts:

- bars processed: `2801`
- all row diff count: `2801`
- action diff count: `0`
- reason-only diff count: `2801`
- behavioral row diff count: `31`
- parameter-only diff count: `2770`

So the seam is not inert.

It changes row payloads everywhere on the annual surface, but almost all of that change is parameter-only, and even the `31` broader behavior-level row diffs do not alter action.

### 3. The continuation-release footprint inside the full year is tiny and still aligned with the old local January pocket

Continuation-release counts:

- baseline continuation-release rows: `11`
- `release_zero` continuation-release rows: `8`
- continuation-release diff count: `11`

Representative continuation-release rows in the annual artifact reproduce the same January `2024-01-17 -> 2024-01-19` pocket already studied locally:

- early min-dwell rows
- middle hysteresis vs continuation-supported rows
- late stable-continuation rows

So the broader annual surface is not revealing a second hidden continuation-release cluster elsewhere in `2024`.

It is mostly confirming that the already-known January pocket is the seam's visible exercising region.

### 4. Even the behavior-level annual diffs stay action-neutral

This is the important bridge to issue `#104`.

The annual slice shows:

- `31` rows where behavior-level state differs after normalizing away irrelevant parameter echoes
- `0` rows where action changes
- `0.0` delta on the annual top line

So the seam can change routed state, selected policy, or size-related internals without producing a different annual execution ledger or annual P&L result on this fixed `2024` surface.

### 5. The explicit “2024 harm” concern does not collapse to this seam

This matters because the standing concern was:

> maybe the `continuation_release_hysteresis` seam itself is part of why 2024 became worse.

This slice now says something narrower and stronger:

> on the fixed annual `2024` same-stack surface, toggling `continuation_release_hysteresis` from implicit shared hysteresis to `0` leaves annual return, annual capital, annual profit factor, annual drawdown, and annual net position PnL unchanged.

So the seam does **not** explain broader `2024` annual harm on this surface.

## Inferred

### 1. Issue `#104`'s missing broader `All ON minus X` column is now partly answered for `2024`

The current local chain had already shown:

- exact local packet asymmetry
- exact local economic flatline
- exact local execution equivalence
- late breadcrumb decay

This new annual slice adds:

> the same seam is also annual-topline invariant on the fixed `2024` stack surface.

That is a much stronger negative finding against the simple “this seam harmed 2024” story.

### 2. The seam appears heavily compensated, not broadly harmful

The smallest honest reading is:

> `continuation_release_hysteresis` does alter row-level router payloads throughout `2024`, but on the fixed annual stack surface those changes are almost entirely parameter-only and otherwise remain action-neutral and ledger-neutral.

That places the seam closer to:

- compensated
- masked
- research-only local state effect

than to a clean annual failure mechanism.

### 3. The broader 2024 concern must live elsewhere if it is real

Because the seam now fails to explain `2024` on both:

- the exhausted exact local path, and
- the fixed annual same-stack path,

the remaining `2024` concern must lie elsewhere if it remains real at all:

- another router mechanism
- another interaction surface
- or only the whole-leaf enabled-vs-absent layer rather than this one seam

## Unverified

The following remain open:

1. whether a positive-year control (for example `2025`) is equally invariant on the same seam-specific annual surface
2. whether the `31` action-neutral behavioral rows reduce to one compact row family that is still worth isolating descriptively
3. whether the remaining annual `2024` concern sits outside `continuation_release_hysteresis` and belongs instead to another RI router branch or to the leaf-level enabled-vs-absent interaction surface

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_annual_2024_contribution_20260526.py` -> emitted artifact with packet status `annual_2024_topline_mixed_or_flat_between_baseline_and_release_zero`
- `black scripts/analyze/ri_policy_router_continuation_release_hysteresis_annual_2024_contribution_20260526.py` -> pass
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_annual_2024_contribution_20260526.py` -> pass

## Bottom line

This slice answers the missing issue-`#104` question for the most relevant bad year surface without overclaiming.

What is now supported is:

> on fixed full-year `2024`, `continuation_release_hysteresis` changes many row payloads but produces zero action diffs and zero annual top-line delta against the same enabled stack with `continuation_release_hysteresis = 0`.

So the seam itself is not a credible standalone explanation for broader `2024` harm on this surface.
