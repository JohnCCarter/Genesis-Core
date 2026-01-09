## 2025-11-14 — Phase 7d (Champion-återställning & Optuna remodel)

### Utfört

- Återställde championfilen `config/strategy/champions/tBTCUSD_1h.json` till originalparametrarna från `run_20251023_141747` (höga `entry_conf_overall`, aktiva HTF/LTF-fib-gates, HTF-exit med partials och trailing).
- Kör manuellt backtest med den återställda championen över snapshotperioden (`scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h --start 2024-10-22 --end 2025-10-01`). Resultat: 0 trades (score -100.2) → bekräftar att aktuellt runtime-flöde fortfarande saknar `htf_fib`/`ltf_fib` metadata när gatesen är på.
- Skapade och validerade `config/optimizer/tBTCUSD_1h_optuna_remodel_v1.yaml` (120 trials, 32 bootstrap, bred sökrymd för thresholds/signal_adaptation/fib-gates/risk_map/exit/MTF). Preflight + champion-validering OK.
- Startade Optuna-run `run_20251114_remodel_bootstrap` med nya konfigurationen (miljö: FAST_WINDOW, PRECOMPUTE, RANDOM_SEED=42, MAX_CONCURRENT=4, OPTUNA_MAX_DUPLICATE_STREAK=2000).

### Körningsstatus

- Bootstrapfasen producerar nu riktiga trials (20 sparade `trial_*.json` hittills). Exempel: `trial_002` → 282 trades, PF 1.10, score 0.21.
- Bästa constraint-godkända trial just nu: `trial_021` (139 trades, PF 1.74, score 0.99). Trials med 1–2 trades flaggas korrekt av `constraints.min_trades`.
- Resultatfiler och loggar: `results/hparam_search/run_20251114_remodel_bootstrap/`.

### Observationer

- Champion-backtest 0 trades även med originalparametrar → fib/MTF-gaten saknar fortfarande input i `evaluate_pipeline`. Behöver koppla in `htf_fibonacci`/`ltf_fib` metadata innan champion (eller Optuna-trials där gates=on) kan producera trades.
- Optuna-runnen visar att remodel-sökrymden fungerar: inga zero-trade-trials i JSON-statistiken, och risk_map-deltor + overrides varierar enligt YAML.

### Nästa steg

1. Säkerställ att `feats_meta["htf_fibonacci"]` och LTF-data förs in i state/out-decisions så championens gates släpper igenom signaler (annars måste de inaktiveras även i Optuna-konfigen).
2. Fortsätt övervaka `run_20251114_remodel_bootstrap`: exportera topp-trials efter bootstrapfasen och analysera gemensamma parametrar (t.ex. risk_map och override-trösklar).
3. Uppdatera championens referensbacktest när fib-dataflödet är fixat för att åter bekräfta 75 trades / PF 3.30.
