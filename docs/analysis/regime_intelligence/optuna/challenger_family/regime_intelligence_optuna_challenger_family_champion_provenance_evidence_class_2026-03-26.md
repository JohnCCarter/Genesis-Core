# Regime Intelligence challenger family — champion provenance supplementary evidence class

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `definition-only / admissibility-only`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet defines a new supplementary bounded evidence class for future promotion-track reasoning, but does not approve runtime comparison, promotion-readiness, promotion, or writeback
- **Required Path:** `Quick`
- **Objective:** Define whether champion provenance / authority-lineage is an admissible supplementary bounded evidence class for a future successor lane after the closed slice8 promotion-readiness / incumbent-comparison chain.
- **Candidate:** `slice8 full tuple as lead RI research candidate`
- **Base SHA:** `c0881fce`

### Scope

- **Scope IN:** docs-only definition of a new supplementary evidence class; admissible-source boundaries; explicit permitted use and explicit non-use boundaries; explicit preservation of incumbent same-head control artifact status.
- **Scope OUT:** no source-code changes, no config changes, no tests, no runtime comparison approval, no new performance-comparison surface, no promotion-readiness approval, no promotion-decision contract, no promotion approval, no champion replacement approval, no writeback approval.
- **Expected changed files:** `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_champion_provenance_evidence_class_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- every conclusion must remain admissibility-only
- no sentence may devalue, replace, or reweight the incumbent same-head control artifact
- no sentence may imply that provenance context is a performance result
- no sentence may imply that provenance context, alone or together with the current comparison-only surface, is sufficient for readiness, promotion, or writeback
- no sentence may imply that a promotion-decision contract is now open

### Stop Conditions

- any wording that implicitly turns provenance context into comparative performance evidence
- any wording that implicitly weakens the incumbent same-head control artifact
- any wording that implies bootstrap status by itself justifies readiness reopening
- any wording that implies bootstrap status plus current comparison-only evidence is enough for readiness, promotion, or writeback
- any wording that opens runtime comparison, promotion-readiness approval, promotion, or writeback

### Output required

- reviewable evidence-class definition packet
- explicit decision label
- explicit admissible-source inventory
- explicit permitted-use and non-use boundaries
- explicit next allowed step below any promotion-decision contract

## What this packet does and does not do

This packet defines only a **new supplementary bounded evidence class** for possible use in a future separately governed lane.

It does **not**:

- reopen the closed slice8 promotion-readiness / incumbent-comparison lane
- create a new performance-comparison surface
- decide whether the slice8 candidate is stronger on runtime or promotion-grade terms
- approve promotion-readiness reconsideration
- open a promotion-decision contract
- approve promotion
- approve champion-file writeback
- change any runtime/default behavior

## Decision label

The decision recorded by this packet is:

- `DEFINED — admissible supplementary evidence class: champion provenance / authority-lineage only`

## Meaning of that label

This label means only the following:

- champion provenance / authority-lineage may be treated as a separately bounded supplementary evidence class
- that class may be used only to classify what kind of authority artifact the current champion file represents
- that class may contribute supplementary context in a future separately governed readiness-reconsideration lane
- that class does not replace, devalue, or reweight the incumbent same-head control artifact

This label does **not** mean:

- provenance context is now a performance result
- provenance context is now a same-head comparison result
- the closed slice8 lane has reopened
- promotion-readiness is now established
- promotion is near approval
- writeback is now permitted

## Governing basis for defining this evidence class

This packet is downstream of the current tracked March 26 governance chain, especially:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_non_runtime_evidence_sufficiency_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_readiness_reconsideration_surface_disposition_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_terminal_closeout_2026-03-26.md`

Those packets closed the present slice8 lane and explicitly required any future promotion-track continuation to begin through a **new evidence class** or **supplementary bounded surface**.

This packet chooses the narrower of those two openings:

- a provenance / authority-lineage supplementary evidence class

## Defined supplementary evidence class

### Name

- `bootstrap champion provenance / authority-lineage supplementary evidence class`

### Core question this class is allowed to answer

The only question this class is allowed to answer is:

- what kind of authority artifact the current operational champion file represents in the tracked repository state

In particular, this class may distinguish between:

- a bootstrap / placeholder authority artifact, and
- a validated optimizer-winner authority artifact

### Why this class is governance-legitimate

This class is governance-legitimate because it addresses **artifact provenance and authority shape**, not competitive performance.

It therefore stays bounded below:

- runtime comparison
- promotion-readiness determination
- promotion decision
- writeback authority

## Admissible evidence sources for this class

### Primary operational provenance artifact

The primary admissible source for this class is:

- `config/strategy/champions/tBTCUSD_3h.json`

This artifact is admissible for provenance / authority-lineage classification because it contains tracked repository fields about:

- `run_id`
- `score`
- `metrics`
- metadata note text
- metadata recommended-next text
- stored champion/config shape

### Supporting historical framing sources

The following sources are admissible only as **framing / precedent context**, not as controlling performance proof:

- `docs/analysis/recommendations/tBTCUSD_3h_champion_promotion_recommendation_2026-03-13.md`
- `docs/analysis/recommendations/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_parity_artifact_matrix_2026-03-17.md`

Their admissible use is limited to:

- showing repository precedent for distinguishing artifact type from approval status
- showing that analysis artifacts may classify evidence surfaces without themselves granting promotion
- providing historical contrast between bootstrap authority context and validated challenger evidence

### Governing-boundary sources

The following sources are admissible only to preserve boundary discipline:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_non_runtime_evidence_sufficiency_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_readiness_reconsideration_surface_disposition_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_terminal_closeout_2026-03-26.md`

Their role is not to prove provenance facts.

Their role is to prevent this new class from being misread as a reopening or promotion authorization.

## What this evidence class may support

This evidence class may support only the following bounded conclusions.

### 1. Classification of the current champion authority artifact

This class may support a conclusion about whether the current `tBTCUSD_3h` champion file is best classified as:

- bootstrap / placeholder authority context, or
- validated optimizer-winner authority provenance

### 2. Supplementary context for a future successor lane

If such a classification is later applied in a separate packet, that result may serve as:

- supplementary context for a future successor readiness-reconsideration lane

### 3. Authority-lineage interpretation only

This class may support statements about:

- whether the operational champion file encodes a validated competitive winner lineage
- whether the file instead documents an operational bootstrap used to unblock workflow continuity

## What this evidence class may not support

This class may **not** support any of the following.

### 1. No performance conclusion

This class may not be used to conclude that:

- the slice8 candidate is better than the incumbent on a performance basis
- the incumbent is weaker on a same-head comparison basis
- provenance context is equivalent to runtime or validation evidence

### 2. No devaluation of incumbent same-head control artifact

This class may not be used to:

- devalue the incumbent same-head control artifact
- replace the incumbent same-head control artifact
- reweight the incumbent same-head control artifact inside any comparison score narrative

The incumbent same-head control artifact remains what it already is in the tracked record.

This packet changes none of that.

### 3. No readiness sufficiency

This class is **not sufficient**:

- by itself, or
- together with the current slice8 comparison-only non-runtime surface

for any of the following:

- promotion-readiness determination
- promotion-decision contract opening
- promotion approval
- champion writeback approval

### 4. No runtime or writeback authority

This class may not be used to authorize:

- runtime materialization
- canonical same-head execution comparison
- champion replacement
- writeback into `config/strategy/champions/tBTCUSD_3h.json`

## Initial admissibility reading from the tracked artifact shape

At the evidence-class definition level, the repository already shows that the champion file is eligible for provenance classification because the tracked artifact shape includes all of the following repository-visible features:

- `run_id = baseline_timeframe_switch_3h`
- `score = 0.0`
- empty `metrics`
- metadata note identifying the artifact as bootstrap context to unblock 3h workflow continuity
- metadata recommended-next text pointing to a future validated run

This packet does **not** convert those observations into a final promotion-track disposition.

It only records that such fields are admissible inputs for the newly defined provenance class.

## Relationship to the closed slice8 lane

This packet does **not** continue the closed slice8 lane.

Instead, it defines an input class that may be used only in a **new separately governed successor lane**.

The closed lane remains closed.

Nothing here reopens it.

## Next allowed step

The next allowed step after this packet remains below any promotion-decision contract.

The next allowed step is only:

1. a separate governed packet that applies this evidence class to the concrete `tBTCUSD_3h` champion artifact and records the resulting provenance classification, and/or
2. a separate governed packet that decides whether that classified provenance result is admissible supplementary context for a successor readiness-reconsideration lane

Neither of those steps is completed by this packet.

## Bottom line

The current tracked state now has a newly defined supplementary evidence class for the promotion track:

- `champion provenance / authority-lineage`

That class is admissible only for bounded authority-artifact classification.

It does **not** create a new performance surface, does **not** weaken the incumbent same-head control artifact, and is **not sufficient** — either alone or together with the current slice8 comparison-only surface — for readiness, promotion, or writeback.

It is simply the first governance-legitimate successor opening after the closed slice8 lane.
