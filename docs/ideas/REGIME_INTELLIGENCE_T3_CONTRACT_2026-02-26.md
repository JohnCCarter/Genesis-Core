# REGIME INTELLIGENCE T3 CONTRACT (Module extraction with adapter parity)

Date: 2026-02-26
Category: `refactor(server)`

## 1) Commit contract

### Scope IN

- `src/core/strategy/regime_intelligence.py` (new)
- `src/core/strategy/evaluate.py`
- `tests/test_evaluate_pipeline.py`
- `tests/test_evaluate_regime_precomputed_index.py`
- `tests/test_ui_endpoints.py`
- `docs/ideas/REGIME_INTELLIGENCE_T3_CONTRACT_2026-02-26.md` (new)

### Scope OUT

- `src/core/strategy/decision.py`
- `src/core/strategy/prob_model.py`
- `src/core/strategy/confidence.py`
- `src/core/strategy/regime_unified.py`
- `src/core/config/schema.py`
- `src/core/config/authority.py`
- `config/runtime.json`
- `config/runtime.seed.json`
- `src/core/server.py` API-envelope/shape
- `src/core/backtest/*`
- `src/core/optimizer/*`
- `config/strategy/champions/*`
- `.github/workflows/champion-freeze-guard.yml`

### Constraints

- Default: **NO BEHAVIOR CHANGE**.
- `detect_regime_unified` remains authority in decision path.
- Shadow mismatch remains additive observability only.
- No endpoint envelope change (`result`, `meta`) and no decision input changes.
- Keep local adapters/wrappers in `evaluate.py` where tests rely on local symbols.

## 2) T3 implementation intent

- Extract regime-intelligence logic to `src/core/strategy/regime_intelligence.py`.
- Keep evaluate orchestration stable and preserve monkeypatch points in `evaluate.py`.
- Preserve precomputed EMA50 + `_global_index` behavior for windowed backtest flows.

## 3) Skills-first and gate matrix (PRE/POST identical)

1. `pre-commit run --files src/core/strategy/evaluate.py src/core/strategy/regime_intelligence.py tests/test_evaluate_pipeline.py tests/test_evaluate_regime_precomputed_index.py tests/test_ui_endpoints.py docs/ideas/REGIME_INTELLIGENCE_T3_CONTRACT_2026-02-26.md`
2. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
3. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`
4. `pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `pytest -q tests/test_backtest_determinism_smoke.py`
6. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
7. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
8. `pytest -q tests/test_evaluate_pipeline.py tests/test_evaluate_regime_precomputed_index.py tests/test_ui_endpoints.py`

## 4) Done criteria

- Scope remains within Scope IN.
- PRE and POST gate matrix executed and reported.
- Policy-attestation handling explicit: `feature_parity_check` STOP/no_steps is expected, not a regression fail.
- Decision-path authority and endpoint envelope parity preserved.
