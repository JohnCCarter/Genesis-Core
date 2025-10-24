# Optimeringssammanfattning – 23 oktober 2025

## Dagens körningar

- **Proxy‑Optuna (2-mån fönster)**

  - Konfig: `config/optimizer/tBTCUSD_1h_proxy_optuna.yaml`
  - Resultatkatalog: `results/hparam_search/run_20251023_131910`
  - Topptrial: `trial_003`
    - `entry_conf_overall=0.40`, `regime_balanced=0.80`
    - `risk_map=[[0.4,0.01],[0.5,0.02],[0.6,0.03]]`
    - `exit_conf_threshold=0.60`, `max_hold_bars=15`
    - Score **224.66** → backtest `results/backtests/tBTCUSD_1h_20251023_152720.json`
    - Netto +8.98 % (3 520 USD vinster, –2 187 USD förluster), PF 3.03, 75 affärer.

- **Fullperiodsvalidering (6 månader)**

  - Konfig: `config/optimizer/tBTCUSD_1h_new_optuna.yaml`
  - Resultatkatalog: uppdaterad `results/hparam_search/run_20251023_120952`
  - Ingen trial slog ovanstående baseline; bästa nya score 186.65 (`risk_map` med större storlekar).

- **Finjustering runt vinnaren**
  - Konfig: `config/optimizer/tBTCUSD_1h_fine_optuna.yaml`
  - Resultatkatalog: `results/hparam_search/run_20251023_141747`
  - Bästa score **260.73** (`trial_002`)
    - `entry_conf_overall=0.35`, `regime_balanced=0.70`
    - `risk_map=[[0.45,0.015],[0.55,0.025],[0.65,0.035]]`
    - `exit_conf_threshold=0.40`, `max_hold_bars=20`
    - Backtest `results/backtests/tBTCUSD_1h_20251023_162506.json` → netto +10.43 %, PF 3.30.

## Viktiga förändringar

- Infört resultatcache i `src/core/optimizer/runner.py` (`_cache/<hash>.json`).
- Nytt sammanfattningsskript: `scripts/summarize_hparam_results.py`.
- Tre YAML-profiler:
  1. `tBTCUSD_1h_coarse_grid.yaml` – grovsvep
  2. `tBTCUSD_1h_proxy_optuna.yaml` – snabb Optuna (2 månader)
  3. `tBTCUSD_1h_fine_optuna.yaml` – snäv Optuna runt vinnande kombination.

## Rekommenderade nästa steg (fortsätter i morgon)

1. **Promota vinnaren** – uppdatera champion/runtimelogik med `trial_002` från finkörningen (entry 0.35, risk_map 0.45–0.65, exit_conf 0.40, max_hold 20).
2. **Micro‑finjustering** – om vi vill pressa vidare: kör en ännu snävare Optuna (t.ex. entry 0.33–0.38, risk_map små variationer) eller öppna fler rattar (Fibonacci, features).
3. **Automatisera pipeline** – sätt upp sekvensen “coarse → proxy → fine” som standardflöde, eventuellt med tidig stopp och parallellkörning som nästa förbättring.

_Notering_: Alla backtestfiler ligger under `results/backtests/`; Optuna-databaser:
`optuna_tBTCUSD_1h_proxy.db` (proxy), `optuna_tBTCUSD_1h_fine.db` (fine), `optuna_tBTCUSD_1h_6m.db` (fullperiod).

Vi fortsätter arbetet i morgon med champion‑uppdatering och plan för nästa optimeringsfas.
