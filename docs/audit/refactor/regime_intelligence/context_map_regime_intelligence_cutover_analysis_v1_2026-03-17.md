## Context Map

### Current Runtime Authority Surfaces

| Area                | Current state              | Evidence anchor                                                                                           |
| ------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------- |
| RI implementation   | Implemented and integrated | `src/core/intelligence/regime/*`, `src/core/strategy/evaluate.py`, `src/core/strategy/decision_sizing.py` |
| Shim retirement     | Completed                  | retired `src/core/strategy/regime_intelligence.py`; runtime entrypoints import canonical helpers directly |
| Runtime opt-in path | Present and functional     | `authority_mode="regime_module"` handled in `evaluate.py` and resolver tests                              |
| Default authority   | Intentionally still legacy | `src/core/config/schema.py`, `config/runtime.json`                                                        |
| Governance sign-off | Not yet complete           | `docs/ideas/REGIME_INTELLIGENCE_DOD_P1_P2_2026-02-27.md`, parity artifact status                          |

### Existing Selector / Evidence Anchors

| Anchor                                                                                                     | Purpose                                     | Current role in cutover analysis                                                                 |
| ---------------------------------------------------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| `tests/governance/test_authority_mode_resolver.py`                                                         | precedence / fallback contract              | baseline authority semantics                                                                     |
| `tests/backtest/test_evaluate_pipeline.py`                                                                 | evaluate-path authority + source invariants | runtime opt-in / legacy parity selectors                                                         |
| `tests/backtest/test_backtest_determinism_smoke.py`                                                        | determinism replay                          | cutover safety prerequisite                                                                      |
| `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` | pipeline invariant                          | cutover safety prerequisite                                                                      |
| `results/evaluation/ri_p1_off_parity_v1_ri-20260303-003.json`                                              | repo-visible OFF-mode parity artifact       | synthetic/local test `FAIL`, not sign-off evidence                                               |
| `docs/audit/RI_P1_OFF_SIGNOFF_2026-03-04.md`, `logs/skill_runs.jsonl`                                      | March sign-off attestation                  | documented/logged PASS lineage, but log is local-only and artifact file absent from tracked tree |
| GitHub Actions run `22663511442`                                                                           | CI retention check                          | workflow retained `bandit-report` only; no parity artifact bundle found                          |
| `scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev`                                 | artifact validation                         | verifies RI OFF parity evidence quality                                                          |

### Known Evidence Gaps To Analyze

| Gap                                                                            | Why it matters for future cutover                                              |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| Repo-visible OFF-mode artifact is synthetic test output, not approved evidence | prevents the current snapshot from serving as a cutover parity proof           |
| Referenced baseline/PASS artifacts are not present in the repo                 | prevents clean verification chain for parity claims                            |
| Sign-off logs are ignored/local-only and CI retained no parity artifact bundle | prevents reproduction of the March PASS chain from tracked repo state alone    |
| Legacy vs regime output deltas are not yet summarized in one place             | blocks explicit cutover-risk review                                            |
| Operational config surface is only partially exposed through config authority  | matters for governance and rollout control during cutover                      |
| Active champion/default config promotion path is not yet formalized            | affects how a future default cutover would actually land in production/runtime |

### Approved Slice Deliverables

| Deliverable                                                                      | Purpose                                                               |
| -------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `docs/analysis/regime_intelligence_default_cutover_gap_analysis_2026-03-17.md`   | exact gap analysis for a future default cutover                       |
| `docs/analysis/regime_intelligence_parity_artifact_matrix_2026-03-17.md`         | traceability matrix across selectors, artifacts, and readiness claims |
| `docs/analysis/regime_intelligence_cutover_readiness_2026-03-17.md`            | governance-oriented readiness assessment                              |
| `artifacts/regime_intelligence/ri_cutover_analysis_gate_summary_2026-03-17.json` | machine-readable gate summary for this analysis slice                 |
| `tests/governance/test_regime_intelligence_cutover_parity.py`                    | focused authority/cutover parity assertions without runtime changes   |

### Non-Negotiable Boundaries

- No changes to runtime logic, config defaults, or authority precedence
- No committed new baselines under `results/**`
- No promotion of RI to default authority in this slice
- No claim that this slice itself approves cutover
- Any slice-generated auxiliary analysis output belongs under `artifacts/regime_intelligence/`
