# Execution proxy first read

This note is observational only.
It records the first admissible reading of the new execution-proxy artifact surface generated from `trace_rows.fib_phase.ltf_debug.price` and preserves the boundary that proxy evidence is not the same thing as realized execution authority.

> Current status note:
>
> - HISTORICAL 2026-05-05: this first-read memo is no longer the live forward pointer for the execution-proxy lane on `feature/next-slice-2026-05-05`.
> - Its then-next-step recommendation was later consumed by `docs/analysis/diagnostics/execution_proxy_partition_phase1_2026-04-14.md` and its packet `docs/decisions/diagnostic_campaigns/execution_proxy_partition_phase1_packet_2026-04-14.md`.
> - Preserve this note as the first bounded interpretation of the proxy surface, not as current roadmap authority.

## What the new proxy lane now attests

The new proxy lane adds a deterministic price-path surface that did not exist in the original locked Phase 10 execution artifact set.

On the generated proxy surface:

- `analysis_population.join_status = EXACT_ONE_MATCH_PER_TRADE`
- `analysis_population.matched_trade_count = 82`
- `analysis_population.exit_row_resolution_status = EXACT_ONE_EXIT_ROW_PER_TRADE`
- `audit_execution_proxy_determinism.json.match = true`

The proxy lane also attests coverage and shape over the authorized row-price surface:

- `full_window_attested_trade_count = 42`
- `sparse_window_trade_count = 40`
- `exact_exit_proxy_price_count = 68`
- `omitted_exit_proxy_price_count = 14`

It further attests deterministic fixed-horizon proxy summaries over the resolved subset:

- 1 bar: `resolved_trade_count = 79`, `mean_proxy_price_delta = 300.73417721519`, `median_proxy_price_delta = 229.0`
- 4 bars: `resolved_trade_count = 77`, `mean_proxy_price_delta = 509.285714285714`, `median_proxy_price_delta = 506.0`
- 8 bars: `resolved_trade_count = 75`, `mean_proxy_price_delta = 831.773333333333`, `median_proxy_price_delta = 704.0`

The proxy path summary on the attested row-price surface is directionally asymmetric:

- `mean_proxy_mae_price_delta = -910.841463414634`
- `median_proxy_mae_price_delta = -548.0`
- `mean_proxy_mfe_price_delta = 3013.219512195122`
- `median_proxy_mfe_price_delta = 2176.5`

## What the new proxy lane still does not attest

The new lane still does **not** attest:

- realized execution price
- slippage versus intended price
- latency or queue-position effects
- true intratrade OHLC path authority
- causal support or rejection of `execution_inefficiency`

This remains explicit in both the proxy summary and the proxy JSON limitations.

## What changed versus the prior execution gap

Before this lane, the execution gap memo could say only that stronger execution attribution was unavailable on the locked surface.

After this lane, the repository can now say something narrower and more useful:

- a deterministic proxy price-path surface exists
- that surface is materially populated rather than empty
- the surface is incomplete, because 40 trades are sparse-window and 14 trades omit exact exit proxy price
- the surface reduces uncertainty about row-price-path shape, but does not convert proxy observations into fill-quality evidence

So the execution residual is now better bounded, but not resolved.

## What cannot be concluded from this first read

This first read does **not** justify saying:

- that execution inefficiency is the source of the edge
- that execution inefficiency has been ruled out
- that the positive proxy fixed-horizon deltas are equivalent to realized execution advantage
- that sparse-window gaps are innocuous for mechanism attribution

The correct interpretation remains that this is a stronger observational surface than before, not a conclusive execution-mechanism surface.

## Best current reading

The best current reading is:

- the new proxy lane weakens the claim that the execution question is completely opaque on the locked surface
- the new proxy lane does **not** yet make execution a supported mechanism class
- the residual class `execution_inefficiency` therefore remains unresolved, but with a more informative intermediate surface than the original Phase 10 execution artifact alone

## Then-next admissible step from this first read

From this first-read snapshot, the then-next admissible step was not a runtime change.
It was a second analysis slice over the new proxy artifacts, for example one that partitions the proxy surface by:

- resolved versus omitted exit proxy price
- full-window versus sparse-window trades
- short fixed horizons versus longer proxy windows
- winners versus losers on the realized ledger

That follow-up would reduce uncertainty further while still preserving the boundary between proxy evidence and realized execution authority.

## Bottom line

The new execution-proxy lane adds real observational value.
It shows that the locked trace surface contains a usable but incomplete deterministic price-path proxy.
That narrows the execution gap, but it still does not justify a final mechanism claim for `execution_inefficiency`.
