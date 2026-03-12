# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/* -> RESEARCH` for `feature/extract-asof-split`)
- **Risk:** `HIGH` — why: touches `src/core/strategy/*` (`features_asof.py` is a high-sensitivity path for feature parity)
- **Required Path:** `Full` (high-sensitivity path under `src/core/strategy/*`)
- **Objective:** Continue the no-behavior-change internal split of `_extract_asof(...)` by extracting only the core indicator-state assembly block (RSI, Bollinger, ATR/ATR14, volatility-shift) into an internal helper while preserving facade behavior exactly.
- **Candidate:** `extract-asof-split (slice-2)`
- **Base SHA:** `361d2d12`
- **Category:** `api`
- **Constraints:** `NO BEHAVIOR CHANGE` (default behavior, public API, feature values, cache semantics, and meta shape must remain unchanged)

## Scope

- **Scope IN:**
  - `src/core/strategy/features_asof.py`
  - `src/core/strategy/features_asof_parts/indicator_state_utils.py` (new)
  - `tests/utils/test_features_asof_indicator_state.py` (new)
  - `docs/audit/refactor/features_asof/command_packet_extract_asof_split_slice2_2026-03-12.md`
  - `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice2_2026-03-12.md`
- **Scope OUT:**
  - `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice1_2026-03-12.md` (user/local edit remains untouched)
  - all non-listed `src/**` files
  - `src/core/strategy/evaluate.py`
  - `src/core/strategy/features.py`
  - `src/core/strategy/features_asof_parts/fibonacci_*`
  - `src/core/strategy/features_asof_parts/extraction_context_utils.py`
  - `config/**`, `.github/workflows/**`, `mcp_server/**`, `scripts/**`
  - runtime/config authority paths and freeze-sensitive workflow files
- **Expected changed files:** 5
- **Max files touched:** 5

## Gates required

- `python -m black --check src tests`
- `python -m ruff check src tests`
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_features_asof_cache_key_deterministic.py::test_compute_candles_hash_is_deterministic_across_pyhashseed`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`
- `python -m pytest -q tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`
- `python -m pytest -q tests/utils/test_features.py::test_extract_features_atr14_is_true_atr14_even_when_atr_period_differs tests/utils/test_features.py::test_extract_features_stub_shapes`
- focused slice tests:
  - `python -m pytest -q tests/utils/test_features_asof_indicator_state.py`

## Stop Conditions

- Scope drift outside Scope IN
- Any behavior/API drift in `extract_features_live`, `extract_features_backtest`, or `extract_features`
- Any change in RSI fast/slow-path semantics, ATR(14) backcompat semantics, ATR-period override semantics, or volatility-shift fallback semantics
- Determinism/cache/pipeline regression
- Forbidden/high-sensitivity paths touched outside approved scope

## Output required

- **Implementation Report**
- **PR evidence template**

## Skill Usage

- Relevant repo-local governance specs loaded/applied: `.github/skills/repo_clean_refactor.json` and `.github/skills/feature_parity_check.json`.
- Generic context-mapping/refactor-planning aids may be used, but pass/fail governance for this slice is anchored in the repo-local no-drift and parity specs above.
- Slice-2 extracts only the indicator-state assembly from `_extract_asof(...)` into an internal helper module. Public import surface remains `core.strategy.features_asof`, and helper module remains internal-only.
- `FAST_HITS` / `SLOW_HITS` remain owned and mutated only by `core.strategy.features_asof`; the extracted helper must not define or mutate module-global counters and may only return data/flags needed for caller-side accounting.
- Preserve exact semantics for RSI fast/slow path, Bollinger last-3 assembly, ATR/ATR14 selection, ATR long fallback, and volatility-shift derivation.
