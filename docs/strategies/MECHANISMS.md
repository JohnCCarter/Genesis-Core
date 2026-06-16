# Edge Mechanisms Register

> Concept-lane register (Phase 4). This document is **measurement-honest**: it
> records the causal edge hypotheses the trading system bets on, each with a
> falsification condition tied to the Phase 1 cost-stress thresholds. It does
> **not** create authority, readiness, or a new strategy family. Code mirror:
> `src/core/strategy/mechanism_registry.py`.

## Why this exists

The bot has no proven edge (`EDGE_MAP=UNRESOLVED`; the only real OOS number is
negative). Phases 1–2 made our *measurements* honest (stress-tested cost model +
overfitting validation). Phase 3 makes *transfer* checkable (forward-vs-backtest
reconciliation). Phase 4 closes the loop by naming the **mechanisms** we are
actually betting on, so each can be falsified rather than quietly assumed.

A mechanism stays `UNVERIFIED` until it has direct out-of-sample support. The
global edge map remains `UNRESOLVED` while no mechanism is `CANDIDATE`.

## Status ladder

| Status | Meaning |
|---|---|
| `UNVERIFIED` | No direct OOS support; may have thin/in-sample signal only. |
| `EXPERIMENTAL` | Backtest support exists but not validated (robustness/forward). |
| `CANDIDATE` | Passed robustness + forward reconciliation; awaiting promotion. |
| `REJECTED` | Falsification condition met. |

## Falsification thresholds (shared with Phase 1)

An edge is considered **dead** when annualized **Sharpe < 1.0 AND profit factor
< 1.1** at realistic cost. Both must hold, so a thin-but-positive edge is not
rejected on Sharpe noise alone. Constants live in
`scripts/analyze/cost_stress_sweep.py` and `mechanism_registry.py`.

## Registered mechanisms

### `ml_confidence_v1` — ML confidence threshold · **UNVERIFIED**

- **Causal claim**: a gradient-boosted confidence score above a tuned threshold
  marks bars whose forward return distribution has positive expectancy.
- **Signal surface**: `components.ml_confidence` (legacy) / `thresholds.entry_conf_overall`.
- **Gates**: `regime_filter`, `ev_gate`, `cooldown`.
- **Falsification**: `tBTCUSD_1h` PF < 1.1 at realistic cost (≥10 bps total), or
  no profitable confidence threshold exists with ≥30 trades.
- **Current evidence (Phase 1)**: edge only survives at `conf ≥ 0.60`
  (PF=1.24, Sharpe=0.72, 183 trades); unprofitable below. Thin, not OOS-validated.
- **Evidence**: `artifacts/diagnostics/cost_stress_sweep_2026-06-16.md`,
  `config/strategy/champions/tBTCUSD_1h.json`.

### `regime_intelligence_v1` — Regime-conditioned entry · **EXPERIMENTAL**

- **Causal claim**: conditioning entries on detected market-regime persistence
  (trend vs range) raises expectancy by avoiding low-edge regimes.
- **Signal surface**: `thresholds.signal_adaptation` + `multi_timeframe.regime_intelligence`.
- **Gates**: `regime_filter`, `htf_gate`, `ev_gate`.
- **Falsification**: `tBTCUSD_3h` PF < 1.1 at realistic cost (edge does not
  survive slippage ≥ 40 bps).
- **Current evidence (Phase 1)**: 3h PF=1.585 at low cost, but Sharpe < 1.0
  everywhere and PF collapses to ~1.11 by slip=40bps. Backtest-only support.
- **Evidence**: `artifacts/diagnostics/cost_stress_sweep_2026-06-16.md`,
  `config/strategy/champions/tBTCUSD_3h.json`, `src/core/optimizer/robustness.py`.

## Promotion rule

A mechanism may move `EXPERIMENTAL → CANDIDATE` only with:

1. Robustness pass (deflated Sharpe / PBO-CSCV / Benjamini–Hochberg — Phase 2).
2. Forward-vs-backtest reconciliation with high fidelity at realistic cost
   (Phase 3, `tools/reconcile_forward_backtest.py`).
3. A bounded statement of what the edge means and does not mean, citing both
   evidence endpoints (`docs/knowledge/EDGE_MAP.md` admission rule).
