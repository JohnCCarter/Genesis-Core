# Structural market microstructure artifact gap

This note is observational only.
It explains why `structural_market_microstructure` remains `UNATTESTED` on the current locked artifact surface and what minimum future evidence would be needed before stronger market-microstructure claims become admissible.

## What the current surface already supports

- `GENESIS-CORE-POST PHASE-9-ROADMAP.md` includes structural market microstructure as one of the packet-authorized possible edge classes.
- `docs/governance/edge_classification_phase13_packet_2026-04-02.md` explicitly forbids `SUPPORTED` for `structural_market_microstructure` because no packet-authorized market-microstructure artifact surface exists in the locked inputs.
- `results/research/fa_v2_adaptation_off/phase13_edge_classification/edge_classification.json` therefore emits `structural_market_microstructure = UNATTESTED` on the locked classification matrix.
- `results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md` preserves that boundary by stating that `structural_market_microstructure` remains `UNATTESTED`, not `REJECTED`.

## What the current surface does not support

The current locked surface does **not** yet support a direct attribution from the observed edge to a market-microstructure mechanism.

More specifically, the current packet-authorized surface does not expose attested artifacts for:

- bid/ask spread dynamics
- order-book depth or imbalance
- queue position or fill-priority effects
- microstructure-specific latency diagnostics
- microstructure-specific execution counterfactuals
- any packet-authorized decomposition that separates microstructure from the other residual classes

## Why `structural_market_microstructure` remains UNATTESTED

The current evidence preserves the class only as an available residual hypothesis.
It does **not** elevate the class into an attested mechanism.

That distinction matters:

1. the roadmap says market microstructure is a possible class
2. the Phase 13 packet says the locked inputs do not contain a packet-authorized market-microstructure artifact surface
3. the locked Phase 13 output therefore keeps the class at `UNATTESTED`
4. the Phase 14 report preserves that same boundary without treating it as disproven

So the correct locked status remains:

- `structural_market_microstructure = UNATTESTED`

## What can be said now

- market microstructure remains a live residual category in the roadmap classification universe
- the current locked artifact surface does not authorize a positive or negative market-microstructure conclusion
- the unresolved status is caused by missing authorized evidence surface, not by a proved rejection

## What cannot be said now

- that the edge is caused by market microstructure
- that market microstructure has been ruled out
- that current execution, selection, stability, or minimality artifacts already stand in for a microstructure lane
- that generic structural language is enough to upgrade the class from residual hypothesis to attested mechanism

## Minimum future evidence needed

To move `structural_market_microstructure` beyond `UNATTESTED`, a future stricter lane would minimally need one or more of the following:

- a packet-authorized artifact surface that explicitly captures market-microstructure evidence rather than inferring it indirectly
- attested spread, depth, order-book, or fill-quality fields tied to the analyzed trades or opportunities
- deterministic microstructure-specific counterfactuals or decompositions that can test whether the residual edge survives or collapses under those surfaces
- a governed separation between microstructure effects and the still-unresolved execution or drift classes

## Next admissible lane

Two admissible continuations exist:

1. **Docs-only closeout**
   - Keep `structural_market_microstructure` explicitly unresolved.
   - Treat the current memo as the freeze point for why the class remains `UNATTESTED`.

2. **Future stricter evidence lane**
   - Open a governed slice dedicated to defining and capturing a packet-authorized market-microstructure evidence surface.
   - That lane should be treated as stricter than the current docs-only step because it would need new authorized artifact types rather than a restatement of locked findings.

## Bottom line

The current repository state does not yet justify a market-microstructure conclusion.
It does justify a precise statement of the gap: `structural_market_microstructure` remains unresolved because the class exists in the roadmap taxonomy, but the locked artifact surface still does not include a packet-authorized microstructure lane capable of attesting or rejecting it.
