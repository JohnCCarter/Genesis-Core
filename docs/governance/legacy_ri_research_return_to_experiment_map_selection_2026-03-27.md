# Legacy + RI research return to experiment-map selection

Date: 2026-03-27
Status: tracked / analysis-only / no implementation authority
Lane: `run_intent: research_experiment`
Phase: return to experiment-map selection

## Purpose

This artifact pauses further RI slice iteration and returns the research lane to experiment-map selection after the currently tested RI formulation was locally exhausted.

This artifact does not authorize implementation, config changes, launches, comparison, readiness, promotion, runtime changes, or production writeback.

## Basis for return

- RI regime slice: `degradation`
- RI decision slice: `degradation`
- RI objective slice: `plateau`
- no positive signal was observed across these independent RI dimensions

## Conclusion

- The current RI formulation is locally exhausted for the presently opened line of inquiry.
- Do not open another RI slice from the current parameterization chain.

## Next hypothesis class

- The next hypothesis class should be `B. Legacy internal next-hypothesis experiments`.

## Why this class is orthogonal to the previous RI slices

- It moves the search to a different strategy family rather than another RI-local surface.
- It does not depend on the RI calibration, RI decision gating, or RI objective ranking surfaces that were just tested.
- It preserves family separation because Legacy is evaluated on its own internal terms rather than by mixing or adapting RI semantics.
- It tests whether productive research room still exists in Legacy before any coordination or router layer is considered.

## Why not coordination yet

- RI exhaustion alone is not enough to justify jumping straight to cross-family coordination.
- The roadmap order still favors checking whether Legacy has remaining internal research room before opening a higher-layer orchestration class.
- Opening coordination now would widen scope before both family-local tracks have been adequately resolved.

## Explicit non-goals

- no new RI slice
- no Legacy slice yet
- no coordination or router opening yet
- no implementation work

## Next admissible step

- The next admissible step after this return artifact is one docs-only class-opening artifact for `B. Legacy internal next-hypothesis experiments`.
- That next step must define the Legacy class only and must not open a concrete Legacy slice in the same move.
