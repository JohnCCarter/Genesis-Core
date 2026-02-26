# REGIME INTELLIGENCE T8 CONTRACT (Lifecycle Attestation + Validation Surface Rollout)

Date: 2026-02-26
Category: `docs`
Status: **T0–T7 införd (implemented), T8 föreslagen (proposed).**

## 1) Commit contract

### Scope IN (strict)

- `docs/ideas/REGIME_INTELLIGENCE_T8_CONTRACT_2026-02-26.md` (new)

### Scope OUT (strict)

- All existing source, test, config, workflow, and runtime files.
- Any change to endpoint contracts, response envelopes, or runtime defaults.
- Any change under `config/strategy/champions/*` and `.github/workflows/champion-freeze-guard.yml`.

### Constraints

- Default mode: **NO BEHAVIOR CHANGE**.
- T8 is a docs-only tranche; no implementation behavior may be changed in this contract commit.
- Enable-switch semantics are locked: explicit `ON` enables rollout; default `OFF` keeps legacy/default behavior unchanged.

## 2) T8 objective

Define and freeze rollout intent for lifecycle attestation and validation surface unification for authority resolve:

- Establish one single validation surface for authority resolve that covers canonical, alias, invalid, and default paths.
- Lock deterministic reject paths for malformed/unsupported authority inputs.
- Lock enable-switch rollout semantics (`ON` = active rollout, default `OFF` = no-behavior-change).

## 3) Required behavior locks

1. A single validation surface must evaluate authority resolve inputs across: canonical, alias, invalid, and default fallback path.
2. Canonical path remains SSOT for persisted/runtime representation.
3. Alias path remains compatibility input only and must normalize through the same validation surface.
4. Invalid inputs must fail via deterministic reject paths (stable decision outcome for equivalent invalid payloads).
5. Default/OFF mode must preserve current behavior (no behavioral drift).
6. Enable-switch must be explicit: rollout behavior is active only when switch is explicitly `ON`.
7. Unknown/unsupported authority source states must be locked by authority source-invariant checks.

## 4) Gate interpretation lock

- T7 baseline gates are **införd** and remain mandatory baseline in T8 PRE/POST matrix.
- `shadow_mismatch` gate is required as T8 rollout evidence for lifecycle attestation.
- Unknown invariant gate is interpreted as the authority source-invariant lock.
- `shadow_error_rate` is **föreslagen** in T8 and explicitly non-executable in this tranche; its absence as executable evidence is not, by itself, a T8 failure.
- `feature_parity_check` remains policy-attestation semantics (`STOP` / `no_steps`) and is not, by itself, a tranche failure.

## 5) Skill-first note

- Skill-first policy remains in effect for lifecycle/authority attestation work.
- `config_authority_lifecycle_check` remains **föreslagen** as dedicated lifecycle-attestation skill.
- `shadow_error_rate` attestation skill/check is **föreslagen** and non-executable in T8.

## 6) PRE/POST gate commands (exact)

### PRE gates

1. `pre-commit run --files src/core/config/authority.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_config_endpoints.py docs/ideas/REGIME_INTELLIGENCE_T8_CONTRACT_2026-02-26.md`
2. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
3. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`
4. `pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `pytest -q tests/test_backtest_determinism_smoke.py`
6. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
7. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
8. `pytest -q tests/test_evaluate_pipeline.py tests/test_evaluate_regime_precomputed_index.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_config_endpoints.py tests/test_ui_endpoints.py::test_ui_get_and_evaluate_post`
9. `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_regime_observer_preserves_default_parity`
10. `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_canonical_invalid_alias_valid_falls_back_to_legacy tests/test_evaluate_regime_precomputed_index.py::test_evaluate_pipeline_regime_uses_global_index_for_precomputed_ema50`

FÖRESLAGEN (ej körbar i T8): shadow_error_rate gate (saknar införd executable skill/check).

### POST gates

1. `pre-commit run --files src/core/config/authority.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_config_endpoints.py docs/ideas/REGIME_INTELLIGENCE_T8_CONTRACT_2026-02-26.md`
2. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
3. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`
4. `pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `pytest -q tests/test_backtest_determinism_smoke.py`
6. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
7. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
8. `pytest -q tests/test_evaluate_pipeline.py tests/test_evaluate_regime_precomputed_index.py tests/test_config_ssot.py tests/test_config_api_e2e.py tests/test_config_endpoints.py tests/test_ui_endpoints.py::test_ui_get_and_evaluate_post`
9. `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_regime_observer_preserves_default_parity`
10. `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_canonical_invalid_alias_valid_falls_back_to_legacy tests/test_evaluate_regime_precomputed_index.py::test_evaluate_pipeline_regime_uses_global_index_for_precomputed_ema50`

FÖRESLAGEN (ej körbar i T8): shadow_error_rate gate (saknar införd executable skill/check).

## 7) Done criteria

- T8 contract exists with explicit lifecycle-attestation rollout objective.
- Single validation surface requirement is documented for canonical/alias/invalid/default authority resolve paths.
- Deterministic reject paths are explicitly locked.
- Enable-switch semantics are explicit (`ON`) with default `OFF` / no-behavior-change lock.
- PRE/POST matrix includes T7 baseline plus T8 additions: `shadow_mismatch`, unknown source-invariant, and `shadow_error_rate` marked **föreslagen/non-executable**.
