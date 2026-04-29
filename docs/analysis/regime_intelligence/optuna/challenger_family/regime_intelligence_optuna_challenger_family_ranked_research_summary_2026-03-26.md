# Regime Intelligence challenger family — ranked research summary

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `research-summary only / RI-family-internal ordering / no comparison-readiness-promotion reopening`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this file consolidates tracked RI-family research outputs into a ranked continuation surface and therefore requires strict wording discipline to avoid reopening comparison, readiness, or promotion scope.
- **Required Path:** `Quick`
- **Objective:** Record a short RI-family-internal ranked research summary for slice7, slice8, and slice9, while keeping incumbent context in a separate reference-only section.
- **Scope IN:** one docs-only summary under `docs/governance/`; RI-family-internal ordering of slice7/slice8/slice9 using already tracked artifacts; explicit non-claim language; incumbent same-head control as reference-only context.
- **Scope OUT:** no source-code changes, no config changes, no runtime/default changes, no new run execution, no reopening of incumbent comparison, no readiness claim, no promotion claim, no writeback authority, no new evidence class.
- **Expected changed files:** `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_ranked_research_summary_2026-03-26.md`
- **Max files touched:** `1`

### Skill usage

- No repository skill is evidenced for this docs-only governance summary.
- This packet uses manual governance review only.
- Any future skill coverage for this summary shape remains `föreslagen` until implemented and verified.

### Gates required

For this packet itself:

- markdown/file validation only

Interpretation discipline that must remain true:

- RI slices may be ordered only inside the open RI-family research lane
- slice7, slice8, and slice9 must be stated as tied on tracked validation outcome
- duplicate ratio may be used only as a research-process tie-breaker, not as trading-performance proof
- incumbent same-head control must remain in a separate reference-only section, not in the RI rank table
- no sentence may reopen comparison, readiness, or promotion by implication

## Purpose

This document records only a **research-lane-internal continuation ordering** for the currently tracked RI challenger family surfaces.

It is downstream of the open RI research / Optuna lane packet:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`

That lane remains explicitly limited to **RI-family-internal research only** and does not reopen:

- incumbent comparison
- readiness
- promotion

## Evidence base

Primary tracked artifacts used here:

- slice7 run meta: `results/hparam_search/run_20260324_171511/run_meta.json`
- slice7 validation winner: `results/hparam_search/run_20260324_171511/validation/trial_001.json`
- slice8 run meta: `results/hparam_search/ri_slice8_launch_20260326/run_meta.json`
- slice8 validation winner: `results/hparam_search/ri_slice8_launch_20260326/validation/trial_001.json`
- slice9 tracked research summary: `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice9_20260326.json`
- incumbent same-head control reference artifact: `results/backtests/tBTCUSD_3h_20260324_170603.json`

## RI-family-internal ranking (research only)

### Equality statement

Across the tracked RI-family artifacts, **slice7, slice8, and slice9 are equal on the currently tracked validation outcome**:

- validation score: `0.26974911658712664`
- profit factor: `1.8845797002042906`
- max drawdown: `0.027808774550017137`
- trades: `63`

Accordingly, the ordering below is **not a trading-performance ranking**.
It is only a **research continuation ordering** based on search-surface cleanliness after the tied validation outcome is acknowledged.

| Rank | Surface | Validation score | PF | Max DD | Trades | Duplicate ratio | Research interpretation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | slice8 | 0.26974911658712664 | 1.8845797002042906 | 0.027808774550017137 | 63 | 0.2604166666666667 | Same tracked validation outcome as slice7/slice9, with the cleanest observed search surface of the three. Preferred continuation surface. |
| 2 | slice9 | 0.26974911658712664 | 1.8845797002042906 | 0.027808774550017137 | 63 | 0.3466666666666667 | Same tracked validation outcome as slice7/slice8. Useful robustness corroboration at a non-slice8 management tuple, but less process-clean than slice8. |
| 3 | slice7 | 0.26974911658712664 | 1.8845797002042906 | 0.027808774550017137 | 63 | 0.90625 | Same tracked validation outcome as slice8/slice9, but with the noisiest search surface by duplicate ratio. Informative, not preferred for next research continuation. |

## Why slice8 is the preferred continuation surface

Slice8 is preferred **only as the next RI-family research surface**, for these bounded reasons:

1. It matches the tracked validation outcome already seen in slice7 and slice9.
2. Its duplicate ratio (`0.2604166666666667`) is materially cleaner than slice9 (`0.3466666666666667`) and far cleaner than slice7 (`0.90625`).
3. Its completed tracked research run is already recorded inside the current research lane, which makes it a cleaner continuation surface than reopening a noisier search neighborhood.

This means:

- **slice8 is the preferred continuation surface for future RI research work**

This does **not** mean:

- slice8 has proven superior trading performance versus slice7 or slice9
- slice8 is comparison-ready
- slice8 is readiness-ready
- slice8 is promotion-ready

## Incumbent same-head control (reference only)

The incumbent same-head control remains **reference context only** and is **not part of the RI-family rank table above**.

Reference artifact:

- `results/backtests/tBTCUSD_3h_20260324_170603.json`

Tracked reference metrics from that artifact:

- total return: `0.42059270143001415%`
- profit factor: `1.8721119891064304`
- max drawdown: `0.014705034784627329`
- trades: `37`

This section exists only to preserve context about the already tracked same-head control artifact.
It does **not** reopen incumbent comparison and must not be read as a merged ranking surface with the RI table above.

## Bounded conclusions

Allowed conclusions from this document:

- slice7, slice8, and slice9 are tied on tracked validation outcome
- slice8 is the cleanest current RI-family continuation surface by duplicate-ratio tie-breaker
- slice9 adds robustness evidence at a different management tuple
- slice7 remains informative but is the least attractive continuation surface among the three on research-process cleanliness

Disallowed conclusions from this document:

- RI has now won an incumbent comparison
- this document reopens readiness or promotion
- duplicate ratio proves superior trading quality
- incumbent and RI surfaces are now jointly ranked in one governed comparison table

## Research recommendation

If a later RI-only follow-up is separately opened, the preferred continuation order should be:

1. continue from slice8 first
2. retain slice9 as corroborating robustness evidence
3. treat slice7 as already informative but no longer the preferred next research surface

That recommendation is still **research-lane only** and does not authorize any comparison, readiness, or promotion action.
