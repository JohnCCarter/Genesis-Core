# RI advisory environment-fit — Phase 3 materially different surface inventory

This memo is docs-only and fail-closed.
It decides whether the repository already contains any **already materialized** evidence surface that is materially different enough to reopen deterministic RI advisory-baseline work after the current capture-v2 surface failed exact-label authority.

Governance packet: `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_materially_different_surface_inventory_packet_2026-04-17.md`

## Source surface used

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_exact_label_authority_preflight_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_alternative_evidence_surface_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_strategy_family_bridge_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_non_runtime_evidence_namespace_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_bundle_surface_reliability_opening_2026-04-17.md`
- `artifacts/research_ledger/artifacts/ART-2026-0001.json`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/materialized_exact_label_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/manifest.json`

## Decision question

After `NOT_RECOVERED` closed the current capture-v2 surface for same-surface authority-bearing continuation, does the repository already contain any materially different evidence surface that could honestly reopen deterministic advisory-baseline work?

## What counts as materially different here

The earlier admissibility closeout already fixed the relevant boundary:

- the current capture-v2 row surface is exhausted for the exact-label-authority question
- same-surface continuation is closed
- any continuation must come through a materially different evidence surface instead

For this inventory, a candidate surface survives only if it already exists in the repository and satisfies all of the following:

1. **co-resident observability and authority**
   - it carries RI-relevant observability and authority-bearing outcomes on the same surface, rather than depending on the same sparse `7 / 90` join-back failure
2. **deterministic completeness**
   - any required join remains exact, unique, and materially complete enough that row-level authority is not mostly absent by construction
3. **RI-only / advisory-only discipline**
   - it does not depend on cross-family leakage, runtime-authority drift, or bridge-authoring disguised as neutral packaging
4. **contradiction-year usefulness**
   - it could support honest multi-year evaluation, especially against `2025`, rather than merely preserving a discovery-year local story

## Provenance is not the same thing as an evidence surface

This inventory uses `tmp/**` scripts and the research-ledger record only as provenance/index aids.
They help identify where existing surfaces came from.
They are **not** admissible candidate evidence surfaces by themselves.

That means the following do not count as candidates on their own:

- `tmp/ri_advisory_environment_fit_capture_v2_20260417.py`
- `tmp/ri_advisory_environment_fit_reliability_exact_label_authority_preflight_20260417.py`
- `artifacts/research_ledger/artifacts/ART-2026-0001.json`

## Candidate inventory

### 1. Current bundle-driven capture-v2 RI row surface

Candidate surface:

- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/`

Verdict:

- **reject**

Why:

This is the surface that the current lane already used for:

- selector-side admissibility
- proxy restoration
- dirty-research shaping
- exact-label-authority preflight

It is therefore the exhausted surface for the already-closed question, not a new one.
The exact-label-authority preflight then failed closed with:

- shared comparison rows: `90`
- rows matched back to capture-v2: `7`
- supportive rows on capture-v2: `1`
- hostile rows on capture-v2: `2`
- non-evaluable rows: `143`

So repackaging, re-describing, or re-summarizing this same bundle/capture-v2 surface does **not** make it materially different for the authority-bearing continuation question.
That closure is already fixed by:

- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_capture_v2_baseline_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_exact_label_authority_preflight_admissibility_2026-04-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_alternative_evidence_surface_admissibility_2026-04-17.md`

### 2. Materialized exact-label rows from the preflight

Candidate surface:

- `results/research/ri_advisory_environment_fit/phase3_reliability_exact_label_authority_preflight_2026-04-17/materialized_exact_label_rows.ndjson`

Verdict:

- **reject**

Why:

This file is not an independent new evidence surface.
It is the fail-closed output of the same authority test on the same exhausted question.
Its own content demonstrates that authority is too sparse on the capture-v2 mapping surface:

- only `3` rows became exact authoritative outcome rows
- `143` rows remained `non_evaluable_context`

That means it proves the failure cleanly.
It does not supply a materially different co-resident RI observability-and-authority surface.

### 3. Locked baseline-vs-candidate comparison chain

Candidate surface family:

- `tmp/current_atr_900_env_profile_20260416.py`
- baseline/candidate configs under `results/research/fa_v2_adaptation_off/...`

Verdict:

- **reject**

Why:

This chain can replay exact authority locally.
That part is real.
But it still fails the continuation test for this RI lane because it is not a co-resident RI-native surface.
Instead, it remains:

- a locked authority chain from the current-ATR comparison lane
- dependent on join-back into the RI capture-v2 rows
- already proven incomplete for the current RI authority question through the `7 / 90` overlap failure

So it does not solve the core problem.
It externalizes authority into another chain and then falls back to sparse re-materialization on the RI surface.
That is exactly what the materially-different-surface test was meant to rule out.

It also comes too close to cross-family or cross-lane leakage to be reframed as RI-native authority without a separate explicit governance exception.

### 4. Research-ledger record plus frozen bundle identity

Candidate surface family:

- `artifacts/research_ledger/artifacts/ART-2026-0001.json`
- the referenced frozen bundle path

Verdict:

- **reject as candidate surface**

Why:

The ledger and bundle namespace were useful because they created a non-runtime evidence object and enabled the already executed capture-v2 work.
But they do not themselves create a new authority-bearing evaluation surface.

The ledger record is explicit that it is:

- descriptive classification only
- runtime authority `none`
- a reference to a bundle payload rather than a row-level authority table

That makes it valid provenance and packaging.
It does **not** by itself create co-resident RI observability plus exact authority.

### 5. Earlier fixed-carrier RI capture surface

Candidate surface:

- `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/`

Verdict:

- **reject**

Why:

This older surface was already superseded because it was too thin on the RI observability dimensions that mattered.
It was the lane’s earlier blocker, not a later rescue path.
It therefore fails both directions:

- not enough authority-bearing completeness for the current question
- not enough RI selector richness to justify reopening the deterministic baseline discussion instead

So it is weaker than the current bundle-driven surface, not more materially useful.

## What survives the inventory

No currently materialized repository surface survives all four criteria.

More specifically, the repository does **not** currently contain a surface that is simultaneously:

- already materialized
- materially different from the exhausted capture-v2 authority question
- RI-native enough to preserve family boundaries
- complete enough in authority-bearing outcomes to avoid the same sparse join-back failure

## Consequence under the current repository state

Under the current repository state, the honest fallback is now:

- **lane-close is required**

This does **not** mean the RI advisory lane is impossible forever.
It means something narrower and governance-cleaner:

- no currently materialized repository surface satisfies the materially-different continuation criteria
- so under the current repository state and current constraints, the lane should stop rather than continue surface hunting by rhetoric

That is the fail-closed answer the current evidence supports.

## What this does not authorize

This memo does **not** authorize:

- inventing a hypothetical future surface and treating it as already admissible
- reopening the exhausted capture-v2 surface under new wording
- treating provenance containers as authority-bearing surfaces
- cross-family promotion of the current-ATR authority chain into RI-native evaluation authority
- Phase 4
- runtime readiness
- score implementation

## Bottom line

The repository has already yielded the strongest currently materialized surfaces it can offer for this question.
None of them are good enough to count as a materially different continuation surface after the current capture-v2 authority failure.

So the honest state is now:

- **same-surface continuation remains closed**
- **no already materialized materially different continuation surface is available**
- **under the current repository state, lane-close is the required fallback**

If the advisory program ever continues later, it will need a separately governed, genuinely different evidence surface to be materialized first.
That is a future possibility, not something this inventory treats as already present.
