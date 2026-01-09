## `config/tmp/` profiler (2025-11-03)

Den här katalogen samlar experimentella strategikonfigurationer som inte ska checkas in i produktionen men som används för riktade backtester.

- `champion_base.json` – ren kopia av nuvarande champion (`config/strategy/champions/tBTCUSD_1h.json`) för referenstester.
- `conservative.json`, `balanced.json`, `trend_follow.json`, `aggressive.json` – varianter kring championens risk/entry/exit-parametrar för snabba A/B-tester.
- `balanced_htf_tune.json` – dagens HTF-experiment (fib-threshold 0.85, trailing 1.6, HTF tolerance 0.55) som gav färre fallback-exits i loggarna. Använd denna som utgångspunkt för vidare HTF-tuning.

> Obs! Profilerna versioneras här tills Optuna/grids visar att de bör promoveras. Flytta i så fall in i `config/strategy/` eller `config/optimizer/` och uppdatera dokumentationen.
