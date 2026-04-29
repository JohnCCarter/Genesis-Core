# Regime Intelligence challenger family — slice8 structural search-space seam decision packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `decision-only / exact seam selected / no config or launch scope`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet is sensitive only in governance-signaling terms because it selects exactly one admissible structural seam for a later separate design/authorizing step, but it remains exactly one docs-only file with no runtime, config, schema, env, or high-sensitivity code changes.
- **Required Path:** `Quick`
- **Objective:** Decide exactly one admissible structural seam for any later separate design/authorizing step in the slice8 structural-search-space lane, while keeping the current objective/version/metric surface fixed and authorizing no config creation or launch.
- **Candidate:** `slice8 structural seam decision`
- **Base SHA:** `0b8ad72c`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Decision-only / non-authorizing`
- `No config materialization`
- `No search-space range or bounds decision`
- `No launch authorization`
- `No objective-change opening`
- `No comparison/readiness/promotion reopening`
- `No env/config semantics changes`

### Skill usage

- No repository skill is evidenced for this docs-only seam-decision packet.
- Guardrail surfaces may be cited only as future references for later separate authorizing work.
- Any future skill coverage for a later config/launch step remains `föreslagen` until implemented and verified.

### Scope

- **Scope IN:**
  - exactly one docs-only decision packet under `docs/governance/`
  - explicit chosen-seam and not-chosen-seam labels
  - explicit rationale for selecting the bounded management/override seam now
  - explicit statement that slice9 is used only as secondary management/override evidence around the slice8 backbone
  - explicit fail-closed statement that this packet still does not create config, choose ranges, authorize launch, or reopen objective design
- **Scope OUT:**
  - no source-code changes
  - no `tests/**`, `config/**`, or `results/**` changes
  - no config creation or config-path reservation
  - no parameter ranges or exact bounds
  - no launch authorization
  - no actual replay or Optuna execution
  - no objective-change opening
  - no incumbent comparison reopening
  - no readiness reopening
  - no promotion reopening
  - no writeback
  - no runtime/default/env/config-authority change
- **Expected changed files:** `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_seam_decision_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- exactly one seam must be chosen now and one seam must be not chosen now
- choosing the bounded management/override seam must not imply exact ranges, bounds, config design, config reservation, or launch approval
- not choosing the gating/selectivity seam now must remain present-state and non-permanent
- slice9 evidence must not be upgraded into anchor, readiness, promotion, or launch support
- objective/version/metric must remain explicitly fixed

### Stop Conditions

- any wording that selects ranges, bounds, sampler settings, config path, storage path, or run contract
- any wording that turns this packet into launch authorization or execution authorization
- any wording that reopens objective design, incumbent comparison, readiness, promotion, or writeback
- any wording that treats slice9 as a co-primary continuation surface or as anchor-grade evidence
- any wording that reads `not chosen now` as a permanent veto
- any need to modify files outside this one scoped packet

### Output required

- reviewable structural-seam decision packet
- explicit chosen-seam label
- explicit not-chosen-seam label
- explicit bounded rationale for the chosen seam
- explicit statement that config/ranges/launch remain out of scope

## Purpose

This packet answers one narrow question only:

- which exact structural seam is admissible for the next separate design/authorizing step inside the already-open slice8 structural-search-space lane?

This packet does **not**:

- choose parameter ranges or bounds
- create a config
- reserve a config path
- authorize launch
- execute a replay or Optuna run
- reopen objective design
- reopen comparison, readiness, promotion, or writeback

Fail-closed interpretation:

> This document selects only one admissible structural seam for a later separate design or
> authorizing step. It does not approve ranges, bounds, sampler choices, config creation,
> config-path reservation, launch, replay, Optuna execution, objective redesign, comparison,
> readiness, promotion, or writeback. The current objective/version/metric surface remains
> fixed and no run can begin from this packet alone.

## Governing basis

This packet is downstream of the following already tracked documents:

- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_research_question_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_structural_search_space_setup_only_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_cross_regime_execution_outcome_signoff_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice9_execution_outcome_signoff_summary_2026-03-26.md`
- `docs/analysis/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`

Carried-forward meaning from those documents:

1. the active lane remains RI-family-internal research only
2. slice8 remains the primary continuation surface for the current structural lane
3. slice9 remains secondary robustness context only
4. slice7 remains historical context only
5. the exact frozen slice8 tuple failed the bounded 2025 cross-regime replay
6. the current objective/version/metric surface remains fixed unless a separate later packet reopens it
7. the structural lane has setup-only status so far, with no config or launch authorization yet

## Seam options under decision

### Option 1 — bounded management/override seam

Meaning:

- use the slice8 backbone as the continued fixed reference surface
- treat the following reopened seam as the admissible target for a later separate design step:
  - `exit.max_hold_bars`
  - `exit.exit_conf_threshold`
  - `multi_timeframe.ltf_override_threshold`

Evidence basis:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice9_execution_outcome_signoff_summary_2026-03-26.md`

Interpretation boundary:

- this is a bounded management/override seam only
- this does not decide ranges, bounds, or config shape
- this does not decide whether a later authorizing packet will actually approve a run

### Option 2 — gating/selectivity seam

Meaning:

- treat the following slice8 search seam as the next seam to reopen again in a later separate design step:
  - `thresholds.entry_conf_overall`
  - `thresholds.regime_proba.balanced`
  - `gates.hysteresis_steps`
  - `gates.cooldown_bars`

Evidence basis:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice7_execution_outcome_signoff_summary_2026-03-24.md`

Interpretation boundary:

- this remains a legitimate structural candidate seam in general
- this packet decides only that it is **not chosen now**
- this packet does not permanently reject or forbid a later separately governed reopening of this seam

## Decision

### Chosen seam label

- `CHOSEN NOW — bounded management/override seam`

Exact seam selected now:

- `exit.max_hold_bars`
- `exit.exit_conf_threshold`
- `multi_timeframe.ltf_override_threshold`

### Not-chosen seam label

- `NOT CHOSEN NOW — gating/selectivity seam`

Exact seam not chosen now:

- `thresholds.entry_conf_overall`
- `thresholds.regime_proba.balanced`
- `gates.hysteresis_steps`
- `gates.cooldown_bars`

This is a present-state decision for this lane only.
It does **not** permanently veto or forbid a later separately governed reopening of the gating/selectivity seam.

## Why the bounded management/override seam is chosen now

The bounded management/override seam is chosen now for the following narrow governance reasons:

1. the exact frozen slice8 tuple has already been falsified on one bounded 2025 OOS surface, so a structural adjustment is now a legitimate next lane question
2. slice9 already provided governed evidence that the slice8 entry/gating backbone survives one nearby management/override perturbation without dropping below the incumbent same-head control on governed score
3. slice9 did so using a seam that is already concretely evidenced in tracked config and outcome documents, which makes it narrower and less speculative than immediately reopening the broader earlier slice8 gating/selectivity seam again
4. selecting the bounded management/override seam now keeps the current objective/version/metric surface fixed while moving from exact frozen tuple replay toward one already evidenced nearby structural surface

These reasons support seam selection only.
They do **not** support range selection, config creation, launch approval, or any promotion-grade claim.

## Why the gating/selectivity seam is not chosen now

The gating/selectivity seam is not chosen now for the following present-state reasons:

1. slice8 already reopened that seam in the current tracked RI-family continuation surface
2. the immediate next structural question is narrower if it uses the already evidenced nearby management/override surface rather than reopening the earlier slice8 search seam again first
3. not choosing this seam now preserves a one-seam-at-a-time governance discipline for the next separate design/authorizing step

This non-selection is temporary and bounded.
It is not a permanent rejection of the gating/selectivity seam.

## Allowed use of slice9 evidence in this packet

Slice9 is used here only as secondary evidence for bounded management/override robustness around the slice8 backbone.

Slice9 is **not** used here as:

- a co-primary continuation surface
- anchor approval
- readiness support
- promotion support
- launch support

## What this decision still does not authorize

This packet still does **not** authorize:

- exact parameter ranges or bounds
- sampler settings
- config creation
- config-path reservation
- storage-path reservation
- launch authorization
- replay or Optuna execution
- result-interpretation standards
- objective redesign
- incumbent comparison reopening
- readiness reopening
- promotion reopening
- writeback

## Next admissible step after this packet

If a later governance step is separately proposed and separately approved, the next admissible packet shape would be:

- one bounded design/authorizing packet that binds the chosen bounded management/override seam to an exact config surface, exact ranges, validator/preflight discipline, and a later separate launch decision if warranted

This document does **not** authorize that later step by itself.

## Bottom line

This packet selects exactly one structural seam now:

- **chosen now:** bounded management/override seam
- **not chosen now:** gating/selectivity seam

Within this packet:

- the chosen seam is limited to `exit.max_hold_bars`, `exit.exit_conf_threshold`, and `multi_timeframe.ltf_override_threshold`
- the objective/version/metric surface remains fixed
- slice9 remains secondary evidence only
- no ranges, bounds, config, or launch are approved

Any operational or config-bearing step beyond this would require a **separate future governance packet** and is not authorized here.
