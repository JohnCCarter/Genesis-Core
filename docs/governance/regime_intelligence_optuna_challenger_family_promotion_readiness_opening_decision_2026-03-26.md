# Regime Intelligence challenger family — promotion-readiness opening decision

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `decision-summary / APPROVE_OPENING_DISCUSSION_ONLY / no promotion approved`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet decides whether the current RI evidence is sufficient to open a promotion-readiness discussion, but it does not approve promotion, champion replacement, writeback, or runtime/default change
- **Required Path:** `Quick`
- **Objective:** Decide whether the tracked RI evidence line is sufficient to open a promotion-readiness discussion for the slice8 lead research candidate while explicitly keeping all actual promotion decisions out of scope.
- **Candidate:** `slice8 full tuple as lead RI research candidate`
- **Base SHA:** `2f00c80c`

### Scope

- **Scope IN:** docs-only governance interpretation of whether a promotion-readiness discussion may now be opened; explicit citation of the governing 2026-03-26 RI packet chain; explicit statement of what remains mandatory before any promotion decision.
- **Scope OUT:** no source-code changes, no config changes, no tests, no runtime materialization, no new comparison tooling, no incumbent-score recomputation, no new canonical comparison/materialization contract, no promotion approval, no champion replacement, no writeback, no runtime/default change.
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_challenger_family_promotion_readiness_opening_decision_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For decision discipline inside this packet:

- cite only already tracked RI governance and evidence artifacts
- keep the incumbent comparison explicitly citation-based on the governed non-runtime surface only
- state near the top that this is **not** a promotion decision
- include a mandatory-before-any-promotion-decision list

### Stop Conditions

- any wording that implies promotion is now approved
- any wording that implies runtime materialization is no longer blocked
- any wording that treats the non-runtime comparison surface as a canonical comparison contract
- any wording that upgrades this packet into writeback or champion replacement authority
- any wording that suppresses the unresolved metadata quirk or the runtime-materialization blocker

### Output required

- reviewable opening-decision packet
- explicit decision label
- explicit evidence basis
- explicit mandatory-before-promotion list

## This is not a promotion decision

This packet does **not** approve:

- promotion
- champion replacement
- champion writeback
- runtime materialization
- runtime/default change
- cutover
- canonical RI comparison/materialization authority

Its only job is to decide whether the repository now has enough tracked RI evidence to **open a promotion-readiness discussion**.

## Decision label

The decision recorded by this packet is:

- `APPROVE_OPENING_DISCUSSION_ONLY`

## Meaning of that label

This label means only the following:

- the current tracked RI evidence line is now strong enough to justify opening a separate promotion-readiness discussion for the slice8 lead research candidate
- that discussion may now be framed using the existing tracked candidate-definition and comparison packets
- the discussion remains reviewable, bounded, and explicitly non-authoritative unless a later packet widens scope

This label does **not** mean:

- promotion is approved
- the candidate is a new champion
- writeback is approved
- runtime superiority is proven
- the runtime-materialization blocker is resolved
- the repository now has a canonical new RI comparison contract

## Governing evidence basis

This decision is downstream of the following tracked RI governance chain:

- `docs/governance/regime_intelligence_optuna_challenger_family_anchor_decision_governance_review_summary_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_candidate_definition_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_incumbent_comparison_prep_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_incumbent_comparison_execution_blocker_summary_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_comparison_input_surface_decision_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_non_runtime_comparison_surface_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_non_runtime_comparison_summary_2026-03-26.md`

Additional cited evidence context:

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json`
- `results/hparam_search/run_20260324_174006/validation/trial_001.json`
- `results/backtests/tBTCUSD_3h_20260324_170603.json`

## Why discussion may now open

A promotion-readiness discussion may now open because the repository has a coherent, bounded, and already governed evidence line that is stronger than it was before the March 26 packet chain.

### 1. The candidate is already named

The slice8 full tuple is not a vague challenger family anymore.

It is already the explicitly named **lead RI research candidate** in tracked governance.

That matters because promotion-readiness discussion should not open around an unnamed or drifting candidate surface.

### 2. The candidate now has a governed comparison result

The repository now contains a tracked comparison-only packet that applies the approved slice8-specific non-runtime surface and records the bounded outcome label:

- `candidate stronger on the mapped non-runtime surface`

That matters because the current question is no longer whether the RI line is merely interesting.

The current question is whether the evidence line is mature enough to justify structured promotion-readiness discussion.

### 3. The evidence remains bounded rather than inflated

The current comparison result is governance-safer than an improvised recommendation because it was explicitly bounded to:

- a slice8-specific surface
- a tracked artifact chain
- citation-only incumbent score use
- explicit prohibition on runtime materialization and synthetic artifact homogenization

That matters because opening a discussion is only justified when the evidence surface is controlled enough to prevent accidental promotion-by-drift.

### 4. The repository already distinguishes discussion from approval

The current RI packet chain repeatedly distinguishes:

- research anchor
- lead candidate definition
- comparison prep
- blocked execution path
- non-runtime comparison surface
- comparison-only outcome

This layered structure means an opening-discussion packet can stay safely below approval level without blurring authority boundaries.

## Why this is still below promotion approval

The evidence line is now discussion-worthy.

It is **not** promotion-complete.

### 1. Runtime materialization remains blocked

The execution blocker summary still stands.

Therefore the repository does not yet have an approved runtime-complete comparison path for the slice8 candidate versus the incumbent.

### 2. The comparison surface is explicitly non-runtime only

The existing comparison summary is strong enough to support structured discussion.

It is not a substitute for a canonical runtime comparison contract.

### 3. The metadata quirk remains unresolved

Candidate-adjacent artifacts still disclose `merged_config.strategy_family=legacy` as an open metadata quirk.

This packet does not resolve that issue and does not downgrade it to irrelevant.

### 4. Writeback authority remains unopened

Nothing in the current packet chain authorizes writeback into:

- `config/strategy/champions/tBTCUSD_3h.json`

That authority remains out of scope.

## Mandatory before any promotion decision

Before any later packet may recommend or approve promotion, at least the following must be addressed explicitly:

1. **Runtime materialization disposition**
   - either the blocker is resolved through an approved governed path,
   - or governance explicitly states why a promotion-grade decision may proceed without that path

2. **Metadata quirk disposition**
   - the `merged_config.strategy_family=legacy` disclosure must be resolved or explicitly dispositioned in a later packet

3. **Promotion scope declaration**
   - the later packet must say explicitly whether promotion, writeback, champion replacement, or runtime/default change is actually in scope

4. **Decision contract clarity**
   - the later packet must state the exact acceptance/rejection rule for any promotion claim instead of relying on general narrative momentum

5. **Writeback authority**
   - no file replacement or champion update may occur without an explicit later packet that opens and governs that step

## Precedent framing only

The repository contains earlier recommendation-style documents such as:

- `docs/analysis/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`
- `docs/analysis/tBTCUSD_3h_champion_promotion_recommendation_2026-03-13.md`

Those documents may be used as **precedent framing only**.

They do not override the March 26 RI governance chain and they do not by themselves authorize promotion here.

## Interpretation boundary

### Approved by this packet

This packet approves only the following interpretation:

- the slice8 RI evidence line is now strong enough to justify a structured promotion-readiness discussion
- that discussion must remain subordinate to the already tracked March 26 governance chain
- a later packet must still decide whether promotion is actually in scope and whether the remaining blockers are acceptable or resolved

### Not approved by this packet

This packet does **not** approve:

- promotion readiness itself
- promotion
- champion replacement
- writeback
- runtime/default change
- cutover
- a new canonical RI comparison/materialization contract

## Bottom line

The current RI evidence line has crossed an important threshold:

- not the threshold for promotion approval,
- but the threshold for **opening a promotion-readiness discussion**.

That is why the correct decision label here is:

- `APPROVE_OPENING_DISCUSSION_ONLY`

Anything stronger than that would exceed the evidence and authority boundaries currently established in the repository.
