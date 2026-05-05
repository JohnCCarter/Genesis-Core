# Regime Intelligence challenger family — slice8 follow-up research lane packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical lane-selection snapshot / superseded by later question chain / no active lane authority`

> Current status note:
>
> - [HISTORICAL 2026-05-05] This file records an earlier slice8-first lane selection on `feature/ri-role-map-implementation-2026-03-24`, not an active lane authority on `feature/next-slice-2026-05-05`.
> - Its forward role was later narrowed through the downstream cross-regime and structural-search-space question chain.
> - Preserve this file as historical lane-selection provenance only.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet narrows the next RI-family-internal research continuation surface after the ranked research summary, but must remain docs-only and must not reopen comparison, readiness, promotion, setup authorization, or launch authorization.
- **Required Path:** `Quick`
- **Objective:** Define one bounded slice8-first RI follow-up research lane after the ranked research summary, including the admissible continuation surface, the allowed role of slice9 and slice7, and the fail-closed boundary around any later separately governed setup proposal.
- **Candidate:** `slice8-first RI follow-up research lane`
- **Base SHA:** `c00900fc`

### Scope

- **Scope IN:** one docs-only lane packet under `docs/governance/`; explicit slice8-first follow-up framing; admissible inputs limited to already tracked RI-family research artifacts; explicit statement that slice9 is secondary robustness context only; explicit statement that slice7 is historical context only; explicit next-step wording constrained to future separate proposal/approval only.
- **Scope OUT:** no source-code changes, no config changes, no runtime/default changes, no new run execution, no setup authorization, no launch authorization, no incumbent comparison reopening, no readiness reopening, no promotion reopening, no writeback authority, no new evidence class.
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_followup_research_lane_packet_2026-03-26.md`
- **Max files touched:** `1`

### Skill usage

- No repository skill is evidenced for this docs-only governance packet.
- This packet uses manual governance review only.
- Any future skill coverage for this packet shape remains `föreslagen` until implemented and verified.

### Gates required

For this packet itself:

- markdown/file validation only

Interpretation discipline that must remain true:

- the follow-up lane must remain RI-family-internal research only
- slice8 must remain the only preferred continuation surface named by this packet
- slice9 may appear only as secondary robustness context and must not widen the continuation surface
- slice7 may appear only as historical context and must not be restored as an active continuation surface
- no sentence may authorize setup, execution, comparison, readiness, promotion, or writeback
- no sentence may create a new evidence class by implication

### Stop Conditions

- any wording that makes slice9 a co-preferred continuation surface or backup execution candidate
- any wording that restores slice7 as an active next-lane surface
- any wording that turns this packet into setup authorization or launch authorization
- any wording that reopens incumbent comparison, readiness, promotion, or writeback
- any wording that treats process cleanliness as trading-performance proof

### Output required

- reviewable slice8-first follow-up research lane packet
- explicit admissible input surface
- explicit inadmissible action surface
- explicit slice9 secondary-context rule
- explicit slice7 historical-context rule
- explicit next-governance-step wording that remains future-separate and fail-closed

## Purpose

This packet narrows the next **RI-family-internal research continuation lane** after the ranked research summary.

Its purpose is to preserve the ranked-summary conclusion that:

- slice7, slice8, and slice9 are tied on tracked validation outcome
- slice8 is the cleanest current research continuation surface by duplicate-ratio tie-breaker

This packet therefore opens only a **slice8-first follow-up research lane**.

This packet does **not** authorize:

- setup
- execution
- incumbent comparison
- readiness
- promotion
- writeback

## Governing basis

This packet is downstream of the following already tracked documents:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_next_admissible_lane_decision_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`

Carried-forward meaning from those documents:

1. the active lane remains RI-family-internal research only
2. incumbent comparison, readiness, and promotion remain outside the active lane
3. slice7, slice8, and slice9 are tied on tracked validation outcome
4. slice8 is preferred only as a research continuation surface because its process surface is cleaner than slice9 and far cleaner than slice7
5. slice9 may support robustness interpretation only and must not expand the continuation surface

## Follow-up research objective

The objective of this follow-up lane is intentionally narrow:

- keep `slice8` as the sole preferred continuation surface for the next RI-family-internal follow-up framing
- retain `slice9` only as corroborating robustness context at a non-slice8 management tuple
- retain `slice7` only as already-informative historical context
- identify the next admissible governance action only at the level of a possible future separate setup proposal

This objective does **not** ask:

- whether slice8 is superior to the incumbent
- whether slice9 should become a parallel next lane
- whether slice7 should be reopened as an active continuation surface
- whether execution should be authorized now
- whether readiness or promotion should open

## Admissible input surface

Only the following inputs are admissible inside this packet.

### 1. RI lane-governance anchors

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_next_admissible_lane_decision_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`

Allowed use:

- preserve the already-open research-lane boundary
- preserve the ranked-summary conclusion without re-ranking outside that summary
- preserve the fail-closed separation from comparison, readiness, and promotion

### 2. Slice8 continuation anchor

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- `results/hparam_search/ri_slice8_launch_20260326/run_meta.json`
- `results/hparam_search/ri_slice8_launch_20260326/validation/trial_001.json`

Allowed use:

- identify the current preferred RI follow-up surface
- preserve the exact surface that already produced the cleanest tracked duplicate ratio among the tied RI contenders
- frame a future separate setup proposal only around the slice8-follow-up surface

### 3. Slice9 secondary robustness context only

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice9_20260326.json`

Allowed use:

- retain evidence that a non-slice8 management tuple also reached the same tracked validation outcome
- support the bounded statement that slice9 remains corroborating robustness context only

Disallowed use:

- expanding the preferred continuation surface beyond slice8
- defining slice9 as co-preferred, backup, parallel, or separately advanced by this packet

### 4. Slice7 historical context only

Slice7 may be referenced only through the already tracked ranked research summary and prior RI research history.

Allowed use:

- preserve that slice7 is already informative history inside the tied validation cluster

Disallowed use:

- restoring slice7 as an active follow-up lane
- widening this packet into a multi-surface continuation decision

## Exact continuation meaning of this lane

The continuation meaning of this lane is:

- `slice8 first`

That phrase means only the following:

- if a later RI-only follow-up is separately proposed and separately approved, the next bounded setup framing should be anchored to the existing slice8 surface first

That phrase does **not** mean:

- slice8 is authorized for execution now
- slice8 has won an incumbent comparison
- slice9 is also selected as a concurrent continuation surface
- slice7 has been reopened as a next-step candidate
- readiness or promotion may open

## Inadmissible actions inside this lane

This packet does not allow any of the following:

- launch authorization
- setup authorization
- new execution contract
- incumbent comparison reopening
- same-head ranking with incumbent
- readiness reopening
- promotion reopening
- writeback recommendation
- candidate advancement language that implies approval for execution

## Next admissible governance action

The next admissible governance action after this packet, if separately proposed and separately approved later, would be:

- one bounded `slice8-first` follow-up setup packet inside the already-open RI-family research track

This document provides **no** authorization to start that setup step now.

This document also provides **no** authorization for:

- execution
- launch approval
- comparison interpretation
- readiness interpretation
- promotion interpretation

## Bottom line

After the ranked RI-family research summary, the follow-up research lane is now narrowed to:

- **slice8-first follow-up framing only**

Within this packet:

- slice8 is the sole preferred continuation surface
- slice9 is retained only as secondary robustness context
- slice7 is retained only as historical context

Any later setup or execution step would require a **separate future governance packet** and is not authorized by this document.
