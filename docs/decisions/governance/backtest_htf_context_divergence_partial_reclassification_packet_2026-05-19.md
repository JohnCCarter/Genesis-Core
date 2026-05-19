# Backtest HTF-context divergence partial reclassification packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `decision-recorded / tests-backed / non-authorizing`

This packet records one bounded partial reclassification only for baseline finding `#9`. It does not claim that all HTF divergence risk is solved. It records that the current tracked consumer path in `src/core/backtest/engine.py::_check_htf_exit_conditions()` is already narrower and safer on this branch than the baseline row alone suggests: when precomputed HTF mapping is present, the engine now behaves as **precomputed-or-unavailable**, including the invalid `0.0/NaN` seam and the out-of-range index seam, rather than silently adopting `meta["features"]["htf_fibonacci"]` for those cases.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `tooling`
- **Risk:** `LOW` — why: focused backtest regression proof plus docs partial reclassification; no runtime/code/config behavior change
- **Required Path:** `Bounded RESEARCH slice / tests + docs only`
- **Lane:** `Research-evidence` — why: this slice narrows interpretation of current branch-visible behavior without changing runtime authority surfaces
- **Objective:** record that the exact `#9` carry-forward reading should be narrowed because the tracked BacktestEngine consumer path already standardizes on precomputed data when present, else unavailable on invalid/out-of-range precomputed access, and no longer silently falls back to `meta["features"]["htf_fibonacci"]` for those failure cases
- **Related artifacts:** `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`, `src/core/backtest/engine.py`, `src/core/backtest/engine_precompute.py`, `tests/backtest/test_backtest_engine.py`, `docs/audit/BACKTEST_ENGINE_AUDIT.md`
- **Skill usage:** no suitable repo-local skill was identified for this bounded backtest regression + docs truthfulness slice; no skill change is introduced here

### Scope

- **Scope IN:** this packet; one focused regression test in `tests/backtest/test_backtest_engine.py`; one later-branch partial-reclassification note in the BacktestEngine section of `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Scope OUT:** any runtime edit in `src/core/backtest/engine.py` or `src/core/backtest/engine_precompute.py`; any claim that HTF divergence is fully eliminated project-wide; any broader `#1` evidence/authority reclassification; any redesign of `htf_exit_config["enabled"]`
- **Expected changed files:** `tests/backtest/test_backtest_engine.py`, `docs/decisions/governance/backtest_htf_context_divergence_partial_reclassification_packet_2026-05-19.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`

## Purpose

This slice answers one narrow question only:

- what is the honest current-branch reading of `#9` for the tracked `BacktestEngine` HTF consumer path after reading current code and locking the out-of-range precomputed-index seam with a focused regression test?

## Governing basis

### Observed

1. `src/core/backtest/engine.py::_check_htf_exit_conditions()` prefers precomputed HTF mapping when `bar_index` is known and `self._precomputed_features` carries HTF mapping columns.
2. In that precomputed branch, invalid `0.0`, `NaN`, non-finite, or non-positive HTF values are sanitized through `_to_positive_finite(...)`, and incomplete/invalid levels or swing bounds force `htf_fib_context = {"available": False}`.
3. The same precomputed branch catches `IndexError`, `KeyError`, `TypeError`, and `ValueError` and also forces `htf_fib_context = {"available": False}` instead of falling back to `meta["features"]["htf_fibonacci"]`.
4. `tests/backtest/test_backtest_engine.py::test_check_htf_exit_invalid_precomputed_context_forces_unavailable` passes and proves that invalid `0.0/NaN` precomputed HTF values are not exposed as available context.
5. `tests/backtest/test_backtest_engine.py::test_check_htf_exit_valid_precomputed_context_remains_available` passes and proves that valid precomputed HTF values are still forwarded as available context.
6. `tests/backtest/test_backtest_engine.py::test_check_htf_exit_out_of_range_precomputed_context_does_not_fallback_to_meta` now passes and proves that out-of-range precomputed access does not silently adopt valid `meta["features"]["htf_fibonacci"]` fallback data.
7. `src/core/backtest/engine_precompute.py` still serializes mapped HTF columns with `.fillna(0.0).tolist()`, so the current hardening lives in the consumer-side `precomputed-or-unavailable` interpretation rather than in the producer serialization format itself.

### Inferred

- the exact current `#9` carry-forward reading is narrower than `precomputed mapping can still silently become fake available HTF context or silently fall back to meta`
- the tracked consumer path is currently standardized as **precomputed-or-unavailable** for the invalid-value and out-of-range seams covered above
- the honest current residual is broader cross-path equivalence work or future drift in producer/consumer assumptions, not an unchanged live branch reading of silent invalid-precomputed adoption for the tracked `BacktestEngine` path

### Unverified

- whether every other HTF-consuming path in the repository applies the same `precomputed-or-unavailable` contract
- whether runs with no precomputed HTF mapping remain behaviorally equivalent to precomputed-present runs under all conditions
- whether future producer-side changes to HTF mapping serialization could reopen the seam without the new regression test being updated

## Verification performed

- Focused gate run:
  - `pytest tests/backtest/test_backtest_engine.py -k "test_check_htf_exit_invalid_precomputed_context_forces_unavailable or test_check_htf_exit_out_of_range_precomputed_context_does_not_fallback_to_meta or test_check_htf_exit_valid_precomputed_context_remains_available"`
  - Result: `3 passed, 47 deselected`
- Changed-file gate run:
  - `pytest tests/backtest/test_backtest_engine.py`
  - Result: `50 passed`
- No additional repository Markdown-specific validator was identified for this slice.

## Bottom line

Finding `#9` should be **partially reclassified** on this branch. Current `BacktestEngine` behavior for the tracked HTF consumer path is no longer well-described by an unchanged “invalid precomputed mapping can silently drift into alternate HTF context” reading: current code and focused tests show a `precomputed-or-unavailable` rule for invalid and out-of-range precomputed HTF access. This slice does **not** claim that all HTF divergence risk is solved, and it does **not** change runtime behavior; it only corrects the current branch-visible evidence picture.
