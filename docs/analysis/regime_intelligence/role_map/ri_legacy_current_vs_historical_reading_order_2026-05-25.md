# RI vs Legacy current-vs-historical reading order

Date: 2026-05-25
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Authority: `NON_AUTHORIZING`
Promotion intent: `NONE`
Status: `completed / docs-only read-only reading-order note / observational only`

This slice is a bounded clarification follow-up to the RI-vs-Legacy friction notes.
Its question is narrow:
when a reader wants to understand the present RI-vs-Legacy situation, what should be read first as current branch framing, and what should be read later as historical/provenance context only?

This slice reads current code and committed docs only.
It does **not** change runtime/config/tests/family rules, does **not** rewrite historical files, and does **not** create promotion/readiness authority.

## Scope boundary

### Scope IN

- map the current branch-safe reading order for RI-vs-Legacy materials
- distinguish current branch framing from historical/provenance material
- use existing authority/provenance guidance rather than inventing a new authority layer
- emit one bounded non-authorizing reading-order note

### Scope OUT

- runtime/config/schema/test changes
- rewriting historical packets or feature docs
- new index infrastructure
- Canon updates
- promotion packets
- readiness claims
- runtime/default/config authority claims

## Evidence inputs used in this slice

### Current-use / provenance aids

- `docs/CURRENT_AUTHORITY_INDEX.md`
- `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`

### Current branch question-specific notes

- `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_classification_2026-05-25.md`
- `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_all_boxes_followup_2026-05-25.md`
- `docs/analysis/regime_intelligence/role_map/ri_legacy_terminology_map_2026-05-25.md`
- `docs/analysis/regime_intelligence/role_map/ri_legacy_identity_admission_run_intent_map_2026-05-25.md`

### Older still-useful domain surfaces

- `docs/analysis/regime_intelligence/role_map/ri_legacy_role_map_2026-03-20.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `docs/decisions/legacy/policy_router/legacy_policy_router_surface_separation_precode_packet_2026-04-30.md`

### Historical/provenance surfaces

- `docs/features/feature-regime-intelligence-strategy-family-1.md`
- `docs/scpe_ri_v1_architecture.md`
- `plan/ri-family-admission-roadmap-2026-03-24.md`

## Observed

### 1. Current authority/provenance aids already tell the reader not to infer present truth from filename prominence or history alone

Observed from `docs/CURRENT_AUTHORITY_INDEX.md`:

- repository material is non-authoritative by default unless explicitly listed or promoted through a current path
- historical, archive, audit, plan, analysis, research, and output surfaces may provide context without becoming current authority
- `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md` is a derivative navigation aid, not a new authority layer

So the repo already provides a meta-reading rule:
read documents in their cited role, not by recency aura or folder drama.

### 2. Several RI-adjacent documents are explicitly marked as historical on later branches

Observed from `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md` and later-status notes in the cited files:

- `docs/scpe_ri_v1_architecture.md` is recorded as bounded historical architecture context only on later branches
- `plan/ri-family-admission-roadmap-2026-03-24.md` is recorded as archived historical planning context only on later branches
- the strategy-family feature doc is explicitly archived historical design framing

So these files remain useful, but they are not the right first read for a current branch RI-vs-Legacy question.

### 3. The current branch now has question-specific synthesis notes

Observed from the current role-map folder:

- the friction classification note states the four-box model
- the all-box follow-up note walks all four boxes
- the terminology note separates the main overloaded terms
- the identity/admission note separates structural validity, family identity, family admission, and `run_intent`

So for the present branch question, the repo now has fresh branch-local synthesis surfaces that did not previously exist.

### 4. Older domain notes still matter, but they work best as second-pass support

Observed from the role-map note, champion-compatibility finding, and Legacy separation packet:

- the role-map note still provides the clearest compact statement of shared backbone plus separate families
- the champion-compatibility finding still provides the key empirical reason why overlay language hardened into topology language
- the Legacy separation packet still provides the clearest warning against reading RI `absent` as Legacy baseline

These are still important, but they make more sense after the reader has already oriented themselves to the current branch framing.

## Inferred

### 1. The cheapest safe reading order is “current branch synthesis first, historical provenance later”

Because the branch now has dedicated synthesis notes, a cold reader is less likely to get lost if they first read:

- current branch friction notes
- current branch terminology/identity clarifiers
- then older domain evidence and historical packets

That ordering reduces the chance that historical wording drift gets mistaken for current branch indecision.

### 2. Historical docs are most useful after the reader knows what role they are supposed to play

If a reader opens archived design/roadmap files too early, they can over-weight older questions such as overlay framing, future refactor intent, or family-admission redesign plans.
Those are useful provenance, but they are not the cheapest first-pass explanation of the current branch state.

### 3. The current branch notes should be read as synthesis, not as a new authority layer

The new role-map notes help the reader understand the present question.
But they remain non-authorizing research notes.
That means their role is explanatory compression, not a replacement for the active governance stack or current authority routing surfaces.

## Unverified

- This slice did **not** test whether other readers would actually reach fewer wrong conclusions with this proposed order.
- This slice did **not** attempt a repo-wide RI search-order audit.
- This slice did **not** determine whether an eventual README/index pointer would be worth adding; it only maps the current cheap reading order.

## Recommended reading order for this branch question

### Step 1 — current-use boundary and provenance posture

Read first:

1. `docs/CURRENT_AUTHORITY_INDEX.md`
2. `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`

Purpose:

- understand what counts as active authority vs derivative navigation vs historical context
- avoid treating branch-old materials as live instructions by default

### Step 2 — current branch RI-vs-Legacy synthesis

Read next:

1. `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_classification_2026-05-25.md`
2. `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_all_boxes_followup_2026-05-25.md`
3. `docs/analysis/regime_intelligence/role_map/ri_legacy_terminology_map_2026-05-25.md`
4. `docs/analysis/regime_intelligence/role_map/ri_legacy_identity_admission_run_intent_map_2026-05-25.md`

Purpose:

- get the current branch question framing first
- reduce term-level and box-level confusion before reopening older evidence

### Step 3 — older still-useful domain evidence

Read after that:

1. `docs/analysis/regime_intelligence/role_map/ri_legacy_role_map_2026-03-20.md`
2. `docs/analysis/regime_intelligence/core/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
3. `docs/decisions/legacy/policy_router/legacy_policy_router_surface_separation_precode_packet_2026-04-30.md`

Purpose:

- recover the compact two-family/shared-backbone reading
- recover the empirical overlay-failure basis
- recover the RI-absent-vs-Legacy naming guardrail

### Step 4 — historical/provenance material only

Read last, and only in historical/provenance role:

1. `docs/features/feature-regime-intelligence-strategy-family-1.md`
2. `docs/scpe_ri_v1_architecture.md`
3. `plan/ri-family-admission-roadmap-2026-03-24.md`

Purpose:

- understand earlier design framing and archived future-shape thinking
- do **not** treat these as current branch execution guidance or live authority

## Minimal anti-confusion rule

If a document says or is recorded as:

- archived historical
- retained for provenance
- bounded historical architecture context only
- archived historical planning context only

then it should answer:

- “what was previously asked or frozen?”

not automatically:

- “what should I do now on this branch?”

## No Canon / no promotion / no readiness / no runtime authority claim

This slice makes **no** claim of:

- Canon update
- promotion eligibility
- readiness
- runtime/default/config authority
- replacement of the active governance stack
- independent authority for the reading-order note itself

All conclusions in this note remain bounded, observational, and non-authorizing.

## Slice summary

- **Observed:** current authority/provenance aids and later-status notes already distinguish current-use vs historical roles; the branch now also has dedicated RI-vs-Legacy synthesis notes.
- **Inferred:** the cheapest safe order is current-use boundary first, then current branch synthesis, then older domain evidence, and only then historical/provenance material.
- **Unverified:** whether this order materially reduces cold-reader confusion remains open.
- **Working answer:** for the present branch question, the main win is not to suppress historical docs, but to stop reading them before the current branch framing has been established.
