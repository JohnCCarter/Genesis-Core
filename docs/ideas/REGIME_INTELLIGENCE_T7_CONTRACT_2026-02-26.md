# REGIME INTELLIGENCE T7 CONTRACT (Authority Alias Lifecycle Hardening)

Date: 2026-02-26
Category: `api`

## 1) Commit contract

### Scope IN (strict)

- `docs/ideas/REGIME_INTELLIGENCE_T7_CONTRACT_2026-02-26.md` (new)
- `src/core/config/authority.py`
- `tests/test_config_ssot.py`
- `tests/test_config_api_e2e.py`
- `tests/test_config_endpoints.py`

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

- Default mode: **NO BEHAVIOR CHANGE**.
- Canonical path remains SSOT:
  `multi_timeframe.regime_intelligence.authority_mode`.
- Deterministic precedence/fallback from T6 must remain unchanged.
- `/strategy/evaluate` response envelope remains exactly `{result, meta}`.

## 2) T7 objective

Harden authority alias lifecycle validation without changing default runtime behavior:

- Reject non-dict alias payloads under `regime_unified` deterministically.
- Reject alias payloads containing keys other than `authority_mode`.
- Preserve canonicalization in `/config/runtime/validate` response payload (`cfg`).

## 3) Required behavior locks

1. Alias root key `regime_unified` must be a dict when present.
2. Alias dict must contain exactly one key: `authority_mode`.
3. Canonical key still wins conflict resolution.
4. Invalid canonical value is rejected in config authority validate/propose; evaluate-path legacy fallback behavior remains unchanged.
5. Alias input accepted for compatibility, but persisted/runtime canonical payload must not include `regime_unified`.

## 4) Gate interpretation lock (skills)

- `feature_parity_check` is currently a policy-attestation skill with no executable steps.
- Expected outcome in this repository state: `STOP` with `no_steps` semantics.
- This expected `STOP` is attestation evidence and is **not** a tranche failure by itself.
- `genesis_backtest_verify` must return PASS.

## 5) Skill-first note

- `config_authority_lifecycle_check` is **föreslagen** for future dedicated lifecycle attestation.
- Not introduced in T7; no manifest/registry change in this tranche.

## 6) PRE/POST gate commands (exact)

### PRE gates

1. `pre-commit run --files src/core/config/authority.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_config_endpoints.py docs/ideas/REGIME_INTELLIGENCE_T7_CONTRACT_2026-02-26.md`
2. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
3. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`
4. `pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `pytest -q tests/test_backtest_determinism_smoke.py`
6. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
7. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
8. `pytest -q tests/test_evaluate_pipeline.py tests/test_evaluate_regime_precomputed_index.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_config_endpoints.py tests/test_ui_endpoints.py::test_ui_get_and_evaluate_post`

### POST gates

1. `pre-commit run --files src/core/config/authority.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_config_endpoints.py docs/ideas/REGIME_INTELLIGENCE_T7_CONTRACT_2026-02-26.md`
2. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
3. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`
4. `pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `pytest -q tests/test_backtest_determinism_smoke.py`
6. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
7. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
8. `pytest -q tests/test_evaluate_pipeline.py tests/test_evaluate_regime_precomputed_index.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_config_endpoints.py tests/test_ui_endpoints.py::test_ui_get_and_evaluate_post`

## 7) Done criteria

- Alias lifecycle hardening implemented with minimal diff in `authority.py`.
- New SSOT tests cover non-dict alias and alias extra-key rejection.
- Validate endpoint confirms canonicalized `cfg` payload (no `regime_unified`).
- PRE and POST gates pass with documented skill-attestation semantics.
