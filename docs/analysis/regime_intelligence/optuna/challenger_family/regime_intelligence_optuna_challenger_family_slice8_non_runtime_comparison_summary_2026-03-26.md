# Regime Intelligence challenger family — slice8 non-runtime comparison summary

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `comparison-only / mapped non-runtime surface applied / no execution or promotion approved`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet records an outcome label on the already approved slice8-specific non-runtime comparison surface, but does not approve execution, promotion, or runtime/default change
- **Required Path:** `Quick`
- **Objective:** Apply the already defined slice8-specific governed non-runtime comparison surface to the tracked candidate and incumbent artifacts, and record the comparison-only outcome using the allowed surface language.
- **Candidate:** `slice8 full tuple as lead RI research candidate`
- **Base SHA:** `13bfbc2a`

### Scope

- **Scope IN:** comparison-only interpretation on the already approved slice8 non-runtime surface; explicit citation of the allowed artifacts; explicit mapped-field comparison; explicit non-promotion boundary.
- **Scope OUT:** no source-code changes, no config changes, no tests, no runtime materialization, no incumbent-score recomputation, no new comparison tooling, no new canonical RI comparison contract, no promotion decision, no champion replacement, no writeback approval.
- **Expected changed files:** `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_non_runtime_comparison_summary_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- cite only the allowed tracked artifact chain
- use only the explicitly mapped fields from the non-runtime surface packet
- keep incumbent score citation-only
- keep outcome language limited to the approved mapped-surface labels

### Stop Conditions

- any wording that implies runtime superiority has now been proven
- any wording that implies promotion readiness is approved
- any wording that silently reinterprets trade count as an unconditional plus
- any wording that silently suppresses the worse candidate drawdown
- any wording that expands this slice8-specific packet into a general RI comparison standard

### Output required

- reviewable comparison-only packet
- explicit mapped field table
- bounded outcome label
- explicit residual cautions and out-of-scope boundary

## Purpose

This packet applies the already defined **slice8-specific governed non-runtime comparison surface** to the tracked candidate and incumbent artifacts.

Its role is intentionally narrow.

It does:

- compare only the explicitly mapped fields already approved on that surface
- record the bounded outcome label required by that surface
- disclose both the candidate advantages and the incumbent advantages on the mapped surface

It does **not**:

- approve execution
- approve runtime materialization
- approve promotion
- approve champion replacement
- approve writeback
- approve runtime/default change
- create a new canonical RI comparison contract

## Upstream governed chain

This packet is downstream of the following tracked packets:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_candidate_definition_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_incumbent_comparison_prep_packet_2026-03-26.md`
- `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_incumbent_comparison_execution_blocker_summary_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_comparison_input_surface_decision_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_non_runtime_comparison_surface_packet_2026-03-26.md`

Relevant carried-forward interpretation:

- slice8 remains the lead RI research candidate
- incumbent same-head control remains the only primary comparator surface
- runtime materialization remains blocked and out of scope
- the comparison must remain slice8-specific and non-runtime only

## Allowed artifact chain actually used

This packet uses only the allowed tracked artifacts from the non-runtime surface packet.

### Candidate-side artifacts used

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json`
- `results/hparam_search/run_20260324_174006/validation/trial_001.json`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_execution_outcome_signoff_summary_2026-03-24.md`

### Incumbent-side artifacts used

- `results/backtests/tBTCUSD_3h_20260324_170603.json`
- incumbent score citation carried from `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json` → `comparisons.incumbent_same_head_control`

## Exact mapped comparison

Only the fields already allowed by the non-runtime surface packet are used below.

### Mapped field outcomes

| Comparison dimension | Candidate value | Incumbent value | Surface reading |
| --- | --- | --- | --- |
| validation score | `0.26974911658712664` | `0.2616884080730424` | candidate higher |
| total return (fractional) | `0.0319034694105756` | `0.004205927014300142` | candidate higher |
| profit factor | `1.8845797002042906` | `1.8721119891064304` | candidate higher |
| max drawdown (fractional) | `0.027808774550017137` | `0.014705034784627329` | incumbent better |
| trade count | `63` | `37` | candidate higher activity; not treated as an unconditional plus |

### Interpretation of the mapped table

On the allowed mapped surface:

- the candidate is stronger on score
- the candidate is stronger on return
- the candidate is slightly stronger on profit factor
- the incumbent is clearly stronger on drawdown containment
- the candidate shows higher trade count, which is disclosed as context rather than assumed benefit

## Outcome label

The governed outcome label for this packet is:

- `candidate stronger on the mapped non-runtime surface`

## Why that label is used

This label is used because the candidate is stronger on the three most direct mapped performance dimensions available on this surface:

1. validation score
2. total return
3. profit factor

That said, the label is intentionally bounded.

It does **not** mean:

- candidate stronger in a canonical runtime comparison
- candidate ready for champion promotion
- candidate approved for writeback
- candidate has resolved the runtime-materialization blocker
- candidate has won every mapped dimension

The incumbent remains stronger on drawdown on this surface, and that drawback must stay visible in any downstream reference.

## Required cautions

### Drawdown caution stays live

The candidate's mapped max drawdown is worse than the incumbent's on this surface:

- candidate: `0.027808774550017137`
- incumbent: `0.014705034784627329`

This prevents any honest reading of this packet as a clean all-dimensions victory.

### Trade count is context, not a hidden plus

The candidate's trade count is higher:

- candidate: `63`
- incumbent: `37`

This packet does **not** interpret that fact as automatically better.

It is disclosed only as activity context on the mapped surface.

### Incumbent score remains citation-only

The incumbent score used here comes only from already tracked RI evidence:

- `results/evaluation/tBTCUSD_3h_ri_challenger_family_slice8_20260324.json` → `comparisons.incumbent_same_head_control`

This packet does **not** authorize or perform:

- score recomputation from the incumbent backtest artifact
- synthetic backfilling of a new incumbent score artifact
- homogenization of the candidate and incumbent artifacts into a fabricated common runtime schema

## Interpretation boundary

### Approved by this packet

This packet approves only the following bounded interpretation:

- on the slice8-specific governed non-runtime comparison surface, the candidate is stronger than the incumbent overall
- that statement is limited to the mapped fields and the tracked artifact chain used here
- the comparison remains evidence-only and non-runtime

### Not approved by this packet

This packet does **not** approve:

- execution
- runtime materialization
- promotion readiness
- champion replacement
- champion writeback
- runtime/default change
- any claim that the comparison is canonical, production-grade, or cutover-grade

## Residual cautions

### 1. This is not a runtime-complete decision surface

The comparison surface used here exists precisely because runtime materialization remains blocked.

Therefore this packet cannot be read as a substitute for a successfully governed runtime comparison path.

### 2. Metadata quirk remains open

Candidate-adjacent run artifacts still disclose `merged_config.strategy_family=legacy` as a metadata quirk.

This packet does not resolve that issue and does not suppress it.

### 3. Surface scope remains slice8-specific

This packet must not be generalized into a broader repository-wide or RI-wide comparison standard.

Its scope is the slice8 lead research candidate only.

## Bottom line

Using only the already approved mapped non-runtime comparison surface and the allowed tracked artifact chain, the correct bounded label is:

- `candidate stronger on the mapped non-runtime surface`

That is the strongest statement this packet makes.

It is still only a **comparison-only** statement.

It is **not** execution approval, promotion approval, champion replacement approval, or runtime/default authority change.
