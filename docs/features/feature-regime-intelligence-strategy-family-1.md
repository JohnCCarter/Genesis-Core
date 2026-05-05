---
goal: Formalize regime intelligence as a separate strategy family for tBTCUSD 3h research and candidate evaluation
version: 1
date_created: 2026-03-18
last_updated: 2026-03-18
owner: fa06662
status: "Archived historical design"
tags:
  - feature
  - regime
  - intelligence
  - strategy-family
  - research
  - candidate
---

# Introduction

![Status: Historical](https://img.shields.io/badge/status-Historical-lightgrey)

> [ARCHIVED 2026-05-05] This RI strategy-family document is not an active design lane on `feature/next-slice-2026-05-05`.
> Preserve it as historical decision-framing context only; current live anchors belong to `GENESIS_WORKING_CONTRACT.md` plus the later RI policy-router and governed RI follow-up docs.

Formalize Regime Intelligence (RI) as a **separate strategy family** for `tBTCUSD_3h`, rather than as a thin overlay or migration patch on the current incumbent champion. This document defines the family boundary, the minimum RI baseline, classification rules for future candidates, integration notes for research/optimizer workflows, and the promotion implications of treating RI as its own topology.

This is a design and decision-framing artifact only. It does **not** approve promotion, runtime-default changes, champion replacement, or family merging.

## 1. Requirements & Constraints

- **REQ-001**: The current `config/strategy/champions/tBTCUSD_3h.json` remains the incumbent control baseline until a governed challenger beats it on the approved comparison path.
- **REQ-002**: RI must be treated as a separate strategy family when reasoning about search-space design, candidate comparison, and promotion readiness.
- **REQ-003**: Future RI research must compete against the incumbent champion as a full challenger candidate, not as a partial overlay on the incumbent champion surface.
- **REQ-003A**: Legacy and RI challenger work must run as separate optimizer/backtest tracks; they must not be collapsed into a single mixed-family Optuna study.
- **REQ-004**: The RI family definition must be anchored in observed evidence from governed slice-1, slice-2, and slice-3 artifacts.
- **REQ-005**: The minimum RI baseline must capture the smallest evidence-backed compatibility cluster required for an RI candidate to be considered part of the RI family.
- **REQ-006**: Classification rules must distinguish between:
  - legacy / incumbent control surfaces
  - RI family candidates
  - invalid hybrid overlays that should not be interpreted as valid RI promotion candidates
- **REQ-007**: The document must preserve explicit separation between research classification, challenger development, and any later promotion decision.
- **CON-001**: No changes to `src/**`, `tests/**`, runtime defaults, champion files, or optimizer behavior are allowed in this slice.
- **CON-002**: This document must not redefine the incumbent champion as RI-compatible without new evidence.
- **CON-003**: This document must not imply that `authority_mode = regime_module` alone is sufficient to classify a surface as a valid RI candidate.
- **CON-003A**: This document must not allow "RI overlaid on top of the incumbent champion" to be treated as the default RI research path or as a valid promotion candidate shape.
- **CON-004**: This document must not weaken the existing train/validate/blind discipline or allow blind-window retuning.

## 2. Strategy Family Definitions

### 2.1 Legacy / incumbent family

The **legacy / incumbent family** is the currently active champion topology represented by `config/strategy/champions/tBTCUSD_3h.json` and by direct control replays that preserve its native decision surface.

Family traits observed in the incumbent control path include:

- native champion threshold family
- `thresholds.signal_adaptation.atr_period = 28`
- gating cadence `hysteresis_steps = 2`, `cooldown_bars = 0`
- incumbent-compatible HTF/LTF Fib entry surface
- incumbent-calibrated LTF override policy
- direct validation evidence that the control surface still trades and scores positively

This family remains the active benchmark and control surface for all RI challenger work.

### 2.2 Regime Intelligence family

The **Regime Intelligence family** is a separate strategy topology whose entry/decision surface is built around the RI authority path and its compatible calibration cluster. It is not defined by a single parameter toggle. It is defined by a small set of mutually compatible family traits that were repeatedly present in the RI-positive challenger path.

The RI family is therefore a **candidate family**, not an incumbent overlay mode.

### 2.3 Invalid hybrid overlay

An **invalid hybrid overlay** is a configuration that attempts to preserve the incumbent champion surface while applying RI authority or partial RI components without also adopting the minimum RI-compatible baseline.

Current evidence shows that the most important example is:

- incumbent champion surface + `authority_mode = regime_module`

This hybrid should not be treated as a valid RI promotion candidate because the observed result was a zero-trade collapse, which indicates topology incompatibility rather than simple under-tuning.

## 3. Evidence Basis

The family definition in this document is grounded in the following evidence:

- `docs/analysis/regime_intelligence/core/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `docs/analysis/recommendations/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`
- `docs/features/feature-ri-optuna-train-validate-blind-1.md`
- `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice3_2026-03-18.md`
- `results/hparam_search/run_20260318_112046/*`
- `results/hparam_search/run_20260318_131831/*`
- `results/hparam_search/run_20260318_134535/*`
- incumbent control replays and RI challenger replays referenced by the above analysis artifacts

Summary of the evidence:

1. The incumbent champion remains the best current validated candidate on the governed validation comparison.
2. The RI challenger family is real, tradable, and coherent, but not yet promotable.
3. The incumbent champion does not survive a direct RI authority overlay.
4. The smallest evidence-backed RI compatibility unit is a cluster, not a single flag.

## 4. RI_BASELINE

`RI_BASELINE` is the minimum evidence-backed compatibility surface required to treat a candidate as part of the RI family.

The validated reference anchor for `RI_BASELINE` is the slice-1 leader family represented by `results/hparam_search/run_20260318_112046/validation/trial_001.json` and its equivalent `trial_002` / `trial_005` family members.

### 4.1 Required family identity

The following fields define the RI authority identity:

- `multi_timeframe.regime_intelligence.enabled = true`
- `multi_timeframe.regime_intelligence.version = "v2"`
- `multi_timeframe.regime_intelligence.authority_mode = "regime_module"`

### 4.2 Required compatibility cluster

The current evidence supports the following cluster as the minimum RI-compatible baseline:

1. **RI-native threshold family**
   - the threshold surface must be derived from an RI challenger path rather than copied unchanged from the incumbent champion family
2. **ATR adaptation period**
   - `thresholds.signal_adaptation.atr_period = 14`
3. **RI-family gating cadence**
   - `gates.hysteresis_steps = 3`
   - `gates.cooldown_bars = 2`
4. **Compatibility stance for clarity and risk-state**
   - default compatibility stance: `clarity_score.enabled = false`
   - `risk_state.enabled = true` is the currently validated challenger-family baseline, though it is a downstream family trait rather than the sole defining feature

### 4.3 Validated reference signature

The current validated RI reference signature is the leader family from slice-1 validation, anchored by `trial_001`.

Reference values:

- `thresholds.entry_conf_overall = 0.25`
- `thresholds.regime_proba.balanced = 0.36`
- `thresholds.signal_adaptation.zones.low.entry_conf_overall = 0.16`
- `thresholds.signal_adaptation.zones.low.regime_proba = 0.33`
- `thresholds.signal_adaptation.zones.mid.entry_conf_overall = 0.40`
- `thresholds.signal_adaptation.zones.mid.regime_proba = 0.51`
- `thresholds.signal_adaptation.zones.high.entry_conf_overall = 0.32`
- `thresholds.signal_adaptation.zones.high.regime_proba = 0.57`
- `thresholds.signal_adaptation.atr_period = 14`
- `gates.hysteresis_steps = 3`
- `gates.cooldown_bars = 2`
- `multi_timeframe.regime_intelligence.enabled = true`
- `multi_timeframe.regime_intelligence.version = "v2"`
- `multi_timeframe.regime_intelligence.authority_mode = "regime_module"`
- `multi_timeframe.regime_intelligence.clarity_score.enabled = false`
- `multi_timeframe.regime_intelligence.risk_state.enabled = true`

This reference signature should be treated as the current RI-family anchor for classification and governed research framing. It is not a claim that every future RI candidate must exactly equal every downstream tuning value, but it is the current validated baseline for the core family-defining surface.

### 4.4 Downstream tuning surface

The following areas remain part of RI-family development, but are not currently required to establish family identity by themselves:

- `multi_timeframe.ltf_override_threshold`
- `htf_fib.entry.*`
- `ltf_fib.entry.*`
- `exit.*`
- `htf_exit_config.*`
- bounded `risk_state.*` refinements

These should be treated as **within-family tuning axes**, not as the primary family-definition levers.

## 5. Classification Rules

The classification goal is deterministic family labeling for research and governance. It is not runtime logic and must not alter regime processing behavior.

### 5.0 Deterministic family inputs

The deterministic classifier uses four primary inputs:

1. `authority_mode`
2. `thresholds.signal_adaptation.atr_period`
3. threshold surface shape
4. gating structure

The threshold surface shape is defined from the effective config using:

- `thresholds.entry_conf_overall`
- `thresholds.regime_proba.balanced`
- `thresholds.signal_adaptation.zones.low.entry_conf_overall`
- `thresholds.signal_adaptation.zones.mid.entry_conf_overall`
- `thresholds.signal_adaptation.zones.high.entry_conf_overall`
- `thresholds.signal_adaptation.zones.low.regime_proba`
- `thresholds.signal_adaptation.zones.mid.regime_proba`
- `thresholds.signal_adaptation.zones.high.regime_proba`

### 5.0.1 Family surface signatures

The current evidence supports the following family signatures.

`legacy_signature`

- no RI authority identity in the effective surface
- `atr_period = 28`
- gates `2/0`
- champion-style threshold family anchored by:
  - `entry_conf_overall = 0.26`
  - `balanced = 0.50`
  - zone entry thresholds `0.24 / 0.30 / 0.36`
  - zone regime thresholds `0.36 / 0.44 / 0.56`

`ri_signature`

- RI authority identity present
- `atr_period = 14`
- gates `3/2`
- RI-family threshold surface anchored by:
  - `entry_conf_overall = 0.25`
  - `balanced = 0.36`
  - zone entry thresholds `0.16 / 0.40 / 0.32`
  - zone regime thresholds `0.33 / 0.51 / 0.57`

### 5.0.2 Deterministic classification procedure

The deterministic procedure should be interpreted as follows:

1. Extract the effective config surface after all config merging.
2. Derive `authority_mode`, `atr_period`, gating tuple, and threshold shape signature.
3. Apply family rules in this order:
   - if the RI authority identity is present **and** the config matches the RI compatibility cluster, classify as `ri`
   - else if the config matches the legacy signature and does not present the RI compatibility cluster, classify as `legacy`
   - else fail closed on the rejected hybrid surface (historical analysis artifacts may describe this diagnostic shape as `invalid_hybrid_overlay`)
4. Never silently coerce a rejected hybrid surface into `legacy` or `ri`.

Pseudo-logic:

- `ri` if:
  - `enabled = true`
  - `version = "v2"`
  - `authority_mode = "regime_module"`
  - `atr_period = 14`
  - gates are `3/2`
  - threshold surface matches the RI-family anchor pattern
- `legacy` if:
  - RI authority identity is absent
  - `atr_period = 28`
  - gates are `2/0`
  - threshold surface matches the incumbent champion pattern
- otherwise:
  - reject/fail closed (historically documented as `invalid_hybrid_overlay` in some analysis artifacts)

### 5.1 Classify as `legacy`

A surface should be classified as `legacy` when it preserves the incumbent champion decision topology and is evaluated as the control baseline or as a legacy-style challenger.

Typical signs include:

- incumbent/native champion threshold family
- `atr_period = 28`
- gates `2/0`
- incumbent Fib/override surface
- no RI authority path, or no evidence-backed RI compatibility cluster

### 5.2 Classify as `ri`

A surface should be classified as `ri` only when all of the following are true:

1. RI authority identity is present:
   - `enabled = true`
   - `version = "v2"`
   - `authority_mode = "regime_module"`
2. The surface uses the minimum compatibility cluster:
   - RI-native threshold family
   - `atr_period = 14`
   - gates `3/2`
3. The candidate is evaluated as a full challenger surface, not as a partial overlay on the incumbent champion
4. The candidate is judged on governed train/validate/blind rules against the incumbent control

### 5.3 Reject hybrid surfaces (historical diagnostic label: `invalid_hybrid_overlay`)

A surface should be rejected fail-closed when it combines RI authority or RI subcomponents with the incumbent champion surface but does not adopt the minimum RI baseline. Earlier analysis artifacts may refer to this rejected diagnostic shape as `invalid_hybrid_overlay`, but that is not a third accepted canonical `strategy_family` label.

Typical signs include:

- champion surface + RI authority-only overlay
- champion surface + partial RI additions that still preserve the incompatible legacy threshold/gating/adaptation cluster
- interpretation framed as “small migration patch” despite zero-trade or topology-break evidence

These surfaces may still be useful as diagnostics, but they are **not** valid RI promotion candidates.

## 6. Research-System Integration Notes

The integration goal is to make strategy-family handling explicit in the research system **without changing existing contracts**.

### 6.1 Optimizer and campaign framing

Future RI campaigns should continue under the RI challenger-family taxonomy rather than under incumbent-patch framing.

Recommended framing:

- incumbent champion = control baseline
- RI family = separate challenger track
- blind 2025 = deferred until candidate freeze

### 6.1.1 Family-aware campaign taxonomy

Campaigns should be named and grouped by family before ranking by score. At minimum:

- incumbent/legacy control runs remain labeled as `legacy`
- RI challenger runs remain labeled as `ri`
- compatibility probes remain rejected hybrid diagnostics rather than stored third-family labels

This prevents an overlay probe from being misread as a promotable RI candidate.

### 6.2 Ledger integration

The research ledger already supports record-level `metadata` and `intelligence_refs.metadata`, so family labeling should be introduced there rather than by changing record contracts.

Design note:

- store `strategy_family` in record metadata for:
  - `HypothesisRecord`
  - `ProposalRecord`
  - `ExperimentRecord`
  - `ArtifactRecord`
  - `GovernanceDecisionRecord`
  - `PromotionRecord`
  - `ChampionRecord`
- where needed, also store `strategy_family` in `IntelligenceRef.metadata` for family-specific evidence links

Minimum metadata convention:

- `metadata.strategy_family = "legacy" | "ri"`
- `metadata.strategy_family_source = "family_registry_v1"`

This satisfies the requirement that the ledger stores `strategy_family` while preserving the existing ledger schema and record dataclasses.

### 6.3 Orchestrator integration

The current `ResearchTask` / `ResearchResult` contracts do not expose a dedicated family field. Therefore, family-aware orchestration should be implemented as a scheduling and aggregation rule around the existing orchestrator, not as a contract change.

Design note:

- a multi-family research run is modeled as a set of family-scoped tasks
- each task is constructed from a family-homogeneous candidate/config set
- the outer scheduler aggregates results by family after orchestrator completion
- the resulting artifacts and ledger records are tagged with `strategy_family`

Implication:

- `DeterministicResearchOrchestrator` remains single-task and contract-stable
- multi-family support exists at the run-composition layer, not via a changed orchestrator API

### 6.4 Parameter-intelligence integration

Parameter intelligence should support both:

- **intra-family comparison**
- **cross-family comparison**

without changing the current `ParameterAnalysisRequest` or `ParameterRecommendation` contracts.

Design note:

1. Build family-homogeneous analysis requests for the standard analyzer flow.
2. Run the existing analyzer separately for each family.
3. Produce intra-family rankings from the ordinary per-family analyzer outputs.
4. Produce cross-family comparison as an explicit higher-level analysis artifact that compares the top family representatives.

This keeps the existing parameter-intelligence contract stable while adding family-aware interpretation.

### 6.4.1 Comparison semantics

`intra-family`

- compares candidates only against others in the same family
- used for challenger refinement and within-family freeze decisions

`cross-family`

- compares already-labeled family representatives explicitly
- used for incumbent-vs-RI competition or other future family-vs-family comparisons
- must never be inferred from a silent overlay replay

### 6.5 Candidate freeze rule

An RI candidate should be frozen only after it wins the governed development path inside the RI family and then clears the required comparison step against the incumbent control.

Freeze order:

1. RI family train/tune search
2. governed validation ranking
3. incumbent-vs-RI direct comparison on identical windows and flags
4. candidate freeze
5. blind evaluation

### 6.6 Result interpretation rule

Results should be interpreted by family first, then by score.

This means:

- do not read an RI challenger result as evidence that the incumbent has become RI-compatible
- do not read an incumbent control win as evidence that RI research should stop
- do read a strong RI result as evidence about the RI family surface only

### 6.7 Ledger / reporting implication

Analysis artifacts should explicitly label the candidate family when summarizing findings. At minimum, future RI reporting should distinguish:

- incumbent control
- RI family challenger
- invalid hybrid overlay / compatibility probe

This keeps topology findings from being collapsed into a misleading single-leaderboard narrative.

## 7. Promotion Implications

### 7.1 What promotion means here

If RI is ever promoted, that promotion should mean:

- a fully frozen RI-family challenger beat the incumbent through the governed comparison path
- the promoted artifact is a new champion candidate in its own right
- the promotion is justified by RI-family evidence, not by a claim that the incumbent absorbed a minor RI patch

### 7.1.1 Promotion comparison rules

Promotion logic must follow these rules:

1. **Within-family comparison is mandatory by default**
   - choose the family representative inside `legacy` or `ri` first
2. **Cross-family competition must be explicit**
   - incumbent-vs-RI comparison is a deliberate governed step, not an implicit side effect of optimizer ranking
3. **Silent overlay comparison is forbidden**
   - a rejected hybrid probe (historically described as `invalid_hybrid_overlay`) must not be treated as proof that one family beat another
4. **Promotion target must preserve family identity**
   - if an RI candidate wins, it is promoted as an RI-family champion candidate, not as a retroactively relabeled legacy champion

### 7.2 What promotion does not mean

Promotion does **not** mean:

- toggling RI onto the incumbent champion and calling it migrated
- treating authority-only overlay as sufficient compatibility proof
- merging families conceptually before the evidence supports it
- bypassing blind or robustness gates because train performance looked strong

### 7.3 Default operational stance

Until contrary evidence exists, the default stance is:

- incumbent champion remains active control
- RI remains a separate challenger family under research
- no family merge is assumed
- no overlay-based migration story is accepted

## 8. Decision Rules Going Forward

- **DEC-001**: Compare incumbent and RI on identical windows, flags, and scoring rules.
- **DEC-002**: Treat RI optimization as within-family search, not as incumbent patch refinement.
- **DEC-003**: Reject “migration candidate” framing unless a future minimal compatibility path survives without topology break.
- **DEC-004**: Keep `RI_BASELINE` stable unless new governed evidence proves a different minimum compatibility cluster.
- **DEC-005**: Promote only a frozen RI-family challenger, never an invalid hybrid overlay.
- **DEC-006**: Store `strategy_family` in ledger metadata rather than introducing a new ledger contract field in this slice.
- **DEC-007**: Support multi-family research as an orchestration/scheduling concern around the existing orchestrator contract, not by changing `ResearchTask` or `ResearchResult`.
- **DEC-008**: Run parameter intelligence in two layers: per-family analysis first, explicit cross-family comparison second.

## 9. Files

- **FILE-001**: `docs/features/feature-regime-intelligence-strategy-family-1.md` — this formal family-definition artifact
- **FILE-002**: `docs/analysis/regime_intelligence/core/regime_intelligence_champion_compatibility_findings_2026-03-18.md` — compatibility evidence basis
- **FILE-003**: `docs/analysis/recommendations/tBTCUSD_3h_candidate_recommendation_2026-03-18.md` — candidate-status evidence basis
- **FILE-004**: `docs/features/feature-ri-optuna-train-validate-blind-1.md` — experiment-framework reference
- **FILE-005**: `docs/analysis/regime_intelligence/core/regime_intelligence_strategy_family_integration_stub_2026-03-18.md` — companion docs-only implementation stub for metadata labeling, orchestration, and family-aware comparison

## 10. Validation

- **VAL-001**: The document must remain consistent with the existing compatibility findings and candidate recommendation artifacts.
- **VAL-002**: The document must not introduce behavior claims that contradict the incumbent-vs-RI replay evidence.
- **VAL-003**: The document must preserve the no-runtime-change, no-promotion, no-family-merge stance.

## 11. Risks & Assumptions

- **RISK-001**: Future evidence may refine the minimum RI compatibility cluster. Mitigation: keep this artifact versioned and update only through new governed evidence.
- **RISK-002**: Readers may confuse family classification with promotion readiness. Mitigation: keep the incumbent-control and no-promotion stance explicit in every related summary.
- **RISK-003**: Hybrid overlay diagnostics may be over-interpreted as deployable candidates. Mitigation: keep them explicitly documented as rejected hybrid probes rather than as canonical family labels.
- **ASSUMPTION-001**: The incumbent control evidence and the slice-1/2/3 RI challenger evidence remain the current best basis for family classification.
- **ASSUMPTION-002**: `authority_mode = regime_module` remains necessary but not sufficient for valid RI-family classification.

## 12. Related Specifications / Further Reading

- `docs/analysis/regime_intelligence/core/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `docs/analysis/recommendations/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`
- `docs/features/feature-ri-optuna-train-validate-blind-1.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_strategy_family_integration_stub_2026-03-18.md`
- `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice3_2026-03-18.md`
- `results/archive/bundles/ri_slices_bundle_20260318_1458.zip`
