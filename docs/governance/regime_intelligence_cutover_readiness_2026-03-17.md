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
| Governance sign-off        | Not ready   | repo-verifiable OFF-mode parity PASS chain is incomplete                         |
| Operational config surface | Partial     | `authority_mode` is governed; broader RI runtime control surface remains limited |

## Readiness criteria for a future default-cutover proposal

A future `feature/regime-intelligence-default-cutover-v1` slice should only be considered if all of the following are satisfied:

1. OFF-mode parity is PASS according to the DoD artifact contract.
2. Legacy vs `regime_module` output differences are explicitly cataloged.
3. Determinism and pipeline invariant selectors are green.
4. Governance review concludes that remaining differences are acceptable for promotion.
5. Cutover mechanics (runtime config, champion path, operational control surface) are explicit and reviewable.

## Current blockers

### 1. Repo-verifiable OFF-mode parity evidence is incomplete

The currently visible `results/evaluation/ri_p1_off_parity_v1_ri-20260303-003.json` file is not sufficient for sign-off and should not be treated as runtime parity evidence. Its metadata matches the intentionally failing unit test fixture in `tests/backtest/test_compare_backtest_results.py`.

### 2. Evidence chain is incomplete

The referenced baseline artifact is not present in the current repository snapshot, and the March PASS artifact `results/evaluation/ri_p1_off_parity_v1_ri-20260303-005.json` is documented in sign-off records but absent from the tracked git tree.

### 3. Behavior delta summary is missing

The repo has selectors but lacks a consolidated cutover-focused decision record for expected vs unacceptable differences.

### 4. Operational governance surface is only partially ready

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

## Lineage finding for this slice

- Current repo-visible `003` `FAIL` artifact is best classified as local synthetic test output, not a live parity regression signal.
- Missing baseline/`005` repository artifacts mean the repo snapshot cannot independently reproduce the March PASS chain from tracked files alone.
- Because `baseline_artifact_ref` is metadata-only in `tools/compare_backtest_results.py`, a missing baseline file cannot by itself explain a `FAIL`; the remaining issue is provenance and reproducibility, not a confirmed runtime behavior break.
- `logs/skill_runs.jsonl` confirms a local `PASS` attestation for `run_id=c8c3b77cd2c1`, but the file is ignored and not tracked.
- GitHub Actions retention for PR #58 currently exposes only `bandit-report`; no CI-retained parity artifact or baseline bundle was found.

## Reproducibility verdict

**sign-off evidence cannot be reproduced from tracked repository state**.

Current classification:

- tracked repo state preserves the parity contract, tooling shape, and human sign-off claims
- tracked repo state does **not** preserve the PASS artifact, baseline artifact, or raw decision-row inputs needed to replay the March sign-off chain
- therefore the March PASS chain is not independently reconstructable from tracked repository contents alone

Recommended next step:

- perform a **governed parity rerun** under the frozen `ri_p1_off_parity_v1` spec unless the missing PASS artifact plus baseline/candidate inputs can be recovered from an external retention source

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
