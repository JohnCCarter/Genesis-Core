# Regime Intelligence challenger family — candidate definition packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Category: `obs`
Status: `analysis-only / lead research candidate defined / no promotion approved`
Constraint: `NO BEHAVIOR CHANGE`

## Purpose

This packet defines the next **lead RI research candidate tuple** to carry into a future governed incumbent-comparison path.

This packet is intentionally narrower than promotion.

It does:

- build directly on the approved RI research-anchor decision dated 2026-03-26
- choose a single lead RI research candidate tuple for future governed comparison prep
- record why slice8 is the lead candidate and slice9 is supporting robustness evidence
- frame the incumbent and bootstrap-champion context without claiming a governed replacement

It does **not**:

- approve promotion
- approve champion replacement
- approve default/runtime change
- approve cutover
- approve champion writeback into `config/strategy/champions/tBTCUSD_3h.json`

## Scope IN / Scope OUT

### Scope IN

- analysis/governance interpretation of the RI challenger-family evidence line through slice9
- naming one lead RI research candidate tuple for the next governed comparison step
- explicit documentation of what still remains open before any promotion-grade decision

### Scope OUT

- all runtime code
- all tests
- all config changes
- all champion-file changes
- all result-artifact rewrites
- any claim that the RI line is already approved as incumbent replacement

## Governing prior decision

This packet is downstream of the approved research-anchor review summary:

- `docs/governance/regime_intelligence_optuna_challenger_family_anchor_decision_governance_review_summary_2026-03-26.md`

Approved research-anchor backbone from that summary:

- `thresholds.entry_conf_overall=0.27`
- `thresholds.regime_proba.balanced=0.36`
- `gates.hysteresis_steps=4`
- `gates.cooldown_bars=1`

That approval was explicitly **research-anchor only**.

This packet must therefore be read as **candidate-definition for future governed comparison**, not as promotion approval.

## Reviewed evidence basis

### RI challenger-family evidence

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_execution_outcome_signoff_summary_2026-03-24.md`
- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice9_20260326.json`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice9_execution_outcome_signoff_summary_2026-03-26.md`
- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice9_2024_v1.yaml`

### Incumbent / champion context

- `results/backtests/tBTCUSD_3h_20260324_170603.json`
- `config/strategy/champions/tBTCUSD_3h.json`
- `docs/analysis/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`

## Current question

After the research-anchor approval, the next question is no longer:

- "do we have a research backbone?"

That question is already answered.

The next question is:

- "which full RI tuple should serve as the lead research candidate for the next governed incumbent-comparison path?"

The answer in this packet is:

- use the **slice8 full tuple** as the lead RI research candidate
- use **slice9** as supporting robustness evidence for the same backbone, not as the co-primary candidate

## Lead RI research candidate

### Chosen lead tuple

The lead RI research candidate is the slice8 local winner geometry consisting of:

- `thresholds.entry_conf_overall=0.27`
- `thresholds.regime_proba.balanced=0.36`
- `gates.hysteresis_steps=4`
- `gates.cooldown_bars=1`
- `exit.max_hold_bars=8`
- `exit.exit_conf_threshold=0.42`
- `multi_timeframe.ltf_override_threshold=0.40`

Supporting fixed family identity carried by the slice8 YAML:

- `strategy_family=ri`
- `multi_timeframe.regime_intelligence.enabled=true`
- `multi_timeframe.regime_intelligence.version=v2`
- `multi_timeframe.regime_intelligence.authority_mode=regime_module`
- `multi_timeframe.regime_intelligence.clarity_score.enabled=false`
- `multi_timeframe.regime_intelligence.risk_state.enabled=true`

### Why slice8 is the lead candidate

Slice8 is selected as the lead RI research candidate because:

1. it reproduced the current RI validation high-water line `0.26974911658712664`
2. it did so while materially reducing duplicate collapse versus slice7 from `0.90625` to `0.2604166666666667`
3. its local geometry therefore remains the cleanest search-quality expression of the currently approved research backbone
4. slice9 later showed that the same backbone survives at least one nearby management perturbation, which strengthens confidence in the backbone without displacing slice8 as the cleaner primary candidate

This is a **candidate-definition** judgment, not a promotion judgment.

## Why slice9 is supporting evidence rather than the lead candidate

Slice9 remains important governed evidence.

It showed that the approved slice8-backed backbone preserved the same validation winner score `0.26974911658712664` on a nearby management tuple:

- `exit.max_hold_bars=8`
- `exit.exit_conf_threshold=0.40`
- `multi_timeframe.ltf_override_threshold=0.38`

Within the same existing same-head validation-control framing, it remained above the referenced incumbent control value `0.2616884080730424`; this is supporting comparison context only and does not by itself imply promotion, replacement, or final incumbent victory.

That matters because it demonstrates backbone robustness across a bounded management-surface perturbation.

However, slice9 is **not** selected as the lead candidate because:

- it did not exceed the slice8/slice7 validation high-water line
- its duplicate ratio `0.3466666666666667` was worse than slice8's `0.2604166666666667`
- its strongest role in the evidence chain is falsification support, not cleaner candidate nomination

## Incumbent and champion context

### Same-head incumbent control

The incumbent same-head control artifact remains:

- `results/backtests/tBTCUSD_3h_20260324_170603.json`

Observed context from that artifact:

- total return: `0.42059270143001415%`
- profit factor: `1.8721119891064304`
- max drawdown: `1.4705034784627329%`
- trades: `37`

This packet uses that artifact as comparison context only.

It does **not** claim that the RI line has already won a final governed incumbent-comparison path.

### Bootstrap champion file context

The current champion file remains:

- `config/strategy/champions/tBTCUSD_3h.json`

Observed context from that file:

- `run_id=baseline_timeframe_switch_3h`
- `score=0.0`
- `metadata.note` describes it as a bootstrap champion used to unblock 3h workflow migration
- `metadata.recommended_next` explicitly points toward validated run evidence as the next step

This matters because the operational champion file is still bootstrap-shaped.

Even so, this packet does **not** treat the bootstrap file as already displaced.

The correct next step is a governed comparison/preparation path, not automatic writeback.

## Interpretation boundary

### Approved by this packet

This packet approves only the following analytical interpretation:

- the RI challenger-family evidence line is now strong enough to name a single **lead research candidate tuple** for the next governed incumbent-comparison step
- that lead tuple should be the slice8 full tuple
- slice9 should travel with that decision as supporting robustness evidence for the same entry/gating backbone

### Not approved by this packet

This packet does **not** approve:

- promotion readiness
- champion replacement
- automatic writeback
- canonical anchor freeze
- runtime/default authority change
- cutover to RI as default behavior
- any claim that validation evidence alone has completed a governed backtest superiority case

## Residual cautions

### 1. The validation plateau is replicated, not broken upward

Slice7, slice8, and slice9 all converged on the same validation high-water score `0.26974911658712664`.

This supports replication and local robustness.

It does **not** by itself prove promotion superiority.

### 2. Incumbent comparison is still incomplete at promotion grade

The same-head incumbent control gives useful context, but the next formal step still needs a governed packet that compares the chosen RI candidate against the incumbent under the intended comparison contract.

That future packet should make explicit:

- exact execution path
- comparison metrics
- acceptance/rejection rule
- whether a champion writeback decision is even in scope

### 3. Metadata quirk remains open

Some RI run artifacts still show `merged_config.strategy_family=legacy`.

Current interpretation:

- treat this as an open packaging/metadata issue
- do not treat it as evidence against the RI family identity
- do not treat it as resolved by this packet
- keep it disclosed in any later promotion-grade or cutover-grade governance work

## Recommended next governed step

Open a separate governed comparison-prep or promotion-prep packet that:

1. uses the slice8 full tuple as the named RI lead research candidate
2. attaches slice9 as bounded robustness evidence for the same backbone
3. compares that candidate deliberately against the incumbent control path
4. defines in advance whether the goal is:
   - research comparison only, or
   - actual promotion-readiness assessment

## Bottom line

The repository still does **not** have a newly approved RI champion.

What it now has is something narrower and cleaner:

- an approved RI research anchor, and
- a defined **lead RI research candidate tuple** for the next governed incumbent-comparison step

That lead tuple is the **slice8 full tuple**, with **slice9 carried as supporting robustness evidence rather than as the primary candidate**.
