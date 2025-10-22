# Phase 7a – Testresultat

## Baseline 2024-10-22 → 2025-10-01
- Kommando: `python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --start 2024-10-22 --end 2025-10-01 --warmup 150`
- Resultatfil: `results/backtests/tBTCUSD_1h_20251020_155245.json`
- Nyckeltal:
  - Total Return: 21.24%
  - Trades: 82
  - Win Rate: 37.8%
  - Sharpe Ratio: 0.133
  - Max Drawdown: 11.92%
  - Profit Factor: 2.45

> Alla kommande optimeringskörningar loggas här. Ange alltid snapshot-id, parametrar, resultatfiler och nyckeltal.

## Walk-forward – Champion baseline (2025-10-21)
- Run ID: `wf_tBTCUSD_1h_20251021_092714`
- Championkälla: fallback `baseline:1h` (ingen signal_adaptation)
- Trades per period: P1=0, P2=2, P3=0, P4=0, P5=0, P6=2
- Zonetiketter: endast `ZONE:base@0.400`
- Nyckeltal (per period)
  - P2: +1.65 % (2 trades, PF 1.84)
  - P6: +1.10 % (2 trades, PF ∞)

## Walk-forward – Champion med ATR-zoner (2025-10-21)
- Run ID: `wf_tBTCUSD_1h_20251021_094334`
- Championkälla: `config/strategy/champions/tBTCUSD_1h.json` (signal_adaptation aktiverad)
- Zon-distribution: `low` dominerar (P1=3, P2=2, P3=1, P4=1), `mid` aktiveras i P1–P3; inga `high` ännu
- Trades per period: P1=4, P2=3, P3=2, P4=1, P5=0, P6=0
- Nyckeltal (per period)
  - P1: +1.14 % (PF 4.46, 4 trades)
  - P2: –0.68 % (PF 1.67, 3 trades)
  - P3: –2.44 % (2 trades, båda förlust)
  - P4: –0.74 % (1 trade)
  - P5–P6: 0 % (inga triggers)
- Observationer: Zonlogiken ger fler trades men kräver vidare tuning (höj mid/high trösklar, utvärdera filter för att minska förluster i P3–P4).
