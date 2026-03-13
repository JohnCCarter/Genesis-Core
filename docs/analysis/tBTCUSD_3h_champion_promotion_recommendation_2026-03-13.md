# tBTCUSD 3h Champion Promotion Recommendation (2026-03-13)

Mode: `RESEARCH`
Branch: `feature/Regime-Intelligence`
Category: `obs`
Constraint: `NO BEHAVIOR CHANGE` in this document; analysis only.

## Recommendation

**Recommend promoting the fresh RI candidate (`trial_082`) to replace the current
bootstrap `tBTCUSD_3h` champion, subject to the final governance/merge-readiness
decision for champion writeback.**

## Why this recommendation exists

The current official champion file for `tBTCUSD 3h` is not a validated optimizer
winner. It is a bootstrap placeholder created to unblock 3h workflow migration.
A fresh RI rerun has now produced a validated, reproducible candidate with both
in-sample and out-of-sample evidence.

## Current official champion

Source: `config/strategy/champions/tBTCUSD_3h.json`

Observed status:

- `run_id`: `baseline_timeframe_switch_3h`
- `score`: `0.0`
- `metrics`: empty
- metadata explicitly says it is a bootstrap champion to unblock runs
- metadata also recommends a validated Optuna run as the next step

Interpretation:

- this file is operationally useful as a placeholder
- it is **not** a real competitive champion selected from a validated search

## Candidate under consideration

Source: `results/hparam_search/ri_phaseB_rerun_20260313/best_trial.json`

Candidate identity:

- trial: `trial_082`
- run: `ri_phaseB_rerun_20260313`
- score: `0.3336954196`
- constraints: `ok=true`

In-sample metrics (2024):

- return: `+2.69%`
- profit factor: `2.06`
- max drawdown: `1.31%`
- sharpe: `0.252`
- trades: `108`

Supporting OOS evidence (2025):

Source: `results/hparam_search/ri_phaseC_rerun_20260313/best_trial.json`

- score: `0.1612487234`
- return: `-2.08%`
- profit factor: `1.46`
- max drawdown: `3.90%`
- sharpe: `0.122`
- trades: `122`

## Comparison summary

### Official champion vs RI candidate

| Dimension          | Official `tBTCUSD_3h` champion | RI candidate `trial_082`     |
| ------------------ | ------------------------------ | ---------------------------- |
| Champion type      | Bootstrap placeholder          | Validated optimizer winner   |
| Score              | `0.0`                          | `0.3336954196`               |
| Metrics            | Empty                          | Present and reproducible     |
| Constraints        | Bootstrap note only            | `ok=true`                    |
| In-sample evidence | None                           | Strong                       |
| OOS evidence       | None                           | Present                      |
| Reproducibility    | Not search-backed              | Backed by rerun + storage DB |

### Strategy/config differences worth noting

The RI candidate introduces meaningful behavioral differences relative to the
bootstrap champion:

- explicit `multi_timeframe.regime_intelligence` enablement
- `authority_mode: regime_module`
- clarity-score weighting and size-multiplier controls
- tighter exit profile (`max_hold_bars=8`, `trailing_stop_pct=0.022`)
- more stable signal gating (`hysteresis_steps=3`, `cooldown_bars=2`)

These are not cosmetic differences. They are part of the thesis that produced
better risk-adjusted performance.

## Why promotion is justified

Promotion is justified because:

1. the current official champion is a bootstrap placeholder, not a real winner
2. the RI candidate materially outperforms the baseline evidence chain
3. the Phase B result was freshly reproduced on the current branch
4. the Phase C OOS rerun confirms the candidate remains better than baseline
5. the previous Phase B study-level evidence gap has been closed

## Why promotion did not happen automatically

The rerun logs explicitly showed:

- `Promotion avstängd via config (tBTCUSD 3h)`

Therefore, the repository currently has:

- a **new champion candidate**, but
- **no automatic champion writeback** yet

## Recommendation detail

### Recommended decision

**Promote `results/hparam_search/ri_phaseB_rerun_20260313/best_trial.json`
as the new `tBTCUSD_3h` champion candidate for writeback into
`config/strategy/champions/tBTCUSD_3h.json`, provided final governance checks
for champion replacement are satisfied.**

### Not recommended

- keeping the bootstrap `score=0.0` champion as the long-term 3h authority
- treating the current official champion file as stronger evidence than the RI rerun
- conflating Phase D/E (RI + risk_state) with the pure RI champion decision

## Residual caution

This recommendation answers the question **"is the RI candidate stronger than the
current champion?"** with a clear yes.

It does **not** by itself complete all remaining STRICT merge/promotion gates.
If the repository requires additional deterministic or invariant checks before
writing champion files, those should still be completed deliberately.

## Bottom line

**Yes: the repository now has a substantially stronger 3h champion candidate than
the current official bootstrap champion. Promotion is recommended.**
