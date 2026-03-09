# REGIME INTELLIGENCE T2 CONTRACT (Shadow mismatch observability)

Date: 2026-02-26
Category: `refactor(server)`

## 1) Commit contract

### Scope IN

- `src/core/strategy/evaluate.py`
- `tests/test_evaluate_pipeline.py`
- `docs/ideas/REGIME_INTELLIGENCE_T2_CONTRACT_2026-02-26.md`

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
- T2 adds observability-only shadow mismatch signal.
- No impact on prediction/confidence/decision/sizing inputs.
- No public API envelope change (`result`, `meta` remains unchanged).

## 2) Authority lock and Opus wording

For T2, `detect_regime_unified` remains authority in evaluate path.
`_detect_shadow_regime_from_regime_module(...)` remains non-authoritative observer.
T2 does not change endpoint envelope, and shadow information is additive observability only, not a decision input.

## 3) T2 implementation intent

- Emit additive shadow-regime mismatch observability in `meta` under a clear namespace.
- Preserve all decision-path inputs and outputs in default behavior.
- Keep authority/non-authority separation explicit in metadata.

## 4) Skills-first commands

Run these explicitly:

1. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
2. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`

Status discipline:

- Process/tooling changes are `föreslagen` until implemented and verified.
- Mark `införd` only after verified implementation in this repository.

## 5) Test requirement

Add or update focused test in `tests/test_evaluate_pipeline.py` proving:

- mismatch signal is visible in meta/observability,
- action/confidence/regime remain identical despite shadow mismatch.

## 6) Required PRE/POST gates

### PRE gates

1. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
2. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`
3. `pre-commit run --files src/core/strategy/evaluate.py tests/test_evaluate_pipeline.py docs/ideas/REGIME_INTELLIGENCE_T2_CONTRACT_2026-02-26.md`
4. `pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `pytest -q tests/backtest/test_backtest_determinism_smoke.py`
6. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
7. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

### POST gates

1. `python scripts/run_skill.py --skill feature_parity_check --manifest dev`
2. `python scripts/run_skill.py --skill genesis_backtest_verify --manifest stable`
3. `pre-commit run --files src/core/strategy/evaluate.py tests/test_evaluate_pipeline.py docs/ideas/REGIME_INTELLIGENCE_T2_CONTRACT_2026-02-26.md`
4. `pytest -q tests/test_import_smoke_backtest_optuna.py`
5. `pytest -q tests/backtest/test_backtest_determinism_smoke.py`
6. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
7. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
8. `pytest -q tests/test_evaluate_pipeline.py`

## 7) Done criteria

- Scope remains strictly within Scope IN.
- PRE gates are executed and reported.
- T2 mismatch observability is additive only.
- Test proves mismatch observability + parity in decision outputs.
- POST gates pass.
- Commit message includes Category / Why / What / Gates.
