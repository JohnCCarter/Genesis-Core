# RI vs Legacy split friction — all-box follow-up

Date: 2026-05-25
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Authority: `NON_AUTHORIZING`
Promotion intent: `NONE`
Status: `completed / docs-only read-only all-box follow-up / observational only`

This slice is a bounded follow-up to:

- `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_classification_2026-05-25.md`

The earlier note classified the present RI-vs-Legacy friction into four boxes.
This follow-up runs **all four boxes** one by one and asks a narrower question inside each box:
what is actually real here, what kind of confusion does it create, and what is the cheapest admissible next research step if the box is reopened later?

This slice reads current code plus committed historical/current docs only.
It does **not** change runtime/config/tests/family rules, does **not** propose family merge, does **not** open cross-family routing, and does **not** create promotion/readiness authority.

## Scope boundary

### Scope IN

- reread the current four-box friction classification
- reread current family identity/admission surfaces
- reread validator-facing family/admission outputs
- reread RI-family-local router placement and contract boundaries
- reread historical surfaces that preserve overlay wording, invalid-hybrid wording, and Legacy-vs-RI naming separation
- emit one bounded non-authorizing all-box follow-up note

### Scope OUT

- runtime/config/schema/test changes
- family-registry or family-admission edits
- naming cleanup implementation
- glossary/index implementation
- family merging
- cross-family router design
- new backtests or new result artifacts
- Canon updates
- promotion packets
- readiness claims
- runtime/default/config authority claims

## Evidence inputs used in this slice

### Current classification anchor

- `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_classification_2026-05-25.md`

### Code surfaces

- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/ri_policy_router.py`
- `scripts/validate/validate_optimizer_config.py`

### Historical/current docs surfaces

- `docs/analysis/regime_intelligence/role_map/ri_legacy_role_map_2026-03-20.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_strategy_family_integration_stub_2026-03-18.md`
- `docs/features/feature-regime-intelligence-strategy-family-1.md`
- `docs/scpe_ri_v1_architecture.md`
- `docs/decisions/legacy/policy_router/legacy_policy_router_surface_separation_precode_packet_2026-04-30.md`
- `plan/ri-family-admission-roadmap-2026-03-24.md`

## Observed

### Box 1 — Runtime-required separation

Observed from the champion-compatibility finding, current role-map, current `decision.py`, and `ri_policy_router.py`:

- the historical authority-only overlay on the active champion collapsed to zero trades
- the committed reading of that result was topology break, not small additive patch
- the shared runtime backbone remains real, but the RI router semantics are RI-family-local rather than cross-family
- the current router does not expose any family-selection concept; it selects only among RI-local policy states

So this box contains a **real runtime/topology seam**.
The confusion here comes from the fact that shared orchestration is visually stronger than the downstream family-local semantics when reading code quickly.

### Box 2 — Contract / policy-imposed separation

Observed from `family_registry.py`, `family_admission.py`, `validate_optimizer_config.py`, and the Legacy surface-separation packet:

- current family identity is fail-closed and two-valued: `legacy` or `ri`
- hybrid or authority-mismatched surfaces are rejected rather than stored as a third accepted family label
- RI research slices are allowed through admission as `research_slice`, but stricter run intents require canonical RI cluster compatibility
- optimizer validation surfaces these distinctions back to the user as separate `family_identity` vs `family_admission` failures
- the Legacy packet adds explicit naming/namespace guardrails so RI-family `absent` results are not silently relabeled as Legacy results

So this box contains a **real contract-enforced separation layer**.
The confusion here comes from the fact that contract/validator boundaries can be read as if they are pure ontology proof, when part of their job is also traceability and fail-closed governance.

### Box 3 — Historical wording drift

Observed from the archived strategy-family feature doc, the historical integration stub, the champion-compatibility finding, and the archived family-admission roadmap:

- older docs preserve overlay/migration wording because that was the historical question under test
- the historical integration stub still refers to older **föreslagen** labels like `invalid_hybrid_overlay`, while current code now fails closed instead of accepting a third family label
- later/current docs formalize RI as a separate family and explicitly reject overlay as the live reading
- archived notes often include later-status warnings, but the historical wording still sits close to current terminology in search results and rereads

So this box contains a **real chronology / document-layer seam**.
The confusion here comes from nearby documents recording different stages of model stabilization rather than making the exact same kind of statement.

### Box 4 — Naming / reading ambiguity

Observed from code and docs terminology:

- `authority_mode`, `strategy_family`, `run_intent`, `research_policy_router`, and `enabled`/`absent` all live close to one another conceptually
- `decision.py` is shared, which visually suggests generic routing even when the router contract is RI-family-local only
- the repo distinguishes identity from admission, but the terms are easy to blur during fast reading
- the Legacy separation packet exists largely to prevent naming/label drift from turning into false cross-family equivalence

So this box contains a **real reading/ergonomics problem**.
The confusion here is not that the repo lacks terms; it is that several nearby terms are easy to collapse into each other.

## Inferred

### Box 1 — Runtime-required separation

The runtime box looks like the most genuinely non-negotiable one.
The strongest evidence so far still says:

- RI did not survive as a thin overlay on the incumbent champion surface
- RI behavior required a broader compatibility cluster
- RI policy-router work was intentionally kept family-local rather than generalized into a family selector

So if this box is reopened later, the right question is probably not “can we abolish the split with cleaner words?”
It is more likely “which exact parts of the split are truly topology-required, and which parts were bundled together for safety?”

### Box 2 — Contract / policy-imposed separation

This box looks partly protective and partly stiffening.
The contract surfaces are doing useful work:

- preserving traceability
- preventing hybrid ambiguity
- preventing cross-family artifact relabeling
- distinguishing research-admissible RI from stricter comparison/freeze surfaces

But because these protections are strong and visible, they can make the current family split look more absolute than the underlying runtime evidence alone necessarily proves.
So this box likely contributes materially to the feeling of “hard split,” even when the original driver was empirical.

### Box 3 — Historical wording drift

This box appears to amplify the first two boxes more than it creates a new conflict by itself.
Historical notes preserve the rejected questions honestly, which is good provenance.
But once those notes live alongside later stabilized family language, a reader can easily misread “historical question preserved” as “current branch ambiguity unresolved.”

So this box is probably a **friction multiplier** rather than the root cause.

### Box 4 — Naming / reading ambiguity

This box appears to be the cheapest confusion source to reduce later, because it does not require re-proving topology or rewriting family rules.
The repo already has most of the right distinctions; the pain comes from how easily the reader can conflate them:

- authority vs family
- family identity vs family admission
- shared decision backbone vs family-local router
- RI absent vs Legacy baseline

That suggests this box may be the cheapest future clarification target, even if it is not the deepest root cause.

## Unverified

### Box 1 — Runtime-required separation

- This slice did **not** determine which current RI-defining markers are indispensable topology requirements and which are comparison-safety bundling.
- This slice did **not** reopen any counterfactual where RI is conceptualized as a higher-level layer over Legacy while leaving runtime family rules unchanged.

### Box 2 — Contract / policy-imposed separation

- This slice did **not** determine how much the present pain would shrink if the repo exposed identity/admission distinctions more explicitly in docs/readme/index surfaces.
- This slice did **not** test whether current validator messages are already sufficient for a cold reader.

### Box 3 — Historical wording drift

- This slice did **not** audit the full search-result surface for how often old overlay vocabulary appears before newer family-contract vocabulary.
- This slice did **not** test whether a small current-use index would neutralize most of the drift effect.

### Box 4 — Naming / reading ambiguity

- This slice did **not** test a concrete glossary, reading-order note, or one-page terminology map.
- This slice did **not** measure whether another reader would still confuse RI absent with Legacy baseline after seeing a minimal naming guide.

## Cheapest admissible next step per box

| Box                                  | Cheapest later step                                                                                      | Why that step is the smallest honest one                                                  |
| ------------------------------------ | -------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| Runtime-required separation          | bounded reread of which RI markers are topology-required vs comparison-safe bundling                     | this tests the deepest seam without proposing merge or runtime redesign                   |
| Contract / policy-imposed separation | bounded doc note mapping `family identity` vs `family admission` vs `run_intent` using current code only | this clarifies the contract layer without changing validators or policy                   |
| Historical wording drift             | bounded search/index note listing historical-vs-current anchor docs in recommended reading order         | this reduces chronology confusion without rewriting historical files                      |
| Naming / reading ambiguity           | bounded glossary / terminology map for authority, family, admission, router, enabled/absent              | this is the cheapest clarification move because it does not touch runtime or policy logic |

## Working read after running all four boxes

After walking all four boxes, the present RI-vs-Legacy friction looks like this:

1. there **is** a real runtime/topology seam
2. that seam is then reinforced by contract and traceability rules
3. historical document layers preserve older question framing near newer stabilized framing
4. naming and reading ergonomics make the whole stack feel more contradictory than it is

So the current situation is neither:

- “only docs debt”, nor
- “pure runtime contradiction”

It is a stacked friction model where a real empirical split is made harder to reason about by later contract hardening, preserved historical wording, and term-level ambiguity.

## No Canon / no promotion / no readiness / no runtime authority claim

This slice makes **no** claim of:

- Canon update
- promotion eligibility
- readiness
- runtime/default/config authority
- family merge approval
- cross-family router approval
- implementation readiness for architectural change

All conclusions in this note remain bounded, observational, and non-authorizing.

## Slice summary

- **Observed:** all four friction boxes are repo-backed: runtime separation, contract reinforcement, historical wording drift, and naming ambiguity each contribute something real.
- **Inferred:** the deepest seam still appears runtime/topology-related, but the cheapest later clarification target is naming/reading ambiguity, with identity/admission mapping close behind.
- **Unverified:** how much of the current split is permanently topology-required versus historically bundled and governance-stabilized remains open.
- **Working answer after running all boxes:** the RI-vs-Legacy problem is best read as a stacked friction model, not as a single bug, single contradiction, or single docs issue.
