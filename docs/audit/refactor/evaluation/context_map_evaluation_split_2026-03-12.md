# Context Map — evaluation split

- **Date:** 2026-03-12
- **Mode:** `RESEARCH` (source=`feature/evaluation-split`)
- **Risk:** `MED`
- **Constraint:** `NO BEHAVIOR CHANGE` for default/public API

## Objective

Split `src/core/ml/evaluation.py` into smaller helper modules by responsibility, while preserving the existing public import surface from `core.ml.evaluation`.

Target helper modules:

- `src/core/ml/evaluation_metrics.py`
- `src/core/ml/evaluation_trading.py`
- `src/core/ml/evaluation_report.py`

## Primary file under change

### `src/core/ml/evaluation.py`

Current responsibilities found in-file:

1. Binary classification metrics (`evaluate_binary_classification`)
2. Calibration metrics (`evaluate_calibration`)
3. Trading metrics (`evaluate_trading_performance`)
4. Report assembly (`generate_evaluation_report`)
5. Report persistence (`save_evaluation_report`)
6. HTML rendering (`generate_html_report`)

The file is already logically separated by function boundaries, which makes it a strong helper-extraction candidate.

## Known import surface

### Direct imports of `core.ml.evaluation`

- `tests/backtest/test_evaluation.py`

Observed public symbols imported there:

- `evaluate_binary_classification`
- `evaluate_calibration`
- `evaluate_trading_performance`
- `generate_evaluation_report`
- `generate_html_report`
- `save_evaluation_report`

No other workspace Python files currently import this module directly.

## Expected extraction map

### `src/core/ml/evaluation_metrics.py`

Candidate functions:

- `evaluate_binary_classification`
- `evaluate_calibration`

### `src/core/ml/evaluation_trading.py`

Candidate functions:

- `evaluate_trading_performance`

### `src/core/ml/evaluation_report.py`

Candidate functions:

- `generate_evaluation_report`
- `save_evaluation_report`
- `generate_html_report`

### `src/core/ml/evaluation.py`

Post-split role:

- Compatibility façade/re-export module retaining the existing public API and import path.

## Test surface

### Primary targeted tests

- `tests/backtest/test_evaluation.py`

Coverage already present there includes:

- classification metrics
- calibration metrics
- trading performance metrics
- report assembly
- JSON save
- HTML save
- HTML content rendering
- end-to-end evaluation pipeline

### Governance regression selectors relevant to repo mode

- `tests/backtest/test_backtest_determinism_smoke.py`
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

## Main risks

1. **Public API drift**
   - Risk: callers/tests break if symbols stop exporting from `core.ml.evaluation`.
   - Mitigation: keep façade exports stable in `evaluation.py`.

2. **Import cycle introduction**
   - Risk: report helpers depending back on façade module.
   - Mitigation: keep helper modules acyclic; `evaluation_report.py` imports helper functions directly from metrics/trading modules, not through façade.

3. **HTML/report behavior drift**
   - Risk: string formatting or HTML layout changes inadvertently.
   - Mitigation: preserve existing template text verbatim; rely on existing HTML assertions in `tests/backtest/test_evaluation.py`.

4. **Scope creep**
   - Risk: touching adjacent ML helpers like `calibration.py` or `visualization.py`.
   - Mitigation: explicit Scope OUT in command packet.

## Scope recommendation

### Scope IN

- `src/core/ml/evaluation.py`
- `src/core/ml/evaluation_metrics.py`
- `src/core/ml/evaluation_trading.py`
- `src/core/ml/evaluation_report.py`
- `tests/backtest/test_evaluation.py` (only if import adaptation or additional parity assertions are needed)
- `docs/audit/refactor/evaluation/context_map_evaluation_split_2026-03-12.md`
- `docs/audit/refactor/evaluation/command_packet_evaluation_split_2026-03-12.md`

### Scope OUT

- `src/core/ml/calibration.py`
- `src/core/ml/visualization.py`
- any training/runtime/backtest logic
- config files
- pipeline/governance implementation files

## Implementation style

- Prefer pure extraction/move of existing functions.
- Preserve docstrings and return shapes.
- Preserve import path `core.ml.evaluation`.
- Avoid opportunistic renames or numeric/formatting changes.
