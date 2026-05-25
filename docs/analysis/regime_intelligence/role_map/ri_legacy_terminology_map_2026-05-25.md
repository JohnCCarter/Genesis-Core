# RI vs Legacy terminology map

Date: 2026-05-25
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Authority: `NON_AUTHORIZING`
Promotion intent: `NONE`
Status: `completed / docs-only read-only terminology map / observational only`

This slice is a bounded terminology follow-up to:

- `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_classification_2026-05-25.md`
- `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_all_boxes_followup_2026-05-25.md`

The goal is narrow:
make the current repo reading cheaper by mapping a small set of nearby terms that are easy to conflate when reading RI-vs-Legacy material quickly.

This slice reads current code and committed docs only.
It does **not** change runtime/config/tests/family rules, does **not** propose family merge, does **not** open cross-family routing, and does **not** create promotion/readiness authority.

## Scope boundary

### Scope IN

- map the current repo meaning of `strategy_family`
- map the current repo meaning of `authority_mode`
- map the current repo meaning of `run_intent`
- map the current repo meaning of family identity vs family admission
- map the current repo meaning of `research_policy_router`
- map the current repo meaning of RI `enabled` / `absent` wording in policy-router material
- emit one bounded non-authorizing terminology note

### Scope OUT

- runtime/config/schema/test changes
- family-registry or family-admission edits
- validator message edits
- new glossary/index infrastructure
- family merging
- cross-family router design
- new backtests or new result artifacts
- Canon updates
- promotion packets
- readiness claims
- runtime/default/config authority claims

## Evidence inputs used in this slice

### Current analysis anchors

- `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_classification_2026-05-25.md`
- `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_all_boxes_followup_2026-05-25.md`

### Code and validator surfaces

- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/ri_policy_router.py`
- `scripts/validate/validate_optimizer_config.py`

### Supporting docs surfaces

- `docs/analysis/regime_intelligence/role_map/ri_legacy_role_map_2026-03-20.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_strategy_family_bridge_admissibility_2026-04-17.md`
- `docs/decisions/legacy/policy_router/legacy_policy_router_surface_separation_precode_packet_2026-04-30.md`
- `docs/features/feature-regime-intelligence-strategy-family-1.md`
- `plan/ri-family-admission-roadmap-2026-03-24.md`

## Observed

### 1. `strategy_family`

Current repo reading:

- `strategy_family` is executable family identity, not decorative provenance
- supported values are `legacy` and `ri`
- current docs and code treat it as part of the effective config contract
- the repository exposes explicit family validation/classification behavior around it

Observed support:

- `family_registry.py` validates `strategy_family` as mandatory family identity
- the advisory environment-fit memo says `strategy_family` is runtime identity, not decorative metadata
- the role-map note uses `strategy_family ∈ {"legacy", "ri"}` as the current top-level family reading

What this term is **not** in the current repo reading:

- not a harmless label that can be added without semantic effect
- not a synonym for “this config feels RI-like”
- not a generic provenance tag detached from validation semantics

### 2. `authority_mode`

Current repo reading:

- `authority_mode` is an important authority/calibration-path marker
- `authority_mode = regime_module` is required for RI-shaped surfaces
- but `authority_mode = regime_module` alone is **not** sufficient to establish a valid RI family surface

Observed support:

- `family_registry.py` requires `authority_mode = regime_module` for RI
- `feature-regime-intelligence-strategy-family-1.md` explicitly says the doc must not imply that `authority_mode = regime_module` alone is enough to classify a valid RI candidate
- the role-map note says authority is one divergence layer among several, not the whole family definition

What this term is **not** in the current repo reading:

- not equivalent to `strategy_family`
- not a complete family classifier by itself
- not shorthand for “RI overlay succeeded”

### 3. `run_intent`

Current repo reading:

- `run_intent` is a policy/admission concept for the purpose of a run
- current values in the family-admission roadmap and validator surfaces include `research_slice`, `candidate`, `promotion_compare`, and `champion_freeze`
- `run_intent` sits above family identity rather than replacing it

Observed support:

- the family-admission roadmap defines `run_intent` as the typed concept for what a given RI/Legacy surface is allowed to do
- `family_admission.py` checks family admission against `run_intent`
- `validate_optimizer_config.py` surfaces separate run-intent / family-admission failures rather than folding them into generic family identity failures

What this term is **not** in the current repo reading:

- not the same thing as `strategy_family`
- not a synonym for architecture or topology
- not proof that a surface is runtime-ready or promotable

### 4. `family identity`

Current repo reading:

- family identity answers a narrower question: what family is this surface, if any?
- identity must distinguish `legacy`, `ri`, and invalid hybrid/mismatch situations
- identity is intended to remain narrower than run-purpose policy

Observed support:

- the family-admission roadmap explicitly separates family identity from family admission policy
- `family_registry.py` currently carries fail-fast identity logic for legacy/RI/hybrid mismatch handling
- the all-box follow-up note observed that the repo already encodes identity-vs-admission as a real seam

What this term is **not** in the current repo reading:

- not the whole policy stack
- not equivalent to promotion admissibility
- not equivalent to research permissibility

### 5. `family admission`

Current repo reading:

- family admission answers a different question: given a family identity, is this surface admissible for a specific `run_intent`?
- admission can be looser for `research_slice` than for stricter RI intents
- admission is where purpose-specific policy starts to matter explicitly

Observed support:

- `family_admission.py` allows RI `research_slice` without always requiring the full canonical RI cluster
- stricter RI run intents fail if the canonical RI cluster requirement is not met
- validator output already distinguishes family-admission failures from family-identity failures

What this term is **not** in the current repo reading:

- not a replacement for identity
- not generic runtime validation as a whole
- not proof that the family split itself is ontologically final

### 6. `research_policy_router`

Current repo reading:

- `research_policy_router` is an RI-family-local routing surface
- it chooses among RI-local policy states such as continuation, defensive transition, and no-trade
- it is called inside shared `decision.py`, but it is not a cross-family selector

Observed support:

- `decision.py` calls `resolve_research_policy_router(...)` within the shared decision flow
- `ri_policy_router.py` defines only RI-local policies and RI-local state/debug keys
- the SCPE RI V1 architecture packet says RI router work must remain RI-family-local and must not introduce a family router

What this term is **not** in the current repo reading:

- not a general `RI vs Legacy` router
- not a family selector
- not evidence that shared `decision.py` implies shared family semantics

### 7. RI `enabled` / `absent`

Current repo reading in the policy-router line:

- RI `enabled` / `absent` refers to a comparison inside an RI-family carrier
- `absent` means the RI-family surface without the router leaf, not a true Legacy baseline
- this wording is intentionally guarded because it is easy to misread as a cross-family comparison

Observed support:

- the Legacy policy-router separation packet says the existing annual `enabled` vs `absent` results belong to the RI-family line
- the same packet explicitly says those results must not be relabeled as `Legacy absent` or `Legacy baseline`

What this term is **not** in the current repo reading:

- not a synonym for Legacy control
- not a cross-family baseline by default
- not proof that RI and Legacy were directly compared in that exact probe

## Inferred

### 1. The most error-prone term pair is `strategy_family` vs `authority_mode`

These terms sit close together because both are involved in RI reading.
But the repo evidence consistently points to this distinction:

- `authority_mode` is one important marker inside the RI path
- `strategy_family` is the explicit family identity contract

That means readers who collapse the two will tend to over-read authority changes as if they were full family equivalence.

### 2. The second most error-prone pair is `family identity` vs `family admission`

The roadmap and validator surfaces suggest that the repo already knows these are different layers.
But because they are both “family rules,” they are easy to blur.
A cold reader can otherwise miss the distinction between:

- “what family is this?” and
- “what is this family allowed to do for this run purpose?”

### 3. The router confusion is mostly positional, not semantic

The router lives inside shared `decision.py`, which visually invites a generic reading.
But the actual router contract is narrower:

- RI-local inputs
- RI-local policies
- no family selection

So the confusion seems to come more from where the router appears in code than from what the router text actually says.

### 4. `enabled` / `absent` is the easiest place for cross-family misreading to leak in

Because `enabled` and `absent` sound neutral, they can be read too broadly.
The Legacy separation packet exists largely to stop that drift.
That suggests this term pair is especially dangerous in summaries, filenames, and future rereads.

## Unverified

- This slice did **not** test whether a one-page terminology map is already enough to reduce confusion for a cold reader.
- This slice did **not** test whether `family identity` vs `family admission` should be made more explicit in a current-use index or README surface.
- This slice did **not** determine whether validator message wording should ever change; it only maps the current reading.
- This slice did **not** test whether search ordering across historical/current docs still biases readers toward overlay language first.

## Compact reading rule

For the current branch, the cheapest accurate terminology read appears to be:

- `strategy_family` = family identity contract
- `authority_mode` = authority/calibration-path marker, not full family identity by itself
- `run_intent` = purpose/admission context for a run
- `family identity` = what family this surface is
- `family admission` = whether that family-surface is allowed for this run purpose
- `research_policy_router` = RI-family-local policy router, not family selector
- RI `enabled` / `absent` = RI-family internal comparison unless a slice explicitly proves otherwise

## Minimal anti-confusion table

| If you see                                | Read it as                             | Do not automatically read it as                 |
| ----------------------------------------- | -------------------------------------- | ----------------------------------------------- |
| `strategy_family = ri`                    | explicit RI family identity            | harmless provenance tag only                    |
| `authority_mode = regime_module`          | one RI-significant marker              | full valid RI family by itself                  |
| `run_intent = research_slice`             | research-purpose admission context     | proof of promotion readiness                    |
| family-identity failure                   | surface/family mismatch                | generic admission failure                       |
| family-admission failure                  | run-purpose policy failure             | proof that the surface has no RI meaning at all |
| `research_policy_router` in `decision.py` | RI-local router inside shared backbone | cross-family selector                           |
| RI `absent`                               | RI-family carrier without router leaf  | Legacy baseline                                 |

## No Canon / no promotion / no readiness / no runtime authority claim

This slice makes **no** claim of:

- Canon update
- promotion eligibility
- readiness
- runtime/default/config authority
- family merge approval
- cross-family router approval
- implementation readiness for terminology cleanup

All conclusions in this note remain bounded, observational, and non-authorizing.

## Slice summary

- **Observed:** current repo surfaces already distinguish `strategy_family`, `authority_mode`, `run_intent`, family identity, family admission, router scope, and RI `enabled` / `absent`, but the distinctions are spread across code and docs.
- **Inferred:** the cheapest current clarification gain likely comes from keeping these terms explicitly separated, especially `strategy_family` vs `authority_mode` and identity vs admission.
- **Unverified:** whether this note alone materially reduces cold-reader confusion remains open.
- **Working answer:** the terminology seam is real but mostly tractable; the repo already contains the distinctions, and the main task is to keep them from collapsing into each other during rereads.
