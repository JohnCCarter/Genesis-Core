# RI policy router issue #104 evidence-first comparison — 2026-05-26

## Scope

Bounded RESEARCH comparison between the current local evidence-first `continuation_release_hysteresis` chain and GitHub issue [#104](https://github.com/JohnCCarter/Genesis-Core/issues/104), which asks for a policy contribution matrix before any RI policy promotion or widening claim.

Question:

> does the current evidence-first chain already satisfy the validation intent of issue `#104`, where does it only partially satisfy it, and what remains genuinely missing?

This slice is docs-only and observational.

It does **not** authorize new runtime work, redefine policy authority, or claim that the `continuation_release_hysteresis` seam is promotion-ready just because one local chain has now been exhausted carefully.

## Inputs

- GitHub issue [#104](https://github.com/JohnCCarter/Genesis-Core/issues/104): `Research: define policy contribution matrix for RI policy-router validation`
- bounded router-leaf contribution proof: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_bounded_contribution_evidence_2026-04-28.md`
- annual router-leaf contribution proof: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_annual_evidence_2026-04-28.md`
- curated annual router-leaf evidence: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- negative/positive year pocket comparison chain:
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_negative_year_pocket_isolation_2026-04-28.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_vs_negative_pocket_comparison_2026-04-28.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_selective_feature_gate_contrast_2026-04-30.md`
- current local seam chain for `continuation_release_hysteresis`:
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2024_01_2026-05-26.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_local_envelope_cancellation_candidate_2024_01_2026-05-26.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_local_action_position_equivalence_candidate_2024_01_2026-05-26.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_control_mode_only_residual_inventory_candidate_2024_01_2026-05-26.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_switch_control_mode_semantics_candidate_2024_01_2026-05-26.md`

## What changed and what did not

- **Changed:** one bounded comparison note maps issue `#104`'s requested validation matrix against the repo's current evidence-first RI router chain.
- **Did not change:** no runtime/config/test file changed, no new evidence artifact was generated, and the note does not convert a research comparison into promotion or authority.

## Observed

### 1. Issue `#104` asks for a policy contribution matrix, not another local micro-proof by itself

Issue `#104` asks for a validation matrix containing at least:

- OFF baseline
- Single ON
- All ON
- All ON minus X
- affected rows
- unaffected rows
- failure mode
- year/regime split
- masking/compensation
- verdict

It also states two important boundaries:

- prefer artifact-only / read-only evidence first
- no promotion, widening, or implementation authority is granted by the issue itself

So the issue is mostly asking for a validation contract and evidence map, not for immediate code.

### 2. The repo already covers much of the matrix for the **whole RI router leaf**

Existing evidence already answers several issue-`#104` columns for the active `research_policy_router` leaf:

#### Incremental effect under real stack conditions

- bounded enabled-vs-absent carrier proof:
  - `ri_policy_router_enabled_vs_absent_bounded_contribution_evidence_2026-04-28.md`
- annual enabled-vs-absent proof:
  - `ri_policy_router_enabled_vs_absent_annual_evidence_2026-04-28.md`
- curated multi-year enabled-vs-absent proof:
  - `ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`

These already answer a practical version of:

- what happens with the leaf enabled vs absent
- whether the leaf changes real rows
- whether the sign of benefit flips across years

#### Affected/unaffected rows and failure mode structure

- negative-year pocket isolation
- positive-vs-negative pocket comparison
- insufficient-evidence feature-gate contrast

These already go beyond top-line ledger deltas and ask:

- which rows are actually changing
- whether the same shape appears in positive and negative years
- which bounded discriminators might separate harmful vs non-harmful cohorts

So for the full router leaf, the repo already has substantial issue-`#104` coverage.

### 3. The current `continuation_release_hysteresis` chain covers a **different** subset of the issue matrix

The current local evidence-first seam chain gives unusually strong coverage on these matrix dimensions:

- **All ON vs All ON minus X**
  - baseline: same enabled carrier as-is
  - comparison: same enabled carrier with `continuation_release_hysteresis = 0`
- **affected rows**
  - exact local packet surfaces (`2021-04`, `2020-06`, `2024-01`)
- **unaffected rows**
  - month-level economics remain flat on the same months
- **masking / compensation**
  - action-position equivalence shows the retained asymmetry is absorbed before execution
- **failure-mode localization**
  - late residual inventory isolates candidate-only breadcrumb tails after the last locked-size row

So the evidence-first seam chain is already answering the issue's row-level and compensation questions quite well.

### 4. But the seam chain does **not** yet satisfy the whole issue contract by itself

The current `continuation_release_hysteresis` chain still lacks at least four things that issue `#104` asks for explicitly or implicitly:

#### A. No explicit matrix packaging

The evidence exists in pieces, but it is not yet gathered in one explicit `policy_contribution_matrix` surface.

#### B. No meaningful isolated-contribution lane for the seam alone

Issue `#104` asks for something like `Single ON` vs `OFF baseline`.

For the router leaf, enabled-vs-absent artifacts already approximate this.

For `continuation_release_hysteresis` specifically, that comparison is less natural because the seam is not a standalone policy leaf; it is a local control parameter on one release edge inside an already-active router.

So the current seam chain mainly answers incremental contribution inside the active stack, not isolated policy identity.

#### C. No broader annual/cross-cohort `All ON minus X` evidence for the seam itself

The local chain is strong on exact row-bound surfaces, but it does not yet answer:

> across a wider annual or cohort-level surface, does `continuation_release_hysteresis` improve, harm, or merely reshuffle outcomes under the full active stack?

That matters especially because the user's standing caution is explicitly about `2024` harm.

#### D. No explicit seam verdict language mapped to issue `#104`

The local chain currently implies:

- real affected rows exist
- local economic harm is repeatedly falsified on the bounded exact-envelope path
- remaining local residuals decay into compensation/breadcrumb surfaces

But it does not yet place that in one issue-`#104` verdict bucket such as:

- redundant or masked
- research-only
- conditional split required
- park

### 5. The new `2024-01` local chain does **not** contradict issue `#104`; it fills one of its hardest columns

The widened `2024-01` chain now says:

- packet asymmetry survives locally
- exact local envelope economics remain flat
- exact local execution remains equivalent
- the late candidate-only tail collapses to `switch_control_mode` breadcrumb semantics

That is not a rejection of issue `#104`.

It is a strong answer to one of its most important subquestions:

> if the seam changes rows, is the effect still present at the ledger and execution layers, or is it being masked/compensated inside the active stack?

For the bounded local `2024-01` surface, the answer is currently:

> the seam changes rows, but the effect is compensated before it becomes a local economic or execution divergence.

### 6. The explicit “2024 harm” concern still lives at a broader surface than the exhausted local chain

The repo already has annual router-leaf evidence showing:

- enabled worse than absent in `2024`
- enabled better than absent in `2025`

The new local `2024-01` chain shows something narrower:

- one exact `2024` continuation-release candidate month does **not** open a bounded local economic or execution gap on the seam-specific exact local path

So the correct comparison is:

- issue `#104` asks whether policy contribution survives real-stack and cohort/year conditions
- the current local seam chain shows that the `2024` concern is **not** explained by this exact local seam pocket alone

That narrows the question instead of resolving the broader year-level concern.

## Inferred

### 1. The current evidence-first approach is already a strong **submatrix**, not a full replacement for issue `#104`

The smallest honest synthesis is:

> the repo already has substantial issue-`#104` coverage, and the new evidence-first `continuation_release_hysteresis` chain is best understood as the matrix's high-resolution local incremental-contribution / masking / compensation branch rather than as the whole validation contract by itself.

### 2. Issue `#104` and the local evidence-first chain are complementary, not competing framings

Issue `#104` asks for a disciplined policy-level validation contract.

The local chain answers one crucial part of that contract very well:

- exact affected rows
- exact unaffected rows
- exact compensation path
- exact breadcrumb decay after the last locked-size row

So the issue does not invalidate the local chain.

The local chain supplies a sharper layer beneath the issue.

### 3. The cheapest honest next move is a docs-only matrix map, not immediate new runtime work

Because issue `#104` explicitly prefers artifact-only/read-only evidence first, and because the repo already contains most of the needed pieces, the cheapest admissible next step is not code.

It is one docs-only matrix map that:

- lists the issue columns explicitly
- points each column to already-existing artifacts where possible
- marks the seam-specific gaps clearly
- keeps the output non-authorizing

That would satisfy the issue's contract intent with much less churn than reopening runtime or widening blindly.

### 4. If a non-doc slice is chosen instead, it should target the missing column — broader seam contribution under stack conditions

If the work stays evidence-first but moves beyond docs, the next honest non-doc slice is not another local envelope variant.

It would be a bounded comparison that addresses the still-missing column:

> does `continuation_release_hysteresis` show any broader `All ON minus X` contribution or harm on a fixed annual/cohort surface, especially around the standing `2024` concern?

## Unverified

The following remain open:

1. whether a single docs-only matrix note is enough to satisfy issue `#104`, or whether the repo should also add a more formal non-authorizing contract packet
2. whether `continuation_release_hysteresis` has any measurable broader annual/cross-cohort `All ON minus X` contribution beyond the exact local surfaces now repeatedly falsified
3. whether the remaining `2024` concern sits in another router mechanism, another time surface, or only at the whole-leaf stack layer rather than inside this seam-specific local path

## Bottom line

Issue `#104` is not asking us to throw away the current local evidence-first work.

It is asking us to package and interpret it correctly.

What is now supported is:

> the repo already contains much of the evidence that issue `#104` asks for, and the newly exhausted `continuation_release_hysteresis` local chain fills the matrix's high-resolution affected-row / masking / compensation columns especially well; what is still missing is explicit matrix packaging and any broader annual/cohort `All ON minus X` evidence for the seam itself.

So the most honest next move is either:

- a docs-only issue-`#104` matrix map, or
- one bounded broader seam-contribution slice on a fixed `2024`-relevant surface.
