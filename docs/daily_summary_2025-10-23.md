# Dagsrapport – 23 oktober 2025

## Körningar
- **Proxy-Optuna** (`config/optimizer/tBTCUSD_1h_proxy_optuna.yaml`)  
  - Resultat: `results/hparam_search/run_20251023_131910`  
  - Topptrial: `trial_003` → score 224.66, PF 3.03, 75 trades  
  - Parametrar: `entry_conf=0.40`, `regime_bal=0.80`, `risk_map=[[0.4,0.01],[0.5,0.02],[0.6,0.03]]`, `exit_conf=0.60`, `max_hold=15`  
  - Backtest: `results/backtests/tBTCUSD_1h_20251023_152720.json` (netto +8.98 %, vinster 3 520 USD, förluster –2 187 USD)

- **6-mån validering** (`config/optimizer/tBTCUSD_1h_new_optuna.yaml`)  
  - Studie: `optuna_tBTCUSD_1h_6m.db`  
  - Nya trials gav score ≤ 186.65 – ingen förbättring jämfört med proxyvinnaren.

- **Finjustering** (`config/optimizer/tBTCUSD_1h_fine_optuna.yaml`)  
  - Resultat: `results/hparam_search/run_20251023_141747`  
  - Bästa trial: `trial_002` → score 260.73, PF 3.30, 75 trades  
  - Parametrar: `entry_conf=0.35`, `regime_bal=0.70`, `risk_map=[[0.45,0.015],[0.55,0.025],[0.65,0.035]]`, `exit_conf=0.40`, `max_hold=20`  
  - Backtest: `results/backtests/tBTCUSD_1h_20251023_162506.json` (netto +10.43 %, vinster 3 641 USD, förluster –2 554 USD)

## Kod- och verktygsändringar
- Resultatcache i `src/core/optimizer/runner.py` (`_cache/<hash>.json`).
- Nytt sammanfattningsskript: `scripts/summarize_hparam_results.py`.
- YAML-profiler för coarse/proxy/fine-optimering.
- `test_optuna_new_1_3months.py` tar nu `--config`-flaggan och speglar konfigen dynamiskt.

## Rekommendationer inför nästa pass
1. Uppdatera champion (`config/strategy/champions/tBTCUSD_1h.json`) med finvinnaren efter egen kontroll.
2. Överväg mikrotuning (ännu snävare intervall eller nya parametrar, exempelvis Fibonacci).
3. Automatisera pipeline “coarse → proxy → fine” och planera ev. tidig stopp i backtesten.
4. Dokumentera champion-uppdateringen i `docs/optimizer.md`.

## Övrigt
- Optuna-databaser:  
  - Proxy: `optuna_tBTCUSD_1h_proxy.db`  
  - Fullperiod: `optuna_tBTCUSD_1h_6m.db`  
  - Fine: `optuna_tBTCUSD_1h_fine.db`
- Samtliga backtestfiler sparas i `results/backtests/`.
