# README för AI-agenter (lokal utveckling)
_Senast uppdaterad: 2025-10-23_

Den här filen summerar hur vi arbetar lokalt med Genesis-Core, vad som levererades i dag och vad nästa agent behöver veta.

## 1. Dagens leveranser (23 oktober 2025)
- Resultatcache i `src/core/optimizer/runner.py` (`results/hparam_search/<run>/_cache/<hash>.json`) så att identiska parametrar inte backtestas igen.
- Ny optimeringspipeline:
  1. `config/optimizer/tBTCUSD_1h_coarse_grid.yaml` – grovsvep (27 kombinationer).
  2. `config/optimizer/tBTCUSD_1h_proxy_optuna.yaml` – 2 mån Optuna + Hyperband.
  3. `config/optimizer/tBTCUSD_1h_fine_optuna.yaml` – 6 mån finjustering runt vinnarna.
- Sammanfattningsverktyg: `python -m scripts.summarize_hparam_results --run-dir <results/hparam_search/run_...>` listar topptrials.
- Bästa konfiguration (trial_002, run_20251023_141747):
  - `entry_conf_overall = 0.35`
  - `regime_proba.balanced = 0.70`
  - `risk_map = [[0.45, 0.015], [0.55, 0.025], [0.65, 0.035]]`
  - `exit_conf_threshold = 0.40`, `max_hold_bars = 20`
  - Backtest: `results/backtests/tBTCUSD_1h_20251023_162506.json` → netto +10.43 %, PF 3.30, 75 affärer.

## 2. Arbetsflöde för optimering (coarse → proxy → fine)
1. Kör grovsvepet: `python -m core.optimizer.runner config/optimizer/tBTCUSD_1h_coarse_grid.yaml`.
2. Kör proxy-Optuna: `python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_proxy_optuna.yaml`.
3. Kör finjustering: `python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_fine_optuna.yaml`.
4. Sammanfatta varje run med `scripts/summarize_hparam_results`.
5. Validera fullperiod (vid behov) med `config/optimizer/tBTCUSD_1h_new_optuna.yaml`.
6. Kontrollera `_cache` innan nya backtester startas för att återanvända resultat.

### Snabbkommandon
```powershell
python -m scripts.summarize_hparam_results --run-dir results/hparam_search/run_YYYYMMDD_HHMMSS
python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_proxy_optuna.yaml
python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_fine_optuna.yaml
```

## 3. Rekommenderad championkandidat (att verifiera i morgon)
| Parameter | Värde |
|-----------|-------|
| `entry_conf_overall` | 0.35 |
| `regime_proba.balanced` | 0.70 |
| `risk_map` | `[[0.45, 0.015], [0.55, 0.025], [0.65, 0.035]]` |
| `exit_conf_threshold` | 0.40 |
| `max_hold_bars` | 20 |

- Källa: `results/hparam_search/run_20251023_141747/trial_002.json`.
- Nästa agent bör uppdatera `config/strategy/champions/tBTCUSD_1h.json` efter egen kontroll.
- Proxyvinnaren (`results/backtests/tBTCUSD_1h_20251023_152720.json`) är kvar som referens (+8.98 %, PF 3.03).

## 4. Nästa steg (fortsätter i morgon)
1. Promota vinnaren till champion och uppdatera runtime-config.
2. Överväg mikrotuning (ännu snävare intervall eller nya parametrar såsom Fibonacci).
3. Automatisera hela “coarse → proxy → fine”-flödet och titta på tidig stopp i backtesten.
4. Dokumentera champion-uppdateringen i `docs/optimizer.md`.
5. Planera eventuell feature-expansion så att fler rattar kan autotunas i nästa iteration.

## 5. Historik (Phase-7a/7b, 21 oktober 2025)
- Snapshot låst: `tBTCUSD_1h_2024-10-22_2025-10-01_v1`.
- Baseline-backtest loggad (`results/backtests/tBTCUSD_1h_20251020_155245.json`).
- Runner fick resume/skip, metadata, concurrency och retries.
- ChampionManager & ChampionLoader integrerades i pipeline/backtest.
- Walk-forward-körningar (`wf_tBTCUSD_1h_20251021_090446`, ATR-zonjustering `wf_tBTCUSD_1h_20251021_094334`).
- Optuna-stöd (median-pruner) infördes; `scripts/optimizer.py summarize --top N` och dokumentation uppdaterades (`docs/optimizer.md`, `docs/TODO.md`).
- Se `docs/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md` för planerade exit-förbättringar.

## 6. Deployment och drift
- Genesis-Core är byggt för **single-user**-drift; API-nycklar hanteras via `.env`.
- Produktion körs bäst på egen VPS/cloud; Champion-filer ligger i `config/strategy/champions/`.
- `ChampionLoader` ansvarar för auto-reload i pipeline/backtest.

## 7. Regler för agenter
- Följ separation of concerns – `core/strategy/*` ska vara deterministiska.
- Ingen hemlig data i loggar; använd `core.utils.logging_redaction` vid behov.
- Pausa vid osäkerhet och verifiera med tester innan du fortsätter.
- Skriv enhetstester vid ny logik; mål < 20 ms per modul.
- `metrics` används endast i orkestreringslagret (`core/strategy/evaluate.py`).
- Respektera cachen och spara alltid backtestresultat i `results/backtests/`.

## 8. Setup (Windows PowerShell)
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev,ml]
```

## 9. Quick start, referenser och viktiga skript
- Feature-pipeline: `src/core/strategy/features_asof.py`, `scripts/precompute_features_v17.py`.
- Backtest: `scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --capital 10000`.
- Modellträning: `scripts/train_model.py` (se `docs/FEATURE_COMPUTATION_MODES.md`).
- Indikatorreferens: `docs/INDICATORS_REFERENCE.md`.
- Exit-logik: `docs/EXIT_LOGIC_IMPLEMENTATION.md`.
- Valideringschecklista: `docs/VALIDATION_CHECKLIST.md`.
- Nästa fas (Fibonacci fraktal exits): `docs/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md`.
- Modell-cache: `curl -X POST http://127.0.0.1:8000/models/reload` efter ny modell.

---

> **Kom ihåg:** följ kedjan _coarse → proxy → fine_, utnyttja cachen och skriv alltid in resultat i `docs/daily_summary_YYYY-MM-DD.md`. Nästa agent börjar med att promota vinnaren och uppdatera dokumentationen.
