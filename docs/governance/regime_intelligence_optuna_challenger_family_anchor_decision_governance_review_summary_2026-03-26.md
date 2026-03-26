# Regime Intelligence challenger family — anchor decision governance review summary

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `review-summary / APPROVE_OPTION_A / research-anchor only / no canonical anchor or promotion approved by this summary`

## Purpose

This review summary records the governance response to the refreshed RI challenger-family anchor-decision packet dated 2026-03-26.

Reviewed packet:

- `docs/governance/regime_intelligence_optuna_challenger_family_anchor_decision_candidate_packet_2026-03-26.md`

This summary is intentionally narrow.

It does **approve** a research-anchor decision inside the RI research workflow.
It does **not** approve canonical anchor adoption.
It does **not** approve champion promotion.
It does **not** approve default/runtime behavior change.
It does **not** approve cutover.

## Governance response

Governance response shape:

- `APPROVE_OPTION_A`

Approved meaning:

- adopt the current slice8-backed backbone as the next **research anchor only** for future RI challenger-family slices

Approved research-anchor backbone:

- `thresholds.entry_conf_overall=0.27`
- `thresholds.regime_proba.balanced=0.36`
- `gates.hysteresis_steps=4`
- `gates.cooldown_bars=1`

This approval is limited to the RI research workflow.

It must not be interpreted as:

- canonical anchor approval
- promotion approval
- champion approval
- default authority change
- runtime configuration change

## Evidence basis reviewed

The reviewed evidence line for this decision consists of:

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice7_20260324.json`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice7_execution_outcome_signoff_summary_2026-03-24.md`
- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice8_execution_outcome_signoff_summary_2026-03-24.md`
- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice9_20260326.json`
- `docs/governance/regime_intelligence_optuna_challenger_family_slice9_execution_outcome_signoff_summary_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_anchor_decision_candidate_packet_2026-03-26.md`

## Decision basis

The governance basis for `APPROVE_OPTION_A` is the following:

- slice7, slice8, and slice9 all converged on the same RI high-water validation score `0.26974911658712664`
- slice8 preserved that winner while materially reducing duplicate collapse versus slice7 (`0.2604166666666667` vs `0.90625`)
- slice8 therefore remains the cleanest local research anchor in the current evidence line
- slice9 preserved the same entry/gating backbone while reopening a nearby management surface and still remained above the incumbent same-head control `0.2616884080730424`
- slice9 did this on a **non-slice8 management tuple** (`8 / 0.40 / 0.38` rather than `8 / 0.42 / 0.40` on the reopened axes), which strengthens robustness evidence for the backbone without implying canonical validation
- no reviewed slice in this evidence line produced a higher validation score than the current RI high-water line, which supports reading the current line as a replicated plateau rather than an unresolved local frontier

## Explicit governance interpretation

The approved interpretation is:

- the slice8-backed backbone is sufficiently robust to serve as the next **research reference backbone** for further RI challenger-family work

The approved interpretation is **not**:

- that RI now has a new operational champion
- that the current backbone is approved as a canonical baseline for production/runtime use
- that no further falsification is possible or useful
- that the metadata quirk in run packaging has been resolved

## Residual cautions

### 1. Approval scope is research-only

This summary approves a research-anchor choice only.

Any future packet that attempts:

- champion promotion
- canonical anchor declaration
- default/runtime cutover
- config authority change

must be prepared and reviewed separately.

### 2. Metadata quirk remains open

Run artifacts in this RI line still show `merged_config.strategy_family=legacy`.

Current status:

- treated as open
- treated as non-blocking for execution packaging only
- not resolved by this summary
- must remain disclosed in later promotion-grade governance work

### 3. No higher validation score was achieved

This approval is based on repeated preservation of the current RI high-water validation line together with improved robustness evidence, not on a new score breakout.

That means:

- this is a research-anchor decision
- not a superiority proof for promotion/default use

## Next governed step

The next governed step after this summary should be one of the following:

1. open the next RI slice from the approved research anchor with explicit no-promotion/no-runtime-change constraints, or
2. if the goal shifts from research anchoring to operational adoption, prepare a separate promotion/candidate packet that compares the RI line directly against the incumbent champion under the required governed path

## Final reminder

This summary approves **research-anchor selection only**.

It does **not** approve:

- champion replacement
- promotion
- freeze
- default/runtime behavior change
