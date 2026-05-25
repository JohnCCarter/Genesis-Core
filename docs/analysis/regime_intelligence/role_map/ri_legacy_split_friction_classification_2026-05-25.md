# RI vs Legacy split friction classification

Date: 2026-05-25
Branch: `feature/research-next-bounded-case-2026-05-25`
Mode: `RESEARCH`
Authority: `NON_AUTHORIZING`
Promotion intent: `NONE`
Status: `completed / docs-only read-only friction classification / observational only`

This slice is a bounded reread of the current `RI` vs `Legacy` split question.
It asks one narrow question only:
where does the present confusion/friction actually sit — runtime topology, family contract, historical wording drift, or naming/reading ergonomics?

It reads existing code and committed analysis/design surfaces only.
It does **not** change runtime/config/tests/family rules, does **not** propose family merge, does **not** open cross-family routing, and does **not** create promotion/readiness authority.

## Scope boundary

### Scope IN

- reread current family identity/admission code
- reread the shared decision-path placement of the RI router
- reread the committed RI-vs-overlay evidence chain
- reread the current role-map and historical family framing
- emit one bounded non-authorizing friction-classification note

### Scope OUT

- runtime/config/schema/test changes
- family-registry or family-admission edits
- family merging
- cross-family router design
- new backtests or new result artifacts
- Canon updates
- promotion packets
- readiness claims
- runtime/default/config authority claims

## Evidence inputs used in this slice

### Code surfaces

- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/ri_policy_router.py`

### Current and historical analysis/design surfaces

- `docs/analysis/regime_intelligence/role_map/ri_legacy_role_map_2026-03-20.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `docs/features/feature-regime-intelligence-strategy-family-1.md`
- `docs/scpe_ri_v1_architecture.md`
- `plan/ri-family-admission-roadmap-2026-03-24.md`

## Observed

### 1. Shared runtime backbone and separate family boundaries coexist deliberately

Observed from `docs/analysis/regime_intelligence/role_map/ri_legacy_role_map_2026-03-20.md`:

- the repo already describes `legacy` and `ri` as two separate strategy families
- the repo also explicitly says both families still pass through the same broad runtime chain `evaluate -> decide`
- the stated divergence points are family signature, authority/calibration, thresholds, cadence, survival, and sizing

So the current reading is not “two engines” and not “one family with small flags.”
It is “one shared backbone with separate family-conditioned surfaces.”

### 2. Current code treats family identity as stricter than a simple authority switch

Observed from `src/core/strategy/family_registry.py`:

- only two accepted families exist: `legacy` and `ri`
- `ri` requires `authority_mode = regime_module`
- `ri` also requires the current RI-defining ATR, gate, and threshold-cluster markers in the strict config validator
- authority-only or partial RI-marker combinations fail closed as hybrid mismatches rather than being accepted as a third state

This means the current code does **not** treat “turn on regime authority” as equivalent to “becoming RI.”

### 3. The repository already distinguishes identity from admission, but the distinction remains family-centered

Observed from `src/core/strategy/family_admission.py` and the archived `plan/ri-family-admission-roadmap-2026-03-24.md`:

- the code separates `family` identity checks from `run_intent` admission checks
- `strategy_family=ri` is admissible for `research_slice` without requiring the full canonical RI cluster at the admission layer
- stricter RI run intents still require the canonical RI cluster
- the archived roadmap exists precisely because the repo had already identified pressure between “what counts as RI” and “what is allowed for a given run purpose”

So the repository has already recognized this seam as real enough to model explicitly.
The seam is not imaginary; it is already encoded as identity-vs-admission layering.

### 4. The RI router is embedded in the shared decision path, but its contract is RI-family-local

Observed from `src/core/strategy/decision.py`, `src/core/strategy/ri_policy_router.py`, and `docs/scpe_ri_v1_architecture.md`:

- the shared `decision.py` flow calls `resolve_research_policy_router(...)` after post-Fib gating and before final sizing effects are applied
- the router module defines only RI-local policy states: continuation, defensive transition, and no-trade
- the router state/debug keys are RI-scoped
- the architecture packet explicitly says V1 must remain RI-family-local, must not introduce `FamilyRouterDecision`, and must not choose between `ri` and `legacy`

So the router sits **inside** shared orchestration but is **not** a cross-family selector.
Its placement is shared; its semantics are family-local.

### 5. Historical evidence preserved the overlay question, but the committed conclusion rejected overlay as the live family model

Observed from `docs/analysis/regime_intelligence/core/regime_intelligence_champion_compatibility_findings_2026-03-18.md` and `docs/features/feature-regime-intelligence-strategy-family-1.md`:

- the champion-compatibility finding says the active champion is not RI-compatible as a simple overlay
- the authority-only overlay probe collapsed to zero trades
- the documented conclusion was “strategy-topology finding,” not “small migration patch”
- the later strategy-family feature doc formalized RI as a separate family rather than a thin overlay or migration patch
- both surfaces preserve strong “not an overlay” wording without claiming family merge or reinterpretation

So the current two-family reading was not introduced arbitrarily.
It was stabilized after committed overlay evidence was read as topology-breaking rather than patch-like.

## Inferred

### 1. The main current risk is semantic/workflow confusion, not a direct runtime contradiction

The current code-and-doc stack appears internally consistent:

- family identity is two-valued
- hybrid surfaces fail closed
- the RI router is local rather than generic
- historical overlay language is preserved as rejected evidence, not as the active live contract

That points more to a reading/coordination problem than to a hard implementation contradiction.

### 2. The friction is produced by three different axes being easy to read as one

The strongest source of confusion appears to be that readers can collapse these three axes into a single mental model:

1. shared execution backbone
2. separate family identity/admission
3. RI-family-local policy-routing behavior

When those axes are mentally fused, the repo can look more contradictory than it actually is.

### 3. The current split looks partly empirical and partly stabilized by later contract surfaces

The overlay evidence appears to have created the initial break:

- authority-only overlay failed
- RI-compatible behavior required a broader cluster
- the result was read as a different strategy topology

After that, later docs and validators appear to have frozen this interpretation into clearer family boundaries.
So the present friction looks inherited from a real empirical break and then reinforced by later contract surfaces.

### 4. The identity/admission seam is itself a sign of historical pressure in this area

Because the repo already introduced a dedicated family-admission layer and archived a roadmap about shrinking identity back to identity, it is reasonable to infer that:

- the confusion is not only in the reader’s head
- this zone has already produced enough ambiguity to require explicit architectural separation of concerns

That does **not** prove the current model is wrong.
It does suggest the friction is structural, not merely rhetorical.

## Unverified

- This slice did **not** determine exactly how much of today’s pain would disappear through naming/documentation cleanup alone.
- This slice did **not** determine whether the present two-family model is the best target architecture, only that it is the current repo-backed reading.
- This slice did **not** prove how much of the current RI identity surface is truly topology-required versus historically frozen for governance/comparison safety.
- This slice did **not** reopen whether RI could someday be reframed as a layer over Legacy on a higher conceptual level without changing runtime family rules.
- This slice did **not** test whether another agent, starting cold, would independently draw the same friction map.

## Four-box friction map

| Friction box                       | What currently sits here                                                                                        | Why it creates confusion                                                                                           | Current confidence |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ------------------ |
| Runtime-required separation        | overlay failure, RI-compatible cluster, RI-only router semantics                                                | shared backbone can make these look optional even when committed evidence says they are not                        | high               |
| Contract/policy-imposed separation | two-family registry, hybrid fail-closed rules, run-intent admission gates, cross-family promotion override rule | readers may experience governance/validator boundaries as if they were direct proofs of ontology                   | medium-high        |
| Historical wording drift           | older overlay/migration wording preserved as evidence, later family docs formalizing separate-family framing    | nearby documents can sound like they are making different claims when they are actually recording different stages | high               |
| Naming / reading ambiguity         | `authority_mode`, shared `decision.py`, `research_policy_router`, identity vs admission terminology             | nearby terms invite readers to conflate authority, family, router, and run-purpose                                 | high               |

## Practical reading rule from this slice

For the current branch, the cheapest accurate reading appears to be:

- shared backbone **does not** mean shared family
- `authority_mode = regime_module` **does not** by itself mean “valid RI family surface”
- RI router placement inside `decision.py` **does not** make it a cross-family router
- preserved overlay evidence **does not** override the current two-family contract reading

That reading keeps the current repo coherent without claiming that the current family split is the final ideal architecture.

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

- **Observed:** current code and docs deliberately combine a shared runtime backbone with separate family identity/admission and an RI-family-local policy router; overlay-as-layer was historically probed and then stabilized into separate-family framing after committed failure evidence.
- **Inferred:** the main present risk is semantic/workflow confusion rather than a strict runtime contradiction; the confusion is amplified because backbone, family identity/admission, and RI-local policy behavior are easy to collapse into one mental model.
- **Unverified:** how much of the pain is naming/docs debt versus genuine topology necessity, and how much of the current split is permanently required rather than historically stabilized, remain open.
- **Working answer:** the present RI-vs-Legacy friction appears to be real, but it is best classified as a mixed four-box problem — runtime-required separation, contract reinforcement, historical wording drift, and naming ambiguity — rather than as a single contradiction.
