# Legacy + RI research Phase 3 Legacy preparation

Date: 2026-03-27
Status: tracked / preparation-only / no execution yet
Lane: `run_intent: research_experiment`
Phase: `3 - Legacy internal research track`
Selected class: `B. Legacy internal next-hypothesis experiments`
Selected subtrack: `L-S3 - Legacy decision or gating hypothesis`
Slice: `legacy decision slice 1`

## Purpose

This artifact selects the smallest admissible first probe for the already defined Legacy `L-S3` slice.

This artifact does not authorize comparison, readiness, promotion, runtime mutation, or production writeback.

## Preparation decision

- The first Legacy `L-S3` probe should remain config-only and isolate one threshold / candidate question before any code-level reopening is considered.
- The initial research comparison is therefore:
  - `control`: the current Legacy 3h incumbent surface replayed through an isolated research config
  - `candidate`: one bounded Legacy threshold / candidate variant that tightens only the balanced-zone threshold surface

## Why this is the smallest admissible probe

- The current slice-definition targets the Legacy threshold / candidate layer, not survival, sizing, exits, or RI semantics.
- A config-only probe can exercise that layer through the existing backtest and optimizer tooling without reopening `src/core/**`.
- This keeps the first Legacy question narrow: whether a slightly stricter balanced-zone threshold surface improves Legacy-only robustness on the existing 3h train/validation windows.

## Exact bounded preparation surface

- isolated backtest configs under `config/research/backtest/legacy_decision_slice1/`
- one isolated optimizer config under `config/optimizer/3h/legacy_decision_slice1/`
- only Legacy-family threshold / candidate parameters

## Fixed surface

- `strategy_family = legacy`
- Legacy family admission semantics
- RI authority, RI calibration, RI thresholds, and RI gate semantics
- `decision_fib_gating.py`
- `decision_sizing.py`
- exit, observability, runtime defaults, and champion artifacts

## Decision rule for the first probe

- If the candidate improves Legacy-only score or robustness evidence on the fixed 2024/2025 windows without widening into survival, sizing, or RI semantics, the `L-S3` line may continue.
- If the candidate is neutral or degrading, close or falsify this first threshold / candidate probe before widening the Legacy lane.

## Next admissible step

- The next admissible step after this preparation artifact is to run the isolated Legacy control/candidate backtests and one bounded Legacy-only Optuna search for this exact slice.
- Those runs must remain research-only and must not be presented as comparison-eligible or runtime-valid evidence.
