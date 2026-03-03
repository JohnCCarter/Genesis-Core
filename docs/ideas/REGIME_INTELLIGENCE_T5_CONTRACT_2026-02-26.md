# REGIME INTELLIGENCE T5-A CONTRACT (Docs+Tests Evidence)

Date: 2026-02-26
Category: `api`

## 1) Commit contract

### Scope IN (strict)

- `docs/ideas/REGIME_INTELLIGENCE_T5_CONTRACT_2026-02-26.md` (new)
- `docs/ideas/REGIME_INTELLIGENCE_T0_CONTRACT_2026-02-26.md`
- `tests/test_evaluate_pipeline.py`
- `tests/test_ui_endpoints.py`

### Scope OUT (strict)

- Any `src/*` runtime logic files
- `src/core/strategy/decision.py`
- `src/core/strategy/prob_model.py`
- `src/core/strategy/confidence.py`
- `src/core/backtest/*`
- `src/core/optimizer/*`
- `config/runtime.json`
- `config/runtime.seed.json`
- `config/strategy/champions/*`
- `.github/workflows/champion-freeze-guard.yml`

### Constraints

- **NO BEHAVIOR CHANGE**
- Evidence tranche only (docs + tests).
- No runtime/API strategy logic changes under `src/**`.

## 2) T5-A objective

- Close SSOT wording drift by clarifying gate interpretation and PRE-file targeting.
- Close API observability test gap on `/strategy/evaluate` success path without envelope drift.
- Add explicit parity proof for invalid `authority_mode` fallback to legacy.

## 3) Gate interpretation lock

- `feature_parity_check` is a policy attestation in current repo state.
- Expected outcome: `STOP` with `no_steps`.
- This expected `STOP` is recorded as attestation outcome, not as tranche failure.

## 4) PRE/POST gate commands (exact)

### PRE gates (existing files only)

1. `pre-commit run --files docs/ideas/REGIME_INTELLIGENCE_T0_CONTRACT_2026-02-26.md tests/test_evaluate_pipeline.py tests/test_ui_endpoints.py`
2. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
3. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`
4. `pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `pytest -q tests/test_backtest_determinism_smoke.py`
6. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
7. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
8. `pytest -q tests/test_evaluate_pipeline.py tests/test_ui_endpoints.py`

### POST gates

1. `pre-commit run --files docs/ideas/REGIME_INTELLIGENCE_T5_CONTRACT_2026-02-26.md docs/ideas/REGIME_INTELLIGENCE_T0_CONTRACT_2026-02-26.md tests/test_evaluate_pipeline.py tests/test_ui_endpoints.py`
2. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
3. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`
4. `pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `pytest -q tests/test_backtest_determinism_smoke.py`
6. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
7. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
8. `pytest -q tests/test_evaluate_pipeline.py tests/test_ui_endpoints.py`

## 5) Done criteria

- Scope-constrained diffs only in listed files.
- PRE gates pass with expected policy-attestation STOP semantics documented.
- Added parity test for invalid `authority_mode` fallback to legacy and default parity.
- Added ON-path `/strategy/evaluate` observability assertion in `meta` with unchanged envelope keys.
- POST gates pass.
