# Regime Intelligence cutover readiness assessment

Date: 2026-03-17
Slice: `feature/regime-intelligence-cutover-analysis-v1`
Status: `analysis-only / not a cutover approval`

## Executive summary

Regime Intelligence is already implemented, integrated, and functional as an opt-in runtime path.

This readiness assessment covers only the question:

> Is the repository ready to propose a separate default-cutover slice?

Current answer: **not yet ready for default cutover approval**.

## Current status snapshot

| Dimension                  | Status      | Notes                                                                            |
| -------------------------- | ----------- | -------------------------------------------------------------------------------- |
| RI implementation          | Ready       | canonical module exists and is integrated                                        |
| Shim retirement            | Ready       | legacy shim path has been retired from runtime entrypoints                       |
| Runtime opt-in path        | Ready       | `authority_mode=regime_module` is supported                                      |
| Default authority          | Not changed | remains intentionally `legacy`                                                   |
| Governance sign-off        | Partial     | OFF-mode parity sign-off is restored; default-cutover governance is still open   |
| Operational config surface | Partial     | `authority_mode` is governed; broader RI runtime control surface remains limited |

## Readiness criteria for a future default-cutover proposal

A future `feature/regime-intelligence-default-cutover-v1` slice should only be considered if all of the following are satisfied:

1. OFF-mode parity is PASS according to the DoD artifact contract.
2. Legacy vs `regime_module` output differences are explicitly cataloged.
3. Determinism and pipeline invariant selectors are green.
4. Governance review concludes that remaining differences are acceptable for promotion.
5. Cutover mechanics (runtime config, champion path, operational control surface) are explicit and reviewable.

## Current blockers

### 1. Behavior delta summary is missing

The repo has selectors but lacks a consolidated cutover-focused decision record for expected vs unacceptable differences.

### 2. Operational governance surface is only partially ready

`authority_mode` is correctly preserved as a governance control, but the full RI control surface is not yet represented as a first-class governed runtime interface.

## Governance stance for this slice

- keep `authority_mode`
- do not change default authority
- do not alter precedence/fallback logic
- do not interpret analysis artifacts as promotion approval
- use this slice only to decide whether a later cutover slice is justified

## Required evidence to attach before any cutover decision

- exact selector outcomes from this analysis slice
- updated parity artifact matrix
- explicit note on baseline artifact lineage
- explicit risk statement for any known legacy vs regime deltas
- final governance recommendation: `ready`, `ready with prerequisites`, or `not ready`

## Parity evidence update

- The repo-visible `003` `FAIL` artifact remains synthetic test output and must not be treated as sign-off evidence.
- The governed baseline reset rerun completed with canonical artifact `results/evaluation/ri_p1_off_parity_v1_ri-20260317-001.json` and `parity_verdict=PASS`.
- Supplemental retained evidence exists under `docs/audit/refactor/regime_intelligence/evidence/` and is linked by manifest SHA256 values.
- The parity evidence gap identified earlier is therefore closed for the frozen OFF-mode spec, even though default-cutover governance remains open.

## Reproducibility verdict

**OFF-mode sign-off evidence is now reproducible from tracked repository state for the governed rerun artifact chain.**

Current classification:

- tracked repo state preserves the parity contract, tooling shape, the governed rerun PASS artifact, and the retained baseline/candidate/manifest evidence for that rerun
- the older March sign-off chain is still not independently reconstructable from tracked repository contents alone
- current governance discussion should therefore rely on the governed rerun evidence chain, not the older missing March artifact chain

Recommended next step:

- keep default authority unchanged and evaluate remaining cutover blockers against the now-restored governed parity evidence chain

## Observed slice gates (2026-03-17)

Executed in this slice:

- `python -m black --check tests/governance/test_regime_intelligence_cutover_parity.py` → `PASS`
- `python -m ruff check tests/governance/test_regime_intelligence_cutover_parity.py` → `PASS`
- `python -m pytest -q tests/governance/test_regime_intelligence_cutover_parity.py` → `PASS` (`10 passed`)
- `python -m pytest -q tests/governance/test_authority_mode_resolver.py` → `PASS` (`14 passed`)
- `python -m pytest -q tests/backtest/test_evaluate_pipeline.py -k "authority_mode or source_invariant"` → `PASS` (`6 passed`)
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py` → `PASS` (`3 passed`)
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` → `PASS` (`1 passed`)
- `python scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev` → `PASS`

Intentionally not executed:

- `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
  - reason: this slice makes no feature-pipeline parity claim beyond the rerun selectors already listed.

Slice-local machine-readable gate summary:

- `artifacts/regime_intelligence/ri_cutover_analysis_gate_summary_2026-03-17.json`

## Preliminary recommendation

Proceed with the analysis slice. Do **not** open a default-cutover implementation slice until the parity chain and governance evidence are materially stronger than they are today. The immediate follow-up should be evidence recovery or a governed parity rerun, not runtime remediation.

Updated interpretation from current tracked repo state:

- do **not** open a default-cutover implementation slice yet
- do keep default authority unchanged
- do treat the governed rerun evidence chain as the active parity baseline for further cutover analysis
- the immediate follow-up should now be delta-summary/governance review work, not runtime remediation
