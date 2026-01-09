# Daily Summary - 23 Oct 2025

## Runs
- **Proxy Optuna** (`config/optimizer/tBTCUSD_1h_proxy_optuna.yaml`)
  - Results in `results/hparam_search/run_20251023_131910`
  - Best trial `trial_003`: score 224.66, PF 3.03, 75 trades
  - Parameters: `entry_conf=0.40`, `regime_bal=0.80`, `risk_map=[[0.4,0.01],[0.5,0.02],[0.6,0.03]]`, `exit_conf=0.60`, `max_hold=15`
  - Backtest: `results/backtests/tBTCUSD_1h_20251023_152720.json` (net +8.98 %, profit 3,520 USD, loss -2,187 USD)

- **Full 6-month validation** (`config/optimizer/tBTCUSD_1h_new_optuna.yaml`)
  - Study `optuna_tBTCUSD_1h_6m.db`
  - New trials reached at most score 186.65 (no improvement over proxy winner)

- **Fine Optuna** (`config/optimizer/tBTCUSD_1h_fine_optuna.yaml`)
  - Results in `results/hparam_search/run_20251023_141747`
  - Best trial `trial_002`: score 260.73, PF 3.30, 75 trades
  - Parameters: `entry_conf=0.35`, `regime_bal=0.70`, `risk_map=[[0.45,0.015],[0.55,0.025],[0.65,0.035]]`, `exit_conf=0.40`, `max_hold=20`
  - Backtest: `results/backtests/tBTCUSD_1h_20251023_162506.json` (net +10.43 %, profit 3,641 USD, loss -2,554 USD)

## Code and tooling updates
- Added cache support to `src/core/optimizer/runner.py` (`_cache/<hash>.json`).
- New helper script `scripts/summarize_hparam_results.py`.
- YAML profiles for coarse/proxy/fine tuning.
- `test_optuna_new_1_3months.py` now accepts `--config` and reflects the chosen YAML.

## Recommendations for next session
1. Promote the fine-phase winner to champion (`config/strategy/champions/tBTCUSD_1h.json`) after a sanity check.
2. Consider micro-tuning (even tighter ranges or exposing new parameters such as Fibonacci).
3. Automate the coarse -> proxy -> fine pipeline and plan early-stop handling in backtests.
4. Update `docs/optimizer.md` once the champion is changed.

## Miscellaneous
- Optuna databases:
  - Proxy: `optuna_tBTCUSD_1h_proxy.db`
  - Full period: `optuna_tBTCUSD_1h_6m.db`
  - Fine: `optuna_tBTCUSD_1h_fine.db`
- All backtest results are stored in `results/backtests/`.
