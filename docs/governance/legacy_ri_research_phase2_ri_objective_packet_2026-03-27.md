# Legacy + RI research Phase 2 RI objective packet

Date: 2026-03-27
Status: tracked / analysis-only / no implementation authority
Lane: `run_intent: research_experiment`
Phase: `2 - RI internal research track`
Selected class: `A. RI internal next-hypothesis experiments`
Selected subtrack: `RI-S4 - objective hypothesis`

## Purpose

This artifact returns the RI lane to governed selection after two bounded negative slices and opens exactly one new RI hypothesis class.

This artifact does not authorize implementation, config changes, launches, comparison, readiness, promotion, runtime changes, or production writeback.

## Current state entering this packet

- The RI regime-calibration slice was executed and classified `degradation`.
- The RI balanced-conflict decision slice was executed and classified `degradation`.
- Those two results are negative evidence for additional near-runtime RI mutations on adjacent regime/decision surfaces.
- RI remains a valid separate family baseline, but the most recent bounded behavior-changing slices did not produce uplift.

## Exact hypothesis

- The next RI question should shift away from another nearby runtime mutation and into objective selection.
- The hypothesis is: the current RI family may be limited more by how candidate quality is ranked across windows than by another immediate change inside `prob_model.py` or `decision_gates.py`.
- Therefore the next RI slice should test a research-only objective or scoring rule that emphasizes robustness across fixed train and validation windows while leaving RI runtime decision behavior unchanged.

## Why this class is opened next

- Phase 1 allowed `signal`, `regime`, `decision`, and `objective` as separate RI next-hypothesis classes.
- The first bounded `regime` slice degraded.
- The next bounded `decision` slice also degraded.
- The disciplined next move is therefore to change hypothesis class instead of continuing to probe adjacent runtime gates.
- An objective slice can test whether RI selection quality improves without reopening thresholds, exits, sizing, or other already constrained runtime surfaces.

## Allowed surface

- research-only candidate ranking or score interpretation for RI experiments
- research-only evaluation across fixed train and validation windows
- bounded future work only if it remains explicit, reproducible, and isolated from runtime authority

## Fixed surface

- `strategy_family = ri`
- `authority_mode = regime_module`
- `src/core/strategy/prob_model.py`
- `src/core/strategy/decision_gates.py`
- threshold topology
- exits, fib gating, sizing, `risk_state`, and `clarity`
- Legacy internals
- champions
- runtime defaults

## Explicit non-goals

- no reopening of the failed calibration hypothesis
- no reopening of the failed balanced-conflict abstention hypothesis
- no new threshold retuning
- no new exit, hold, override, or sizing experiments
- no Legacy-overlay, coordination, router, ensemble, comparison, readiness, or promotion work

## Minimal evidence package for the next slice

- one bounded slice-definition artifact naming the exact objective surface
- one fixed evaluation matrix covering the same train and validation windows already used in this lane
- drift guard only if a code seam becomes necessary

## Decision rule

- If a research-only objective slice improves ranking discipline or robustness evidence without mutating runtime behavior, the RI lane may continue within `RI-S4`.
- If the objective slice also fails to produce meaningful evidence, RI should return to governed selection again and may need to pause rather than continue exploring adjacent local surfaces.
- Fail closed on ambiguity.

## Next admissible step

- The next admissible step after this packet is one bounded RI objective slice-definition artifact for exactly one research-only scoring or ranking hypothesis.
- That next step must remain docs-first and must not combine implementation and execution in the same move.
