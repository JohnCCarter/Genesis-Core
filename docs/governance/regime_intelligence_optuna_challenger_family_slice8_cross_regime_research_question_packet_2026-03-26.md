# Regime Intelligence challenger family — slice8 cross-regime research question packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `research-question only / docs-only / no setup or launch authorization / no replay-window decision`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet defines the next bounded RI-family research question after slice8 reproduction, but must remain docs-only and must not drift into replay-surface selection, setup authorization, launch authorization, comparison, readiness, promotion, or runtime/default change.
- **Required Path:** `Quick`
- **Objective:** Define one bounded research question asking whether the reproduced slice8 full tuple should be subjected, in a later separately authorized replay, to one fixed non-2024 OOS window as a falsification step before any lane for structural search-space change or objective change is opened.
- **Candidate:** `slice8 cross-regime research question`
- **Base SHA:** `bc64cd29`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research-question only / non-authorizing`
- `No replay-window decision`
- `No comparison/readiness/promotion reopening`
- `No env/config semantics changes`

### Skill usage

- No repository skill is evidenced for this docs-only governance packet.
- This packet uses manual governance review only.
- Any future skill coverage for this packet shape remains `föreslagen` until implemented and verified.

### Scope

- **Scope IN:**
  - exactly one docs-only research-question packet under `docs/governance/`
  - explicit framing that the next bounded question is whether the reproduced slice8 full tuple should face a later separately authorized fixed non-2024 OOS falsification replay before any structural search-space or objective-change lane opens
  - explicit preservation that slice8 remains the primary RI research surface, slice9 remains secondary robustness context only, and slice7 remains historical context only
  - explicit statement that any specific replay-window choice, including `2025` OOS, remains candidate-level only until a separate later setup/authorization packet exists
  - explicit fail-closed boundary that this packet authorizes no setup, no launch, no comparison, no readiness, no promotion, no writeback, and no new evidence class
- **Scope OUT:**
  - no source-code changes
  - no `tests/**`, `config/**`, or `results/**` changes
  - no setup authorization
  - no launch authorization
  - no replay-window selection decision
  - no incumbent comparison reopening
  - no readiness reopening
  - no promotion reopening
  - no writeback
  - no new evidence class
  - no runtime/default/env/config-authority change
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_challenger_family_slice8_cross_regime_research_question_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must remain a research question only
- no sentence may choose a replay window
- no sentence may authorize setup, launch, execution, comparison, readiness, promotion, or writeback
- no sentence may define pass/fail thresholds, score gates, output requirements, or later decision logic
- no sentence may restore slice9 or slice7 as active continuation surfaces
- no sentence may turn the reproduced slice8 full tuple into a runtime/default candidate by implication

### Stop Conditions

- any wording that states or implies that `2025` OOS has already been selected as the replay surface
- any wording that turns this packet into setup authorization or launch authorization
- any wording that reopens incumbent comparison, readiness, promotion, or writeback
- any wording that defines pass/fail thresholds, score gates, artifact outputs, or later decision criteria
- any wording that makes slice9 a co-primary or backup continuation surface
- any wording that restores slice7 as an active continuation surface
- any wording that treats the reproduced slice8 tuple as operationally approved rather than research-only
- any need to modify files outside this one scoped packet

### Output required

- reviewable cross-regime research-question packet
- explicit statement of the bounded research question only
- explicit primary/secondary/historical lane boundary statement for slice8/slice9/slice7
- explicit candidate-only treatment of any fixed non-2024 OOS surface, including `2025` OOS
- explicit non-authorizations and stop conditions

## Purpose

This packet defines only the next bounded **research question** after the successful slice8 follow-up reproduction.

That reproduced run confirmed that the slice8 surface is runnable and locally repeatable on the already-tracked 2024 development/validation split.
It did **not** establish a new edge, did **not** reopen comparison, and did **not** answer whether the frozen slice8 tuple survives outside the current 2024 window pair.

This document therefore asks only whether the next bounded question should be:

- whether the reproduced slice8 full tuple should later be challenged on one fixed non-2024 OOS surface before any structural search-space or objective-change lane is opened

This packet does **not** authorize:

- setup
- launch
- execution
- incumbent comparison
- readiness
- promotion
- writeback
- any replay-window selection decision

Fail-closed interpretation:

> This document defines only the next bounded research question: whether the reproduced
> slice8 full tuple should be tested, in a separate later-authorized replay, against one
> fixed non-2024 OOS window as a falsification step before any lane for structural
> search-space change or objective change is opened. This document does not authorize
> setup, execution, comparison, readiness, promotion, writeback, or any runtime/config
> changes. Any replay-window choice, including `2025` OOS, remains candidate-level only
> until a separate setup/authorization packet exists.

## Upstream governed basis

This packet is downstream of the following already tracked documents:

- `docs/governance/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_followup_research_lane_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_followup_setup_only_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_followup_launch_authorization_packet_2026-03-26.md`

Carried-forward meaning from those documents:

1. the active lane remains RI-family-internal research only
2. slice8 remains the sole primary continuation surface
3. slice9 remains secondary robustness context only
4. slice7 remains historical context only
5. comparison, readiness, promotion, and writeback remain outside the active lane
6. the slice8 follow-up launch authorization was exact-anchor and exact-state bound rather than a general widening of lane authority
7. the completed slice8 follow-up run reproduced the known local result rather than creating a new high-water edge

## Why this question is next

The most informative next bounded question is no longer another local search-space perturbation on the same 2024 window pair.

That is because:

1. the reproduced slice8 follow-up run already answered the narrow repeatability question for the current local surface
2. a structural search-space change would widen the intervention surface before the current frozen tuple has been falsified outside the present 2024 frame
3. an objective change would widen interpretation and ranking semantics before the current frozen tuple has been challenged on a different regime/window surface
4. a fixed non-2024 OOS falsification question is narrower than either A) structural search-space change or B) objective change

This reasoning is lane-governance only.
It is not execution authority.

## Exact research question

The exact research question opened by this packet is:

- **Should the reproduced slice8 full tuple be subjected, in a later separately authorized replay, to one fixed non-2024 OOS window as a falsification step before any lane for structural search-space change or objective change is opened?**

This packet opens that question only.
It does **not** answer it operationally.

This question does **not** ask:

- whether `2025` OOS has already been selected as the replay surface
- whether setup should begin now
- whether launch should occur now
- whether incumbent comparison should reopen
- whether readiness or promotion should open
- whether pass/fail thresholds should be defined here
- whether the reproduced slice8 tuple is now a runtime/default candidate

## Admissible input surface

Only the following inputs are admissible inside this packet.

### 1. RI lane-governance anchors

- `docs/governance/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_followup_research_lane_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_followup_setup_only_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_followup_launch_authorization_packet_2026-03-26.md`

Allowed use:

- preserve the already-open RI research-lane boundary
- preserve slice8 as the sole primary continuation surface
- preserve slice9 and slice7 at their already bounded secondary/historical roles
- preserve that setup and launch require separate later packets

### 2. Reproduced slice8 evidence surface

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- `results/hparam_search/ri_slice8_followup_launch_20260326/run_meta.json`
- `results/hparam_search/ri_slice8_followup_launch_20260326/best_trial.json`
- `results/hparam_search/ri_slice8_followup_launch_20260326/validation/trial_001.json`

Allowed use:

- identify the exact slice8 surface that was just reproduced under separate launch authority
- preserve that the reproduced subject is a frozen local tuple rather than a new search-space proposal
- preserve the bounded claim that the current question is now generalization/falsification rather than another same-surface repeatability check

Disallowed use:

- treating the reproduced tuple as comparison-ready
- treating the reproduced tuple as readiness-ready or promotion-ready
- claiming that local reproduction alone proves cross-regime stability

### 3. Cross-window / OOS context only

- `docs/features/feature-ri-optuna-train-validate-blind-1.md`
- `config/optimizer/3h/phased_v3/tBTCUSD_3h_phased_v3_phaseE_oos.yaml`
- `docs/analysis/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`

Allowed use:

- preserve that the repository already has a blind/OOS taxonomy and existing non-2024 OOS precedent
- preserve that robustness across additional windows is an already-recognized stronger standard than single-window local peak
- preserve that `2025` OOS exists as candidate context for a later question about cross-regime falsification

Disallowed use:

- selecting `2025` OOS by implication in this packet
- converting contextual OOS precedent into setup or launch authority
- importing older candidate/promotion reasoning as if it were an already-open lane here

### 4. Slice9 and slice7 bounded context only

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice9_20260326.json`
- the already tracked ranked-summary discussion of slice7

Allowed use:

- preserve that slice9 remains supporting robustness context only
- preserve that slice7 remains historical context only
- explain why the current question should stay centered on the reproduced slice8 tuple rather than widening back to a multi-surface decision

Disallowed use:

- making slice9 a co-primary or backup replay candidate in this packet
- restoring slice7 as an active follow-up surface

## Cross-regime interpretation boundary

Inside this packet, `cross-regime` means only the following:

- a later separately authorized falsification replay on one fixed non-2024 OOS surface
- performed only if a later setup and authorization packet chooses to pursue that question
- used only to determine whether the reproduced slice8 tuple should face broader falsification before lane A or lane B opens

Inside this packet, `cross-regime` does **not** mean:

- a chosen replay surface already exists
- multiple replay windows are now opened
- the incumbent comparison lane is reopened
- slice9 becomes an alternate candidate surface
- a blind result would automatically trigger readiness or promotion

## Candidate non-2024 OOS surface remains undecided

This packet does **not** choose the replay window.

The only bounded statement allowed here is:

- if a later separate setup packet is ever proposed, it may evaluate whether one fixed non-2024 OOS surface should be used as the falsification subject for the reproduced slice8 tuple

Existing repository context makes the following statement admissible and nothing stronger:

- a non-2024 OOS surface, including `2025`-era OOS context, may be referenced here only at candidate level because the repository already contains blind/OOS planning and evaluation patterns outside the current 2024 window pair

This packet must **not** be read as saying:

- `2025` has been selected
- `2025` should be run now
- `2025` is the only acceptable future candidate surface

## Inadmissible actions inside this packet

This packet does not allow any of the following:

- setup authorization
- launch authorization
- execution command authorization
- replay-window selection
- pass/fail threshold definition
- score-gate definition
- output-artifact requirement definition
- incumbent comparison reopening
- readiness reopening
- promotion reopening
- writeback recommendation
- candidate advancement language that implies operational approval

## Next admissible governance action

If a later governance step is separately proposed and separately approved, one admissible next packet shape would be:

- one bounded setup-only packet asking whether to prepare a fixed non-2024 OOS replay surface for the reproduced slice8 tuple

This document provides **no** authorization to start that setup step now.

If a later packet needs to specify:

- the exact replay window
- the exact replay config surface
- the exact launch preconditions
- the exact output discipline
- the exact pass/fail logic

then that later packet must be treated as a separate governance step and not as an extension of this quick-path question packet.

## Bottom line

After the slice8 follow-up reproduction, the next bounded question is not yet another local search tweak.

The next bounded question is whether the reproduced slice8 full tuple should later be challenged on **one fixed non-2024 OOS surface** before any structural search-space or objective-change lane opens.

Within this packet:

- slice8 remains the sole primary surface
- slice9 remains supporting robustness context only
- slice7 remains historical context only
- any fixed non-2024 OOS surface, including `2025` OOS, remains candidate-level only

Any setup, authorization, execution, comparison, readiness, promotion, or writeback step would require a **separate future governance packet** and is not authorized by this document.
