# Feature Attribution v1 — Phase 3 baseline-metrics packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `phase3-proposed / docs-only / research-only / non-authorizing`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet freezes the baseline snapshot and future metrics-adapter boundary for Feature Attribution v1 and therefore carries authority-drift risk even though it remains docs-only and non-authorizing.
- **Required Path:** `Quick`
- **Objective:** Define the locked historical baseline metric source and the future metrics-adapter boundary for Feature Attribution v1 without authorizing implementation, evidence generation, result-schema changes, comparison authority, or promotion logic.
- **Candidate:** `future Feature Attribution v1 baseline-metrics contract`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** one docs-only RESEARCH packet; inherited-lock confirmation from Phase 0 through Phase 2; locked historical baseline metric source; exact semantic-label-to-source-field mapping; locked minimum baseline metric set; `expectancy` handling as citation-only; future metrics-adapter boundary phrased as projection-only and normalization-only; explicit non-adoption of comparison/promotion semantics; future evidence requirements phrased as future requirements only.
- **Scope OUT:** no source-code changes; no tests; no runtime/backtest/result changes; no artifact generation; no result-schema authority; no comparison authority; no promotion/cutover/family replacement authority; no config changes; no changes under `src/**`, `tests/**`, `config/**`, `results/**`, or `config/strategy/champions/**`; no fib reopening.
- **Expected changed files:** `docs/governance/feature_attribution_v1_phase3_baseline_metrics_packet_2026-03-31.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- read-only consistency check against controlling Phase 0, Phase 1, and Phase 2 packets
- read-only citation check against the locked baseline summary
- manual wording audit that the packet remains non-authorizing
- manual wording audit that no comparison, promotion, or result-schema authority is created

For interpretation discipline inside this packet:

- the baseline is a historical attribution reference only
- `config/strategy/champions/tBTCUSD_3h.json` remains config-source anchor only
- the minimum baseline metric set must not be replaced or silently redefined
- `expectancy` remains citation-only unless a later packet locks source field, definition, and units
- any future adapter must remain projection-only and normalization-only

### Stop Conditions

- any wording that authorizes implementation, evidence generation, artifact generation, or schema changes
- any wording that treats the baseline as comparison, promotion, cutover, runtime, or result-schema authority
- any wording that adopts comparison semantics from another repository surface by reference
- any wording that silently upgrades `expectancy` into a decision-bearing locked metric without an explicit definition and units
- any wording that reopens fib-derived comparison or promotion lanes

### Output required

- one reviewable Phase 3 RESEARCH baseline-metrics packet
- one locked historical baseline source declaration
- one semantic-label-to-source-field mapping table
- one locked minimum baseline metric set
- one projection-only future metrics-adapter boundary

## What this packet is

This packet is documentation-only and research-only.
It does **not** authorize implementation, evidence generation, artifact creation, schema changes, ranking, promotion, cutover, keep/no-promotion decisions, family replacement, runtime/backtest changes, or result-schema authority.

The baseline referenced here is a **historical attribution reference only**.
It is not comparison authority, promotion authority, runtime authority, backtest authority, or result-schema authority.

Any future implementation, execution, artifact generation, comparison workflow, or evidence production requires a separate later packet with explicit scope, gates, selectors, and approval.

## Inherited controlling packets

This packet inherits and does not weaken:

- `docs/governance/feature_attribution_v1_phase0_scope_freeze_packet_2026-03-31.md`
- `docs/governance/feature_attribution_v1_phase1_feature_inventory_packet_2026-03-31.md`
- `docs/governance/feature_attribution_v1_phase2_toggle_boundary_packet_2026-03-31.md`

The following remain locked and unchanged:

- research-only
- additive-only
- no-default-behavior-change
- fib non-reopen
- canonical baseline observational context = `tBTCUSD`, `3h`, `2023-01-01 -> 2024-12-31`
- reserved namespace only = `results/research/feature_attribution_v1/`

## Locked baseline source declaration

The locked historical baseline metric source for this lane is:

- `results/research/fib_baseline_backtest_v1/summary.md`

That summary is used here only as the historical attribution reference for baseline metrics.

The following file is used only as config-source anchor for that same locked baseline context:

- `config/strategy/champions/tBTCUSD_3h.json`

`config/strategy/champions/tBTCUSD_3h.json` is **config-source anchor only** in this packet.
It is not a metric source, evidence source, ranking input, winner proof, or promotion authority.

## Locked minimum baseline metric set

The locked minimum decision-bearing baseline metric set for future attribution reporting is:

- `total_return_pct`
- `profit_factor`
- `max_drawdown`
- `trade_count`
- `win_rate`

These five fields are locked because they are explicitly present in the historical baseline summary and are sufficiently stable as reporting labels for a future attribution lane.

## Citation-only metric

The following metric remains citation-only in this packet:

- `expectancy`

It is cited from the baseline summary as historical context only.
It is **not** upgraded to a locked decision-bearing baseline metric in this packet because no exact formula, units, or semantic contract are frozen here.

A later packet may only promote `expectancy` into the locked minimum baseline metric set if that packet also freezes:

- exact source field
- exact semantic definition
- exact units

## Semantic label to source-field mapping

The following mapping is locked for this packet:

| Semantic label     | Locked source artifact                                 | Exact source field name | Phase 3 status        |
| ------------------ | ------------------------------------------------------ | ----------------------- | --------------------- |
| `total_return_pct` | `results/research/fib_baseline_backtest_v1/summary.md` | `total_return_pct`      | locked minimum metric |
| `profit_factor`    | `results/research/fib_baseline_backtest_v1/summary.md` | `profit_factor`         | locked minimum metric |
| `max_drawdown`     | `results/research/fib_baseline_backtest_v1/summary.md` | `max_drawdown`          | locked minimum metric |
| `trade_count`      | `results/research/fib_baseline_backtest_v1/summary.md` | `trade_count`           | locked minimum metric |
| `win_rate`         | `results/research/fib_baseline_backtest_v1/summary.md` | `win_rate`              | locked minimum metric |
| `expectancy`       | `results/research/fib_baseline_backtest_v1/summary.md` | `expectancy`            | citation-only         |

This mapping does not create a runtime schema.
It freezes only the future reporting labels that a later attribution adapter would have to project from the locked historical source.

## Future metrics-adapter boundary

Any future Feature Attribution v1 metrics adapter must be:

- projection-only
- normalization-only
- additive-only
- non-decision-making

A future adapter may project locked baseline metrics and candidate metrics into a reporting surface, but it must **not**:

- create new comparison authority
- define PASS/FAIL semantics
- define promote/keep/no-promotion semantics
- rank multiple candidates
- select a winner
- replace or shadow the locked minimum baseline metric set
- change runtime or backtest outputs by implication

This packet does **not** authorize implementing such an adapter now.
It freezes only the future admissibility boundary.

## Candidate-vs-baseline boundary

Any future attribution comparison under this lane must remain:

- candidate-vs-locked-baseline only
- one selected Phase 1 row at a time, as constrained by Phase 2
- non-ranking
- non-promotional
- non-cutover

This packet does not authorize multi-candidate ranking, family replacement analysis, or promotion decisions.

## Comparison non-adoption boundary

Any repository comparison surface cited in connection with this packet is a cautionary non-adoption anchor only.

In particular:

- `src/core/decision/comparison.py` is cited only as a reminder that comparison and promotion semantics exist elsewhere in the repository.
- Those semantics are **not** adopted, imported, mirrored, or re-exposed in Feature Attribution v1 by this packet.

Nothing in this packet authorizes:

- `ComparisonDecision` semantics
- `DecisionReason` semantics
- promotion margins
- family replacement logic
- keep/no-promotion decision surfaces

## Additive diagnostics boundary

A later packet may allow additive diagnostic metrics only if they remain clearly marked as:

- additive
- non-decision
- non-authoritative
- non-replacing

Such diagnostics must not replace, reweight, redefine, or shadow the locked minimum baseline metric set.

## Future minimum evidence requirements

If a later packet ever opens implementation or execution, future evidence must record at minimum:

- baseline git SHA
- controlling Phase 0 packet path
- controlling Phase 1 packet path
- controlling Phase 2 packet path
- controlling Phase 3 packet path
- selected exact Phase 1 row label
- baseline metric snapshot using the locked minimum baseline metric set
- candidate metric snapshot using the same locked minimum baseline metric labels
- delta snapshot across the same locked minimum baseline metric labels
- any citation-only diagnostics kept separate from the locked minimum set

These are future requirements only.
This packet does **not** authorize producing evidence, artifacts, manifests, or result schemas now.

## Explicit preservation of non-reopen boundaries

Nothing in this packet reopens:

- fib-derived runtime lanes
- fib-derived comparison lanes
- fib-derived promotion lanes
- citation-only or excluded Phase 1 rows
- promotion or cutover logic
- champion mutation authority
- runtime/backtest result authority

## Bottom line

Phase 3 now freezes the baseline-metrics boundary for Feature Attribution v1 by stating that:

- the historical baseline source is `results/research/fib_baseline_backtest_v1/summary.md`
- `config/strategy/champions/tBTCUSD_3h.json` is config-source anchor only
- five baseline metrics are locked as the future minimum reporting set
- `expectancy` remains citation-only for now
- any future metrics adapter must be projection-only and normalization-only
- comparison/promotion semantics are not adopted by reference
- future evidence rules remain future-facing only

This packet fixes the metric fence.
It does not create a scoring authority.
