# Daily Summary 2025-11-19 – Runtime-schemat öppnat upp

## Utfört

### RuntimeConfig uppdaterad
- `src/core/config/schema.py` accepterar nu `warmup_bars`, `htf_exit_config` och fullständiga `htf_fib`/`ltf_fib`-block (inkl. override-konfidens och fib-targetlistor). Detta gör att `scripts/apply_runtime_patch.py --full` kan skriva hela championprofiler utan att Pydantic klipper bort sektioner.
- Verifierade med:
  - `python -c "import json;from core.config.schema import RuntimeConfig;RuntimeConfig(**json.load(open('config/tmp/tmp_user_test.json'))['cfg'])"`
  - `python -c "import json;from core.config.schema import RuntimeConfig;payload=json.load(open('config/strategy/champions/tBTCUSD_1h.json'));RuntimeConfig(**payload['cfg']['parameters'])"`
  - `python -c "import json;from core.config.schema import RuntimeConfig;payload=json.load(open('config/runtime.json'));RuntimeConfig(**payload['cfg'])"`

### Runtime synkad mot champion
- `config/runtime.json` version 94 speglar nu championparametrarna från `config/strategy/champions/tBTCUSD_1h.json` (entry 0.35, ATR-zoner 0.25/0.28/0.32, fib-gates på 0.5 tolerance, HTF-exit-partials 0.6/0.5, warmup_bars 150).
- Keepade tidigare `ev.R_default`, `exit.stop_loss/take_profit` och `ltf_override_threshold=0.75` för att bibehålla säkerhetsnätet medan championens fib/MTF-block är aktiva.
- Ger identisk runtime som champion för backtester/servrar utan att behöva manuella patchar innan körning.

## Nästa
- Rulla ett sanity-backtest mot `scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h` för att verifiera att fib-gates nu producerar trades i runtime igen.
- Uppdatera eventuell dokumentation om hur `apply_runtime_patch.py --full` ska användas när hela champion-profiler importeras.
