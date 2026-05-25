# RI policy router research-lane smoke test counterfactual reread

Date: 2026-05-25
Branch: `feature/research-case-lane-smoke-test`
Mode: `RESEARCH`
Authority: `NON_AUTHORIZING`
Promotion intent: `NONE`
Status: `completed / docs-only read-only lane smoke test / observational only`

This slice is a bounded smoke test of the current research-evidence lane using the already-materialized exact `2024` vs `2020` `insufficient_evidence` counterfactual question.
It reads existing analysis, evaluation, and research-boundary surfaces only, plus one optional read-only findings/preflight lookup.
It does **not** update Canon, create a promotion packet, claim readiness, claim runtime authority, change runtime/config/tests, change schemas, add new helpers, add new research infrastructure, reopen historical cleanup, or expand lineage.

## Scope boundary

### Scope IN

- reread one already-bounded `2024` vs `2020` `insufficient_evidence` counterfactual question
- use existing analysis/evaluation/research-boundary surfaces only
- perform one optional read-only findings/preflight lookup
- emit one observational smoke-test note with an embedded friction/gap summary

### Scope OUT

- Canon updates
- promotion packets
- readiness claims
- runtime/default/config authority claims
- runtime/config/test changes
- schema or artifact changes
- new helpers or new research infrastructure
- historical cleanup
- broad lineage expansion

## Evidence inputs used in this smoke test

### Research-boundary surfaces

- `docs/contracts/research_experiment_infrastructure_inventory_contract.md`
- `docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md`
- `.github/copilot-instructions.md`

### Primary bounded subject surfaces

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.md`
- `results/evaluation/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.json`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md`

### Optional read-only reuse check

- `scripts/preflight/findings_preflight_lookup.py`
- lookup run: `scripts/preflight/findings_preflight_lookup.py --domain ri_policy_router --text-contains insufficient_evidence --json`

## Observed

### 1. The research-lane boundaries were explicit before subject work began

The current boundary surfaces already say, in committed text, that:

- research/evidence work in `RESEARCH` should prefer the smallest admissible evidence step
- research surfaces remain non-authorizing unless explicitly promoted through the current authority path
- findings bundles/indexes and research outputs may support observation and reuse without becoming governance, readiness, promotion, or runtime authority

That meant this smoke test could stay entirely inside read-only evidence work without opening a governance, promotion, or runtime packet.

### 2. The bounded `2024` vs `2020` subject was recoverable from existing committed surfaces

The existing counterfactual-screen note and evaluation artifact already lock the exact bounded subject and its outcome.

Observed from `results/evaluation/ri_policy_router_insufficient_evidence_counterfactual_screen_2026-04-30.json` and its paired note:

- artifact outcome: `no_surviving_screen`
- `best_surviving_candidate = null`
- strongest descriptive separator: `bars_since_regime_change <= 282`
- `2024` target `fwd_16` mean: `-0.855705%`
- `2020` control `fwd_16` mean: `-0.875411%`
- `truth_surface_is_opposed = false`

So the exact bounded question was already answerable from committed material without reopening raw source mining, helper edits, or new artifact creation.

### 3. The 2024 side was already locally framed as weak, but still non-authorizing

Observed from `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2024_regression_pocket_reason_split_2026-04-30.md`:

- the exact `2024` `insufficient_evidence` subset is the weaker local subset in the fixed 2024 pocket
- the exact `2024` `insufficient_evidence` rows had `fwd_16` mean `-0.855705%`
- the same note explicitly says this does **not** justify runtime-authoritative `insufficient_evidence` conclusions by itself

That existing bounded framing fit the smoke test cleanly: it offered a committed local interpretation while already keeping authority claims closed.

### 4. The optional findings/preflight reuse check returned no direct coverage for this exact subcase

Observed from the read-only findings lookup run on this branch:

- filters: `domain = ri_policy_router`, `text_contains = insufficient_evidence`
- matched findings: `0`
- blocking findings: `0`

So the current findings bank did not directly cover this exact `insufficient_evidence` counterfactual branch, even though the broader research/evidence chain exists elsewhere in committed notes and artifacts.

## Inferred

### 1. The research-lane contract reduced authority friction for this slice

Because the boundary documents were explicit up front, there was little ambiguity about:

- which surfaces were safe to read
- which surfaces remained non-authorizing
- when escalation would be required
- why this slice should stop at observation only

So the contract appears to have reduced friction on the authority/governance side of the work.

### 2. The main reusable surface for this subject is currently `docs/analysis/**` plus `results/evaluation/**`, not findings-bank reuse

The zero-match findings lookup suggests that, for this exact bounded subcase, reuse currently lives more in:

- committed analysis notes
- committed evaluation artifacts

than in the findings bank / findings index layer.

That is a workable path for a smoke test, but it also means the easiest reusable entry point for this exact subject was not the preflight findings surface.

### 3. The lane model supported a cheap, honest stop condition

The smoke test did not need to invent a new packet, new helper, or new authority route.
It could simply reread the existing bounded result and stop at:

- `no_surviving_screen`
- descriptive separator only
- no runtime implication

That is exactly the kind of cheap, evidence-only stopping point the lane model is supposed to make easier.

## Unverified

- This slice did **not** rerun the original counterfactual helper or produce a fresh evaluation artifact.
- This slice did **not** test whether a different non-March negative-year pair would create an actually truth-opposed bounded screen.
- This slice did **not** determine whether the findings-bank miss for `insufficient_evidence` is intentional, temporary, or simply not yet seeded.
- This slice did **not** audit broader discoverability across all RI policy-router research notes.
- This slice did **not** validate whether a future agent would independently choose the same subject without prior human guidance.

## No Canon / no promotion / no readiness / no runtime authority claim

This smoke test makes **no** claim of:

- Canon update
- promotion eligibility
- readiness
- runtime/default/config authority
- family admission
- policy admission
- implementation readiness

All conclusions in this note remain bounded, observational, and non-authorizing.

## Friction and workflow-gap summary

### What was easy

- the branch/mode/lane posture was clear
- the research contract clearly separated evidence reuse from authority
- the subject already existed as a bounded committed question
- the exact stop condition (`no_surviving_screen`) was already visible in existing evidence surfaces
- the optional findings lookup was easy to use as a read-only reuse check without treating it as a gate

### What was hard

- the most obvious reusable evidence for this exact subcase was still spread across analysis notes and evaluation artifacts rather than discoverable through the findings surface
- that means cross-surface subject discovery still required some manual repo reading even though authority boundaries were clearer

### Did the research-lane contract reduce friction?

Yes, on the authority/governance side.
It was straightforward to keep this slice inside `RESEARCH`, inside the research-evidence lane, and outside Canon/promotion/runtime authority.
The contract removed uncertainty about what the note was allowed to be.

### Was a workflow gap found?

Yes, a narrow one.
For this exact `insufficient_evidence` counterfactual branch, the findings/preflight layer returned `0` direct matches, so the primary reusable path remained `docs/analysis/**` plus `results/evaluation/**` rather than findings-bank discovery.

That is a discoverability/reuse gap, not an authority gap.
It does **not** justify adding new infrastructure in this slice.

## Smoke-test summary

- **Observed:** the exact `2024` vs `2020` counterfactual question was recoverable from committed analysis/evaluation surfaces; the bounded result remained `no_surviving_screen`; the strongest surviving pattern was descriptive only (`bars_since_regime_change <= 282`); the optional findings lookup returned `0` matches for this exact subcase.
- **Inferred:** the research-lane contract and agent adoption reduced authority friction by making allowed surfaces and stop conditions explicit; for this subject, primary reuse currently lives in analysis/evaluation surfaces rather than findings-bank reuse.
- **Unverified:** whether a different bounded pair would yield a better counterfactual screen, whether findings coverage for this branch should exist, and whether another agent would independently select the same evidence path remain untested.
- **Contract reduced friction:** `yes`, materially on authority-boundary clarity.
- **Workflow gap found:** `yes`, but it is a narrow findings/discoverability gap rather than a governance or authority gap.
