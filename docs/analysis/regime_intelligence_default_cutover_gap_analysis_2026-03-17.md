# Regime Intelligence default cutover gap analysis

Date: 2026-03-17
Slice: `feature/regime-intelligence-cutover-analysis-v1`

## Purpose

This document analyzes the remaining gaps for a **future default runtime cutover** of Regime Intelligence.

It does **not** question whether Regime Intelligence is implemented. The current working status is:

- RI implementation: klar
- Shim retirement: klar
- Runtime opt-in path: klar
- Default authority: fortfarande legacy (medvetet)
- Governance sign-off: ej klar
- Operational config surface: delvis klar

## Analysis questions for this slice

1. Does OFF-mode parity satisfy the DoD-defined PASS contract?
2. What verified differences exist between legacy and `regime_module` outputs?
3. Which edge cases produce divergent behavior and how material are they?
4. Is current RI behavior deterministic and repeatable under the approved selectors?
5. What governance risks remain before any default-cutover decision?

## Verified starting points

- The canonical RI module is already active as the opt-in path.
- Default authority remains `legacy` by design.
- `authority_mode` remains an intentional governance control and must stay in place.
- Existing selectors already cover authority precedence, source attribution, deterministic `regime_module` routing, determinism replay, and pipeline invariants.

## Known cutover blockers to evaluate

### 1. OFF-mode parity evidence is incomplete

- Current repo-visible artifact: `results/evaluation/ri_p1_off_parity_v1_ri-20260303-003.json`
- Current repo-visible verdict: `FAIL`, but this file matches the intentionally failing test fixture in `tests/backtest/test_compare_backtest_results.py::test_main_ri_off_parity_fail_returns_1` (`run_id=ri-20260303-003`, `git_sha=abc1234`, symbol `tTESTBTC:TESTUSD`, timeframe `1h`).
- Conclusion: the visible `003` artifact is a local synthetic/test artifact, not reliable sign-off evidence for runtime parity.
- Referenced baseline artifact is not present in the repository snapshot, and the March sign-off artifact `results/evaluation/ri_p1_off_parity_v1_ri-20260303-005.json` is documented in audit records but absent from the git tree/history.

### 2. Legacy vs regime output delta map is not yet consolidated

Existing tests prove important invariants, but the repository does not yet have a single cutover-focused summary that answers:

- where outputs match,
- where outputs differ,
- whether differences are expected/accepted,
- and which differences would block default promotion.

### 3. Governance readiness is not yet explicitly signed off

The DoD document still requires a valid parity chain and governance confirmation before default cutover can be considered ready.

### 4. Operational config surface is only partially exposed

Current config authority handling cleanly supports `authority_mode`, but does not yet represent a full RI operational control plane. That may or may not be acceptable for cutover; this slice must assess it explicitly.

## Workstreams for the slice

### A. Parity evidence workstream

- inventory existing parity selectors
- verify current artifact lineage
- classify missing vs failing evidence
- define what must be rerun before a cutover decision

### B. Runtime behavior comparison workstream

- compare legacy and `regime_module` behavior through existing selectors
- record edge cases and whether they are intended
- separate behavioral difference from governance risk

### C. Determinism / repeatability workstream

- verify required determinism and pipeline invariant anchors
- record whether existing selectors are sufficient for a cutover decision
- identify any missing repeatability evidence

### D. Governance readiness workstream

- assess whether the current evidence set supports a future cutover proposal
- identify what must remain opt-in
- identify what must be proven before a `default-cutover-v1` slice can be approved

## Artifact lineage conclusion

- `results/evaluation/ri_p1_off_parity_v1_ri-20260303-003.json` should not be treated as production/sign-off evidence. Its metadata matches the hard-coded failing unit-test invocation in `tests/backtest/test_compare_backtest_results.py`.
- `docs/audit/RI_P1_OFF_SIGNOFF_2026-03-04.md`, `docs/audit/PR_RI_P1_OFF_SIGNOFF_2026-03-04.md`, and `docs/audit/MERGE_READINESS_PR58_2026-03-04.md` consistently reference a different artifact, `results/evaluation/ri_p1_off_parity_v1_ri-20260303-005.json`, with `parity_verdict=PASS`.
- The repository contains supporting local log evidence that the RI OFF parity skill run passed (`logs/skill_runs.jsonl`, `run_id=c8c3b77cd2c1`), but that log file is ignored by `.gitignore` and is not part of tracked repository state. Neither the documented `005` artifact nor `results/evaluation/ri_p1_off_parity_v1_baseline.json` is committed in the current git snapshot.
- `tools/compare_backtest_results.py` records `baseline_artifact_ref` as artifact metadata only; it does not dereference or validate that the referenced baseline file exists. A missing baseline file therefore does not mechanically produce `FAIL`.
- The currently visible `003` `FAIL` likewise does not demonstrate runtime drift. In this repo snapshot it is best explained as synthetic test output. What remains unproven is the March PASS chain, because the approved baseline/candidate inputs are not preserved in tracked repository evidence.

## Artifact provenance inventory

### Tracked in repository state

- `docs/audit/RI_P1_OFF_SIGNOFF_2026-03-04.md`
- `docs/audit/PR_RI_P1_OFF_SIGNOFF_2026-03-04.md`
- `docs/audit/MERGE_READINESS_PR58_2026-03-04.md`
- `docs/ideas/REGIME_INTELLIGENCE_DOD_P1_P2_2026-02-27.md`
- `.github/skills/ri_off_parity_artifact_check.json`
- `tools/compare_backtest_results.py`
- `scripts/run/run_backtest.py`
- `tests/backtest/test_compare_backtest_results.py`

These tracked files preserve the parity contract, the comparator/tooling shape, and the human sign-off claims.

### Present locally or referenced, but not tracked as reproducible sign-off evidence

- `results/evaluation/ri_p1_off_parity_v1_ri-20260303-003.json`
  - present locally, ignored by `.gitignore`
  - synthetic test `FAIL`, not sign-off evidence
- `logs/skill_runs.jsonl`
  - present locally, ignored by `.gitignore`
  - confirms `run_id=c8c3b77cd2c1` reached `PASS`, but does not preserve parity inputs/artifacts in tracked state

### Referenced in documents but absent from tracked repository state

- `results/evaluation/ri_p1_off_parity_v1_ri-20260303-005.json`
  - documented as `PASS` in sign-off and merge-readiness docs
  - not present in git tree/history
- `results/evaluation/ri_p1_off_parity_v1_baseline.json`
  - referenced by DoD/example/docs and artifact metadata contract
  - not present in git tree/history
- `tmp/strict_gates_rerun_20260304c.log`
  - cited in sign-off docs as gate replay source
  - ignored by `.gitignore` and not present in current snapshot

### CI/pipeline retention finding

- GitHub Actions run for PR #58 (`actions/runs/22663511442`) exposes only one retained workflow artifact: `bandit-report`.
- No uploaded CI artifact was found for:
  - `ri_p1_off_parity_v1_ri-20260303-005.json`
  - `ri_p1_off_parity_v1_baseline.json`
  - decision-row baseline/candidate inputs

## Reproducibility status

- **A) PASS-körningen kan rekonstrueras från historiska inputs:** not demonstrated.
- **B) Governed rerun krävs för att återställa sign-off-evidens:** yes, unless the missing PASS artifact and its governing baseline/candidate inputs can be recovered from an external retention source outside tracked repository state.
- Formal conclusion for this slice: **sign-off evidence cannot be reproduced from tracked repository state**.

## Implication for cutover readiness

- The active blocker is an evidence-lineage gap, not a confirmed runtime-regression finding.
- Before any future default-cutover proposal, the repo needs either:
  - recovery of the approved PASS artifact/baseline provenance, or
  - a clean rerun under the frozen parity spec with reviewable inputs and retained evidence.

## Paths forward from the current evidence state

### 1. Evidence recovery path

- Search external retention sources for either:
  - `results/evaluation/ri_p1_off_parity_v1_baseline.json`, or
  - `results/evaluation/ri_p1_off_parity_v1_ri-20260303-005.json`
- Priority retention sources:
  - earlier local workingtrees
  - local `results/evaluation/` outputs on the workstation
  - CI artifact retention outside tracked repo state
  - local skill-run / gate logs
- Recovery only counts if the recovered artifact chain can be tied to:
  - `window_spec_id=ri_p1_off_parity_v1`
  - matching `git_sha`
  - reviewable run metadata for symbol/timeframe/window
- If that proof chain is recovered, baseline provenance may be restored without changing the frozen spec.

### 2. Governed rerun baseline reset path

- If evidence recovery fails, fall back to a governed baseline reset via parity rerun under frozen spec `ri_p1_off_parity_v1`.
- That path must:
  - keep the canonical parity artifact at `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
  - define the canonical baseline reference path explicitly
  - retain reviewable baseline rows, candidate rows, and manifest evidence outside ignored-only paths
  - preserve the full sign-off gate bundle before any PASS may count as governance sign-off
- This path does **not** imply runtime drift; it is a governance reset path for rebuilding a reproducible baseline/evidence chain when external recovery fails.

## Observed gate outcomes in this slice

Observed on `feature/regime-intelligence-cutover-analysis-v1` during the 2026-03-17 analysis run:

- `python -m black --check tests/governance/test_regime_intelligence_cutover_parity.py` → `PASS`
- `python -m ruff check tests/governance/test_regime_intelligence_cutover_parity.py` → `PASS`
- `python -m pytest -q tests/governance/test_regime_intelligence_cutover_parity.py` → `PASS` (`10 passed`)
- `python -m pytest -q tests/governance/test_authority_mode_resolver.py` → `PASS` (`14 passed`)
- `python -m pytest -q tests/backtest/test_evaluate_pipeline.py -k "authority_mode or source_invariant"` → `PASS` (`6 passed`)
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py` → `PASS` (`3 passed`)
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` → `PASS` (`1 passed`)
- `python scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev` → `PASS`

Not run in this slice:

- `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
  - reason: this slice does not claim feature-pipeline parity beyond the approved selectors/artifacts already rerun above.

Machine-readable gate summary for this run is tracked at:

- `artifacts/regime_intelligence/ri_cutover_analysis_gate_summary_2026-03-17.json`

## Out of scope

- changing default `authority_mode`
- changing runtime behavior
- editing authority precedence or fallback logic
- promoting any champion or runtime config
- minting or committing a new parity baseline in this slice

## Exit criterion for this analysis slice

This slice is complete when the repository has a documented, evidence-linked answer to whether a dedicated `feature/regime-intelligence-default-cutover-v1` slice is justified, deferred, or blocked.
