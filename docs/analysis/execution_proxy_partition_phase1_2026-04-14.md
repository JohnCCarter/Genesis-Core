# Execution proxy partition — Phase 1

This note is observational only.
It partitions the already generated execution-proxy surface so the repository can decide whether execution is being narrowed meaningfully or whether the current proxy lane has reached its honest limit.

Governance packet: `docs/governance/execution_proxy_partition_phase1_packet_2026-04-14.md`

## Source surface used

This memo uses only the already generated execution-proxy artifacts and previously tracked boundary notes:

- `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence/execution_proxy_evidence.json`
- `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence/execution_proxy_summary.md`
- `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence/audit_execution_proxy_determinism.json`
- `docs/analysis/execution_proxy_first_read_2026-04-02.md`
- `docs/analysis/execution_inefficiency_artifact_gap_2026-04-02.md`
- `results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md`

## Why this slice was needed

The first read established that the proxy lane adds real observational value.
What it did **not** establish was whether the new value actually narrows execution as a live driver candidate.

To answer that honestly, the proxy surface had to be partitioned rather than read as one pooled average.

## Partition 1 — full-window vs sparse-window

The proxy surface splits almost evenly:

- `full-window` trades: `42`
- `sparse-window` trades: `40`

But the two groups are not behaviorally symmetric.

| Partition       | Count | Winners | Losers |    Mean pnl | Mean proxy MAE | Mean proxy MFE | 8-bar mean proxy delta |
| --------------- | ----: | ------: | -----: | ----------: | -------------: | -------------: | ---------------------: |
| `full-window`   |  `42` |    `24` |   `18` | `-3.915818` | `-1115.166667` |   `1436.02381` |           `105.439024` |
| `sparse-window` |  `40` |    `37` |    `3` | `18.622404` |       `-696.3` |     `4669.275` |          `1707.647059` |

Best current reading:

- the favorable proxy path story is concentrated much more heavily in the `sparse-window` subset than in the fully observed subset
- the `full-window` subset is materially less favorable and is not obviously carrying the same positive proxy story

That matters because the strongest apparent proxy upside is clustering in the less complete observation surface.

## Partition 2 — resolved vs omitted exit proxy price

Exact exit proxy price resolution also splits unevenly:

- resolved exact exit proxy price: `68`
- omitted exact exit proxy price: `14`

The omitted subset is not neutral missingness.

| Exit proxy status             | Count |    Mean pnl | Mean proxy MAE | Mean proxy MFE |   1-bar mean |   4-bar mean |   8-bar mean |
| ----------------------------- | ----: | ----------: | -------------: | -------------: | -----------: | -----------: | -----------: |
| `PASS`                        |  `68` |  `3.908076` |  `-986.191176` |  `3004.941176` |  `253.30303` | `555.630769` | `781.169231` |
| `OMITTED_MISSING_PROXY_PRICE` |  `14` | `22.477331` |  `-544.857143` |  `3053.428571` | `541.538462` |     `258.25` |     `1160.7` |

Most importantly:

- all `14` omitted exact-exit-proxy trades are winners
- all `14` omitted exact-exit-proxy trades live inside the `sparse-window` subset

So the current proxy surface is least complete exactly where realized outcomes are strongest.

## Partition 3 — winners vs losers

The realized ledger split is also strongly asymmetric on the proxy surface:

- winners: `61`
- losers: `21`

| Realized outcome | Count | Exact exit omitted |     Mean pnl | Mean proxy MAE | Mean proxy MFE |    1-bar mean |    4-bar mean |    8-bar mean |
| ---------------- | ----: | -----------------: | -----------: | -------------: | -------------: | ------------: | ------------: | ------------: |
| Winners          |  `61` |               `14` |  `16.729204` |  `-404.262295` |  `3873.491803` |  `517.293103` |  `904.392857` | `1428.732143` |
| Losers           |  `21` |                `0` | `-20.954745` | `-2382.333333` |   `514.333333` | `-297.380952` | `-544.333333` | `-927.684211` |

This split does show that the proxy surface is directionally meaningful.
But the interpretation is limited by the fact that the strongest favorable region is not the most complete region.

## Partition 4 — winners/losers inside full vs sparse windows

This is the decisive cross-check.

| Partition               | Count |     Mean pnl | 8-bar mean proxy delta |
| ----------------------- | ----: | -----------: | ---------------------: |
| `full-window winners`   |  `24` |   `8.288857` |           `961.291667` |
| `full-window losers`    |  `18` |  `-20.18872` |         `-1102.823529` |
| `sparse-window winners` |  `37` |  `22.204023` |            `1779.3125` |
| `sparse-window losers`  |   `3` | `-25.550899` |                  `561` |

Two things follow from this:

1. the proxy lane is not random noise; it is clearly separating strong positive and negative realized outcome regions
2. the strongest positive regime sits inside the less complete proxy-observation subset, not the fully observed subset

That means the current lane is informative, but it is also structurally constrained exactly where the proxy story looks strongest.

## What this slice changes

This slice does **not** support a claim that execution is now proved as the Genesis driver.
It does something narrower and still useful:

- it shows that the current proxy surface is not evenly informative across the trade population
- it shows that missingness is outcome-skewed rather than neutral
- it shows that the favorable proxy story is concentrated in the same region where exact exit proxy observations are least complete

So the current proxy lane narrows the gap statement, but it does not close the mechanism question honestly.

## Verdict

**Packet-authorized verdict:** `stricter execution lane justified`

Why this verdict is the most honest one:

- `execution weakened as candidate` would go too far because the proxy surface still contains real directional structure
- `execution strengthened but still non-authoritative` would overstate what the current surface can support, because the strongest favorable subset is also the least complete subset
- `execution still unresolved` is true but too weak, because the partition now shows a specific reason the current proxy lane cannot carry the question much farther on its own

The current best reading is therefore:

- execution remains unresolved on the current proxy surface
- the reason is now more specific than before
- the next execution-specific step, if pursued at all, should be a stricter evidence-capture lane rather than another proxy-only reinterpretation over the same incomplete subset structure

## Consequence for the master roadmap

This slice should **de-escalate further proxy-only execution iteration** on the current bounded surface.

That means the master-roadmap consequence is:

1. keep the execution residual unresolved on the current surface
2. record that a stricter execution lane is justified if execution becomes a priority again
3. continue the current bounded research program with the next planned slice: **sizing-chain synthesis**

## What can now be said more precisely

- the proxy lane added real observational value
- the proxy lane is directionally meaningful, not empty
- the strongest favorable proxy behavior is concentrated in incomplete proxy subsets
- therefore the current proxy lane is no longer the best place to keep spending bounded-slice effort if the goal is closure rather than more intermediate ambiguity

## Bottom line

The execution-proxy lane helped.
But after partitioning, its strongest positive region is still the least complete region.
So the correct Phase 1 closeout is not an execution-mechanism claim.
It is a sharper boundary:

- **execution remains unresolved here, and any serious next execution step now needs a stricter evidence surface**.
- **within the current bounded roadmap, the next best move is Phase 2: sizing-chain synthesis**.
