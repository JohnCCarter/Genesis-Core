# RI advisory environment-fit — Phase 2 label taxonomy

This memo is docs-only and definitional.
It defines which labels and state tags are admissible for the RI advisory environment-fit lane, using only already generated current-ATR evidence and already tracked RI observability surfaces.

Governance packet: `docs/decisions/ri_advisory_environment_fit_phase2_label_taxonomy_packet_2026-04-16.md`

## Source surface used

This memo uses only already tracked surfaces:

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/ri_advisory_environment_fit_phase1_observability_inventory_2026-04-16.md`
- `docs/decisions/current_atr_900_multi_year_env_robustness_packet_2026-04-16.md`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_env_profile_2026-04-16/env_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/robustness_summary.json`
- `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/current_atr_900_multi_year_env_robustness_2026-04-16/closeout.md`

## Why this slice was needed

Phase 1 established that the repository already has meaningful RI observability, but not yet a unified advisory surface.

That means the next real bottleneck is not ML and not runtime integration.
It is label discipline.

Without a clean taxonomy, the lane would risk collapsing into one of two bad outcomes:

- “2024 good-trade memory” disguised as generalization
- circular scores built from the same post-entry information they are supposed to predict

## Core label-design rule

The lane must distinguish **outcome labels** from **state tags**.

### Outcome labels

These are allowed to use post-entry evidence and are used to judge whether a later advisory score was helpful or harmful.

### State tags

These are allowed to use entry-time RI observability and are used to describe context classes such as transition pressure or authority disagreement.

State tags may be ingredients or strata for later analysis.
They must not be confused with ex-post outcome labels.

## Admissible label families

### 1. Supportive outcome label

`supportive_context_outcome`

Definition:

- row belongs to an evaluable RI context cohort
- row is in the bounded active-treatment / active-uplift population used by the current-ATR evidence lane
- post-entry outcome is helpful relative to the bounded baseline comparison surface (`pnl_delta > 0`)

Allowed construction evidence:

- `pnl_delta`
- `mfe_16_atr`
- `continuation_score`
- active-uplift cohort membership

Important constraint:

- the composite discovery seeds used in `2024` are **discovery helpers**, not universal labels
- later supportive labels may inherit the helpful/harmful direction but may not pretend the 2024 top-ranked seed cohort is itself a universal support class

### 2. Hostile outcome label

`hostile_context_outcome`

Definition:

- row belongs to an evaluable RI context cohort
- row is in the bounded active-treatment / active-uplift population used by the evidence lane
- post-entry outcome is harmful relative to the bounded baseline comparison surface (`pnl_delta < 0`)

Allowed construction evidence:

- `pnl_delta`
- `mfe_16_atr`
- `continuation_score`
- active-uplift cohort membership

Interpretation rule:

- hostile does **not** mean “all bad trades everywhere”
- it means a bounded context where the existing strategy expression was unhelpful on the governed evaluation surface

### 3. No-evidence / non-evaluable cohort label

`non_evaluable_context`

Definition:

- row or year has no active-uplift population on the bounded comparison surface

Why this must be explicit:

- years such as `2018`, `2019`, `2020`, and `2023` on the robustness surface have zero active-uplift positions
- those years must not be silently counted as either supportive or hostile evidence

This is not a failure label.
It is a coverage label.

## Admissible state tags

### 4. Transition-risk state tag

`transition_risk_state`

Definition:

- entry-time context indicates elevated regime-transition pressure through already tracked RI observability, such as:
  - `bars_since_regime_change`
  - `ri_risk_state_transition_mult < 1.0`
  - authoritative regime change proximity signals already exposed by the RI state path

Interpretation rule:

- this is a **state tag**, not an ex-post outcome label
- later deterministic scoring may use transition-risk features, but Phase 2 does not authorize any formula yet

### 5. Authority-disagreement state tag

`authority_disagreement_state`

Definition:

- authoritative-vs-shadow regime mismatch is observed at entry time

Allowed construction evidence:

- `meta.observability.shadow_regime.mismatch`
- related authoritative/shadow source metadata

Interpretation rule:

- this tag exists because disagreement is already tracked and explicitly non-authoritative
- it is a useful instability / ambiguity descriptor, not a proof of hostile outcome by itself

### 6. Ambiguity state tag

`ambiguous_state`

Definition:

- row is neither cleanly classifiable as supportive nor hostile on the bounded profile surface, or
- row carries disagreement / transition signals strong enough that a later score should treat it as low-confidence classification territory

Important restriction:

- ambiguity is **not** “anything we do not like later”
- ambiguity must remain a narrow residual bucket for:
  - mixed-distance classification surfaces
  - disagreement-heavy rows
  - transition-heavy rows

## Allowed feature boundary

### Allowed for outcome-label construction only

These may be used only to define or audit ex-post outcomes:

- `pnl_delta`
- `mfe_16_atr`
- `continuation_score`
- discovery-year seed rankings
- helpful / harmful counts from the bounded replay artifacts

These are **forbidden** as direct inputs to a future scoring-time advisory baseline.

### Allowed for later scoring-time baseline inputs

These are admissible candidate inputs for a later deterministic baseline because they are available at or before entry time:

- clarity-derived fields (`ri_clarity_*` family)
- transition-risk proxy fields (`ri_risk_state_*`, `bars_since_regime_change`)
- authoritative-vs-shadow regime disagreement
- regime / htf regime / authority-mode context
- probability / confidence context already available pre-entry
- bounded context descriptors already available at scoring time

### Forbidden leakage

The following are explicitly forbidden in a later scoring-time baseline:

- post-entry `pnl_delta`
- post-entry continuation proxies
- discovery seed ranking membership itself
- any label that is just a restatement of the 2024 selected seed cohort

## Year taxonomy for later evaluation

The current evidence already implies three year classes that the later baseline must report explicitly.

### A. Discovery year

- `2024`

Use:

- shaping / label-definition reference year only

Restriction:

- may not be used as sole proof of generalization

### B. Contradiction-heavy year

- `2025`

Why it is special:

- the robustness slice classified many `2025` rows as `good_environment`, but `bad_environment` still outperformed `good_environment` on mean `pnl_delta`
- therefore `2025` is the mandatory inversion check for any later score

### C. No-evidence years on the bounded uplift surface

- `2018`, `2019`, `2020`, `2023`

Why this matters:

- these are coverage gaps, not hostile evidence
- a later score must report them as non-evaluable or zero-coverage years rather than padding its metrics

### D. Weak-but-evaluable holdout years

- `2017`, `2021`, `2022`

Meaning:

- these years provide some evaluable population, but they differ strongly in class separation quality and sample size

## Required failure taxonomy for later phases

Any later deterministic baseline must report at least these failure classes.

### 1. False-supportive failure

- score or bucket says `supportive`
- realized outcome label is `hostile`

### 2. False-hostile failure

- score or bucket says `hostile`
- realized outcome label is `supportive`

### 3. Transition miss

- row carries strong transition-risk state
- score still treats it as clean stable support/hostility without degradation or caution

### 4. Disagreement miss

- authoritative-vs-shadow mismatch exists
- score still treats the row as high-certainty without penalty or explicit ambiguity handling

### 5. Coverage failure

- score claims broad usefulness but most years or cohorts are actually non-evaluable / zero-coverage

### 6. Contradiction-year inversion

- score appears good on discovery-shaped evidence
- but inversion survives on `2025` or another contradiction-heavy year

This failure class is mandatory because the whole lane exists partly to avoid mistaking discovery-year fit for durable context recognition.

## Phase 2 verdict

**Verdict:** `continue to Phase 3`

Why that is the honest outcome:

- the label surface is narrow enough to stay non-circular
- the lane now has a clear distinction between outcome labels and state tags
- the required contradiction and coverage classes are explicit
- the next real question is whether a deterministic advisory baseline can use the allowed pre-entry RI/context inputs to separate these labels better than the current implicit picture

## Consequence for the roadmap

The next admissible move is:

- **Phase 3 — deterministic advisory baseline**

That next slice should stay bounded to:

1. a deterministic score definition only
2. allowed scoring-time inputs only
3. explicit reporting against the failure taxonomy above
4. mandatory contradiction-year reporting

What should **not** happen next:

- no runtime integration
- no ML comparator yet
- no post-entry feature leakage into score inputs

## Bottom line

Phase 2 closes with a narrow but usable taxonomy:

- **outcome labels:** `supportive_context_outcome`, `hostile_context_outcome`, `non_evaluable_context`
- **state tags:** `transition_risk_state`, `authority_disagreement_state`, `ambiguous_state`

That is enough structure to make a later deterministic baseline slice admissible.
It is **not** authority to implement that baseline inside runtime.
