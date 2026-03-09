# REGIME INTELLIGENCE T1 CONTRACT (Shadow-only integration)

Date: 2026-02-26
Category: `refactor(server)`

## 1) Commit contract

### Scope IN

- `src/core/strategy/evaluate.py`
- `src/core/strategy/regime.py`
- `tests/test_evaluate_pipeline.py`
- `tests/test_evaluate_regime_precomputed_index.py`
- `tests/test_regime.py`
- `docs/ideas/REGIME_INTELLIGENCE_T1_CONTRACT_2026-02-26.md`

### Scope OUT

- `src/core/backtest/*`
- `src/core/optimizer/*`
- `config/strategy/champions/*`
- `.github/workflows/champion-freeze-guard.yml`
- `src/core/config/schema.py`
- `src/core/config/authority.py`
- `config/runtime.json`
- `config/runtime.seed.json`
- `config/models/*`
- `src/core/server.py` API-shape changes

### Constraints

- **NO BEHAVIOR CHANGE** in default mode.
- No schema/authority/runtime-config authority migration in this tranche.
- No response-shape drift.

## 2) Authority lock (Opus remediation A)

For T1, authority is the existing evaluate-path call to detect_regime_unified in evaluate_pipeline. No schema/authority/runtime-config authority migration is in scope. regime.py is shadow-only and must not affect prediction, decision, or sizing inputs.

## 3) T1 implementation intent

- Integrate `regime.py` in evaluate path as a **shadow-only observer**.
- Keep `detect_regime_unified` as decision-path authority.
- Ensure shadow observer output is ignored by `predict_proba_for(...)`, confidence, and `decide(...)` inputs.

## 4) Skills-first commands (Opus remediation B)

Run these explicitly:

1. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
2. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`

Status discipline:

- Process/tooling changes are `föreslagen` until implemented and verified.
- Mark `införd` only after verified implementation in this repository.

## 5) Parity guard requirement (Opus remediation C)

Add a focused test proving default output parity for `evaluate_pipeline` on:

- `action`
- `confidence` (keys + values)
- `regime` (key + value)

when shadow observer is active but ignored for decision-path inputs.

## 6) Required PRE/POST gates

### PRE gates

1. `pre-commit run --files src/core/strategy/evaluate.py src/core/strategy/regime.py tests/test_evaluate_pipeline.py tests/test_evaluate_regime_precomputed_index.py tests/test_regime.py docs/ideas/REGIME_INTELLIGENCE_T1_CONTRACT_2026-02-26.md`
2. `pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `pytest -q tests/backtest/test_backtest_determinism_smoke.py`
4. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
5. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### POST gates

1. `pre-commit run --files src/core/strategy/evaluate.py src/core/strategy/regime.py tests/test_evaluate_pipeline.py tests/test_evaluate_regime_precomputed_index.py tests/test_regime.py docs/ideas/REGIME_INTELLIGENCE_T1_CONTRACT_2026-02-26.md`
2. `pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `pytest -q tests/backtest/test_backtest_determinism_smoke.py`
4. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
5. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
6. `pytest -q tests/test_evaluate_pipeline.py tests/test_evaluate_regime_precomputed_index.py tests/test_regime.py`

## 7) Done criteria

- Scope remains within Scope IN only.
- PRE gates pass.
- T1 shadow observer is integrated and non-authoritative.
- Parity guard test proves unchanged default outputs.
- POST gates pass.
- Commit message includes Category / Why / What / Gates.
