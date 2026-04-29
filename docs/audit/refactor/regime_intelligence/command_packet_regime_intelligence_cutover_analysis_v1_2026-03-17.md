## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH`
- **Risk:** `MED` — why: analysis/tests only, no runtime/default/authority/config changes permitted in this slice
- **Required Path:** `Full`
- **Objective:** Produce a formal gap analysis for a potential future default cutover of Regime Intelligence without changing current runtime behavior, authority precedence, or default `authority_mode`.
- **Candidate:** `regime intelligence cutover analysis v1`
- **Base SHA:** `1c2f38ad`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_cutover_analysis_v1_2026-03-17.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_cutover_analysis_v1_2026-03-17.md`
  - `docs/analysis/regime_intelligence_default_cutover_gap_analysis_2026-03-17.md`
  - `docs/analysis/regime_intelligence_parity_artifact_matrix_2026-03-17.md`
  - `docs/analysis/regime_intelligence_cutover_readiness_2026-03-17.md`
  - `artifacts/regime_intelligence/ri_cutover_analysis_gate_summary_2026-03-17.json`
  - `tests/governance/test_regime_intelligence_cutover_parity.py`
- **Scope OUT:**
  - `src/**` runtime logic
  - `src/core/config/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - `tests/backtest/**` unless an end-to-end parity assertion proves strictly necessary
  - `results/**` committed baselines or newly manufactured golden artifacts
  - changes to default `multi_timeframe.regime_intelligence.authority_mode`
  - changes to authority precedence/fallback semantics
  - changes to governance enforcement logic
- **Expected changed files:** `6-7`
- **Max files touched:** `7`

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_cutover_analysis_v1_2026-03-17.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_cutover_analysis_v1_2026-03-17.md docs/analysis/regime_intelligence_default_cutover_gap_analysis_2026-03-17.md docs/analysis/regime_intelligence_parity_artifact_matrix_2026-03-17.md docs/analysis/regime_intelligence_cutover_readiness_2026-03-17.md artifacts/regime_intelligence/ri_cutover_analysis_gate_summary_2026-03-17.json tests/governance/test_regime_intelligence_cutover_parity.py`
- `python -m black --check tests/governance/test_regime_intelligence_cutover_parity.py`
- `python -m ruff check tests/governance/test_regime_intelligence_cutover_parity.py`
- `python -m pytest -q tests/governance/test_regime_intelligence_cutover_parity.py`
- `python -m pytest -q tests/governance/test_authority_mode_resolver.py`
- `python -m pytest -q tests/backtest/test_evaluate_pipeline.py -k "authority_mode or source_invariant"`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev`
- `python scripts/run_skill.py --skill feature_parity_check --manifest dev` _(required only if the slice claims feature-pipeline parity beyond existing selectors/artifacts)_

### Stop Conditions

- Any requirement to modify `src/**` runtime logic, `src/core/config/**`, `config/runtime.json`, or `config/strategy/champions/**`
- Any requirement to change default `authority_mode` semantics, precedence, or fallback behavior
- Any requirement to introduce a new runtime monkeypatch seam in `src/core/strategy/evaluate.py`
- Any requirement for the new cutover parity suite to assert cross-mode output equality (`legacy == regime_module` on action/confidence/regime) instead of intra-mode determinism and authority-path observability
- Any parity claim that depends on a newly manufactured baseline instead of an existing approved selector or artifact source
- Any need to commit new baseline/golden artifacts under `results/**`
- Any determinism replay or pipeline hash regression in verification gates

### Output required

- **Implementation Report**
- **PR evidence template**
- **Gate summary artifact:** `artifacts/regime_intelligence/ri_cutover_analysis_gate_summary_2026-03-17.json`

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- Analysis only: no runtime behavior changes and no default cutover in this slice
- Preserve `authority_mode` as an explicit governance control for rollout, fallback, parity verification, and config steering
- Do not modify authority resolver logic, config authority semantics, or active champion selection
- Deliverables must be traceability artifacts and focused tests only
- Slice-generated auxiliary analysis artifacts must live under `artifacts/regime_intelligence/`
- Reclassify immediately to `HIGH/STRICT` and stop for fresh Opus review if scope expands beyond the approved analysis/test surface
