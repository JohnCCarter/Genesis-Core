# Daily Summary - 2025-11-27

## 1. Vad som gjorts

- Remap för precompute i `features_asof.py` är på plats (index-säker offset) och ger korrekt fib i backtester. Manuellt parity-backtest (2023-12-01 → 2025-11-19, warmup 150, seed 42, fast+precompute) gav 886 trades, PF 1.15, +23.56 % (fast hits 17 105, slow 0) sparat i `results/backtests/tBTCUSD_1h_20251127_124059.json`.
- Ny Optuna-konfig `config/optimizer/parity_trial_103749_optuna.yaml` skapad med sample_range (2023-12-01 → 2025-11-19) och ny storage/study (`optuna_parity_trial_103749_v2.db`).
- Körde Optuna parity-run med env `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`, `GENESIS_RANDOM_SEED=42`, `TQDM_DISABLE=1`, `PYTHONIOENCODING=utf-8`, `PYTHONLEGACYWINDOWSSTDIO=1`. Resultat: 1080 trades, PF 0.96, return -7.33 %, score -100.08. Loggar visar slow path (fast hits 0) och “precomputed_features saknas” + “Invalid swing”.

## 2. Kvarstående problem

- Optuna-runner använder fortfarande 17 278 bars (start 2023-11-30 10:00) trots sample_start/end i YAML; backtestet kör 17 255 bars (start 2023-12-01). Period-oskärpa ger olika swings/trades.
- Precompute laddas inte i Optuna-körningen (faller till slow path). Befintlig NPZ `cache/precomputed/tBTCUSD_1h_17255.npz` matchar backtestets 17 255 bars men inte Optuna-perioden; därför fortsatt “Invalid swing”.

## 3. MODE ENFORCEMENT - DETERMINISM LÖST ✅

**Problem:** Non-deterministiska resultat mellan körningar orsakade av att streaming och fast mode körde olika code paths.

**Lösning implementerad:**

1. **Validation i BacktestEngine**: Kastar ValueError om `fast_window=True` utan `GENESIS_PRECOMPUTE_FEATURES=1`
2. **Default till fast mode**: `run_backtest.py` och `runner.py` defaultar till fast mode för determinism
3. **Deprecated streaming mode**: `compare_modes.py` visar varning att använda fast mode

**Verifiering genomförd:**

### Test 6: Manual Backtest Determinism

Två identiska körningar (2024-06-01 till 2024-08-01, champion config):

- **Score**: -100.2217 (exakt match)
- **Trades**: 43 (exakt match)
- **Return**: -1.47% (exakt match)
- **PF**: 0.77 (exakt match)

### Test 7: Optimizer Determinism

Två identiska optimizer-körningar (3 grid trials, olika risk_map):

**Körning 1 (run_20251127_145833):**

- Trial 1: score = -100.21230742157763, trades = 654
- Trial 2: score = -100.37291700448048, trades = 1255
- Trial 3: score = -100.54983284409326, trades = 1854

**Körning 2 (run_20251127_150804):**

- Trial 1: score = -100.21230742157763, trades = 654
- Trial 2: score = -100.37291700448048, trades = 1255
- Trial 3: score = -100.54983284409326, trades = 1854

**Resultat:** Alla scores matchade med 15+ decimalers precision. Både manuella backtester OCH optimizer-körningar är nu 100% deterministiska.

**Miljövariabler för determinism:**

```powershell
GENESIS_FAST_WINDOW=1
GENESIS_PRECOMPUTE_FEATURES=1
GENESIS_RANDOM_SEED=42
GENESIS_MAX_CONCURRENT=1
```

**Dokumentation:**

- `docs/bugs/MODE_ENFORCEMENT_20251127.md` - Fullständig teknisk beskrivning + båda verifieringstesterna
- `AGENTS.md` - Deliverables uppdaterade med verifiering

## 4. Nästa steg

- ✅ Mode enforcement och determinism: **KLART**
- Säkerställ att `_resolve_sample_range` → BacktestEngine verkligen klipper till 2023-12-01 → 2025-11-19 (17255 bars). Om nödvändigt patcha runner/engine så sample_start/End används.
- Se till att precompute för samma spann laddas i Optuna (antingen använd befintlig `tBTCUSD_1h_17255.npz` eller skapa en NPZ för exakt den period Optuna kör). När period + precompute matchar bör Optuna ge samma ~886 trades/PF 1.15 som manuellt backtest.
