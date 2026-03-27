# Research code experiment RI balanced conflict slice 1 execution outcome

Date: 2026-03-27
Status: tracked / execution-complete / classified
Lane: `run_intent: research_code_experiment`
Slice: `ri balanced conflict slice 1`

## Execution basis

- symbol: `tBTCUSD`
- timeframe: `3h`
- setup:
  - train: `2023-01-01..2023-12-31`
  - validation: `2024-01-01..2024-12-31`
- mode: research-only control vs research-only candidate on the same RI anchor setup
- candidate variant: abstain in `balanced` only when both sides pass and `abs(p_buy - p_sell) < 0.05`

## Verification completed

- `black --check` PASS
- `ruff check` PASS
- `pytest -q tests/utils/test_decision_edge.py tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_pipeline_hash_stability` PASS
- `pytest -q tests/utils/test_decision.py tests/utils/test_decision_fib_gating_contract.py` PASS

## Train window results

### Control

- total return: `1.11%`
- trades: `125`
- win rate: `75.2%`
- sharpe: `0.210`
- max drawdown: `0.95%`
- profit factor: `2.12`
- score: `0.2921`

### Candidate

- total return: `0.27%`
- trades: `130`
- win rate: `68.5%`
- sharpe: `0.171`
- max drawdown: `1.58%`
- profit factor: `1.86`
- score: `0.2391`

## Validation window results

### Control

- total return: `5.28%`
- trades: `120`
- win rate: `57.5%`
- sharpe: `0.233`
- max drawdown: `2.97%`
- profit factor: `1.96`
- score: `0.3124`

### Candidate

- total return: `3.69%`
- trades: `116`
- win rate: `58.6%`
- sharpe: `0.204`
- max drawdown: `3.45%`
- profit factor: `1.85`
- score: `0.2751`

## Classification

- classification: `degradation`

## Decision

- Do not continue this exact `balanced conflict abstain` hypothesis as a winning RI path.
- The candidate reduced validation trades slightly, but not enough to offset weaker return, weaker score, and worse drawdown.
- If RI internal research continues, return to governed selection and choose a different next-hypothesis slice rather than widening this one.
