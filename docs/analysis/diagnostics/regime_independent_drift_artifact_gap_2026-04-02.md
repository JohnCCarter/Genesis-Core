# Regime-independent drift artifact gap

This note is observational only.
It explains why `regime_independent_drift` remains `UNATTESTED` on the current locked artifact surface and what minimum future evidence would be needed before stronger drift-mechanism claims become admissible.

## What the current surface already supports

- `phase9_state_isolation/state_edge_matrix.json` attests that the observed edge is **not state-dependent** on the packet-authorized state-partition surface.
- `phase11_edge_stability/edge_stability.json` attests that the observed baseline edge is **stable** on the packet-authorized temporal/bootstrap surface.
- `phase10_edge_origin_isolation/selection_attribution.json` now attests `selection_surface_status = CONTRAST_AVAILABLE` on the timestamp-level opportunity surface.
- `phase10_edge_origin_isolation/execution_attribution.json` still marks execution attribution as `LIMITED_ARTIFACT_SURFACE`.
- `phase13_edge_classification/edge_classification.json` therefore keeps `regime_independent_drift` at `UNATTESTED`.

## What the current surface does not support

The current locked surface does **not** yet support a direct attribution from:

- non-state dependence
- plus temporal stability

to an attested drift mechanism.

More specifically, the current surface does not yet provide:

- a packet-authorized drift-specific counterfactual lane
- a packet-authorized decomposition separating residual edge into drift versus execution or selection effects
- a packet-authorized causal selection-membership surface
- a packet-authorized execution-mechanism surface strong enough to subtract execution explanations cleanly

## Why `regime_independent_drift` remains UNATTESTED

The current evidence says three important things at once:

1. the edge is not concentrated in the packet-authorized state partitions
2. the edge is stable on the packet-authorized temporal/bootstrap surface
3. execution and selection surfaces remain limited in causal strength

That combination is compatible with a drift-like interpretation, but it does **not** prove one.

Temporal stability is not the same thing as a drift mechanism.
Likewise, the absence of state concentration is not the same thing as a direct attestation of state-independent drift.

The correct locked status therefore remains:

- `regime_independent_drift = UNATTESTED`

## What can be said now

- the current artifact surface weakens a state-pocket explanation
- the current artifact surface supports stable realized edge over the authorized temporal/bootstrap lane
- the residual edge is compatible with, but not yet attributable to, a drift-like class

## What cannot be said now

- that the edge is caused by regime-independent drift
- that regime-independent drift has been rejected
- that temporal stability alone upgrades drift from residual hypothesis to attested mechanism
- that current execution or selection surfaces are already strong enough to isolate drift by elimination

## Minimum future evidence needed

To move `regime_independent_drift` beyond `UNATTESTED`, a future stricter lane would minimally need one or more of the following:

- a packet-authorized residual decomposition that can separate drift-like persistence from execution and selection limitations
- a stronger selection-membership surface than the current timestamp-level availability contrast
- a stronger execution surface so execution explanations can be reduced without hand-waving
- a packet-authorized temporal or cross-window probe designed specifically to test persistence without collapsing into state or path explanations

## Next admissible lane

Two admissible continuations exist:

1. **Docs-only closeout**
   - Keep `regime_independent_drift` explicitly unresolved.
   - Treat the current memo as the freeze point for why the class remains `UNATTESTED`.

2. **Future stricter residual-evidence lane**
   - Open a governed slice dedicated to separating residual drift from the still-limited execution and selection surfaces.
   - That lane should be treated as stricter than the current docs-only step because it would need to define new packet-authorized residual tests rather than merely restate locked findings.

## Bottom line

The current repository state does not yet justify a drift-mechanism conclusion.
It does justify a precise statement of the gap: `regime_independent_drift` remains unresolved because the locked surface shows non-state-dependent, temporally stable residual edge, but does not yet expose a packet-authorized decomposition that turns that residual pattern into an attested drift mechanism.
