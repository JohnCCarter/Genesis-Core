## 2025-11-10 — Phase 7d (Optuna fib-tune, robust scoring, performance)

### Utfört

- Robust scoring: `score_backtest` hämtar PF/DD via `core.backtest.metrics.calculate_metrics` (inte direkt från `summary`). Skyddad `return_to_dd` vid noll‑DD.
- `PositionTracker.get_summary()` rapporterar nu korrekt `profit_factor` (gross_profit/gross_loss) och `max_drawdown` via equity‑kurva.
- Determinism: runner sätter `GENESIS_RANDOM_SEED=42` för backtest‑subprocesser om inte redan satt.
- Constraints: separerade från scoringens “hard_failures” och styrs via YAML (`include_scoring_failures`).
- YAML-schema: bladparametrar kräver `type: fixed|grid|float|int|loguniform`. Dokumenterat i `docs/optimizer.md`. Fixade smoke‑konfigen.
- Snabbkörning: aktiverade `GENESIS_FAST_WINDOW` + `GENESIS_PRECOMPUTE_FEATURES`, concurrency=2. Förbättrad throughput.
- Startade fib‑tune Optuna (1000 trials) med breddad sökrymd (entry 0.25–0.65, tolerans‑ATR 0.20–0.80, LTF‑override‑threshold 0.65–0.85), milda constraints.

### Körningsstatus

- Smoke: 2 trials körda end‑to‑end; inga constraints‑validerade trials (0 trades i en trial, soft‑penalty i en annan). Pipeline OK.
- Stor studie: `tBTCUSD_1h_optuna_fib_tune.yaml` (1000 trials) igång i bakgrunden med determinism och fast‑flags.

### Prestanda & stabilitet

- Avsevärt snabbare trials tack vare fast‑window, precompute och caching. Mindre dubbletter via TPE (`constant_liar`, `multivariate`, `n_ei_candidates` 512).
- NumPy‑ambiguitetsfel eliminerade (`features_asof`, `regime_unified`).

### Nästa steg

- Följ studien; rapportera topp‑trials (score, trades, PF, max DD) och jämför mot champion.
- Justera concurrency (3–4) om CPU‑headroom finns.
- (Liten) ML‑städning: byt `np.trapz`→`np.trapezoid` i `src/core/ml/evaluation.py` för att ta bort DeprecationWarning.

### Referens

- Uppdaterade filer: `src/core/optimizer/scoring.py`, `src/core/backtest/position_tracker.py`, `src/core/optimizer/runner.py`, `src/core/optimizer/constraints.py`, `config/optimizer/tBTCUSD_1h_optuna_fib_tune.yaml`, `docs/optimizer.md`.
