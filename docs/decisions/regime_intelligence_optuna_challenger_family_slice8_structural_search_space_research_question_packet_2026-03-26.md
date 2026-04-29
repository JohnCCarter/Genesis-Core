# Regime Intelligence challenger family — slice8 structural search-space research question packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `research-question only / docs-only / no setup or launch authorization / no search-space design decision`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet defines one bounded RI-family research question after the negative bounded 2025 cross-regime outcome, but must remain docs-only and must not drift into search-space design, setup authorization, launch authorization, objective reopening, comparison, readiness, promotion, or runtime/default change.
- **Required Path:** `Quick`
- **Objective:** Define one bounded research question asking whether the next separately governed RI-family continuation should open a structural search-space lane around slice8 after the negative bounded 2025 cross-regime outcome, while keeping the current objective/version/metric surface fixed for now.
- **Candidate:** `slice8 structural search-space research question`
- **Base SHA:** `dbc870f3`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research-question only / non-authorizing`
- `No search-space design decision`
- `No objective-change opening`
- `No comparison/readiness/promotion reopening`
- `No env/config semantics changes`

### Skill usage

- No repository skill is evidenced for this docs-only governance packet.
- This packet uses manual governance review only.
- Any future skill coverage for this packet shape remains `föreslagen` until implemented and verified.

### Scope

- **Scope IN:**
  - exactly one docs-only research-question packet under `docs/governance/`
  - explicit framing that this packet asks whether a later separately governed structural search-space lane should open around slice8 after the bounded negative 2025 cross-regime result
  - explicit framing that, for the bounded question in this packet, slice8 remains the primary RI research surface, slice9 remains secondary robustness context only, and slice7 remains historical context only
  - explicit framing that any later structural lane, if separately opened, would test search-surface shape/width/duplicate-pressure hypotheses while keeping the current objective/version/metric surface fixed unless separately reopened later
  - explicit fail-closed boundary that this packet authorizes no search-space design decision, no setup, no config creation, no launch, no comparison, no readiness, no promotion, no writeback, and no new evidence class
- **Scope OUT:**
  - no source-code changes
  - no `tests/**`, `config/**`, or `results/**` changes
  - no setup authorization
  - no launch authorization
  - no search-space parameter or axis decision
  - no objective-change opening
  - no incumbent comparison reopening
  - no readiness reopening
  - no promotion reopening
  - no writeback
  - no new evidence class
  - no runtime/default/env/config-authority change
- **Expected changed files:** `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_research_question_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must remain a research question only
- no sentence may decide a structural search-space shape, width, axis set, or parameter list
- no sentence may authorize setup, launch, execution, comparison, readiness, promotion, or writeback
- no sentence may reopen objective design or imply that objective v2 is already inadequate
- no sentence may restore slice9 or slice7 as active co-primary continuation surfaces
- no sentence may turn the negative bounded 2025 cross-regime result into family-wide rejection of RI or permanent rejection of slice8

### Stop Conditions

- any wording that states or implies that a structural search-space lane is already opened by this packet
- any wording that turns this packet into setup authorization or launch authorization
- any wording that chooses a search-space shape, axis, width, or parameter set
- any wording that reopens objective design, incumbent comparison, readiness, promotion, or writeback
- any wording that makes slice9 a co-primary or backup continuation surface in this packet
- any wording that restores slice7 as an active continuation surface
- any wording that treats the negative bounded 2025 replay as terminal rejection of RI or slice8 research
- any need to modify files outside this one scoped packet

### Output required

- reviewable structural-search-space research-question packet
- explicit statement of the bounded research question only
- explicit primary/secondary/historical lane-boundary statement for slice8/slice9/slice7
- explicit fixed-objective boundary for this packet
- explicit non-authorizations and stop conditions

## Purpose

This packet defines only the next bounded **research question** after the governed slice8 cross-regime replay produced a negative bounded 2025 OOS outcome.

That replay answered the narrower falsification question for the frozen slice8 full tuple on one separately authorized non-2024 surface.
It did **not** authorize structural intervention, did **not** reopen objective design, did **not** reopen comparison, and did **not** create anchor, readiness, or promotion support.

This document therefore asks only whether the next separately governed continuation should be:

- whether a later separately authorized structural search-space lane should be opened around slice8 to test search-surface shape/width/duplicate-pressure hypotheses while the current objective/version/metric surface remains fixed

This packet does **not** authorize:

- setup
- config creation
- launch
- execution
- objective redesign
- incumbent comparison
- readiness
- promotion
- writeback
- any structural search-space design decision

Fail-closed interpretation:

> This document defines only the next bounded research question: whether a later separately
> governed structural search-space lane should be opened around slice8 after the negative
> bounded 2025 cross-regime result. This document does not open that lane, does not approve
> any structural search-space shape, and does not authorize setup, config creation,
> execution, objective redesign, comparison, readiness, promotion, writeback, or any
> runtime/config changes. The current objective/version/metric surface remains fixed unless
> a separate later packet explicitly reopens it.

## Upstream governed basis

This packet is downstream of the following already tracked documents:

- `docs/decisions/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- `docs/analysis/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_cross_regime_research_question_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_cross_regime_setup_only_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_cross_regime_launch_authorization_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_cross_regime_execution_outcome_signoff_summary_2026-03-26.md`

Carried-forward meaning from those documents:

1. the active lane remains RI-family-internal research only
2. slice8 remains the primary continuation surface inside that lane
3. slice9 remains secondary robustness context only
4. slice7 remains historical context only
5. comparison, readiness, promotion, and writeback remain outside the active lane
6. the bounded 2025 cross-regime replay answered negatively for the exact frozen slice8 tuple on that exact replay surface
7. if research continues, the next admissible governance question is whether structural search-space work should be considered before any separate objective-design reopening

## Why this question is next

The next bounded question is no longer whether the same frozen slice8 tuple should simply be replayed again.

That is because:

1. the bounded cross-regime replay already answered the exact-tuple falsification question on one authorized non-2024 surface
2. slice8 remains the cleanest current RI-family continuation surface by the already tracked search-process tie-breaker
3. earlier slice evidence already showed duplicate-pressure and narrow-surface concerns that are structural-search-surface questions rather than pure objective questions
4. reopening objective design now would widen scoring semantics before this packet's narrower question has been resolved while the current objective/version/metric surface remains fixed

This reasoning is lane-governance only.
It is not setup authority, launch authority, or design approval.

## Exact research question

The exact research question opened by this packet is:

- **Should the next separately governed RI-family continuation open one bounded structural search-space lane around slice8, after the negative bounded 2025 cross-regime result, to test whether a reshaped or widened search surface can produce a more robust RI-family candidate while the current objective/version/metric surface remains fixed?**

This packet opens that question only.
It does **not** answer it operationally.

This question does **not** ask:

- whether setup should begin now
- whether launch should occur now
- whether any specific search-space shape or axis set has already been approved
- whether objective v2 should be replaced now
- whether incumbent comparison should reopen
- whether readiness or promotion should open
- whether the negative bounded 2025 replay permanently invalidates RI or slice8-related research

## Admissible input surface

Only the following inputs are admissible inside this packet.

### 1. RI lane-governance anchors

- `docs/decisions/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- `docs/analysis/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_next_admissible_lane_decision_2026-03-26.md`

Allowed use:

- preserve the already-open RI research-lane boundary
- preserve slice8 as the primary continuation surface for the bounded question in this packet
- preserve slice9 and slice7 at their already bounded secondary/historical roles
- preserve that any continuation beyond this question requires separate later packets

### 2. Cross-regime negative outcome surface

- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_cross_regime_execution_outcome_signoff_summary_2026-03-26.md`
- `results/hparam_search/ri_slice8_cross_regime_oos_launch_20260326/run_meta.json`
- `results/hparam_search/ri_slice8_cross_regime_oos_launch_20260326/best_trial.json`

Allowed use:

- preserve that the exact frozen slice8 tuple has already been challenged on one bounded non-2024 surface
- preserve that this exact-tuple replay produced negative bounded evidence on that surface
- explain why repeating the same frozen tuple again is no longer the narrowest next question

Disallowed use:

- treating the negative bounded replay as a family-wide terminal verdict
- treating the negative bounded replay as objective-failure proof by itself
- treating the negative bounded replay as automatic authority to redesign search-space or objective

### 3. Search-surface cleanliness context

- `docs/analysis/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice7_execution_outcome_signoff_summary_2026-03-24.md`

Allowed use:

- preserve that duplicate ratio and search-surface cleanliness have already been tracked as research-process context
- preserve that slice8 remained the cleanest current continuation surface despite the later negative bounded cross-regime result on the exact frozen tuple
- preserve that duplicate-pressure and narrow-surface concerns are legitimate candidate motivations for a later structural question

Disallowed use:

- converting duplicate ratio into trading-performance proof
- claiming that any specific structural widening is already selected or approved here

### 4. Objective surface boundary

- the currently tracked RI research surface using score version `v2`

Allowed use:

- preserve that the current objective/version/metric surface remains fixed for this packet
- preserve that any objective-change lane is separate, later, and not opened here

Disallowed use:

- implying that objective v2 has failed by governance decision in this packet
- importing any new objective, metric, or ranking semantics into this packet

## Structural-search-space interpretation boundary

Inside this packet, `structural search-space` means only the following:

- a later separately governed RI-family lane
- potentially concerned with search-surface shape, width, duplicate-pressure, or structurally bounded parameter-neighborhood hypotheses
- while leaving the current objective/version/metric surface fixed unless separately reopened later

Inside this packet, `structural search-space` does **not** mean:

- a lane that is already opened
- a chosen axis list already exists
- a chosen parameter list already exists
- a config should be created now
- a launch should be authorized now
- objective redesign has begun

## Candidate structural themes remain undecided

This packet does **not** choose the structural intervention.

The only bounded statement allowed here is:

- if a later separate setup packet is ever proposed, it may ask whether a bounded structural search-space lane around slice8 should enter setup review while the current objective/version/metric surface remains fixed

This packet must **not** be read as saying:

- which parameters should be reopened
- how wide the search surface should be
- whether management axes, gating axes, or another structural seam should be preferred
- whether any search-space expansion should run now

## Inadmissible actions inside this packet

This packet does not allow any of the following:

- setup authorization
- launch authorization
- execution command authorization
- search-space design selection
- parameter-axis selection
- pass/fail threshold definition
- score-gate definition
- output-artifact requirement definition
- objective redesign
- incumbent comparison reopening
- readiness reopening
- promotion reopening
- writeback recommendation
- candidate advancement language that implies operational approval

## Next admissible governance action

If a later governance step is separately proposed and separately approved, one admissible next packet shape would be:

- one bounded setup-only packet asking whether a structural search-space lane around slice8 should enter setup review while the current objective/version/metric surface remains fixed

This document provides **no** authorization to start that setup step now.

If a later packet needs to specify:

- the exact structural seam to reopen
- the exact parameter axes or bounds
- the exact optimizer config surface
- the exact launch preconditions
- the exact output discipline

then that later packet must be treated as a separate governance step and not as an extension of this quick-path question packet.

## Bottom line

After the negative bounded 2025 cross-regime replay, the next bounded question is no longer another replay of the same frozen tuple.

The next bounded question is whether a later separately governed **structural search-space lane** should be opened around slice8 while keeping the current objective/version/metric surface fixed.

Within this packet:

- slice8 remains the primary surface for this bounded question
- slice9 remains supporting robustness context only
- slice7 remains historical context only
- the current objective/version/metric surface remains fixed
- any structural search-space design remains candidate-level only

Any setup, design, authorization, execution, comparison, readiness, promotion, writeback, or objective-change step would require a **separate future governance packet** and is not authorized by this document.
