# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/* -> RESEARCH` for `feature/extract-asof-split`)
- **Risk:** `HIGH` — why: touches `src/core/strategy/*` (`features_asof.py` remains a high-sensitivity feature-parity surface)
- **Required Path:** `Full` (high-sensitivity path under `src/core/strategy/*`)
- **Objective:** Continue the no-behavior-change internal split of `_extract_asof(...)` by extracting only the HTF/LTF Fibonacci context orchestration block into an internal helper while preserving facade behavior exactly.
- **Candidate:** `extract-asof-split (slice-5)`
- **Base SHA:** `7179ab92`
- **Category:** `api` (internal no-behavior-change refactor only; no public API/wrapper/config-authority semantics change)
- **Constraints:** `NO BEHAVIOR CHANGE` (default behavior, public API, timeframe gating semantics, selector passthrough, context availability semantics, and cache semantics must remain unchanged)

## Scope

- **Scope IN:**
  - `src/core/strategy/features_asof.py`
  - `src/core/strategy/features_asof_parts/context_bundle_utils.py` (new)
  - `tests/utils/test_features_asof_context_bundle.py` (new)
  - `docs/audit/refactor/features_asof/command_packet_extract_asof_split_slice5_2026-03-12.md`
  - `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice5_2026-03-12.md`
- **Scope OUT:**
  - `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice1_2026-03-12.md` (user/local edit remains untouched)
  - `docs/audit/refactor/features_asof/context_map_extract_asof_split_slice4_2026-03-12.md` (user/automation edit remains untouched)
  - all non-listed `src/**` files
  - `src/core/strategy/evaluate.py`
  - `src/core/strategy/features.py`
  - `src/core/strategy/features_asof_parts/fibonacci_*`
  - `src/core/strategy/features_asof_parts/extraction_context_utils.py`
  - `src/core/strategy/features_asof_parts/indicator_state_utils.py`
  - `src/core/strategy/features_asof_parts/base_feature_utils.py`
  - `src/core/strategy/features_asof_parts/meta_utils.py`
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
- `python -m pytest -q tests/utils/test_features_asof_cache.py::test_feature_result_cache_lookup_moves_hit_to_mru_end tests/utils/test_features_asof_cache.py::test_feature_result_cache_store_enforces_size_and_overwrite_semantics`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `python -m pytest -q tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`
- `python -m pytest -q tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`
- `python -m pytest -q tests/utils/test_features.py::test_extract_features_atr14_is_true_atr14_even_when_atr_period_differs tests/utils/test_features.py::test_extract_features_stub_shapes`
- `python -m pytest -q tests/utils/test_features_asof_fib_error_handling.py`
- focused slice tests:
  - `python -m pytest -q tests/utils/test_features_asof_context_bundle.py`

Focused slice test must prove exact no-drift bundle semantics: for non-eligible timeframes the helper returns `htf_fibonacci_context={}`, `ltf_fibonacci_context={}`, and `htf_selector_meta=None`, and neither upstream context builder is invoked. For eligible timeframes, the helper must preserve HTF selector passthrough and forward `atr_vals` unchanged to the LTF context builder.

## Stop Conditions

- Scope drift outside Scope IN
- Any behavior/API drift in `extract_features_live`, `extract_features_backtest`, or `extract_features`
- Any change in eligible timeframe gating, selector passthrough, HTF/LTF availability semantics, or top-level meta wiring
- Determinism/cache/pipeline regression
- Forbidden/high-sensitivity paths touched outside approved scope

## Output required

- **Implementation Report**
- **PR evidence template**

## Skill Usage

- Relevant repo-local governance specs loaded/applied: `.github/skills/repo_clean_refactor.json` and `.github/skills/feature_parity_check.json`.
- Generic context-mapping/refactor-planning aids may be used, but pass/fail governance for this slice is anchored in the repo-local no-drift and parity specs above.
- Slice-5 extracts only the HTF/LTF Fibonacci context orchestration from `_extract_asof(...)` into an internal helper module. Public import surface remains `core.strategy.features_asof`, and helper module remains internal-only.
- This slice is an internal refactor of `_extract_asof(...)` context orchestration only. No public API, wrapper signature, config-authority behavior, or runtime default semantics are changed.
- Preserve exact semantics for timeframe eligibility (`1h`, `30m`, `6h`, `15m`), HTF selector passthrough, default empty-context behavior when timeframe is not eligible, and `atr_vals` passthrough into the LTF context builder.
