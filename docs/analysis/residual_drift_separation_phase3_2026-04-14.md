# Residual drift separation — Phase 3

This note is observational only.
It re-reads the residual drift question after the completed execution-proxy partition and sizing-chain synthesis.

Governance packet: `docs/decisions/residual_drift_separation_phase3_packet_2026-04-14.md`

## Source surface used

This memo uses only already tracked evidence:

- `docs/analysis/regime_independent_drift_artifact_gap_2026-04-02.md`
- `docs/analysis/execution_proxy_partition_phase1_2026-04-14.md`
- `docs/analysis/sizing_chain_synthesis_phase2_2026-04-14.md`
- `results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md`

## Starting boundary

Before this slice, the repository already knew that:

- the edge is not state-dependent on the packet-authorized state surface
- the edge is stable on the packet-authorized temporal/bootstrap surface
- `regime_independent_drift` remained `UNATTESTED`

The original gap memo correctly said that this was drift-compatible but not drift-proven.

## What changed after Phase 1 and Phase 2

Two bounded rereads now exist that matter for the residual interpretation.

### Phase 1 consequence

The execution-proxy partition did not prove execution as the driver.
Instead it showed that:

- execution remains unresolved on the current proxy surface
- the strongest favorable proxy behavior clusters in incomplete subsets
- further progress on execution would need a stricter lane, not another bounded proxy-only reinterpretation

So execution did not disappear as a residual class, but it stopped being a good next bounded explanation on the current surface.

### Phase 2 consequence

The sizing-chain synthesis showed that:

- the sizing path is central to preservation and risk-shaping
- the current sizing evidence still does not beat `emergent_system_behavior`
- the sizing story is meaningful but remains mixed, multiplicative, and partially confounded

So sizing also did not become the fully sufficient narrower explanation.

## Residual interpretation after those two rereads

That leaves the drift question in a subtly changed place.

The current bounded surface now says, all at once:

- the edge is not concentrated in packet-authorized state pockets
- the edge is temporally stable on the authorized stability surface
- execution remains bounded but cannot be advanced much farther without stricter evidence
- sizing is central to preservation/risk-shaping, but still does not exhaust the broader origin story

That combination does **not** attest drift.
But it does make drift a cleaner residual interpretation than it was before the Phase 1 and Phase 2 rereads.

## Why drift is still not attested

Drift still fails the mechanism-proof threshold because the repository still lacks:

- a drift-specific counterfactual lane
- a stronger selection-membership surface
- a stronger execution surface that can cleanly subtract execution explanations
- a packet-authorized decomposition that turns residual persistence into direct drift attestation

So the residual remains a residual.
No bounded docs-only reread can honestly change that into mechanism proof.

## Why drift compatibility is stronger anyway

Even though drift is not attested, the residual interpretation is now more disciplined than before.

That is because:

1. the most obvious bounded execution continuation has already stalled into a stricter-lane requirement
2. the strongest bounded subsystem story is sizing, but it still does not collapse the broader system-level explanation into a standalone sizing mechanism
3. the non-state and stable residual edge therefore stands in clearer relief than before

So the current bounded evidence now supports a stronger statement than the original raw gap note alone:

- drift is still not proved
- but drift-compatibility is no longer just a generic leftover phrase; it is now the cleanest bounded residual interpretation remaining once execution and sizing have both been reread conservatively

## Verdict

**Packet-authorized verdict:** `drift compatibility strengthened`

Why this is the most honest verdict:

- `drift remains unattested` is still true, but it misses the fact that the residual picture is now more structured after Phase 1 and Phase 2
- `drift-specific stricter lane justified` would be premature because the current bounded roadmap still had one cheaper residual closeout move left before recommending a future stricter lane
- `drift compatibility strengthened` captures the real update without pretending that residual compatibility equals proof

## Consequence for the roadmap

The roadmap consequence is:

1. keep `regime_independent_drift` unresolved and non-attested
2. record that drift is now the cleanest bounded residual interpretation after the execution and sizing rereads
3. continue to **Phase 4 — microstructure triage** rather than opening a new bounded drift slice immediately

## What can now be said more precisely

- drift still is not a proved mechanism
- but the remaining bounded evidence now fits drift more cleanly than before as a residual interpretation
- if the repository ever wants to go beyond that, the next honest move would be a stricter residual-evidence lane, not another restatement on the same bounded surface

## Bottom line

The current bounded evidence still does not prove regime-independent drift.
But after the execution and sizing rereads, the residual picture is cleaner.

So the correct Phase 3 closeout is:

- **drift remains unresolved as a mechanism**
- **drift compatibility is now more strongly supported as the residual interpretation**
- **the next bounded move is Phase 4: microstructure triage**.
