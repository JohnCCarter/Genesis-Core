# Handoff: Risk State (Phase D) — Branch `feature/Optuna-Phased-v4`

## Vad som gjorts

### Phased Optuna Optimisation (Phase A → E)

Branch `feature/Optuna-Phased-v4` bygger på master efter den stora refaktorn (runner split, decision split).

**Phase A** (150 trials): Threshold + exit-optimering. 13 tunable params.
**Phase B** (100 trials): Regime Intelligence (RI) clarity + sizing. 7 tunable params. Bugfix: `weights` key + `size_multiplier` lookup i `decision_sizing.py`.
**Phase C** (1 trial): OOS-validering 2025. Score=0.1612, PF=1.46, DD=3.90%.
**Phase D** (75 trials): Risk State optimering. 7 tunable params (drawdown_guard + transition_guard).
**Phase E** (1 trial): OOS-validering 2025 med risk_state. Score=0.1580, PF=1.45, DD=3.86%.

### Risk State — implementerade filer

1. **`src/core/backtest/engine.py`** (~rad 888): Injicerar `equity_drawdown_pct` och `_peak_equity` i `self.state` innan `evaluate_pipeline()`.

2. **`src/core/strategy/decision_sizing.py`**:
   - Persisterar `last_regime` + `bars_since_regime_change` i `state_out` (sist i funktionen).
   - Beräknar `risk_state_mult` via `compute_risk_state_multiplier()` och multiplicerar in i `combined_mult`.
   - Skriver `ri_risk_state_*` debug-keys till `state_out`.

3. **`src/core/strategy/regime_intelligence.py`**: Ny funktion `compute_risk_state_multiplier(cfg, equity_drawdown_pct, bars_since_regime_change)`. Returnerar dict med `multiplier` [0.05–1.0], `drawdown_mult`, `transition_mult`.

4. **`src/core/optimizer/runner.py`**: `_inject_base_phase_params()` fixad att acceptera direkt JSON-sökväg (`.json` suffix) utöver katalog.

### Tester

- `tests/utils/test_risk_state_engine.py` — 4 tester (equity injection + regime transition)
- `tests/utils/test_risk_state_multiplier.py` — 9 tester (disabled, drawdown, transition, multiplicative, debug keys)

### YAML-configs

- `config/optimizer/tBTCUSD_3h_phased_v3_phaseD.yaml` — Phase D (75 trials, 7 risk_state tunable + alla A/B fixerade)
- `config/optimizer/tBTCUSD_3h_phased_v3_phaseE_oos.yaml` — Phase E OOS (alla fixerade, 2025)
- `config/optimizer/phased_v3_best_trials/` — best_trial JSON för varje fas

## Resultat

### Phase D IS (2024) — Best trial_039

| Metric | Utan risk_state | Med risk_state | Delta |
|--------|----------------|----------------|-------|
| Score  | 0.3337         | **0.3393**     | +1.7% |
| Return | +3.63%         | +2.79%         | -0.84pp |
| PF     | 2.06           | **2.10**       | +2% |
| Max DD | 1.31%          | **1.30%**      | -0.8% |
| Sharpe | 0.252          | **0.256**      | +1.6% |

### Phase E OOS (2025) — Isoleringstest

| Variant          | Score  | Return | PF   | Max DD | Sharpe |
|-----------------|--------|--------|------|--------|--------|
| Utan risk_state | 0.1612 | -2.08% | 1.46 | 3.90%  | 0.124  |
| Bara drawdown   | 0.1580 | -2.11% | 1.45 | 3.86%  | 0.119  |
| Bara transition | 0.1611 | -2.08% | 1.46 | 3.89%  | 0.121  |
| Båda            | 0.1580 | -2.11% | 1.45 | 3.86%  | 0.119  |

**Slutsats:** Risk_state har minimal effekt på OOS 2025 (max DD bara 3.9%, under drawdown_guard threshold 6%). Funktionaliteten fungerar korrekt men behöver en period med djupare drawdowns för att visa värde.

## Bästa risk_state-parametrar (trial_039)

```yaml
risk_state:
  enabled: true
  drawdown_guard:
    soft_threshold: 0.06
    hard_threshold: 0.06   # = soft, effektiv single-step
    soft_mult: 0.90
    hard_mult: 0.20        # aggressiv vid 6%+ DD
  transition_guard:
    enabled: true
    guard_bars: 8          # 24h skyddsfönster (3h bars)
    mult: 0.40             # 60% reduktion under transitions
```

## Nästa steg att överväga

1. **Testa på mer volatil period** — data med 10-20% drawdowns för att se risk_state i aktion.
2. **Testa andra instrument** — tETHUSD eller liknande med högre volatilitet.
3. **Sänka drawdown_guard thresholds** — nuvarande 6% triggas aldrig i OOS. Testa 2-3% thresholds.
4. **Merge till master** — risk_state-koden är ren, testad, och neutral (enabled=false by default).

## Kommandon

```bash
# Kör alla tester
PYTHONPATH=src pytest tests/utils/test_risk_state_engine.py tests/utils/test_risk_state_multiplier.py -v

# Kör Phase D (75 trials, IS 2024)
PYTHONIOENCODING=utf-8 TQDM_DISABLE=1 PYTHONPATH="$(pwd)/src" python -m core.optimizer.runner config/optimizer/tBTCUSD_3h_phased_v3_phaseD.yaml

# Kör Phase E OOS (1 trial, 2025)
PYTHONIOENCODING=utf-8 TQDM_DISABLE=1 PYTHONPATH="$(pwd)/src" python -m core.optimizer.runner config/optimizer/tBTCUSD_3h_phased_v3_phaseE_oos.yaml
```
