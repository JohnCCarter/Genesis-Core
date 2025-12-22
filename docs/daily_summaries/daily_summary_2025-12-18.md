# Daily Summary - 2025-12-18

## Syfte

Målet idag var att få tillbaka en **stark lärsignal** i Optuna genom att:

- köra en snabb **Explore-stage** på ett kortare fönster (H1 2024),
- därefter köra en striktare **Validate-stage** på ett längre fönster (FY 2024) för top-N kandidater,
- samt se till att smoke/explore-körningar **inte kan råka skriva över champions**.

## Genomfört

### 1) Explore → Validate (tvåstegsflöde)

- `src/core/optimizer/runner.py` stöder nu ett tvåstegsflöde:
  - Explore kör Optuna på primärfönstret.
  - Top-N (sorterat på score) körs om i `validation/` med separat fönster + striktare constraints.
  - Valideringsresultat sparas per run och används för rapportering (och kan prioriteras vid urval).

### 2) Promotion-säkerhet (smoke kan inte uppdatera champion)

- Promotion är uttryckligen konfigstyrd:
  - `promotion.enabled: false` i smoke-konfig.
  - `promotion.min_improvement` finns som extra spärr när promotion är på.
- Tester finns i `tests/test_optimizer_runner.py` (bl.a. att disabled promotion inte skriver champion).

### 3) Smoke-konfig: fönster, constraints och “in-memory” storage

Konfig: `config/optimizer/tBTCUSD_1h_optuna_phase3_fine_v7_smoke_explore_validate.yaml`

- **Explore window**: `2024-01-01 → 2024-06-30`
- **Validate window**: `2024-01-01 → 2024-12-31`
- **Storage**: `optuna.storage: null` (in-memory) för att undvika study/DB-kollisioner vid upprepad smoke.
- **Explore constraints** är medvetet lösare (för mer signal); Validate constraints är striktare:
  - `min_trades: 80`, `max_trades: 320`, `min_profit_factor: 1.0`, `max_max_dd: 0.20`,
    `max_total_commission_pct: 0.05`, `include_scoring_failures: true`.

### 4) Search space-tuning för att eliminera 0-trade slöseri

I samma konfig stramades vissa intervall åt för att undvika regioner som historiskt gav 0 trades:

- `thresholds.signal_adaptation.zones.low.entry_conf_overall.high: 0.27`
- `thresholds.min_edge.high: 0.011`

Resultatet blev **0.0 i zero_trade_ratio** i båda huvudkörningarna nedan.

## Resultat och beslut

### Run A: 30 trials + top-3 validate

- Run-dir: `results/hparam_search/run_20251218_ev_30t_nopromo`
- Explore (H1 2024):
  - `n_trials=30`, `best_value=0.3412553578988905`, `best_trial_number=20`
  - diagnostics: `duplicate_ratio=0.0`, `pruned_ratio=0.0`, `zero_trade_ratio=0.0`
- Validate (FY 2024): `top_n=3`
  - validerade: 3
  - constraints-pass: **1/3**
  - vanligaste fail: `pf<1.0`

### Run B: 60 trials + top-5 validate

- Run-dir: `results/hparam_search/run_20251218_ev_60t_top5_nopromo`
- Explore (H1 2024):
  - `n_trials=60`, `best_value=0.7643925623360731`, `best_trial_number=43`
  - diagnostics: `duplicate_ratio=0.0`, `pruned_ratio=0.0`, `zero_trade_ratio=0.0`
- Validate (FY 2024): `top_n=5`
  - validerade: 5
  - constraints-pass: **4/5**
  - 1 fail: `pf<1.0`

#### Bästa validerade kandidat (FY 2024)

I `validation/` för Run B var bästa constraints-godkända kandidat:

- `validation/trial_002.json`
  - score: `0.560492748560641`
  - metrics: total_return `+4.09%`, PF `1.52`, maxDD `3.99%`, trades `158`, commission_pct `2.56%`

### Champion-status

- Promotion var avstängt i båda runs (`promotion.enabled: false`).
- Ingen champion uppdaterades (med flit).

## Teststatus

- Inga nya kodtester körda i samband med denna sammanfattning.
- Runner-flödet har enhetstester i `tests/test_optimizer_runner.py` (promotion + min_improvement).

## Mini-logg (körningar / artifacts)

- Smoke/EV config: `config/optimizer/tBTCUSD_1h_optuna_phase3_fine_v7_smoke_explore_validate.yaml`
- Run A: `results/hparam_search/run_20251218_ev_30t_nopromo`
  - validation: 1/3 pass
- Run B: `results/hparam_search/run_20251218_ev_60t_top5_nopromo`
  - validation: 4/5 pass (1 fail pf<1.0)

## Stabilisering: canonical mode policy + docs + QA

### Canonical policy (quality decisions) 2025-12-18

- Beslut: **1/1 (fast_window + precompute)** är canonical för alla jämförelser/”quality decisions” (Optuna/Validate/champion/reporting).
- 0/0 är **debug-only** och ska inte jämföras mot canonical.
- För att tillåta icke‑canonical mode krävs explicit markering via `GENESIS_MODE_EXPLICIT=1`.

### Dokumentationsuppdateringar

- `README.md`: tydlig policy‑notis om canonical 1/1 och hänvisning till feature-modes.
- `docs/features/FEATURE_COMPUTATION_MODES.md`: beskriver canonical 1/1, debug-only 0/0 och `GENESIS_MODE_EXPLICIT`.
- `docs/performance/PERFORMANCE_GUIDE.md`: canonical policy + korrigerad precompute cache key‑beskrivning.
- `docs/optuna/OPTUNA_BEST_PRACTICES.md`: notis om canonical 1/1 kontra debug 0/0.

### Små tekniska fixar (stöd för QA)

- `scripts/verify_fib_connection.py` kör nu explicit 1/1 (undviker mixed-mode).
- Bandit: åtgärdade low findings genom att hämta `git` via absolut path (`shutil.which`) och smalare exceptions i defensiva parsningar.

### QA-status (kört idag)

- `black` OK
- `ruff` OK
- `bandit -c bandit.yaml -r src` OK (0 issues)
- `pytest` OK: 529 passed, 1 skipped
- `pre-commit run --all-files` OK

  - Not: på Windows kör vi `pre-commit` (bindestreck), inte `python -m pre_commit`.
