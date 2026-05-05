# Regime Intelligence challenger family — promotion-readiness assessment

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `assessment-only / NOT_READY_FOR_PROMOTION_DECISION_YET / no promotion approved`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet assesses whether the repository is ready to open a promotion-decision packet for the slice8 lead research candidate, but it does not approve promotion, writeback, or runtime/default change
- **Required Path:** `Quick`
- **Objective:** Decide whether the current tracked RI evidence is sufficient to open a promotion-decision packet now, rather than only a promotion-readiness discussion.
- **Candidate:** `slice8 full tuple as lead RI research candidate`
- **Base SHA:** `0e395ee4`

### Scope

- **Scope IN:** docs-only readiness assessment; explicit readiness criteria; explicit blocker table with closure conditions; explicit statement of the next allowed step below promotion approval.
- **Scope OUT:** no source-code changes, no config changes, no tests, no runtime materialization, no new comparison tooling, no promotion approval, no champion replacement, no writeback, no runtime/default change, no new canonical comparison/materialization contract.
- **Expected changed files:** `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_promotion_readiness_assessment_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- cite only already tracked governance and evidence artifacts
- keep all incumbent comparison references explicitly subordinate to the governed non-runtime surface
- state that this is a bounded `not yet` readiness verdict, not a rejection of RI overall
- include explicit closure conditions for each blocker

### Stop Conditions

- any wording that implies the RI line is being rejected overall
- any wording that implies promotion is now denied permanently
- any wording that implies runtime materialization is no longer relevant
- any wording that turns this packet into a hidden promotion denial or hidden writeback decision
- any wording that opens a promotion-decision packet anyway despite the listed blockers

### Output required

- reviewable readiness assessment
- explicit decision label
- readiness criteria table
- blocker table with closure conditions
- explicit next allowed step

## This is not a promotion decision

This packet does **not** approve:

- promotion
- promotion readiness itself
- champion replacement
- champion writeback
- runtime materialization
- runtime/default change
- cutover
- canonical RI comparison/materialization authority

It only answers a narrower question:

> Is the repository ready **right now** to open a promotion-decision packet for the slice8 lead research candidate?

## Decision label

The decision recorded by this packet is:

- `NOT_READY_FOR_PROMOTION_DECISION_YET`

## Meaning of that label

This label means only the following:

- the RI evidence line is strong enough for structured discussion,
- but not yet strong or closed enough to open a promotion-decision packet now,
- because the current blocker set is still materially active.

This label does **not** mean:

- the RI candidate has failed
- the RI family should be abandoned
- the existing research-anchor or lead-candidate decisions are withdrawn
- the non-runtime comparison result is invalid
- promotion can never be revisited

## Governing evidence basis

This assessment is downstream of the following tracked packets:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_anchor_decision_governance_review_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_candidate_definition_packet_2026-03-26.md`
- `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_incumbent_comparison_execution_blocker_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_non_runtime_comparison_surface_packet_2026-03-26.md`
- `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_non_runtime_comparison_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_promotion_readiness_opening_decision_2026-03-26.md`

Precedent framing only:

- `docs/analysis/regime_intelligence/core/regime_intelligence_cutover_readiness_2026-03-17.md`

Supporting tracked evidence context:

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json`
- `results/hparam_search/run_20260324_174006/validation/trial_001.json`
- `results/backtests/tBTCUSD_3h_20260324_170603.json`

## Current readiness snapshot

| Dimension | Current status | Why it matters |
| --- | --- | --- |
| Lead candidate identity | Ready | Slice8 is already named and bounded in tracked governance |
| Discussion threshold | Ready | Opening-discussion decision already exists |
| Comparison evidence | Partial | Candidate is stronger on the mapped non-runtime surface, but that surface is deliberately limited |
| Runtime comparison path | Not ready | Runtime materialization remains blocked |
| Metadata disposition | Not ready | `merged_config.strategy_family=legacy` quirk remains unresolved or undispositioned |
| Writeback authority | Not ready | No later packet has opened champion update authority |
| Promotion-decision contract | Not ready | No packet yet defines a promotion-scope acceptance/rejection contract under resolved blockers |

## Why the answer is not ready yet

The repository has crossed the threshold for discussion.

It has **not** crossed the threshold for a promotion-decision packet.

### 1. Discussion opening is still below approval level

The current packet chain explicitly distinguishes:

- research anchor
- lead candidate definition
- non-runtime comparison
- opening-discussion decision

That layered structure is useful, but it also means the repository has not yet promoted itself to a decision-ready state by narration alone.

### 2. Runtime materialization remains a live blocker

The current execution blocker summary records that the intended runtime-materialization path is still blocked.

As long as that blocker remains active and undispositioned, the repository lacks a runtime-complete candidate-vs-incumbent comparison path.

### 3. The comparison result is real but bounded

The repository now has a governed comparison result:

- `candidate stronger on the mapped non-runtime surface`

That result is meaningful.

It is also deliberately bounded to a slice8-specific non-runtime artifact-matrix surface.

That means it is not yet sufficient by itself to justify opening a full promotion-decision packet.

### 4. Metadata quirk still needs disposition

Candidate-adjacent artifacts still disclose `merged_config.strategy_family=legacy` as an unresolved metadata quirk.

Even if the quirk ultimately proves non-blocking, a promotion-decision packet should not open while the quirk remains merely acknowledged rather than dispositioned.

### 5. Writeback authority is still closed

Nothing in the current March 26 packet chain authorizes updating:

- `config/strategy/champions/tBTCUSD_3h.json`

That does not prevent future promotion work.

It does mean the repo is still one governance step short of a real promotion-decision surface.

## Readiness criteria for a future promotion-decision packet

A future promotion-decision packet should open only if all of the following are satisfied explicitly:

1. the runtime-materialization blocker is resolved or explicitly dispositioned by governance
2. the metadata quirk is resolved or explicitly dispositioned by governance
3. the intended promotion scope is declared up front
4. the exact acceptance/rejection contract is declared up front
5. writeback authority is explicitly opened if champion update is in scope

## Current blocker table

| Blocker | Current state | Upstream basis | Closure condition |
| --- | --- | --- | --- |
| Runtime materialization blocker | Open | `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_incumbent_comparison_execution_blocker_summary_2026-03-26.md` | resolved by an approved governed path, or explicitly dispositioned as acceptable for later promotion-grade reasoning |
| Non-runtime-only comparison surface | Open as a scope limit | `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_non_runtime_comparison_surface_packet_2026-03-26.md` | later packet explicitly defines why promotion-grade reasoning can or cannot proceed beyond this limited surface |
| Metadata quirk (`strategy_family=legacy`) | Open | `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_non_runtime_comparison_summary_2026-03-26.md` | resolved technically or dispositioned explicitly in a later governance packet |
| Writeback authority closed | Open | `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_promotion_readiness_opening_decision_2026-03-26.md` | later packet explicitly opens and governs champion update authority if needed |
| Promotion decision contract absent | Open | current packet chain as a whole | later packet declares the exact promotion-decision acceptance/rejection rule |

## What is already strong enough

To avoid turning this into a hidden rejection of RI overall, the following points remain affirmed:

- the slice8-backed backbone remains the approved research anchor
- slice8 remains the lead RI research candidate
- the candidate is stronger on the mapped non-runtime surface
- the evidence line is strong enough to justify discussion

Those points remain true.

They are simply not enough, yet, for a promotion-decision packet.

## Next allowed step

The next allowed step after this assessment is **not** a promotion-decision packet.

The next allowed step is one of the following bounded actions:

1. a blocker-resolution packet that explicitly dispositions runtime-materialization and/or metadata-quirk status, or
2. a narrowly scoped supplementary evidence packet that clarifies whether promotion-grade reasoning can proceed despite the current non-runtime-only surface limit.

## Not allowed by this packet

This packet does **not** allow:

- opening a promotion-decision packet immediately
- champion replacement
- writeback into `config/strategy/champions/tBTCUSD_3h.json`
- runtime/default change
- treating `NOT_READY_FOR_PROMOTION_DECISION_YET` as a permanent rejection of RI work

## Bottom line

The RI line has now reached a mature governance posture for discussion, but not yet for decision.

That is why the correct readiness verdict is:

- `NOT_READY_FOR_PROMOTION_DECISION_YET`

This is a bounded `not yet` judgment.

It is not a rejection of the candidate, the research-anchor line, or the possibility of future promotion.
