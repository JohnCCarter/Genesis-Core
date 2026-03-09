https://outlook.live.com/mail/

# REGIME INTELLIGENCE T9A — COMMAND PACKET

Date: 2026-03-04
Status: `proposed`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `feature/* -> RESEARCH` (`docs/governance_mode.md`)
- **Risk:** `HIGH` — why: touches `src/core/strategy/*` (high-sensitivity zone)
- **Required Path:** `Full`
- **Category:** `api`
- **Objective:** Implement RI P2 clarity-score v1 in explicit `ON` path while preserving default `OFF` parity.
- **Candidate:** `T9A clarity-score v1 ON-gated rollout`
- **Base SHA:** `b7c3f28a`

## Skill Usage (mandatory)

- `feature_parity_check` (`manifest=dev`, dry-run preflight + evidence reference)
- `config_authority_lifecycle_check` (`manifest=dev`, dry-run preflight + evidence reference)
- `shadow_error_rate_check` (`manifest=dev`, validate selector-driven shadow contract coverage)
- `ri_off_parity_artifact_check` (`manifest=dev`, OFF parity evidence packaging)

Skill runs are supplemental and must not replace determinism/invariance gates.

## Scope

- **Scope IN:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/regime_intelligence.py`
  - `tests/test_decision.py`
  - `tests/test_evaluate_pipeline.py`
  - `docs/ideas/REGIME_INTELLIGENCE_T9A_IMPLEMENTATION_REPORT_2026-03-04.md`
- **Scope OUT:**
  - `config/strategy/champions/*`
  - `.github/workflows/champion-freeze-guard.yml`
  - unrelated refactors/cleanup
  - runtime default changes outside explicit RI v2 ON gating
- **Expected changed files:** `5`
- **Max files touched:** `7`

## Behavior constraints

- Default constraint: **NO BEHAVIOR CHANGE** in `OFF` mode.
- Behavior exception (explicit): RI P2 clarity behavior may change only in `ON` mode behind explicit flag/version.
- OFF/default must preserve parity vs approved P1 baseline.
- Clarity rounding tie policy must be explicit, deterministic, and versioned.
- Authority resolver source attribution must remain intact and logged.

## Gates required (PRE and POST)

1. `pre-commit run --all-files`
2. `pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `pytest -q tests/backtest/test_backtest_determinism_smoke.py`
4. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
5. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
6. `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_error_rate_contract`
7. `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract`
8. `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_legacy_off_parity`
9. `pytest -q tests/test_decision.py::test_clarity_score_v2_on_round_policy_tie_half_even_deterministic`
10. `pytest -q tests/test_decision.py::test_clarity_score_v2_off_preserves_legacy_path`
11. `python scripts/run_skill.py --skill feature_parity_check --manifest dev --dry-run`
12. `python scripts/run_skill.py --skill config_authority_lifecycle_check --manifest dev --dry-run`
13. `python scripts/run_skill.py --skill shadow_error_rate_check --manifest dev --dry-run`
14. `python scripts/run_skill.py --skill ri_off_parity_artifact_check --manifest dev --dry-run`

## Minimal implementation sequence

1. Add ON-gated clarity calculation path in decision flow (no OFF path changes).
2. Wire authority source attribution fields through clarity decision logging.
3. Add/extend tests for ON tie-policy determinism and OFF parity.
4. Run PRE/POST full gates and collect evidence artifacts.
5. Produce implementation report and request Opus post-diff audit.

## Stop Conditions

- Scope drift beyond Scope IN
- Any OFF/default parity drift
- Determinism replay or pipeline invariant failure
- Forbidden path touched
- Implicit behavior activation without explicit ON flag/version

## Output required

- **Implementation Report**
  - Scope IN/OUT summary
  - File-level diff summary
  - Exact gate commands + outcomes
  - Evidence artifact paths/selectors
  - Residual risks and follow-ups
- **PR evidence template**
  - mode/risk/path
  - behavior exception statement
  - OFF parity proof
  - ON behavior proof
  - Opus pre-code + post-diff verdict links
