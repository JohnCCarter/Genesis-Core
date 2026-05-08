# MCP Trading Agent v1 — Research-Evidence Lane Note

**Date:** 2026-05-07
**Branch:** `claude/mcp-trading-agent-snUF4`
**Lane:** research-evidence (per `docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md`)
**Status:** prototype — not promoted to runtime authority

## Why this is research-evidence, not runtime-integration

This packet introduces a **new agent surface** (`src/core/agent/`) and a **new
audit log** (`logs/agent_decisions.jsonl`). It does **not** introduce a new
strategy family, a new public-facing endpoint, or any modification to the
runtime authority files (`config/strategy/champions/*.json`,
`config/runtime.json`, `src/core/strategy/evaluate.py`,
`src/core/strategy/decision.py`).

The agent consumes the existing Fibonacci indicator
(`src/core/indicators/fibonacci.py`) and the existing risk guards
(`src/core/risk/guards.py`, `src/core/risk/pnl.py`) without modification. It
exposes them through MCP tools so a Claude session (or, in v2, a WebSocket
scheduler) can drive deterministic decision evaluation against Bitfinex paper.

Removing the entire branch (`git push origin --delete claude/mcp-trading-agent-snUF4`)
returns the repository to the pre-packet state with no residual artefacts other
than possibly `logs/agent_decisions.jsonl` if it has been written locally.

## Hypothesis under test

> A nested top-down Fibonacci rule (HTF identifies trend + 0.5–0.786 zone, LTF
> confirms a swing inside the zone, entry on a confirmation candle, stop beyond
> the LTF swing, targets at HTF fib-extensions 1.272 / 1.618 / trailing) can be
> evaluated deterministically through MCP tooling against Bitfinex paper, with
> every decision recorded as an auditable JSONL line.

## Falsification criteria

The hypothesis is falsified if any of the following hold during the smoke
runs (sections C and D in the plan):

1. The same `(symbol, trend_tf, entry_tf, candles_hash, params_hash)` produces
   different `fib_signal.action` or `fib_signal.entry`/`stop`/`targets`
   between two runs (non-determinism).
2. A decision record with `risk_check.passed=false` results in a Bitfinex
   submission without explicit `force=true`.
3. `submit_paper_order` is called and the resulting order is not visible in the
   Bitfinex paper account or not recorded as a `submission_followup` line in
   `logs/agent_decisions.jsonl`.
4. `read_candles` succeeds for `timeframe=4h` (Bitfinex does not support 4h —
   if this returns data, the validation logic is bypassed).

## Bounded surface

| Artefact | Path | Mutation |
|---|---|---|
| New agent package | `src/core/agent/` | added |
| New MCP tool module | `mcp_server/trading_tools.py` | added |
| MCP tool registry | `mcp_server/server.py` | additive only (new `Tool(...)` entries + new `elif` dispatch branches) |
| Audit log | `logs/agent_decisions.jsonl` | append-only, single writer assumed |
| Strategy pipeline | `src/core/strategy/evaluate.py` | **untouched** |
| Champion configs | `config/strategy/champions/` | **untouched** |
| Runtime config | `config/runtime.json` | **untouched** |
| Public API | `src/core/api/*.py` | **untouched** (we *consume* `paper_submit` and `public_candles` only) |

## What promotes this to runtime-integration

This packet stays in research-evidence until **all** of the following are
documented (in a follow-up summary in this folder):

- ≥ 100 decision records collected over ≥ 2 weeks of operation.
- Reproducibility check: replay of the recorded `candles_hash` + `params_hash`
  produces an identical `fib_signal` payload.
- Out-of-sample comparison vs. existing champion baselines on the same symbol.
- Explicit Opus-46 governance review attached.

Until those exist, the agent is a **probe**, not a runtime feature.

## Operational defaults

- Default 2-tier MCP inputs: `trend_tf = "6h"`, `entry_tf = "1h"`
- Recommended native 3-tier inputs: `trend_tf = "1D"`, `mid_tf = "6h"`, `entry_tf = "1h"`
- Entry zone default: 0.5–0.786 retracement on both HTF and LTF
- ATR-swing depth: 6.0 (matches `FibonacciConfig` default)
- Risk per trade: 1% of caller-provided current equity
- Stop: beyond LTF swing-extreme
- Targets: 1/3 at 1.272, 1/3 at 1.618, 1/3 trailing — emitted in `FibSignal`,
  exit-management itself is deferred to v2 (requires persistent positions
  tracker)

## Out of scope for v1

WebSocket scheduler, persistent equity-baseline tracker, persistent
positions tracker, multi-symbol orchestration, time-stops,
notifications, automatic exit-order management.
