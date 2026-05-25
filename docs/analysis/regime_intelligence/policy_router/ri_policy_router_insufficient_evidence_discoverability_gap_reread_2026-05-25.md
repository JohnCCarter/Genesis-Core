# RI policy router insufficient-evidence discoverability-gap reread

Date: 2026-05-25
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Authority: `NON_AUTHORIZING`
Promotion intent: `NONE`
Status: `completed / docs-only read-only discoverability reread / observational only`

This slice is a bounded follow-up to the earlier research-lane smoke test.
It asks one narrower question only:

> when the read-only findings/preflight lookup returns `0` matches for `insufficient_evidence`, does that mean the repo lacks committed evidence for this line, or only that current discoverability is weak on the findings side?

This slice does **not** rerun helpers, create new evaluation artifacts, seed the findings bank, change schemas, change runtime/config/tests, reopen the parked `insufficient_evidence` chain, or authorize promotion/runtime work.

## Scope boundary

### Scope IN

- reread the current findings/preflight result for `domain = ri_policy_router`, `text_contains = insufficient_evidence`
- reread the current findings index structure
- reread the committed `insufficient_evidence` analysis/synthesis chain needed to classify the gap honestly
- emit one observational note about whether the current miss is an evidence gap or a discoverability gap

### Scope OUT

- findings-bank writes
- index/schema changes
- new helpers or scripts
- fresh evaluation artifacts
- runtime/default/config/test changes
- promotion/readiness/runtime authority claims
- reopening historical chain conclusions

## Evidence inputs used in this reread

### Current discoverability surfaces

- `scripts/preflight/findings_preflight_lookup.py`
- live lookup run: `.venv/Scripts/python.exe scripts/preflight/findings_preflight_lookup.py --domain ri_policy_router --text-contains insufficient_evidence --json`
- `artifacts/research_ledger/indexes/findings_index.json`

### Committed subject chain surfaces

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.md`
- `results/evaluation/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.md`
- `results/evaluation/ri_policy_router_insufficient_evidence_truth_surface_correction_2026-04-30.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_translation_parking_synthesis_2026-05-04.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_four_surface_synthesis_2026-05-05.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_research_lane_smoke_test_counterfactual_reread_2026-05-25.md`

## Observed

### 1. The live findings/preflight lookup still returns zero direct matches

Observed from the current branch command run:

- `domain = ri_policy_router`
- `text_contains = insufficient_evidence`
- `count = 0`
- `blocking_count = 0`
- `items = []`

So the current discoverability miss recorded in the earlier smoke test still reproduces on the live branch.

### 2. The findings index currently carries RI findings, but not for this exact `insufficient_evidence` chain

Observed from `artifacts/research_ledger/indexes/findings_index.json`:

- the findings index is explicitly a derived, rebuildable projection
- it is explicitly non-authoritative for runtime/promotion/governance
- the current `ri_policy_router` entries are present
- but the visible seam classes in the current index are things like:
  - `aged_weak_continuation_guard`
  - `continuation_split_direction_lock`
  - `weak_pre_aged_release_target_reachability`
  - `weak_pre_aged_release_failset_outcome`
  - `cooldown_displacement_loop`
  - continuation/substituted mixed-window findings

No visible indexed finding in the reread set names the current `insufficient_evidence` chain directly.

### 3. The repo does already contain a committed `insufficient_evidence` evidence chain

Observed from the committed notes and artifacts reread here:

- the exact `2024` vs `2020` counterfactual screen exists and is committed
- the later truth-surface correction exists and is committed
- the translation chain was later synthesized and parked in committed docs
- the D1 four-surface chain was later synthesized and re-anchored in committed docs

So the current repo truth is **not** “no evidence exists.”
The current repo truth is “the evidence exists primarily in committed analysis/evaluation surfaces rather than in the current findings lookup path.”

### 4. The miss is narrower than the earlier smoke test alone suggested

The earlier smoke test was already correct that the exact query had poor findings-side discoverability.
This reread adds one important narrowing:

- the miss is **not** just about the exact `2024` vs `2020` screen note
- the committed `insufficient_evidence` chain is broader than that one note and continues through later April/May synthesis surfaces
- yet the current findings lookup still returns `0`

So the discoverability gap sits specifically on the current findings/indexed-reuse side, not on the existence of a later committed chain.

## Inferred

### 1. This is a discoverability / packaging gap, not an evidence-existence gap

The cheapest honest read is now:

> the current findings/preflight miss does **not** mean the repo lacks committed `insufficient_evidence` evidence; it means the current indexed findings layer is not the primary reusable entry point for this chain.

That is narrower and more useful than saying only that the findings lookup missed “this exact subcase.”

### 2. The current primary reuse path for this chain remains `docs/analysis/**` plus `results/evaluation/**`

Because the later chain is committed and readable there, the practical current reuse path is still:

- analysis notes
- evaluation artifacts
- later synthesis notes

not:

- direct findings-bank lookup

### 3. The findings layer is presently shaped more around other RI seam classes than around this parked insufficient-evidence line

Given the current index contents, the most likely reason the lookup misses this query is structural packaging, not query malfunction.
The findings surface appears to be carrying other RI seam-class outcomes while this parked `insufficient_evidence` chain remains primarily represented through analysis/evaluation/synthesis docs.

## Unverified

- This slice did **not** determine whether the absence of indexed `insufficient_evidence` findings was intentional or accidental.
- This slice did **not** audit every findings bundle under `artifacts/bundles/findings/ri_policy_router/` individually.
- This slice did **not** decide whether the right future fix is seeding findings bundles, improving lookup ergonomics, or leaving the current split as-is.
- This slice did **not** claim that the findings bank ought to cover every parked research chain.
- This slice did **not** reopen the parked `insufficient_evidence` research question itself.

## What changed and what did not change

### What changed

- the current repo-visible reading of the smoke-test gap is now sharper
- the miss is classified as a discoverability / packaging gap on the findings side
- the note explicitly records that the committed `insufficient_evidence` chain extends beyond the earlier exact `2024` vs `2020` reread note

### What did not change

- no runtime/config/default/test behavior changed
- no findings bundle or index entry was added
- no helper or evaluation artifact was created
- no parked `insufficient_evidence` conclusion was reopened
- no promotion/readiness/runtime authority claim was made

## Bottom line

- **Observed:** the live findings/preflight lookup for `insufficient_evidence` still returns `0` direct matches; the current findings index contains RI findings but not a directly indexed `insufficient_evidence` chain; meanwhile the committed `insufficient_evidence` analysis/evaluation/synthesis chain does exist across later April/May notes.
- **Inferred:** the current gap is best classified as discoverability/packaging on the findings side, not as absence of committed evidence.
- **Unverified:** whether that gap should ever be fixed via findings seeding, lookup changes, or left alone remains outside this slice.
