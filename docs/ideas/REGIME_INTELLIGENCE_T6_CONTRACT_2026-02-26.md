# REGIME INTELLIGENCE T6 CONTRACT (Authority Alias SSOT Bridge)

Date: 2026-02-26
Category: `api`

## 1) Commit contract

### Scope IN (strict)

- `docs/ideas/REGIME_INTELLIGENCE_T6_CONTRACT_2026-02-26.md` (new)
- `src/core/config/schema.py`
- `src/core/config/authority.py`
- `src/core/strategy/regime_intelligence.py`
- `src/core/strategy/evaluate.py`
- `tests/test_evaluate_pipeline.py`
- `tests/test_config_ssot.py`
- `tests/test_config_api_e2e.py`
- `tests/test_config_endpoints.py`
- `tests/test_ui_endpoints.py`
- `tests/test_evaluate_regime_precomputed_index.py`

### Scope OUT (strict)

- `src/core/strategy/decision.py`
- `src/core/strategy/prob_model.py`
- `src/core/strategy/confidence.py`
- `src/core/strategy/regime_unified.py`
- `src/core/backtest/*`
- `src/core/optimizer/*`
- `config/runtime.json`
- `config/runtime.seed.json`
- `config/strategy/champions/*`
- `.github/workflows/champion-freeze-guard.yml`
- `src/core/server.py` route/envelope shape changes

### Constraints

- Default mode: **NO BEHAVIOR CHANGE** in legacy default path.
- Alias support is compatibility bridge only.
- Canonical path remains SSOT:
  `multi_timeframe.regime_intelligence.authority_mode`.

## 2) T6 objective

Add SSOT compatibility bridge for authority config alias while preserving default legacy behavior.

- Alias input path: `cfg.regime_unified.authority_mode`
- Canonical path: `multi_timeframe.regime_intelligence.authority_mode`
- Deterministic precedence: canonical key wins when both are present.
- If canonical key is invalid and alias key valid, resolver fallback is legacy (must not switch to alias).

## 3) Required behavior locks

1. Schema supports compatibility alias section for `regime_unified.authority_mode`.
2. ConfigAuthority accepts alias input and canonicalizes alias-only updates before persist.
3. ConfigAuthority enforces strict allowed values and deterministic canonical precedence.
4. Regime resolver exposes deterministic mode + source resolution with legacy fail-safe fallback.
5. Evaluate observability reflects resolved authority mode and source.
6. `decision_input` remains `false` for shadow observer path.

## 4) Gate interpretation lock (skills)

- `feature_parity_check` is currently a policy-attestation skill with no executable steps.
- Expected outcome in this repository state: `STOP` with `no_steps` semantics.
- This expected `STOP` is attestation evidence and is **not** a tranche failure by itself.
- `genesis_backtest_verify` must return PASS.

## 5) PRE/POST gate commands (exact)

### PRE gates

1. `pre-commit run --files src/core/config/schema.py src/core/config/authority.py src/core/strategy/regime_intelligence.py src/core/strategy/evaluate.py tests/test_evaluate_pipeline.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_config_endpoints.py tests/test_ui_endpoints.py tests/test_evaluate_regime_precomputed_index.py docs/ideas/REGIME_INTELLIGENCE_T6_CONTRACT_2026-02-26.md`
2. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
3. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`
4. `pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `pytest -q tests/backtest/test_backtest_determinism_smoke.py`
6. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
7. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
8. `pytest -q tests/test_evaluate_pipeline.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_config_endpoints.py tests/test_ui_endpoints.py::test_ui_get_and_evaluate_post tests/test_evaluate_regime_precomputed_index.py`

### POST gates

1. `pre-commit run --files src/core/config/schema.py src/core/config/authority.py src/core/strategy/regime_intelligence.py src/core/strategy/evaluate.py tests/test_evaluate_pipeline.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_config_endpoints.py tests/test_ui_endpoints.py tests/test_evaluate_regime_precomputed_index.py docs/ideas/REGIME_INTELLIGENCE_T6_CONTRACT_2026-02-26.md`
2. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
3. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`
4. `pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `pytest -q tests/backtest/test_backtest_determinism_smoke.py`
6. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
7. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
8. `pytest -q tests/test_evaluate_pipeline.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_config_endpoints.py tests/test_ui_endpoints.py::test_ui_get_and_evaluate_post tests/test_evaluate_regime_precomputed_index.py`

## 6) Done criteria

- All scope files updated with minimal diff.
- Alias-only propose/validate supported and canonicalized deterministically.
- Conflict handling covered by tests (canonical wins).
- Invalid canonical + valid alias fallback to legacy covered in resolver/evaluate tests.
- UI evaluate response envelope remains exactly `{result, meta}`.
- PRE and POST gates pass with attestation semantics documented for `feature_parity_check`.
