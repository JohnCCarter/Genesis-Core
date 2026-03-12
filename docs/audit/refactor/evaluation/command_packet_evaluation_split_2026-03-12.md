# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `feature/evaluation-split`
- **Risk:** `MED` — public helper module split with preserved façade, low algorithmic risk but non-trivial API exposure
- **Required Path:** `Full`
- **Objective:** Selectively split `src/core/ml/evaluation.py` by responsibility into metrics, trading, and report helpers without changing default behavior or the public import path.
- **Candidate:** `evaluation.py` selective helper extraction
- **Base SHA:** `046b9d5d3a9a7fc5c1905702de432115e7164c4e`

## Scope

- **Scope IN:**
  - `src/core/ml/evaluation.py`
  - `src/core/ml/evaluation_metrics.py`
  - `src/core/ml/evaluation_trading.py`
  - `src/core/ml/evaluation_report.py`
  - `tests/backtest/test_evaluation.py` (only if required for import/parity coverage)
  - `docs/audit/refactor/evaluation/context_map_evaluation_split_2026-03-12.md`
  - `docs/audit/refactor/evaluation/command_packet_evaluation_split_2026-03-12.md`
- **Scope OUT:**
  - `src/core/ml/calibration.py`
  - `src/core/ml/decision_matrix.py`
  - `src/core/ml/visualization.py`
  - runtime/backtest/optimizer/strategy code
  - config/governance enforcement files
- **Expected changed files:** 4–7
- **Max files touched:** 7

## Constraints

- **NO BEHAVIOR CHANGE** by default.
- Preserve public imports from `core.ml.evaluation`.
- Preserve return schemas, keys, thresholds, calculations, and HTML text/layout.
- No opportunistic cleanup outside the split.

## Gates required

- `ruff check src/core/ml/evaluation.py src/core/ml/evaluation_metrics.py src/core/ml/evaluation_trading.py src/core/ml/evaluation_report.py tests/backtest/test_evaluation.py`
- `pytest -q tests/backtest/test_evaluation.py`
- `pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `pytest -q tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

## Stop Conditions

- Scope drift beyond helper extraction/façade preservation
- Any public API break from `core.ml.evaluation`
- Any HTML or report output regression not explained by an approved parity assertion
- Determinism/hash guard regression
- Forbidden paths touched

## Output required

- **Implementation Report**
- **PR evidence template**
