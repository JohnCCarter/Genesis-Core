# REGIME INTELLIGENCE T9A — IMPLEMENTATION REPORT

Date: 2026-03-04
Mode: `RESEARCH` (source: `feature/* -> RESEARCH`)
Risk: `HIGH`
Category: `api`

## Scope summary

### Scope IN (implemented)

- `src/core/strategy/decision.py`
- `src/core/strategy/regime_intelligence.py`
- `tests/test_decision.py`
- `tests/test_evaluate_pipeline.py`
- `docs/ideas/REGIME_INTELLIGENCE_T9A_IMPLEMENTATION_REPORT_2026-03-04.md`

### Scope OUT (respected)

- `config/strategy/champions/*`
- `.github/workflows/champion-freeze-guard.yml`
- runtime default changes outside explicit RI v2 ON gating
- unrelated cleanup/refactor

## Implementation summary

- Added deterministic clarity-score helper in `regime_intelligence`:
  - normalized components in `[0,1]`
  - non-negative normalized weights (`weights_v1`)
  - bounded conversion to `[0,100]` with explicit `half_even` policy
- Integrated ON-gated clarity modulation in `decision` as **sizing-only**:
  - active only when `multi_timeframe.regime_intelligence.enabled=true` and `version=v2` and `clarity_score.enabled=true`
  - OFF/default path unchanged
  - no threshold/EV gate changes and no blocker-reason mutations in ON path
- Added logging/attribution fields in decision `state_out`:
  - `ri_flag_enabled`, `ri_version`
  - `authority_mode`, `authority_mode_source`
  - `ri_clarity_*` breakdown and `size_before_ri_clarity` / `size_after_ri_clarity`

## Stop-condition compliance (user constraint)

Constraint: In v1, clarity may affect sizing only; if ON path modulates EV-threshold or blocker reasons -> STOP.

Status: **PASS**

Evidence:

- Code path applies clarity only after all gates/threshold decisions, inside sizing stage.
- Tests assert OFF/ON action and reasons parity while size differs only in ON mode.

## OFF parity artifact

Artifact selectors:

- `tests/test_decision.py::test_clarity_score_v2_off_preserves_legacy_path`
- `tests/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_legacy_off_parity`

Outcome:

- action parity: PASS
- reasons parity: PASS
- size parity in OFF: PASS

## ON behavior evidence (sizing-only + logging)

Artifact selectors:

- `tests/test_decision.py::test_clarity_score_v2_on_round_policy_tie_half_even_deterministic`
- `tests/test_evaluate_pipeline.py::test_evaluate_pipeline_ri_v2_clarity_on_changes_sizing_only_and_logs`

Outcome:

- ON determinism (same inputs -> same clarity score/size): PASS
- explicit tie policy (`half_even`) observed: PASS
- ON changes size while preserving action/reasons: PASS
- logging breakdown present (`ri_clarity_*`, authority source fields): PASS

## Gates executed and outcomes

### PRE gates (before implementation)

- `pre-commit run --all-files` → PASS
- `pytest -q tests/test_import_smoke_backtest_optuna.py` → PASS
- `pytest -q tests/test_backtest_determinism_smoke.py` → PASS
- `pytest -q tests/test_features_asof_cache_key_deterministic.py` → PASS
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` → PASS
- `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_error_rate_contract` → PASS
- `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract` → PASS
- `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_legacy_off_parity` → PASS
- `pytest -q tests/test_decision.py::test_clarity_score_v2_on_round_policy_tie_half_even_deterministic` → PASS (after selector skeletons were introduced)
- `pytest -q tests/test_decision.py::test_clarity_score_v2_off_preserves_legacy_path` → PASS (after selector skeletons were introduced)
- `python scripts/run_skill.py --skill feature_parity_check --manifest dev --dry-run` → PASS
- `python scripts/run_skill.py --skill config_authority_lifecycle_check --manifest dev --dry-run` → PASS
- `python scripts/run_skill.py --skill shadow_error_rate_check --manifest dev --dry-run` → PASS
- `python scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev --dry-run` → PASS

### POST gates (after implementation)

- `pre-commit run --all-files` → PASS
- `pytest -q tests/test_import_smoke_backtest_optuna.py` → PASS
- `pytest -q tests/test_backtest_determinism_smoke.py` → PASS
- `pytest -q tests/test_features_asof_cache_key_deterministic.py` → PASS
- `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable` → PASS
- `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_error_rate_contract` → PASS
- `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract` → PASS
- `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_legacy_off_parity` → PASS
- `pytest -q tests/test_decision.py::test_clarity_score_v2_on_round_policy_tie_half_even_deterministic` → PASS
- `pytest -q tests/test_decision.py::test_clarity_score_v2_off_preserves_legacy_path` → PASS
- `python scripts/run_skill.py --skill feature_parity_check --manifest dev --dry-run` → PASS
- `python scripts/run_skill.py --skill config_authority_lifecycle_check --manifest dev --dry-run` → PASS
- `python scripts/run_skill.py --skill shadow_error_rate_check --manifest dev --dry-run` → PASS
- `python scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev --dry-run` → PASS

## Residual risks

- Clarity v1 formula and weight defaults are intentionally conservative; future tuning should remain ON-gated and parity-tested.
- Additional scenario tests (bear/short, edge-case confidence) can be added in follow-up without changing default behavior.
