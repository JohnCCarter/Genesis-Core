# Daily Summary 2025-11-19 – Runtime-schemat öppnat upp

## Utfört

### RuntimeConfig uppdaterad

- `src/core/config/schema.py` accepterar nu `warmup_bars`, `htf_exit_config` och fullständiga `htf_fib`/`ltf_fib`-block (inkl. override-konfidens och fib-targetlistor). Detta gör att `scripts/apply_runtime_patch.py --full` kan skriva hela championprofiler utan att Pydantic klipper bort sektioner.
- Verifierade med:
  - `python -c "import json;from core.config.schema import RuntimeConfig;RuntimeConfig(**json.load(open('config/tmp/tmp_user_test.json'))['cfg'])"`
  - `python -c "import json;from core.config.schema import RuntimeConfig;payload=json.load(open('config/strategy/champions/tBTCUSD_1h.json'));RuntimeConfig(**payload['cfg']['parameters'])"`
  - `python -c "import json;from core.config.schema import RuntimeConfig;payload=json.load(open('config/runtime.json'));RuntimeConfig(**payload['cfg'])"`
- `features.percentiles` och `features.versions` stöds också av schemat, så feature-klippning/versionsflaggor från tmp-profiler överlever patchar till runtime.
- Alla runtime-sektioner tillåter nu extra metadata (`description`, `comment`, `feature_coefficients`, `metrics` osv.). `config/tmp/v17_6h_exceptional.json` laddas oförändrad via `RuntimeConfig(**...)` och kan patchas utan att förlora kontext.
- `core/strategy/decision.py` har fått detaljerade `[DECISION]`-loggar som dumpas vid varje gate (EV, proba/edge, HTF/LTF-fib, confidence, hysteresis, cooldown, risk-map). Noll-trade-backtester visar nu exakt vilken spärr som slog ut kandidaten.

### Runtime synkad mot champion

- `config/runtime.json` version 94 speglar nu championparametrarna från `config/strategy/champions/tBTCUSD_1h.json` (entry 0.35, ATR-zoner 0.25/0.28/0.32, fib-gates på 0.5 tolerance, HTF-exit-partials 0.6/0.5, warmup_bars 150).
- Keepade tidigare `ev.R_default`, `exit.stop_loss/take_profit` och `ltf_override_threshold=0.75` för att bibehålla säkerhetsnätet medan championens fib/MTF-block är aktiva.
- Ger identisk runtime som champion för backtester/servrar utan att behöva manuella patchar innan körning.

### Prestandaoptimering – ATR/Fibonacci-cache

- `core/indicators/fibonacci.py`, `core/indicators/htf_fibonacci.py` och `core/strategy/features_asof.py` delar nu ett cache:at ATR-array-flöde. Swing-detektionen arbetar direkt på sekvenser så att HTF/LTF-fibkonteksten inte triggar omberäkningar per bar.
- Feature-fingerprintet (`core/utils/diffing/feature_cache.py`) har fått ett numeriskt snabbspår som behåller tidigare hashlayout men eliminerar kostsamma pandas-flattening-steg.
- `core/strategy/fib_logging.py` är default-off och styrt av runtime-snittet vilket gör att noll-trade-körningar slipper gigantiskt loggbrus.
- Profilering (kommandon: cProfile + PyInstrument på guldkörningen) gav 159.1 s → 100.7 s total tid (−36.7 %) och 183 M → 75 M funktionsanrop (−59 %). `features_asof.extract_features` föll från 125.3 s → 72.7 s och `htf_fibonacci.get_ltf_fibonacci_context` från 62.0 s → 26.5 s.
- Resultat sparade i `reports/profiling/golden_run_after.cprofile` samt `reports/profiling/golden_run_pyinstrument_after.{html,txt}`. Backtestet gav fortfarande 0 trades (PROBA_THRESHOLD_FAIL), så fib-gate-flödet måste felsökas vidare men optimeringen är bekräftad.
- Tester: `pytest tests/test_feature_cache.py tests/test_fib_logging.py tests/test_fibonacci.py tests/test_precompute_vs_runtime.py -q` och `bandit -r src -c bandit.yaml -f txt -o bandit-report.txt` körda utan fel.

## Nästa

- Rulla ett sanity-backtest mot `scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h` för att verifiera att fib-gates nu producerar trades i runtime igen.
- Uppdatera eventuell dokumentation om hur `apply_runtime_patch.py --full` ska användas när hela champion-profiler importeras.
