# Backtest curated-only HTF-context policy fix pre-code packet

Date: 2026-04-22
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `post-diff-audited / APPROVED_WITH_NOTES / implementation verified within locked scope`

Pre-code verdict note (2026-04-22):

- Initial Opus 4.6 verdict for the HTF seam-only packet: `APPROVED_WITH_NOTES`
- The bounded seam implementation was applied and its focused tests passed.
- During touched-flow smoke verification, a stop-condition was triggered: canonical `2018` `curated_only` backtest execution still surfaced HTF-context cache keys under `frozen_first`, proving the policy was not reaching `build_htf_fibonacci_context(...)` unless explicitly present in config overrides.
- This addendum requests the smallest admissible scope expansion: `BacktestEngine.run()` pass-through of the already-selected explicit engine policy into the configs dict used by feature evaluation, plus a targeted regression test.

Post-diff audit note (2026-04-22):

- Opus 4.6 post-diff verdict: `APPROVED_WITH_NOTES`
- Governance conclusion: the minimal `BacktestEngine.run()` pass-through remained within the approved no-default-drift contract because only the explicit non-default `curated_only` lane is propagated into copied eval configs; default `frozen_first` behavior remains implicit and caller configs are not mutated.
- Repository-wide `python -m black --check .` remains failing on pre-existing files outside Scope IN (`scripts/analyze/scpe_ri_v1_*`, `src/core/strategy/family_admission.py`, `tests/utils/test_validate_optimizer_config.py`). All files touched by this slice passed scoped `black --check`; therefore formatting evidence for the slice is sufficient, but repository-wide formatter debt remains unresolved.
- Skill coverage for this slice was explicitly provided via repo-local skill files and retained in this artifact.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `tooling`
- **Risk:** `HIGH` — high-sensitivity scope because `src/core/backtest/engine.py` is now in Scope IN. Default `frozen_first` behavior must remain unchanged, while only the explicit opt-in `curated_only` lane may change HTF decision inputs where raw-first previously shadowed curated data.
- **Required Path:** `Full`
- **Objective:** implement the smallest admissible fix that makes explicit backtest data-source policy authoritative for the HTF Fibonacci context path as well, so `curated_only` governs the same HTF source used by feature extraction/decision-making.
- **Candidate:** `HTF context policy propagation fix (slice 2)`
- **Base SHA:** `e626ca2b`
- **Constraints:** explicit **no-default-drift** contract; default `frozen_first` ordering must remain unchanged; only explicit opt-in `curated_only` behavior may change; no runtime-default/config-authority/champion changes; no broader strategy-logic edits; no auto-fallback heuristics; any engine change must be limited to pass-through of the engine's already-validated explicit non-default policy into the copied backtest configs used by feature evaluation; caller-supplied configs must not be mutated.

## Problem statement

Current evidence shows that the explicit backtest data-source policy is not yet end-to-end authoritative:

1. `BacktestEngine` now honors `data_source_policy` for LTF/HTF candle loading and provenance.
2. But HTF feature-context creation still goes through a separate path:
   - `features_asof_parts/fibonacci_context_utils.py` -> `get_htf_fibonacci_context()`
   - `core/indicators/htf_fibonacci_context.py` -> `load_candles_data()`
   - `core/indicators/htf_fibonacci_data.py` still uses raw-first priority and source-agnostic caches.
3. Read-only probes on 2026-04-22 showed `curated_only` engine provenance together with HTF-context reads from `data/raw/tBTCUSD_1D_frozen.parquet`, causing `HTF_NO_HISTORY` and measurable result drift in 2018.
4. Follow-up touched-flow probe on 2026-04-22 showed the seam-only fix was insufficient for canonical backtests without explicit config overrides:

- `ltf_candles_source` was curated as expected.
- HTF candle cache still populated under `(symbol="tBTCUSD", timeframe="1D", policy="frozen_first", path="...data\\raw\\tBTCUSD_1D_frozen.parquet")`.
- HTF context cache still populated under `tBTCUSD_1D_frozen_first_default`.
- Therefore the missing propagation seam is the `BacktestEngine.run()` -> `configs` path, not the HTF loader/context seam alone.

Therefore the remaining problem is HTF policy propagation across two seams:

1. HTF context builder/loader/cache namespace (already implemented in this slice), and
2. `BacktestEngine.run()` propagation of the explicit engine policy into the configs dict consumed by feature evaluation (still missing in canonical no-override execution).

## Scope

- **Scope IN:**
  - `src/core/backtest/engine.py`
  - `src/core/strategy/features_asof_parts/fibonacci_context_utils.py`
  - `src/core/indicators/htf_fibonacci_context.py`
  - `src/core/indicators/htf_fibonacci_data.py`
  - `tests/backtest/test_backtest_engine.py`
  - `tests/utils/test_features_asof_context_bundle.py`
  - `tests/utils/test_htf_fibonacci_context_edge_cases_table.py`
  - `docs/governance/backtest_curated_only_htf_context_policy_fix_precode_packet_2026-04-22.md`
- **Scope OUT:**
  - `src/core/pipeline.py`, `scripts/run/run_backtest.py` (already covered by prior slice and remain out of scope)
  - `src/core/strategy/evaluate.py`
  - champion/config-authority/runtime-default files under `config/**`
  - optimizer/preflight surfaces
  - any runtime/paper/live behavior surfaces
  - all `results/**`, `artifacts/**`, `logs/**`, `cache/**`
  - unrelated existing untracked docs/agent files
- **Expected changed files:** `5-7`
- **Max files touched:** `9`

## Intended implementation shape

This slice should remain the smallest end-to-end authority fix:

1. Introduce an optional `data_source_policy` passthrough on the HTF context call chain.
2. Ensure `build_htf_fibonacci_context(...)` extracts explicit backtest policy from the provided config and passes it into `get_htf_fibonacci_context(...)`.
3. Ensure `htf_fibonacci_context` forwards the policy to `load_candles_data(...)`.
4. Namespace HTF candle/context caches by selected policy (and chosen source where needed) so `frozen_first` and `curated_only` cannot alias.
5. Ensure `BacktestEngine.run()` injects the engine's already-selected explicit non-default `data_source_policy` into the copied `configs` dict before feature evaluation, so canonical no-override backtests propagate the same policy into `build_htf_fibonacci_context(...)` without materializing a new explicit default value.
6. Add targeted tests proving:
   - `data_source_policy` is forwarded from context builder to HTF context retrieval

- `BacktestEngine.run()` propagates explicit non-default engine policy into evaluation configs without changing default `frozen_first`
- default behavior without explicit policy remains unchanged
- `curated_only` prevents raw-first fallback in the HTF context loader
- cache namespace differs across policies for HTF context/candle reuse
- `curated_only` and `frozen_first` do not share HTF cache entries for the same symbol/timeframe

## Gates required

- `python -m black --check .`
- `python -m ruff check .`
- `python -m bandit -r src -c bandit.yaml`
- focused selectors:
  - `python -m pytest -q tests/backtest/test_backtest_engine.py -k "data_source_policy or curated_only or frozen_first"`
  - `python -m pytest -q tests/utils/test_features_asof_context_bundle.py`
  - `python -m pytest -q tests/utils/test_htf_fibonacci_context_edge_cases_table.py`
- required invariants:
  - `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
  - `python -m pytest -q tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py`
  - `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
  - `python -m pytest -q tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features`
  - `python -m pytest -q tests/integration/test_precompute_vs_runtime.py`
- touched-flow smoke requirements:
  - `2018` canonical `curated_only` backtest no longer uses raw-first HTF context and remains reproducible
  - default `2024` `frozen_first` smoke remains runnable unchanged

## Stop Conditions

- any evidence that default `frozen_first` behavior drifts
- any evidence that no-arg/default HTF context calls or non-backtest callsites change behavior
- any need to edit `evaluate.py`, decision logic, or runtime-authority surfaces
- any need to broaden beyond the minimal `BacktestEngine.run()` pass-through into pipeline/CLI/runtime surfaces
- any need to mutate persistent artifact formats or unrelated caches
- any determinism/cache/pipeline guard regression

## Output required

- minimal implementation diff for HTF policy propagation + cache namespace + minimal engine pass-through only
- targeted regression tests for policy forwarding and fail-closed HTF loading
- implementation report with exact gates and outcomes
- Opus post-diff audit before any commit claim

## Gate outcomes

- `python -m black --check` on touched files in Scope IN (`src/core/backtest/engine.py`, `src/core/strategy/features_asof_parts/fibonacci_context_utils.py`, `src/core/indicators/htf_fibonacci_context.py`, `src/core/indicators/htf_fibonacci_data.py`, `tests/backtest/test_backtest_engine.py`, `tests/utils/test_features_asof_context_bundle.py`, `tests/utils/test_htf_fibonacci_context_edge_cases_table.py`) -> `PASS`
- `python -m black --check .` -> `FAIL` on pre-existing unrelated files outside Scope IN; documented above, not attributable to this slice
- `python -m ruff check .` -> `PASS`
- `python -m bandit -r src -c bandit.yaml` -> `PASS`
- `python -m pytest -q tests/backtest/test_backtest_engine.py -k "data_source_policy or curated_only or frozen_first" tests/utils/test_features_asof_context_bundle.py tests/utils/test_htf_fibonacci_context_edge_cases_table.py` -> `PASS`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable tests/utils/test_feature_parity.py::test_runtime_vs_precomputed_features tests/integration/test_precompute_vs_runtime.py` -> `PASS`

## Smoke evidence

- Canonical `2018` `curated_only` runner -> `PASS`
- Strict two-run `2018` `curated_only` probe -> `PASS`
  - metrics identical across both runs (`total_return`, `total_trades`, `win_rate`)
  - LTF source: `data/curated/v1/candles/tBTCUSD_3h.parquet`
  - HTF candle cache key: `["tBTCUSD", "1D", "curated_only", "...data\\curated\\v1\\candles\\tBTCUSD_1D.parquet"]`
  - HTF context cache key: `tBTCUSD_1D_curated_only_default`
  - no raw-path HTF cache key observed for `curated_only`
- Canonical `2024` `frozen_first` runner -> `PASS`

## Evidence anchor

- `src/core/strategy/features_asof_parts/fibonacci_context_utils.py`
- `src/core/indicators/htf_fibonacci_context.py`
- `src/core/indicators/htf_fibonacci_data.py`
- read-only 2026-04-22 A/B probe showing `curated_only` engine provenance with raw-first HTF context reads and measurable 2018 result drift
- 2026-04-22 touched-flow probe showing `ltf_candles_source` under curated while HTF caches still populated as `frozen_first`/raw in canonical `2018` `curated_only` backtest execution

## Skill usage

- Repo-local skills loaded/applied:
  - `.github/skills/python_engineering.json`
  - `.github/skills/backtest_run.json`
  - `.github/skills/genesis_backtest_verify.json`
  - `.github/skills/feature_parity_check.json`
- `src/core/indicators/htf_fibonacci.py` remains Scope OUT because the public facade already forwards `**kwargs`; the bounded fix should be achievable in the context-builder/context-loader/data-loader seam only.
- Governance authority for this slice remains the packet + Opus review, not the skills themselves.
