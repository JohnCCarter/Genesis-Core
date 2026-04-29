# RI advisory environment-fit — Phase 1 observability inventory

This memo is docs-only and observational.
It inventories the already tracked `ri` observability surfaces that can support the advisory environment-fit roadmap without changing default behavior.

Governance packet: `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase1_observability_inventory_packet_2026-04-16.md`

## Source surface used

This memo uses only already tracked source and roadmap surfaces:

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `src/core/intelligence/regime/clarity.py`
- `src/core/intelligence/regime/risk_state.py`
- `src/core/intelligence/regime/contracts.py`
- `src/core/strategy/decision_sizing.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/family_registry.py`
- `src/core/strategy/family_admission.py`

## Why this slice was needed

The roadmap now asks Genesis to answer a narrower question than threshold tuning:

> can the existing `ri` strategy recognize supportive, hostile, or transition-prone context without replacing the core decision engine?

Before opening a label-definition or scoring slice, the repository first needed an honest inventory of what is already observable today versus what is still missing.

## Inventory summary

The short answer is:

- the repository already has meaningful `ri` observability for **clarity**, **transition-risk proxies**, and **authority-vs-shadow regime disagreement**
- those signals are currently **distributed across state/meta payloads**, not unified into one advisory surface
- the repository does **not** yet expose a first-class `market_fit_score`, `decision_reliability_score`, or `transition_risk_score`
- the family boundary needed for this lane is already explicit and tracked

So the lane is **not starting from zero**, but it is also **not yet one bounded advisory surface**.

## Current observability ledger

| Candidate advisory role                            | Current tracked source                                                                                                                        | Current exposure form                                                         | Current status                        | Notes                                                                                                           |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| clarity / decision quality proxy                   | `compute_clarity_score_v1` in `src/core/intelligence/regime/clarity.py`                                                                       | emitted through `decision_sizing.py` as `ri_clarity_*` fields in sizing state | `already observable`                  | already decomposed into confidence, edge, EV, and regime-alignment components; currently applied only to sizing |
| transition-risk proxy                              | `compute_risk_state_multiplier` in `src/core/intelligence/regime/risk_state.py` plus `_build_regime_transition_state` in `decision_sizing.py` | emitted as `ri_risk_state_*`, `last_regime`, `bars_since_regime_change`       | `already observable via proxy`        | transition handling exists, but not yet as a standalone advisory score                                          |
| authoritative-vs-shadow regime disagreement        | `evaluate.py` + `ShadowRegimeObservability` contract                                                                                          | `meta["observability"]["shadow_regime"]` payload                              | `already observable`                  | contains authority source, shadow source, authority_mode, mismatch flag, and explicit `decision_input=False`    |
| RI family boundary                                 | `family_registry.py` + `family_admission.py`                                                                                                  | validation/admission constraints                                              | `already enforced guardrail`          | not an advisory signal itself, but it cleanly keeps the lane `ri`-only                                          |
| unified decision reliability score                 | distributed across clarity, confidence, and mismatch proxies                                                                                  | not exposed as one score                                                      | `missing / partial ingredients exist` | pieces exist, but no unified reliability surface is tracked yet                                                 |
| unified market fit score                           | no first-class implementation                                                                                                                 | none                                                                          | `missing`                             | current-ATR / environment-profile research fields exist in artifacts, but not as tracked runtime observability  |
| explicit supportive / hostile / transition buckets | no first-class implementation                                                                                                                 | none                                                                          | `missing`                             | requires later label-definition work                                                                            |

## What is already observable today

### 1. Clarity is already a real RI-facing observability surface

`src/core/intelligence/regime/clarity.py` already computes a bounded clarity score with explicit components:

- confidence
- edge
- EV
- regime alignment

`src/core/strategy/decision_sizing.py` then exposes that calculation in tracked state through fields such as:

- `ri_clarity_score`
- `ri_clarity_raw`
- `ri_clarity_components`
- `ri_clarity_weights`
- `ri_clarity_multiplier`

Important boundary:

- this is already meaningful observability
- but it currently lives inside the sizing path
- it is **not yet** a standalone advisory `decision_reliability_score`

So clarity is best classified as:

- **already observable and already decomposed**
- **not yet unified into the roadmap’s target advisory output**

### 2. Transition-risk proxies already exist

`src/core/intelligence/regime/risk_state.py` already computes a risk-state multiplier using:

- drawdown guard
- transition guard
- `bars_since_regime_change`

`decision_sizing.py` also maintains:

- `last_regime`
- `bars_since_regime_change`
- `ri_risk_state_multiplier`
- `ri_risk_state_drawdown_mult`
- `ri_risk_state_transition_mult`

This means the repository already has a tracked view of:

- whether the system thinks it is near a regime change
- whether that transition is severe enough to penalize sizing

Important boundary:

- this is transition-risk **observability**, not yet a formal `transition_risk_score`
- it is currently expressed as multiplier components rather than as one advisory confidence surface

So transition risk is best classified as:

- **already partially observable through explicit proxies**
- **not yet normalized into the roadmap’s target output form**

### 3. Shadow regime observability already exists and is explicitly non-authoritative

`src/core/strategy/evaluate.py` records a shadow-regime payload under `meta["observability"]["shadow_regime"]` with:

- authoritative source
- shadow source
- authority mode
- authority mode source
- authoritative regime
- shadow regime
- mismatch flag
- `decision_input=False`

That last field matters a lot.
The repository already distinguishes:

- what is observed in shadow
- what is actually used for decisions

That is exactly the kind of separation the advisory roadmap wants to preserve.

So shadow mismatch is best classified as:

- **already observable**
- **already correctly separated from decision authority**
- **a strong candidate ingredient for later reliability / transition scoring**

## What is only partially available

### 4. Decision reliability has ingredients, but not yet a single surface

The repository already exposes several pieces that plausibly contribute to a future reliability view:

- clarity score
- clarity component breakdown
- transition multiplier
- bars since regime change
- authoritative-vs-shadow mismatch
- scaled vs exit confidence separation in `evaluate.py`

But those pieces are not yet collected into one explicit tracked concept like:

- `decision_reliability_score`

This matters because a later slice will need to decide whether reliability means:

- confidence under stable regime context
- confidence under low shadow mismatch
- confidence under low transition pressure
- or some bounded combination of the above

Current status:

- **ingredients exist**
- **first-class advisory output does not**

### 5. Transition handling exists, but transition taxonomy does not

The repo already has transition-aware mechanics.
What it does **not** yet have is an explicit taxonomy separating:

- stable supportive context
- hostile context
- regime-transition context
- ambiguous / disagreement context

That missing taxonomy is the main reason Phase 2 exists.

Current status:

- **transition signal pieces exist**
- **transition category definition does not**

## What is missing today

### 6. There is no first-class market-fit surface yet

The current-ATR research lane produced useful artifact-level environment evidence, but those environment descriptors do not yet exist as a tracked unified RI observability surface inside the strategy flow.

There is currently no first-class tracked output equivalent to:

- `market_fit_score`

That means the future market-fit lane cannot honestly claim “already implemented, just unused.”

The honest reading is narrower:

- the repository has research evidence about supportive vs hostile context
- but it does **not** yet expose a stable in-flow market-fit surface

### 7. There is no explicit supportive / hostile label surface yet

Nothing in the currently tracked RI observability directly labels rows as:

- supportive
- hostile
- transition-prone
- ambiguous

That is not a defect in the current runtime.
It just means the roadmap still needs a label-definition slice before any advisory baseline can be evaluated honestly.

## RI-only lane guardrails already exist

This roadmap asked to remain strictly `ri`-only.
The good news is that the repository already has that guardrail in tracked code.

`src/core/strategy/family_registry.py` and `src/core/strategy/family_admission.py` already enforce:

- explicit `legacy` vs `ri` family separation
- `ri` identity via `authority_mode=regime_module`
- bounded admission rules for research slices
- explicit cross-family promotion protection

This is not itself an advisory score.
But it means the roadmap can proceed without pretending that family boundaries are still fuzzy.

## Phase 1 verdict

**Verdict:** `continue to Phase 2`

Why that is the honest outcome:

- the repository already has enough RI observability to support a serious label-definition slice
- the lane is not blocked on “zero existing signal surface”
- but the current observability is still fragmented and lacks explicit supportive / hostile / transition taxonomy
- therefore the next bottleneck is label definition, not ML and not runtime integration

## Consequence for the roadmap

The next admissible move should be:

- **Phase 2 — label definition and failure taxonomy**

That slice should define, in a bounded and non-circular way:

1. supportive vs hostile context labels
2. regime-transition labels
3. ambiguity / disagreement labels
4. which fields may be used for label construction versus later scoring-time evaluation

What should **not** happen next:

- no immediate scoring formula implementation
- no direct runtime integration
- no jump to ML before label logic is stable

## Bottom line

The RI advisory lane is not beginning from scratch.
Genesis already exposes meaningful observability for:

- clarity
- transition-risk proxies
- authoritative-vs-shadow regime disagreement
- RI-only family discipline

But those surfaces are still fragmented.
The repository does **not** yet have a first-class:

- `transition_risk_score`
- `decision_reliability_score`
- `market_fit_score`

So the correct Phase 1 closeout is:

- **enough observability exists to continue**
- **the next real bottleneck is label definition and failure taxonomy, not more threshold work and not premature ML**
