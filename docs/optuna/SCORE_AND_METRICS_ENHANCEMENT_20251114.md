# Score och Metrics Enhancement - 2025-11-14

## Problem

- Backtest-resultat saknade score (används av Optuna för ranking)
- Optuna-output visade endast score, inte de underliggande metrics (return, trades, PF, etc.)

## Lösning

### 1. Backtest: Lägg till score i resultat

**Ändringar i `scripts/run_backtest.py`:**

- Importerar `score_backtest` från `core.optimizer.scoring`
- Beräknar score efter metrics-beräkning
- Lägger till score i results-dict innan sparande
- Visar score i output

**Resultat:**

```json
{
  "summary": {...},
  "score": {
    "score": 0.5865,
    "metrics": {
      "total_return": 0.0596,
      "profit_factor": 1.29,
      "max_drawdown": 0.0329,
      "win_rate": 0.407,
      "num_trades": 145,
      "sharpe_ratio": 0.067,
      "return_to_dd": 1.81
    },
    "hard_failures": []
  },
  "trades": [...]
}
```

**Output:**

```
=== Backtest Metrics ===
Total Return: 5.67%
Total Trades: 148
...

Score: 0.5865
```

### 2. Optuna: Visa metrics i output

**Ändringar i `src/core/optimizer/runner.py`:**

- Förbättrad output för trial-resultat
- Visar nu: score, trades, return, PF, DD, Sharpe, Win Rate

**Före:**

```
[Runner] Trial trial_001 klar på 38.3s (score=0.5865)
```

**Efter:**

```
[Runner] Trial trial_001 klar på 38.3s (score=0.5865, trades=145, return=5.96%, PF=1.29, DD=3.29%, Sharpe=0.067, WR=40.7%)
```

## Fördelar

1. **Konsistens:** Både backtest och Optuna använder samma scoring-metod
2. **Jämförbarhet:** Lättare att jämföra backtest-resultat med Optuna-trials
3. **Transparens:** Optuna-output visar nu alla viktiga metrics direkt
4. **Debugging:** Score finns i backtest-resultat för enklare analys

## Testning

### Backtest med score

```bash
python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h \
  --config-file config/tmp/tmp_user_test.json
```

**Förväntat output:**

- Score visas i terminal
- Score finns i JSON-resultatet

### Optuna med metrics

```bash
python -c "from core.optimizer.runner import run_optimizer; from pathlib import Path; run_optimizer(Path('config/optimizer/tmp_parity_test.yaml'))"
```

**Förväntat output:**

- Trial-resultat visar score + alla metrics

## Kompatibilitet

- ✅ Backwards compatible: Gamla backtest-resultat utan score fungerar fortfarande
- ✅ Optuna-trial-resultat har redan metrics i `score.metrics` (ingen ändring behövs)
- ✅ Score-beräkningen är identisk mellan backtest och Optuna

## Nästa steg

1. ✅ Score i backtest-resultat
2. ✅ Metrics i Optuna-output
3. ⏭️ (Optional) Lägg till score i `print_metrics_report()` för konsistent visning
