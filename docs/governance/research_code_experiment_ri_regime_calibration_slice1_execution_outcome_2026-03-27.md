# Research code experiment RI regime calibration slice 1 execution outcome

Date: 2026-03-27
Status: tracked / execution-complete / classified
Lane: `run_intent: research_code_experiment`
Slice: `ri regime calibration slice 1`

## Execution basis

- symbol: `tBTCUSD`
- timeframe: `3h`
- setup:
  - train: `2023-01-01..2023-12-31`
  - validation: `2024-01-01..2024-12-31`
- mode: research-only control vs research-only candidate on the same isolated slice
- active production model metadata: untouched
- retained narrow-probe decision row artifacts:
  - `results/research/ri_regime_calibration_slice1/control_decision_rows.json`
  - `results/research/ri_regime_calibration_slice1/candidate_decision_rows.json`

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

- total return: `-0.64%`
- trades: `143`
- win rate: `68.5%`
- sharpe: `0.128`
- max drawdown: `3.12%`
- profit factor: `1.56`
- score: `0.1772`

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

- total return: `2.34%`
- trades: `144`
- win rate: `57.6%`
- sharpe: `0.174`
- max drawdown: `4.29%`
- profit factor: `1.68`
- score: `0.2331`

## Classification

- classification: `degradation`

## Decision

- Do not continue this exact `balanced -> explicit RI calibration` hypothesis as a winning path.
- Keep the research seam and isolation controls, but close this specific hypothesis as not confirmed on the stronger train/validation setup.
- If RI internal research continues, return to governed selection and choose a different next-hypothesis slice rather than widening this one.
