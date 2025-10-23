# README för AI-agenter (lokal utveckling)
_Senast uppdaterad: 2025-10-23_

Den här filen summerar hur vi arbetar lokalt med Genesis-Core, vad som levererades i dag och vad nästa agent behöver veta innan arbetet fortsätter.

## 1. Dagens leveranser (23 oktober 2025)
- **Resultatcache i optimizer-runner** – varje trial skrivs till `results/hparam_search/<run>/_cache/<hash>.json`, så identiska parametrar återanvänder backtestresultat.
- **Ny optimeringspipeline**  
  1. `config/optimizer/tBTCUSD_1h_coarse_grid.yaml` – grovsvep (27 kombinationer).  
  2. `config/optimizer/tBTCUSD_1h_proxy_optuna.yaml` – 2 månader, Hyperband, snabb feedback.  
  3. `config/optimizer/tBTCUSD_1h_fine_optuna.yaml` – 6 månader, snäva intervall runt vinnarna.
- **Resultatsammanfattning** – `python -m scripts.summarize_hparam_results --run-dir <results/hparam_search/run_...>` listar topptrials med score, PF, trades och parametrar.
- **Bästa konfiguration hittills** (`trial_002`, run_20251023_141747):  
  `entry_conf_overall=0.35`, `regime_balanced=0.70`, `risk_map=[[0.45,0.015],[0.55,0.025],[0.65,0.035]]`, `exit_conf_threshold=0.40`, `max_hold_bars=20`.  
  Backtest: `results/backtests/tBTCUSD_1h_20251023_162506.json` → netto +10.43 %, PF 3.30, 75 affärer.

## 2. Arbetsflöde för optimering (coarse → proxy → fine)
1. **Grov grid** – kör `python -m core.optimizer.runner config/optimizer/tBTCUSD_1h_coarse_grid.yaml` för att kartlägga området.  
2. **Proxy-Optuna** – kör `python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_proxy_optuna.yaml`. Studien (`optuna_tBTCUSD_1h_proxy.db`) kan återupptas när som helst.  
3. **Finjustering** – kör `python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_fine_optuna.yaml`. Resultatet loggas i `optuna_tBTCUSD_1h_fine.db`.  
4. **Sammanfatta** – använd `scripts/summarize_hparam_results` på respektive run-katalog.  
5. **Full validering** – kör den fulla 6-månaderskonfigurationen `tBTCUSD_1h_new_optuna.yaml` på de bästa kandidaterna om extra bekräftelse behövs.  
6. **Cacha** – kontrollera mappen `_cache` innan du startar fler backtester; samma parametrar återanvänder då resultatet direkt.

### Snabbkommandon
```powershell
python -m scripts.summarize_hparam_results --run-dir results/hparam_search/run_YYYYMMDD_HHMMSS
python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_proxy_optuna.yaml
python test_optuna_new_1_3months.py --config config/optimizer/tBTCUSD_1h_fine_optuna.yaml
```

## 3. Rekommenderad championkandidat (att verifiera i nästa pass)
| Parameter | Värde |
|-----------|-------|
| `entry_conf_overall` | 0.35 |
| `regime_proba.balanced` | 0.70 |
| `risk_map` | `[[0.45, 0.015], [0.55, 0.025], [0.65, 0.035]]` |
| `exit_conf_threshold` | 0.40 |
| `max_hold_bars` | 20 |

- Kandidaten finns i `results/hparam_search/run_20251023_141747/trial_002.json`.  
- Nästa agent bör uppdatera `config/strategy/champions/tBTCUSD_1h.json` efter egen sanity-check.  
- Proxyvinnaren (`results/backtests/tBTCUSD_1h_20251023_152720.json`) är kvar som referens (netto +8.98 %, PF 3.03, 75 trades).

## 4. Nästa steg (att fortsätta i morgon)
1. **Promota vinnaren** till champion och uppdatera runtime-config.  
2. **Överväg mikrotuning** – exempelvis ännu snävare intervall runt entry 0.33–0.38 eller exponera fler rattar (Fibonacci-parametrar, signal-adaptation mm).  
3. **Automatisera pipeline** – script/styrning för hela “coarse → proxy → fine”-flödet + eventuellt tidig stopp i backtesten.  
4. **Dokumentera** i `docs/optimizer.md` när championen är uppdaterad.  
5. **Planera feature-expansion** (när tiden finns): vilka parametrar i features/exits ska öppnas i YAML för autotune.

## 5. Historik (Phase-7a/7b, 21 oktober 2025)
- Snapshot låst: `tBTCUSD_1h_2024-10-22_2025-10-01_v1`.  
- Baseline-backtest loggad (`results/backtests/tBTCUSD_1h_20251020_155245.json`).  
- Runner fick resume/skip, run-metadata, concurrency och retries.  
- ChampionManager & ChampionLoader integrerades (auto-reload i pipeline/backtest).  
- Walk-forward-körningar (`wf_tBTCUSD_1h_20251021_090446`, ATR-zonjustering i `wf_tBTCUSD_1h_20251021_094334`).  
- Optuna-stöd introducerades (median-pruner), rapport-CLI (`scripts/optimizer.py summarize --top N`), och dokumentation (`docs/optimizer.md`, `docs/TODO.md`).  
- Dokumentation för större exit-förändringar finns i `docs/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md`.

## 6. Deployment och drift
- Genesis-Core är byggt för **single-user**-drift (ingen multi-user-access).  
- API-nycklar och secrets hanteras via `.env`.  
- Produktion: personlig VPS eller motsvarande.  
- Champion-filer ligger under `config/strategy/champions/*.json` och laddas av `ChampionLoader`.

## 7. Regler för agenter
- Följ separation of concerns – `core/strategy/*` ska vara deterministiska.  
- Ingen hemlig data i loggar; använd `core.utils.logging_redaction` vid behov.  
- Pausa vid osäkerhet och verifiera med tester innan du fortsätter.  
- Skriv enhetstester när du lägger till logik; sträva efter < 20 ms per modul.  
- `metrics` får endast användas i orkestreringslagret (`core/strategy/evaluate.py`).  
- Respektera cachen och spara alltid backtestresultat i `results/backtests/`.

## 8. Setup (Windows PowerShell)
```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev,ml]
```

## 9. Quick start, referensdokument och viktiga skript
- **Feature-pipeline**: `src/core/strategy/features_asof.py`, `scripts/precompute_features_v17.py`.  
- **Backtest**: `scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --capital 10000`.  
- **Modellträning**: `scripts/train_model.py` (v16-modellen, se `docs/FEATURE_COMPUTATION_MODES.md`).  
- **Indikatorreferens**: `docs/INDICATORS_REFERENCE.md`.  
- **Exit-logik**: `docs/EXIT_LOGIC_IMPLEMENTATION.md`.  
- **Valideringschecklista**: `docs/VALIDATION_CHECKLIST.md`.  
- **Nästa fas (Fibonacci fraktal exits)**: `docs/FIBONACCI_FRAKTAL_EXITS_IMPLEMENTATION_PLAN.md`.  
- **Modell-cache**: `curl -X POST http://127.0.0.1:8000/models/reload` efter ny modell.

---

> **Kom ihåg:** all ny optimering ska följa kedjan _coarse → proxy → fine_, använda cachen och sammanfattas i `docs/daily_summary_YYYY-MM-DD.md`. Nästa agent börjar med att promota vinnaren och uppdatera dokumentationen.*** End Patch
