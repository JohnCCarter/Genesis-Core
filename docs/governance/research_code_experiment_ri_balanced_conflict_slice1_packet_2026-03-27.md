# Research code experiment RI balanced conflict slice 1 packet

Date: 2026-03-27
Status: tracked / packet-open / bounded code-level research
Lane: `run_intent: research_code_experiment`
Phase: `2 - RI internal research track`
Slice: `ri balanced conflict slice 1`

## Exact hypothesis

- The failed calibration slice increased trade count materially on both train and validation.
- The next narrow RI decision hypothesis is: in `balanced` regime only, when both long and short pass the probability threshold and the edge is very small, abstaining may reduce overtrading without reopening threshold retuning.

## Exact bounded code surface

- `src/core/strategy/decision_gates.py`

## Allowed work

- one opt-in research-only decision variant for `balanced` conflict handling
- matching bounded tests to prove:
  - default behavior is unchanged
  - the research-only variant is explicit and isolated
  - only the intended balanced dual-pass conflict cases are affected

## Forbidden work

- threshold retuning
- family rules or family-admission semantics
- champions
- runtime defaults
- active production model metadata
- exit, fib, sizing, risk-state, clarity, Legacy, router, or coordination work

## Minimum evidence package

- focused decision-unit tests for default parity and opt-in conflict abstention
- pipeline hash drift guard
- bounded train and validation backtests on the same RI anchor setup

## Stop conditions

- stop if the slice starts to affect non-balanced regimes
- stop if the slice widens into threshold topology or broader decision rewiring
- stop if the research-only variant cannot remain explicit and opt-in
- fail closed on ambiguity
