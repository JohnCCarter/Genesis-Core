# Legacy + RI research Phase 2 RI objective slice definition

Date: 2026-03-27
Status: tracked / analysis-only / slice-defined / no execution authority
Lane: `run_intent: research_experiment`
Phase: `2 - RI internal research track`
Selected class: `A. RI internal next-hypothesis experiments`
Selected subtrack: `RI-S4 - objective hypothesis`
Slice: `ri objective slice 1`

## Purpose

This artifact defines the first bounded slice for the selected RI objective-hypothesis track.

This artifact does not authorize launches, comparison, readiness, promotion, runtime changes, or production writeback.

## Slice definition

- Candidate surface: `src/core/optimizer/scoring.py`
- Family claim: `ri`
- First drift layer: `objective`
- Core question: can a research-only robustness-first ranking rule improve RI candidate selection across the fixed `2023` train and `2024` validation windows without changing RI runtime decision behavior?

## Scope IN

- research-only score interpretation or ranking for RI candidate evaluation
- explicit use of the same fixed train and validation windows already used in this lane
- only the minimum evidence needed to prove that any observed effect is selection/objective-level rather than runtime-behavior-level

## Scope OUT

- `src/core/strategy/prob_model.py`
- `src/core/strategy/decision_gates.py`
- threshold family or threshold topology
- exits, fib gating, sizing, `risk_state`, and `clarity`
- Legacy internals
- champion artifacts
- runtime defaults
- coordination, router, ensemble, comparison, readiness, or promotion work

## Fixed assumptions

- `strategy_family = ri`
- `authority_mode = regime_module`
- the runtime behavior of the RI anchor remains unchanged during this slice
- the `2023` train and `2024` validation windows remain the fixed evaluation basis

## Minimal evidence package

- one research-only evaluation plan comparing the RI anchor under the selected objective rule on both fixed windows
- one explicit statement of whether the slice uses an existing score version or requires a bounded new research-only variant
- drift guard only if the slice later requires a code seam

## Stop conditions

- stop if the slice starts to mutate runtime decision behavior
- stop if the slice widens into threshold retuning, exit changes, or other local RI runtime surfaces
- stop if it becomes unclear whether the effect comes from objective selection rather than behavior change
- stop if the slice requires strict-only surfaces

## Outcome rule

- classify only as `improvement`, `plateau`, or `degradation`
- fail closed on ambiguity

## Next admissible step

- The next admissible step after this slice definition is one bounded implementation-or-config preparation artifact for this exact objective slice only.
- That next step must remain single-slice, research-only, and must not combine implementation and execution in the same move.
