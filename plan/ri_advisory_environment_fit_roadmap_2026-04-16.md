# RI advisory environment-fit roadmap

Date: 2026-04-16
Mode: `RESEARCH`
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical / parked / archive-only / not active on current branch / planning-only / advisory-only / no-runtime-authority`

> Current status note:
>
> - [ARCHIVED 2026-05-05] This roadmap is not the active lane for `feature/next-slice-2026-05-05`.
> - Current active lane authority after the merge of PR `#79` is `GENESIS_WORKING_CONTRACT.md` plus the merged RI policy-router packet/analysis chain.
> - Preserve it as archived branch-specific planning context from `feature/ri-role-map-implementation-2026-03-24`.
> - Reactivate only via explicit user request or a fresh packet that deliberately reopens the advisory-environment-fit line.

## Why this roadmap exists

The current-ATR research lane has now established an important boundary:

- `current_atr >= 900` produced a useful bounded discovery-year story in `2024`
- the frozen `2024` good-vs-bad environment split did **not** remain robust across later full-year holdouts
- `2025` is the most important contradiction and must be treated as a real counterexample, not as noise

That means the next lane should **not** be more threshold-mining.
It should ask a narrower and more useful question:

> Can Genesis identify when the existing RI strategy is operating inside a supportive versus hostile context, without replacing the core strategy or pretending that one frozen 2024 pattern is universal?

This roadmap exists to sequence that next lane in a controlled way.

## Locked starting context

The following points are already established and should be treated as starting constraints, not open brainstorming inputs:

### A. The current-ATR robustness result is mixed, not promotion-ready

The multi-year `current_atr >= 900` environment-robustness slice closed with a `mixed` verdict.
That is valid evidence.
It is not a failure to be explained away.

### B. The repository already contains RI intelligence building blocks

Existing RI-oriented observability and advisory surfaces already exist in tracked code, including:

- clarity scoring
- risk-state / transition handling
- authoritative-vs-shadow regime observability
- RI-aware sizing hooks

The next roadmap should build from those primitives before inventing new ones.

### C. Family boundaries matter

The repository now explicitly distinguishes:

- `legacy`
- `ri`

This roadmap is for the `ri` family only.
It must not silently create hybrid policy logic across families.

### D. AI/ML is advisory only at this stage

If `src/core/ml` becomes relevant later, it must enter as a shadow comparator or advisory scorer only.
It does **not** receive decision authority, gate authority, sizing authority, or default authority in this roadmap.

## Main objective

The objective is to determine whether Genesis can produce a **deterministic, RI-only advisory layer** that estimates three things without overriding the existing decision engine:

1. `transition_risk_score`
2. `decision_reliability_score`
3. `market_fit_score`

Those outputs are intended to answer:

- are we entering near a regime transition or regime ambiguity?
- does the current state look like a context where the existing RI strategy is usually reliable?
- is the current row closer to historically supportive or historically hostile conditions?

## What this roadmap is not

This roadmap is **not** authority to:

- retune the core strategy until the lane “works”
- claim a universal environment profile
- merge `legacy` and `ri` semantics
- replace deterministic logic with ML
- add runtime gating by advisory score without a later, separate packet

## Global constraints

- no default behavior change
- no runtime authority changes by this roadmap alone
- `ri` family only
- advisory / shadow first
- no cross-family promotion or hybridization
- no threshold sweep as the main next move
- no Optuna or broad tuning campaign until labels and baseline framing are stable
- keep `2025` as a required contradiction year in any serious evaluation set
- preserve the distinction between association and causal proof

## Hard stop rules

Stop the lane immediately if any of the following becomes true:

1. the work drifts into “make 2024 work again” rather than general context recognition
2. a proposed signal depends on post-entry information at scoring time
3. a proposal requires cross-family rule leakage from `legacy` into `ri`
4. ML is being used to bypass missing deterministic framing rather than to compare against it
5. the only way to show value is to give the advisory layer direct runtime authority before shadow evidence exists

## Lane close rule

Close the lane once one of the following becomes true:

- a deterministic advisory baseline is useful enough to justify a later shadow-runtime packet
- the advisory scores remain unstable or contradictory across years and the lane should stop
- ML fails to improve materially on the deterministic baseline and the bounded lane should end

## Priority order from here

1. freeze the advisory question and evidence ledger
2. inventory existing RI observability surfaces
3. define labels and failure taxonomy
4. build deterministic advisory baseline
5. run shadow multi-year evaluation
6. only then consider ML as a comparator

## Phase 0 — roadmap freeze and lane framing

### Goal

Freeze the next research question so the lane does not devolve into more current-ATR threshold iteration.

### Deliverable

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`

### Exit criteria

- one live roadmap anchor exists
- the lane is explicitly RI-only
- advisory-only scope is stated plainly
- `2025` contradiction is preserved as a first-class constraint

## Phase 1 — RI observability inventory

### Goal

Map the already existing RI intelligence surfaces into candidate advisory inputs before adding anything new.

### Core questions

- which current signals already describe transition risk?
- which current signals already describe confidence / clarity / regime agreement?
- what is already observable in shadow form without changing runtime behavior?

### Expected outputs

- one compact inventory memo
- one table mapping existing fields to candidate advisory roles
- explicit note on what is missing versus merely unused

### Required focus surfaces

- clarity scoring
- risk-state transition handling
- authoritative-vs-shadow regime mismatch
- RI sizing observability
- current environment/context descriptors already captured in research slices

### Exit criteria

- existing RI observability surface is mapped clearly
- missing dimensions are stated explicitly
- no new runtime seam is introduced yet

## Phase 2 — label definition and failure taxonomy

### Goal

Define the labels the advisory layer is actually allowed to learn or approximate.

### Required label families

1. supportive vs hostile context
2. transition-risk context
3. ambiguous / low-reliability context

### Required logic boundary

The labels must not collapse into “2024 good trade memory.”
They must distinguish at least:

- good trades / supportive context
- bad trades / hostile context
- regime-transition / ambiguity cases

The `regime transition` category is a required explicit surface, not an optional afterthought.

### Expected outputs

- one label memo or packet
- one compact failure taxonomy
- one explicit list of features allowed for label construction versus scoring-time use

### Exit criteria

- labels are stable enough to evaluate without circular logic
- transition cases are represented explicitly
- the lane is still pre-ML and pre-runtime-authority

## Phase 3 — deterministic advisory baseline

### Goal

Build the smallest admissible deterministic advisory baseline from existing RI/context features.

### Candidate outputs

- `transition_risk_score`
- `decision_reliability_score`
- `market_fit_score`

### Constraints

- use interpretable logic first
- no model-authority
- no runtime gating
- keep default behavior unchanged

### Required evaluation question

Does a deterministic composite built from existing RI/context observability separate supportive, hostile, and transition cases better than the current implicit heuristic picture?

### Expected outputs

- one bounded scoring definition
- one deterministic evaluation memo
- one explicit failure list for where the baseline breaks, especially in `2025`

### Exit criteria

- the baseline either shows useful structure or fails honestly
- the main failure modes are named instead of hand-waved
- the lane can decide whether ML comparison is justified

## Phase 4 — shadow multi-year evaluation

### Goal

Test the deterministic advisory baseline across years without giving it any decision authority.

### Required year discipline

- keep `2024` as discovery / shaping context only where explicitly justified
- include `2025` as mandatory blind contradiction check
- prefer full-year evaluation surfaces over cherry-picked windows

### Required outputs

- year-by-year shadow score behavior
- bucketed outcome tables for supportive / hostile / ambiguous / transition cases
- explicit note on whether the advisory scores degrade, invert, or remain useful across years

### Exit criteria

At least one of the following must be true:

- deterministic advisory scores remain meaningfully useful across multiple years
- the scores are useful only in narrow RI-specific contexts and should stay bounded
- the scores fail to generalize and the lane should stop before ML expansion

## Phase 5 — ML comparator lane (optional, not default)

### Goal

Only if Phase 4 justifies it, compare the deterministic baseline with a bounded ML advisory model.

### Allowed role for ML

ML may:

- estimate the same advisory labels in shadow mode
- act as a comparator against the deterministic baseline
- expose nonlinear interactions the deterministic baseline misses

ML may **not**:

- replace the core strategy
- override decisions or sizing directly
- become a launch shortcut because the deterministic baseline was inconvenient

### Expected outputs

- one comparator memo
- deterministic-vs-ML error decomposition
- bounded recommendation: `stop / keep deterministic / continue ML shadow`

### Exit criteria

- the ML lane proves incremental value clearly, or
- the deterministic baseline remains the preferred bounded surface, or
- the whole advisory lane is closed as non-robust

## Phase 6 — closeout and next-lane decision

### Goal

Decide whether the advisory work deserves a later runtime-shadow packet or should remain research-only.

### Allowed outcomes

- `stop` — no robust advisory lane emerged
- `shadow-only continue` — enough value exists for a later default-off observational runtime lane
- `bounded escalation` — a later packet may test RI-only advisory surfacing with default behavior unchanged

### Explicitly forbidden outcome from this roadmap alone

- direct promotion into runtime authority

## Initial practical sequencing

The first concrete move after this roadmap should be:

1. inventory current RI observability surfaces already in the repo
2. formalize the advisory labels, especially the regime-transition bucket
3. build the deterministic baseline before touching `src/core/ml`

## Success condition

This roadmap succeeds if it prevents the next lane from becoming either:

- endless threshold tuning, or
- premature ML theater

The real win is a bounded, honest answer to whether Genesis can recognize when the existing RI strategy is in a supportive, hostile, or transition-prone environment — without pretending that recognition itself is already a deployable authority.
