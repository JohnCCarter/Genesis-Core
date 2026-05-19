# Fast-window same-bar parity partial reclassification packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `decision-recorded / tests-backed / non-authorizing`

This packet records one bounded partial reclassification only for baseline finding `#13`. It does not claim that fast-window / precompute parity is exhaustively proven. It records that the exact branch-visible reading "no tracked test verifies slow-path vs fast-path identity per bar" is now too strong on this checkout: current tests already prove broad runtime-vs-precompute parity on sample data and fast-window prefix invariance, and this slice adds an explicit same-global-bar parity regression for the remapped fast-window path within a bounded-window recursive-indicator tolerance.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `obs`
- **Risk:** `LOW` — why: tests + docs evidence hardening only; no runtime/backtest code change
- **Required Path:** `Bounded RESEARCH slice / tests + docs only`
- **Lane:** `Research-evidence` — why: this slice narrows a branch-visible feature-parity hypothesis without changing runtime or backtest authority surfaces
- **Skill usage:** `none required` — bounded tests/docs truthfulness slice
- **Objective:** record that the exact `#13` claim of missing per-bar parity proof should be narrowed because current tests already cover broad runtime/precompute parity and this slice adds an explicit same-global-bar fast-window regression with seam-appropriate bounded-window tolerance
- **Related artifacts:** `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`, `src/core/strategy/features_asof.py`, `tests/utils/test_features_asof_fast_window_parity.py`, `tests/integration/test_precompute_vs_runtime.py`, `tests/backtest/test_backtest_engine.py`

### Scope

- **Scope IN:** one focused parity expansion in `tests/utils/test_features_asof_fast_window_parity.py`; this packet; one later-branch partial-reclassification note for `#13` in `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Scope OUT:** any edit under `src/core/strategy/**` or `src/core/backtest/**`; any new runtime flag/default change; any claim that all bars/timeframes/path combinations are now exhaustively proven
- **Expected changed files:** `tests/utils/test_features_asof_fast_window_parity.py`, `docs/decisions/governance/fast_window_same_bar_parity_partial_reclassification_packet_2026-05-19.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`

### Gates required

For this no-behavior-change evidence slice:

- `tests/utils/test_features_asof_fast_window_parity.py`
- `tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime`
- `tests/backtest/test_backtest_engine.py::test_build_candles_window_fast_window_matches_numpy_path`
- manual wording audit that `#13` is narrowed, not closed as a broader fast-window family
- stop-and-reopen rule if the new parity test exposes a real divergence in `src/core/strategy/**` or `src/core/backtest/**`

## Purpose

This slice answers one narrow question only:

- what is the honest current-branch reading of baseline `#13` after checking the current fast-window / precompute parity tests and adding one explicit same-global-bar regression?

## What changed in this slice

- one focused regression now compares full runtime extraction and fast-window remapped precompute extraction on the same global bar within bounded-window recursive-indicator tolerance
- the baseline now carries a dated later-branch note clarifying that tracked parity proof already exists on this checkout and is now more explicit

## What did not change

- no feature extraction logic changed
- no backtest engine logic changed
- no fast-window or precompute defaults changed
- no claim is made that all bars, symbols, or timeframes are exhaustively covered
- no claim is made that a truncated fast-window guarantees exact full-history identity for recursive indicators

## Governing basis

### Observed

1. `tests/integration/test_precompute_vs_runtime.py::test_precompute_features_match_runtime` already compares runtime vs precompute features across a sample dataset and asserts column-wise equality.
2. `tests/utils/test_features_asof_fast_window_parity.py::test_extract_features_backtest_is_prefix_invariant_to_future_bar_mutation` already proves no future-bar mutation leak for the runtime extraction path.
3. `tests/utils/test_features_asof_fast_window_parity.py::test_extract_features_backtest_remapped_precompute_is_prefix_invariant_on_fast_window` already proves no future-bar mutation leak for the remapped fast-window precompute path.
4. `tests/backtest/test_backtest_engine.py::test_build_candles_window_fast_window_matches_numpy_path` already proves the backtest candle-window builder matches the direct numpy slicing path for fast-window selection.
5. This slice adds `test_extract_features_backtest_fast_window_matches_full_runtime_on_same_global_bar`, which directly compares full runtime extraction and fast-window remapped precompute extraction on the same global bar within a seam-specific tolerance suitable for bounded-window recursive indicators.

### Inferred

- the exact `#13` reading is now narrower than "no tracked test verifies slow-path vs fast-path identity per bar"
- the honest current residual is lack of exhaustive parity proof and lack of exact full-history identity guarantees across more bars/timeframes/path permutations, not a total absence of branch-visible parity tests
- a tests-backed partial reclassification is truer than either declaring `#13` solved or leaving the older blanket wording unchanged

### Unverified

- whether broader datasets, additional timeframes, or more global-bar positions could still reveal a parity seam not covered by current tests
- whether adjacent feature pipelines outside the tracked fast-window/remap seam need similar explicit same-bar coverage
- whether a future runtime change could reintroduce divergence without broader matrix testing

## Bottom line

Finding `#13` should be **partially reclassified** on this branch. Current tests already establish multiple parity anchors, and this slice adds a direct same-global-bar regression for fast-window remapped precompute versus full runtime extraction within bounded-window recursive-indicator tolerance. This slice does **not** claim exhaustive proof or exact full-history identity from a truncated fast-window; it only narrows the stale branch-visible reading that there were no tracked parity tests at all.
