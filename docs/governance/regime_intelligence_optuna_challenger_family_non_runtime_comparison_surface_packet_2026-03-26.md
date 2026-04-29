# Regime Intelligence challenger family — non-runtime comparison surface packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `decision-prep / exact non-runtime evidence surface defined / no execution or promotion approved`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet defines the exact non-runtime evidence surface for the slice8 incumbent comparison, but it does not approve execution, promotion, or runtime/default change
- **Required Path:** `Quick`
- **Objective:** Define the exact governed non-runtime evidence surface for the slice8 incumbent comparison after the runtime-materialization path was blocked and the comparison-input surface class was set to Option C.
- **Candidate:** `slice8 full tuple as lead RI research candidate`
- **Base SHA:** `8e7dc965`

### Scope

- **Scope IN:** define the exact slice8-specific non-runtime evidence surface, the allowed tracked artifact chain, the explicit field map, and the disallowed transformations for a future incumbent comparison packet.
- **Scope OUT:** no source-code changes, no config changes, no champion-file changes, no runtime materialization, no artifact homogenization, no new comparator tooling, no new RI canonical materialization contract, no execution approval, no promotion decision.
- **Expected changed files:** `docs/governance/regime_intelligence_optuna_challenger_family_non_runtime_comparison_surface_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For any future packet that uses this surface:

- explicit citation of every artifact in the allowed artifact chain
- explicit field-by-field comparison map
- explicit non-promotion / non-writeback / non-runtime-change boundary
- explicit statement of whether the next step is comparison-only or promotion-preparatory only

### Stop Conditions

- any wording that implies runtime materialization is again permitted
- any wording that silently creates a new RI canonical materialization contract
- any wording that allows synthetic homogenization of mismatched artifact shapes
- any wording that allows local recomputation/backfill of incumbent score outside already tracked RI evidence
- any wording that upgrades this slice8-specific surface into a general repository-wide incumbent-comparison standard

### Output required

- reviewable non-runtime comparison surface packet
- exact allowed artifact chain
- explicit mapped comparison fields
- explicit disallowed derivations and transformations

## Purpose

This packet defines the governed non-runtime evidence surface for the **slice8 incumbent comparison only**.

It authorizes citation-backed comparison of explicitly mapped, semantically overlapping fields across the listed tracked artifacts.

It does **not** authorize:

- runtime materialization
- artifact homogenization into a synthetic common runtime form
- creation of a new RI canonical comparison contract
- execution by itself
- promotion
- champion replacement
- writeback
- runtime/default change

## Upstream governed context

This packet is downstream of the following tracked RI governance chain:

- `docs/governance/regime_intelligence_optuna_challenger_family_candidate_definition_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_incumbent_comparison_prep_packet_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_incumbent_comparison_execution_blocker_summary_2026-03-26.md`
- `docs/governance/regime_intelligence_optuna_challenger_family_comparison_input_surface_decision_packet_2026-03-26.md`

Already-governed interpretation carried into this packet:

- slice8 remains the lead RI research candidate
- incumbent same-head control remains the only primary comparator surface
- bootstrap champion remains background context only
- Option C was selected for comparison-surface class
- no further runtime forcing is permitted from the March 26 blocker state

## Precedent for artifact-matrix style

This packet uses a governed artifact-matrix style consistent with existing repo evidence practice, most clearly exemplified by:

- `docs/analysis/regime_intelligence_parity_artifact_matrix_2026-03-17.md`

Important limit:

- that precedent is cited as an evidence-style reference only
- this packet does **not** promote the present slice8 surface into a general parity or cutover standard

## Chosen exact non-runtime evidence surface

### Surface name

The exact surface defined by this packet is:

- **slice8 governed artifact-matrix surface**

### Why this exact surface is chosen

This packet chooses an artifact-matrix surface because:

1. current local runtime-materialization paths are verified blocked
2. the current comparison-input class decision already rejected further runtime forcing
3. the candidate and incumbent do not already exist in one homogeneous tracked artifact shape
4. a governed matrix can compare only the explicitly overlapping fields that are already tracked without pretending the artifacts are shape-equivalent

## Allowed artifact chain

### Candidate-side artifact anchors

The candidate side of the slice8 comparison may use only the following tracked artifacts:

1. primary candidate provenance and score anchor:
   - `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json`
2. candidate metric detail, where explicitly needed for overlapping field comparison:
   - `results/hparam_search/run_20260324_174006/validation/trial_001.json`
3. candidate sign-off interpretation support:
   - `docs/governance/regime_intelligence_optuna_challenger_family_slice8_execution_outcome_signoff_summary_2026-03-24.md`

### Incumbent-side artifact anchors

The incumbent side of the slice8 comparison may use only the following tracked artifacts:

1. primary comparator artifact:
   - `results/backtests/tBTCUSD_3h_20260324_170603.json`
2. incumbent score anchor only where already recorded in tracked RI evidence:
   - `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json` → `comparisons.incumbent_same_head_control`

### Background context only

The following file remains background context only and is not part of the executable comparison surface:

- `config/strategy/champions/tBTCUSD_3h.json`

## Exact mapped comparison fields

Only the explicitly mapped, semantically overlapping fields below may be compared on this surface.

### Field map

| Comparison dimension      | Candidate source                                                                                      | Incumbent source                                                                                                      | Allowed use                                                                                   |
| ------------------------- | ----------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| validation score          | `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json` → `validation_winner.score` | `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json` → `comparisons.incumbent_same_head_control` | allowed as citation-backed score comparison only                                              |
| total return (fractional) | `results/hparam_search/run_20260324_174006/validation/trial_001.json` → `score.metrics.total_return`  | `results/backtests/tBTCUSD_3h_20260324_170603.json` → `metrics.total_return`                                          | allowed because both are already tracked as fractional return values                          |
| profit factor             | `results/hparam_search/run_20260324_174006/validation/trial_001.json` → `score.metrics.profit_factor` | `results/backtests/tBTCUSD_3h_20260324_170603.json` → `metrics.profit_factor`                                         | allowed                                                                                       |
| max drawdown (fractional) | `results/hparam_search/run_20260324_174006/validation/trial_001.json` → `score.metrics.max_drawdown`  | `results/backtests/tBTCUSD_3h_20260324_170603.json` → `metrics.max_drawdown`                                          | allowed                                                                                       |
| trade count               | `results/hparam_search/run_20260324_174006/validation/trial_001.json` → `score.metrics.num_trades`    | `results/backtests/tBTCUSD_3h_20260324_170603.json` → `metrics.total_trades`                                          | allowed                                                                                       |
| score version provenance  | `results/hparam_search/run_20260324_174006/validation/trial_001.json` → `score.score_version`         | not applicable                                                                                                        | may be cited to qualify the candidate score surface only, not as a symmetric comparison field |

## Explicitly disallowed derivations

The following are out of scope on this surface:

- local runtime materialization of slice8 into `run_backtest.py`
- local recomputation or backfill of incumbent score from unmatched artifact shapes
- use of `tools/compare_backtest_results.py` as if the candidate and incumbent artifacts were already shape-equivalent inputs for that tool
- synthetic normalization that converts candidate and incumbent artifacts into a fabricated common runtime schema
- implicit creation of a new RI canonical materialization contract
- comparison of unmapped fields merely because their names look similar
- use of `summary.total_return` from the incumbent artifact when the mapped candidate return is fractional rather than percent-scaled
- use of bootstrap champion config as an execution input or second decision comparator

## Incumbent score rule

Incumbent score references on this surface are **citation-only**.

They may be used only where the incumbent score is already recorded in tracked RI evidence.

This packet does **not** authorize:

- local derivation of incumbent score from the backtest artifact
- local recomputation of incumbent score under a new scoring pass
- backfilling a synthetic incumbent score into a new artifact for this packet

## Allowed interpretation and output language

A later packet that uses this surface may describe the outcome only as one of the following:

- `candidate stronger on the mapped non-runtime surface`
- `candidate weaker on the mapped non-runtime surface`
- `inconclusive on the mapped non-runtime surface`

That later packet must also state explicitly that:

- the outcome is limited to this slice8-specific governed artifact-matrix surface
- the outcome is not by itself a runtime comparison, promotion decision, champion decision, or writeback authorization

## Constraints on the next packet using this surface

Any next packet that uses this surface must:

1. cite every artifact used from the allowed artifact chain
2. use only the mapped fields listed above
3. keep bootstrap champion context out of the executable comparison surface
4. keep outcome language at comparison-only level unless a later packet explicitly broadens scope
5. restate that runtime/default behavior remains unchanged

## Bottom line

The exact valid non-runtime evidence surface for the slice8 incumbent comparison is now defined.

That surface is:

- a **slice8-specific governed artifact-matrix**,
- using only the listed tracked artifact chain,
- using only explicitly mapped semantically overlapping fields,
- with incumbent score treated as citation-only,
- and with runtime materialization, artifact homogenization, and new canonical materialization contracts kept out of scope.
