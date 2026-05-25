# RI vs Legacy identity-admission-run-intent map

Date: 2026-05-25
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Authority: `NON_AUTHORIZING`
Promotion intent: `NONE`
Status: `completed / docs-only read-only identity-admission map / observational only`

This slice is a bounded clarification follow-up to:

- `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_classification_2026-05-25.md`
- `docs/analysis/regime_intelligence/role_map/ri_legacy_split_friction_all_boxes_followup_2026-05-25.md`
- `docs/analysis/regime_intelligence/role_map/ri_legacy_terminology_map_2026-05-25.md`

The goal is narrow:
make the current repo reading cheaper by separating three nearby questions that are easy to collapse into one:

1. is the surface structurally valid?
2. what family is the surface?
3. is that family-surface admissible for this `run_intent`?

This slice reads current code and committed docs only.
It does **not** change runtime/config/tests/family rules, does **not** propose family merge, and does **not** create promotion/readiness authority.

## Scope boundary

### Scope IN

- map structural validation vs family identity vs family admission
- map where `run_intent` enters the current repo reading
- map how validator-facing failures reflect those layers
- emit one bounded non-authorizing clarification note

### Scope OUT

- runtime/config/schema/test changes
- family-registry or family-admission edits
- validator message edits
- new runtime or optimizer behavior
- family merging
- Canon updates
- promotion packets
- readiness claims
- runtime/default/config authority claims

## Evidence inputs used in this slice

### Code and validator surfaces

- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`
- `scripts/validate/validate_optimizer_config.py`

### Supporting docs surfaces

- `plan/ri-family-admission-roadmap-2026-03-24.md`
- `docs/analysis/regime_intelligence/role_map/ri_legacy_terminology_map_2026-05-25.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_strategy_family_bridge_admissibility_2026-04-17.md`

## Observed

### 1. The repo already models three distinct layers

Observed from `plan/ri-family-admission-roadmap-2026-03-24.md`:

- structural validity is a separate concern
- family identity is a separate concern
- family admission for a specific `run_intent` is a separate concern

The roadmap explicitly frames the target architecture as three layers rather than one combined family rule bucket.

### 2. `strategy_family` sits in the identity layer, not in the run-purpose layer

Observed from `family_registry.py` and the advisory environment-fit memo:

- `strategy_family` is mandatory family identity
- the supported runtime family values are `legacy` and `ri`
- the advisory note explicitly says `strategy_family` is executable identity, not decorative metadata

So the current repo reading treats `strategy_family` as part of the answer to:

> what family is this surface?

not as part of the answer to:

> what is this run allowed to do?

### 3. `authority_mode` participates in identity checks, but does not replace identity

Observed from `family_registry.py` and the historical strategy-family feature doc:

- `authority_mode = regime_module` is required for RI
- but authority-mode alone is not sufficient to classify a valid RI candidate
- hybrid and mismatch cases fail closed rather than being accepted as a valid intermediate family state

So the current repo reading does not allow authority-mode to swallow family identity.

### 4. `family_admission.py` applies run-purpose rules above identity

Observed from `family_admission.py`:

- the function first resolves family identity
- then it resolves `run_intent`
- RI `research_slice` may be admitted without always requiring the full canonical RI cluster
- stricter RI run intents fail if the canonical RI cluster requirement is not met

So `family_admission.py` is answering a different question than `family_registry.py`.
It is not primarily asking “what family is this?”
It is asking “given this family, is this surface admissible for this run purpose?”

### 5. The optimizer validator already exposes identity vs admission as different failure classes

Observed from `scripts/validate/validate_optimizer_config.py`:

- identity problems are surfaced under family-identity style errors such as invalid `strategy_family`, legacy/RI mismatch, or RI requiring fixed `authority_mode`
- admission problems are surfaced separately as `family_admission` failures tied to the chosen `run_intent`
- missing or invalid `run_intent` is also surfaced distinctly for RI optimizer configs

So the validator-facing repo reading already tries to keep these layers from collapsing completely.

## Inferred

### 1. The central anti-confusion rule is question ordering

The current repo seems to want readers to ask these questions in order:

1. is the surface structurally valid?
2. what family is it?
3. for this family, is it admissible for this `run_intent`?

When those questions are asked out of order, identity, admission, and promotion semantics start to bleed into each other.

### 2. A family-admission failure does not automatically erase family meaning

If a surface is RI-shaped enough to have meaningful family identity, it can still fail a stricter `run_intent` admission check.
That means:

- “not admissible for this purpose” is not the same as
- “not RI in any meaningful sense at all”

The roadmap and current admission layer both point toward that distinction.

### 3. A family-identity failure should not be read as a generic governance veto

Identity failures answer a narrower fail-fast question about family mismatch or hybrid invalidity.
They do not by themselves explain every later policy or comparison boundary.
So if a reader sees identity logic and then jumps directly to promotion semantics, they are skipping a layer.

### 4. `run_intent` is a purpose selector, not a topology selector

The current repo reading makes `run_intent` important, but it does not use `run_intent` to redefine what `legacy` and `ri` mean.
Instead, `run_intent` decides what a given family-surface may be used for.
That makes it a policy layer, not a family-ontology layer.

## Unverified

- This slice did **not** determine whether the present identity/admission split is already expressed clearly enough for a cold reader.
- This slice did **not** test whether current validator wording is the best possible wording; it only maps the current layering.
- This slice did **not** determine which RI markers should remain identity-level forever versus later move fully into admission policy.
- This slice did **not** reopen any implementation refactor; it only maps the current repo reading.

## Compact reading rule

For the current branch, the cheapest accurate read appears to be:

- structural validation = “is this config surface well-formed and generically admissible as a config?”
- family identity = “what family is this surface, if any?”
- family admission = “for this family, is the surface allowed for this `run_intent`?”
- `run_intent` = “what kind of run-purpose is being requested?”

## Minimal anti-confusion table

| If you see                        | Read it as                                          | Do not automatically read it as                         |
| --------------------------------- | --------------------------------------------------- | ------------------------------------------------------- |
| missing/invalid `strategy_family` | family identity problem                             | generic run-purpose failure                             |
| `authority_mode = regime_module`  | one RI-significant identity marker                  | complete family proof by itself                         |
| `run_intent = research_slice`     | research-purpose admission context                  | family identity label                                   |
| family-identity failure           | family mismatch / hybrid invalidity                 | total explanation of all later policy boundaries        |
| family-admission failure          | run-purpose inadmissibility for that family surface | proof that the surface has no RI meaning at all         |
| stricter RI run-intent rejection  | comparison/freeze-style policy boundary             | proof that `research_slice` RI has no place in the repo |

## No Canon / no promotion / no readiness / no runtime authority claim

This slice makes **no** claim of:

- Canon update
- promotion eligibility
- readiness
- runtime/default/config authority
- family merge approval
- implementation readiness for validator or admission refactor

All conclusions in this note remain bounded, observational, and non-authorizing.

## Slice summary

- **Observed:** current repo surfaces already separate structural validity, family identity, and family admission for a specific `run_intent`, and the optimizer validator partially exposes that split outward.
- **Inferred:** the cheapest way to avoid confusion is to preserve the question order “structure -> identity -> admission” instead of collapsing those layers into a single family verdict.
- **Unverified:** whether current docs and validator messaging already make this split sufficiently obvious to a cold reader remains open.
- **Working answer:** the identity/admission seam is real, intentional, and narrower than a full architecture debate; most confusion comes from skipping the layer boundaries rather than from their absence.
