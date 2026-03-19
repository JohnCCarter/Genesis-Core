# Regime Intelligence strategy family integration — implementation stub

Date: 2026-03-18
Branch: `feature/ri-optuna-train-validate-blind-v1`
Status: `docs-only / design-stub / implementation not implied`

## Purpose

This document defines the **föreslagen** implementation shape for making strategy-family handling explicit in the Genesis-Core research system.

It is a companion to:

- `docs/features/feature-regime-intelligence-strategy-family-1.md`

It exists to answer a concrete follow-up question:

- where should `strategy_family` live?
- how should multi-family orchestration be composed?
- how should parameter intelligence compare within and across families?
- how should promotion logic avoid silent overlay comparisons?

This document is intentionally concrete, but it does **not**:

- approve implementation
- approve contract changes
- modify runtime regime logic
- imply that strategy-family support is already införd in code

## Reviewed contract boundaries

The current design must respect the following verified boundaries:

- research-ledger records already expose generic `metadata`
- `IntelligenceRef` already exposes `metadata`
- `ResearchTask` does **not** expose a dedicated `strategy_family` field
- `ResearchResult` does **not** expose a dedicated `strategy_family` field
- `ParameterAnalysisRequest` does **not** expose a dedicated `strategy_family` field
- `ParameterRecommendation` does **not** expose a dedicated `strategy_family` field

Therefore, the safe implementation shape is:

- family labeling in metadata
- family-aware orchestration in the outer scheduling layer
- family-aware comparison in the reporting / aggregation layer

## Scope IN

The **föreslagen** future implementation surface is limited to:

- research-ledger metadata population rules
- orchestration composition rules for multi-family runs
- parameter-intelligence comparison framing
- promotion-gate interpretation rules
- machine-readable family summary artifacts

## Scope OUT

The following remain out of scope:

- runtime regime logic changes
- retuning or search-space changes
- champion/default/cutover changes
- new required fields on existing dataclasses or protocol contracts
- family merging
- reinterpretation of invalid hybrid overlays as valid candidates

## Family labels

The historical **föreslagen** label model in this stub was:

- `legacy_family`
- `ri_family`
- `invalid_hybrid_overlay`

The now **införd** implementation instead uses:

- `strategy_family = "legacy" | "ri"`
- `strategy_family_source = "family_registry_v1"`

Important clarification:

- `invalid_hybrid_overlay` is not an införd third family label in current code
- hybrid or RI-mismatched surfaces now fail closed via validation/classification error rather than being stored as a third accepted family

## 1. Föreslagen ledger integration

### 1.1 Metadata convention

The **föreslagen** metadata keys are:

- `metadata.strategy_family`
- `metadata.strategy_family_source`
- `metadata.strategy_family_basis`

Historical/föreslagen values in this stub were:

- `metadata.strategy_family = "legacy_family" | "ri_family" | "invalid_hybrid_overlay"`
- `metadata.strategy_family_source = "deterministic_classifier_v1"`
- `metadata.strategy_family_basis = "effective_config"`

For the införd implementation, the corresponding canonical values are:

- `metadata.strategy_family = "legacy" | "ri"`
- `metadata.strategy_family_source = "family_registry_v1"`
- no third accepted family label is stored for hybrids; invalid hybrid surfaces fail closed and remain, at most, historical/rejected-path diagnostics

### 1.2 Record-placement map

The **föreslagen** placement by record type is:

- `HypothesisRecord.metadata.strategy_family`
- `ProposalRecord.metadata.strategy_family`
- `ExperimentRecord.metadata.strategy_family`
- `ArtifactRecord.metadata.strategy_family`
- `GovernanceDecisionRecord.metadata.strategy_family`
- `PromotionRecord.metadata.strategy_family`
- `ChampionRecord.metadata.strategy_family`

### 1.3 IntelligenceRef placement

Where family-specific evidence links are emitted, the **föreslagen** placement is:

- `IntelligenceRef.metadata.strategy_family`
- `IntelligenceRef.metadata.strategy_family_source`

This keeps supporting evidence family-aware without requiring schema changes.

### 1.4 Minimal write rule

The minimum safe rule is:

1. classify from the effective merged config
2. write `strategy_family` once at experiment creation time
3. copy the same label to downstream artifact/governance/promotion records
4. never infer family retroactively from score alone

## 2. Föreslagen deterministic classifier seam

### 2.1 Input surface

The **föreslagen** classifier input is the effective merged config surface only.

Required extracted values:

- `multi_timeframe.regime_intelligence.enabled`
- `multi_timeframe.regime_intelligence.version`
- `multi_timeframe.regime_intelligence.authority_mode`
- `thresholds.signal_adaptation.atr_period`
- `gates.hysteresis_steps`
- `gates.cooldown_bars`
- threshold-shape anchor values from:
  - `thresholds.entry_conf_overall`
  - `thresholds.regime_proba.balanced`
  - `thresholds.signal_adaptation.zones.low.entry_conf_overall`
  - `thresholds.signal_adaptation.zones.mid.entry_conf_overall`
  - `thresholds.signal_adaptation.zones.high.entry_conf_overall`
  - `thresholds.signal_adaptation.zones.low.regime_proba`
  - `thresholds.signal_adaptation.zones.mid.regime_proba`
  - `thresholds.signal_adaptation.zones.high.regime_proba`

### 2.2 Output contract

The **föreslagen** classifier output is a plain label + evidence payload, for example:

- `strategy_family`
- `strategy_family_source`
- `matched_signature`
- `classification_reasons`

This should be emitted into metadata or a sidecar artifact, not as a new required runtime contract.

### 2.3 Failure mode

If the config cannot be classified cleanly as the historical **föreslagen** labels `legacy_family` or `ri_family`, the fallback in this older stub was:

- `invalid_hybrid_overlay`

In the införd implementation, this idea was narrowed further: hybrid surfaces fail closed with validation/classification error instead of being accepted as a third stored family label. That is the behavior readers should map to current code.

## 3. Föreslagen multi-family orchestration shape

### 3.1 Composition rule

The **föreslagen** model for a multi-family research run is:

- one outer run
- multiple family-scoped task groups
- each group contains only family-homogeneous candidates/configs

The outer scheduler is responsible for:

- building family-specific task batches
- invoking the existing orchestrator per batch
- aggregating outputs after task completion

### 3.2 Why outer scheduling

This shape is preferred because:

- it preserves the current `ResearchTask` contract
- it preserves the current `ResearchResult` contract
- it keeps multi-family logic outside the deterministic core orchestrator
- it allows family-aware reporting without contract churn

### 3.3 Föreslagen family-run manifest

A future implementation may write a family manifest artifact such as:

- `family_run_manifest.json`

Suggested contents:

- run id
- family labels present
- task ids grouped by family
- config paths grouped by family
- classifier source
- aggregation artifact paths

This artifact is **föreslagen**, not currently required.

## 4. Föreslagen parameter-intelligence comparison model

### 4.1 Intra-family analysis

The **föreslagen** default analysis path is:

- run the existing analyzer separately per family
- produce rankings only within each family
- choose each family representative before any cross-family decision

This avoids mixing incompatible surfaces too early.

### 4.2 Cross-family analysis

The **föreslagen** cross-family path is:

- compare already-selected family representatives explicitly
- treat this as a second-stage analysis artifact
- require the family labels to remain attached throughout the comparison

### 4.3 Silent overlay prohibition

The following must remain prohibited:

- using an overlay probe as if it were a valid cross-family representative
- using authority-only overlay failure as if it were a within-family ranking result
- allowing optimizer output to silently mix candidates from incompatible families

### 4.4 Föreslagen comparison artifact

A future implementation may emit a summary artifact such as:

- `family_comparison_summary.json`

Suggested sections:

- `intra_family_rankings`
- `cross_family_representatives`
- `rejected_hybrid_probes`
- `promotion_ready_candidates`

This artifact is **föreslagen**, not currently införd.

## 5. Föreslagen promotion-gate interpretation

### 5.1 Promotion order

The **föreslagen** promotion order is:

1. choose best candidate inside each family
2. run explicit cross-family competition between family representatives
3. reject any rejected hybrid probe (historically `invalid_hybrid_overlay`) from promotion consideration
4. promote only if the winning representative clears the governed evidence chain

### 5.2 Promotion record handling

If a future RI-family candidate wins, the **föreslagen** record behavior is:

- keep `strategy_family = "ri"` on promotion-related records
- keep the winning artifact labeled as RI-family derived
- do not rewrite history by relabeling the winner as legacy-family

### 5.3 Incumbent rule

The incumbent champion remains:

- the control baseline
- a member of `legacy`
- comparable against RI only through explicit governed cross-family competition

## 6. Föreslagen artifact surfaces

If implementation is later approved, the following artifact surfaces are the most natural candidates:

- ledger metadata tags on existing records
- `family_run_manifest.json`
- `family_comparison_summary.json`
- optional per-experiment family-classification sidecar under research artifacts

No artifact listed here is implied to exist today.

## 7. Stop conditions for any future implementation slice

Stop immediately if a future implementation proposal tries to:

- add required dataclass fields to ledger/orchestrator/parameter-intelligence contracts without separate approval
- infer family from score alone
- treat a rejected hybrid probe (`invalid_hybrid_overlay` in historical docs) as promotable
- change runtime regime behavior in the same slice
- merge legacy and RI families conceptually without new evidence

## Bottom line

The safest **föreslagen** implementation path is:

1. classify family from effective config
2. store `strategy_family` in metadata
3. orchestrate multi-family research via outer scheduling
4. compare parameters within family first
5. require explicit cross-family competition
6. reject silent overlay interpretations

That preserves current contracts while making strategy-family reasoning operationally explicit.
