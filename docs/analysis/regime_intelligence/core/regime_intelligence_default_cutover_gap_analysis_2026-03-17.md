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
- Governance sign-off: OFF-mode parity återställd, men default-cutover ej godkänd
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

### 1. OFF-mode parity evidence is restored for the governed rerun, but legacy lineage remains historically incomplete

- Current repo-visible artifact: `results/evaluation/ri_p1_off_parity_v1_ri-20260303-003.json`
- Current repo-visible verdict: `FAIL`, but this file matches the intentionally failing test fixture in `tests/backtest/test_compare_backtest_results.py::test_main_ri_off_parity_fail_returns_1` (`run_id=ri-20260303-003`, `git_sha=abc1234`, symbol `tTESTBTC:TESTUSD`, timeframe `1h`).
- Conclusion: the visible `003` artifact is a local synthetic/test artifact, not reliable sign-off evidence for runtime parity.
- Governed rerun artifact now present: `results/evaluation/ri_p1_off_parity_v1_ri-20260317-001.json` with `parity_verdict=PASS`.
- Supplemental governed rerun evidence is retained under `docs/audit/refactor/regime_intelligence/evidence/`.
- The older March artifact lineage remains historically incomplete, but the repo no longer lacks a tracked PASS evidence chain for the frozen OFF-mode spec.

### 2. Legacy vs regime output delta map is not yet consolidated

Existing tests prove important invariants, but the repository does not yet have a single cutover-focused summary that answers:

- where outputs match,
- where outputs differ,
- whether differences are expected/accepted,
- and which differences would block default promotion.

### 3. Governance readiness is not yet explicitly signed off for default cutover

The DoD requirement for a valid parity chain is now satisfied by the governed rerun, but governance confirmation for default cutover still requires a reviewed delta summary and explicit promotion decision.

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

## Current verified legacy vs `regime_module` delta summary

The current tracked selectors support a narrow but important summary of verified differences.

### Verified expected differences

1. **Authoritative regime source differs by mode**

- `legacy` resolves authority through `regime_unified.detect_regime_unified`
- `regime_module` resolves authority through `regime.detect_regime_from_candles`

2. **Resolved authoritative regime may differ under identical stubbed inputs**

- the cutover parity selector intentionally demonstrates a scenario where `legacy` yields `ranging`
- under the same controlled test setup, `regime_module` yields `bull`
- this is currently treated as an _observed mode difference_, not as a defect by itself

3. **Observability captures the split explicitly**

- `authority_mode`
- `authority_mode_source`
- `authoritative_source`
- `authority`
- `shadow`
- `mismatch`

### Verified invariants that still hold across both modes

1. **Within-mode determinism holds**

- repeated identical inputs remain stable in `legacy`
- repeated identical inputs remain stable in `regime_module`

2. **Decision safety contract remains intact**

- `decision_input` remains `False` in the shadow observability payload
- current selectors therefore support the claim that shadow-path observability does not itself inject decision-path behavior

3. **Authority precedence/fallback remains deterministic**

- canonical `multi_timeframe.regime_intelligence.authority_mode` still wins over alias inputs
- invalid canonical/alias values still fall back deterministically to `legacy`

4. **Pipeline invariants remain green**

- determinism replay remains green
- pipeline component order hash remains green

### Current governance interpretation of those deltas

- The verified mode differences are currently sufficient to say that `legacy` and `regime_module` are **not** being treated as cross-mode equality surfaces.
- The existing evidence instead supports a narrower statement: both modes are deterministic and reviewable, while their authority path and resulting regime can differ in controlled scenarios.
- A future default-cutover proposal therefore still needs an explicit judgment about which observed differences are acceptable for promotion and which would be blocking.

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
- The repository now also contains the governed rerun PASS artifact `results/evaluation/ri_p1_off_parity_v1_ri-20260317-001.json` plus retained baseline/candidate/manifest evidence under `docs/audit/refactor/regime_intelligence/evidence/`.
- The older documented `005` artifact and `results/evaluation/ri_p1_off_parity_v1_baseline.json` are still not committed in the current git snapshot.
- `tools/compare_backtest_results.py` records `baseline_artifact_ref` as artifact metadata only; it does not dereference or validate that the referenced baseline file exists. A missing baseline file therefore does not mechanically produce `FAIL`.
- The currently visible `003` `FAIL` likewise does not demonstrate runtime drift. In this repo snapshot it is best explained as synthetic test output. What remains unproven is the March PASS chain, because the approved baseline/candidate inputs are not preserved in tracked repository evidence.

## Artifact provenance inventory

### Tracked in repository state

- `docs/audit/RI_P1_OFF_SIGNOFF_2026-03-04.md`
- `docs/audit/PR_RI_P1_OFF_SIGNOFF_2026-03-04.md`
- `docs/audit/MERGE_READINESS_PR58_2026-03-04.md`
- `results/evaluation/ri_p1_off_parity_v1_ri-20260317-001.json`
- `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_baseline_rows_ri-20260317-001.json`
- `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_candidate_rows_ri-20260317-001.json`
- `docs/audit/refactor/regime_intelligence/evidence/ri_p1_off_parity_v1_manifest_ri-20260317-001.json`
- `docs/ideas/REGIME_INTELLIGENCE_DOD_P1_P2_2026-02-27.md`
- `.github/skills/ri_off_parity_artifact_check.json`
- `tools/compare_backtest_results.py`
- `scripts/run/run_backtest.py`
- `tests/backtest/test_compare_backtest_results.py`

These tracked files now preserve the parity contract, the comparator/tooling shape, the governed rerun PASS artifact chain, and the human sign-off claims.

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

- **A) Governed PASS-körningen kan rekonstrueras från trackade inputs:** yes, for the governed rerun evidence chain anchored by `ri-20260317-001`.
- **B) Historiska March-artifacts kan rekonstrueras från tracked state:** not demonstrated.
- Formal conclusion for current repo state: **the governed OFF-mode sign-off evidence chain is now reproducible from tracked repository state, but default-cutover readiness remains blocked by non-parity governance gaps**.

## Implication for cutover readiness

- The active blocker is no longer absence of a tracked PASS parity chain.
- Remaining blockers are cutover-governance oriented: accepted delta summary, promotion criteria, and operational control-surface review.
- Before any future default-cutover proposal, the repo needs either:
  - explicit governance acceptance of the current governed rerun evidence as sufficient cutover input, and
  - a reviewed cutover-focused decision record for legacy vs `regime_module` differences.

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

### 2. Post-rerun governance decision path

- Use the governed rerun evidence chain as the active OFF-mode parity anchor under frozen spec `ri_p1_off_parity_v1`.
- Build the missing cutover-focused delta summary for legacy vs `regime_module` behavior.
- Review whether the current operational control surface is sufficient for a future default-cutover slice.
- Keep the rerun artifacts as parity evidence; do not reinterpret them as automatic default-cutover approval.

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
