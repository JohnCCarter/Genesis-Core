# Regime Intelligence challenger family — incumbent comparison prep packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Category: `obs`
Status: `comparison-prep only / no execution approval / no promotion approved`
Constraint: `NO BEHAVIOR CHANGE`

## Purpose

This document is a comparison-prep packet in `RESEARCH` mode.

It defines only the comparison surfaces, evidence requirements, and acceptance/rejection rules for a later governed incumbent-comparison step.

This document does **not** constitute:

- execution approval
- promotion recommendation
- champion replacement
- default/runtime change
- cutover decision
- champion writeback approval

## Scope IN / Scope OUT

### Scope IN

- define the next governed comparison-prep contract for the RI challenger-family line
- name the already selected RI lead research candidate surface
- define the primary comparator surface and background context surface
- define the evidence bundle and stop conditions required before any promotion-grade interpretation

### Scope OUT

- all runtime code
- all tests
- all config changes
- all result-artifact rewrites
- all champion-file changes
- all execution approval
- all promotion or cutover approval

## Upstream packets and decisions

This prep packet is downstream of the following already tracked decisions:

- `docs/decisions/regime_intelligence_optuna_challenger_family_anchor_decision_governance_review_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_candidate_definition_packet_2026-03-26.md`

Relevant upstream interpretation:

- the slice8-backed backbone is approved as **research anchor only**
- the slice8 full tuple is named as the **lead RI research candidate**
- slice9 is retained as **supporting robustness evidence** for the same backbone
- no promotion, champion replacement, default/runtime change, or cutover is approved

## Comparator definition

### RI surface named for later governed comparison

The RI side of the later governed comparison is:

- the **slice8 full tuple**, but only as the named **lead RI research candidate for governed comparison prep**

This naming does **not** imply:

- promotion readiness
- champion superiority
- champion replacement approval
- production-readiness approval

### Primary comparator surface

The primary governed comparator surface for a later packet is:

- the incumbent **same-head control** reference surface

Current tracked reference artifact:

- `results/backtests/tBTCUSD_3h_20260324_170603.json`

This primary comparator should remain the actual decision comparison surface unless a later packet explicitly broadens scope.

### Background context surface only

The current bootstrap champion remains background context only in this prep packet:

- `config/strategy/champions/tBTCUSD_3h.json`

This file may be cited to explain current operational state and bootstrap lineage.

It is **not** opened here as a second decision comparator surface.

## RI candidate surface carried forward

### Named RI lead research candidate

The RI candidate surface named for later governed comparison prep is the slice8 full tuple:

- `thresholds.entry_conf_overall=0.27`
- `thresholds.regime_proba.balanced=0.36`
- `gates.hysteresis_steps=4`
- `gates.cooldown_bars=1`
- `exit.max_hold_bars=8`
- `exit.exit_conf_threshold=0.42`
- `multi_timeframe.ltf_override_threshold=0.40`

Supporting family identity carried by the slice8 YAML remains:

- `strategy_family=ri`
- `multi_timeframe.regime_intelligence.enabled=true`
- `multi_timeframe.regime_intelligence.version=v2`
- `multi_timeframe.regime_intelligence.authority_mode=regime_module`
- `multi_timeframe.regime_intelligence.clarity_score.enabled=false`
- `multi_timeframe.regime_intelligence.risk_state.enabled=true`

### Role of slice9 in this prep packet

Slice9 is treated in this packet only as supporting robustness evidence for the slice8-based research-anchor candidacy.

Slice9 does **not**:

- open a separate promotion track
- function as an alternate lead candidate in this document
- weaken the choice of slice8 as the named RI prep surface

Its approved role here is narrower:

- show that the slice8-backed entry/gating backbone preserved the same validation high-water line on a nearby management tuple
- support the claim that the backbone is sufficiently stable to justify a later governed incumbent-comparison packet

## Required evidence bundle for a later governed comparison

A later comparison packet should not proceed unless it attaches or cites all of the following:

### RI evidence

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice8_execution_outcome_signoff_summary_2026-03-24.md`
- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice9_20260326.json`
- `docs/decisions/regime_intelligence_optuna_challenger_family_slice9_execution_outcome_signoff_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence_optuna_challenger_family_candidate_definition_packet_2026-03-26.md`

### Incumbent evidence

- `results/backtests/tBTCUSD_3h_20260324_170603.json`

### Operational context evidence

- `config/strategy/champions/tBTCUSD_3h.json`

### Governance baseline

- `docs/decisions/regime_intelligence_optuna_challenger_family_anchor_decision_governance_review_summary_2026-03-26.md`

## Required comparison dimensions

A later governed comparison packet should define the candidate-vs-incumbent judgment using explicit dimensions such as:

- validation score
- return
- profit factor
- max drawdown
- trade count
- any additional constraint outcome deemed mandatory by that later packet

The later packet must state whether those dimensions are:

- hard gates,
- advisory context, or
- tie-breakers only.

## Acceptance / rejection contract for the later packet

### Minimum acceptance rule for opening promotion-grade discussion

A later governed comparison packet should only be allowed to recommend opening a promotion-grade discussion if it can demonstrate all of the following explicitly:

1. the named RI lead research candidate was evaluated under the declared comparison contract
2. the incumbent same-head control was evaluated under the declared comparison contract
3. the outcome is written against predeclared comparison dimensions
4. the packet states whether the result is:
   - candidate stronger,
   - candidate weaker, or
   - inconclusive
5. the packet separately states whether promotion/writeback is in scope or still out of scope

### Rejection / stop conditions

A later comparison packet should stop without promotion-grade interpretation if any of the following occurs:

- comparison surfaces are changed without explicit scope reopening
- slice9 is silently upgraded from supporting evidence to co-primary candidate
- bootstrap champion context is silently turned into a second decision comparator without explicit packet language
- metadata quirk disclosure disappears
- the packet implies runtime/default change from research evidence alone

## Residual cautions that remain open

### 1. Research plateau replication is not promotion proof

The current RI line shows repeated preservation of the `0.26974911658712664` validation high-water line.

That is good research evidence.

It is not by itself a promotion verdict.

### 2. Metadata quirk must remain disclosed

Some RI run artifacts still show `merged_config.strategy_family=legacy`.

This prep packet does not resolve that issue.

Any later comparison or promotion-grade packet must keep the issue disclosed.

### 3. No skill coverage is claimed by this packet

This is a trivial docs-only quick-path artifact.

No specialized repository skill is claimed as process coverage by this document.

## What this packet allows and does not allow

### Allowed next step

The allowed next step after this prep packet is:

- prepare a later governed comparison packet that evaluates the named RI lead research candidate against the incumbent same-head control under explicit rules

### Not allowed by this packet

This document does **not** allow:

- launching execution by itself
- declaring the RI line a new champion
- writing back a new champion file
- treating slice9 as an alternate lead without explicit scope reopening
- treating the bootstrap champion context as an additional decision comparator without explicit packet language

## Bottom line

The RI line is now prepared for a cleaner next governed step.

That next step is **not** promotion yet.

It is a later governed incumbent-comparison packet with:

- slice8 full tuple as the named RI lead research candidate surface,
- slice9 as supporting robustness evidence only, and
- incumbent same-head control as the primary comparator surface.
