# Genombrott – Konfigurationsoptimering 2025-11-13

## Problem

Ursprunglig konfiguration gav endast 34 trades med PF 0.92 och negativt resultat (-0.10%). Stegvis isoleringstestning genomfördes för att identifiera flaskhalsen.

## Isoleringstestning

### Test 1: entry_conf_overall (0.32 → 0.28)

- **Resultat:** 34 trades (oförändrat)
- **Slutsats:** Inte flaskhalsen

### Test 2: regime_proba (alla → 0.50)

- **Resultat:** 34 trades (oförändrat)
- **Slutsats:** Inte flaskhalsen

### Test 3: HTF/LTF-gates (disabled)

- **Resultat:** 34 trades (oförändrat)
- **Slutsats:** Gates blockerade inte entry

### Test 4: signal_adaptation ATR-zoner (kraftigt sänkta)

- **Low:** entry 0.33→0.25, regime 0.60–0.70→0.45
- **Mid:** entry 0.39→0.28, regime 0.60–0.75→0.50
- **High:** entry 0.45→0.32, regime 0.60–0.80→0.55
- **Resultat:** **176 trades** (+5×), PF 1.31, Return +4.95%
- **Slutsats:** ✅ **FLASKHALSEN IDENTIFIERAD** – ATR-zonerna styrde alla beslut

## Slutlig Optimerad Konfiguration

### Entry-trösklar (via signal_adaptation zones)

```json
"signal_adaptation": {
  "atr_period": 14,
  "zones": {
    "low": {
      "entry_conf_overall": 0.25,
      "regime_proba": {"ranging": 0.45, "bull": 0.45, "bear": 0.45, "balanced": 0.45}
    },
    "mid": {
      "entry_conf_overall": 0.28,
      "regime_proba": {"ranging": 0.50, "bull": 0.50, "bear": 0.50, "balanced": 0.50}
    },
    "high": {
      "entry_conf_overall": 0.32,
      "regime_proba": {"ranging": 0.55, "bull": 0.55, "bear": 0.55, "balanced": 0.55}
    }
  }
}
```

### Risk Map (3× högre positionsstorlek)

```json
"risk_map": [
  [0.35, 0.015],  // från 0.005
  [0.45, 0.025],  // från 0.015
  [0.55, 0.035],  // från 0.025
  [0.65, 0.045]   // från 0.035
]
```

### Exit-inställningar

```json
"exit": {
  "enabled": true,
  "exit_conf_threshold": 0.35,  // från 0.38
  "max_hold_bars": 20,
  "regime_aware_exits": true
}
```

### HTF/LTF Fibonacci Gates

```json
"htf_fib": {"entry": {"enabled": true, "tolerance_atr": 0.60}},
"ltf_fib": {"entry": {"enabled": true, "tolerance_atr": 0.60}}
```

## Resultat-jämförelse

| Konfiguration | Trades | PF | Return | Max DD | Sharpe |
|---|---:|---:|---:|---:|---:|
| **Original** | 34 | 0.92 | -0.10% | 0.63% | -0.040 |
| **Efter ATR-zon-sänkning** | 176 | 1.31 | +4.95% | 2.25% | 0.072 |
| **Slutlig optimerad** | 176 | **1.32** | **+8.41%** | 3.75% | 0.075 |

**Förbättring:** 5× fler trades, PF från 0.92 → 1.32, Return från -0.10% → +8.41%

## Nyckelinsikter

1. **signal_adaptation ATR-zonerna är den primära entry-kontrollen** – toppnivå-trösklar (`entry_conf_overall`, `regime_proba`) används inte när zoner är definierade.

2. **3× högre positionsstorlek** ger proportionellt högre return utan att dramatiskt öka risk (DD +3.1pp, fortfarande under 4%).

3. **Tidigare exit** (0.35 vs 0.38) fångar vinster snabbare och förbättrar PF marginellt.

4. **HTF/LTF-gates med bredare tolerans** (0.60 vs 0.50–0.55) filtrerar sämre setups utan att blockera för många trades.

5. **HTF-exits fungerar korrekt** efter fix av engine.py (configs['exit'] vs configs['cfg']['exit']).

## Optuna-problemet

**Upptäckt:** Alla Optuna-konfigurationer hade `signal_adaptation` fixerat till **för höga trösklar**:

| Konfig | Low entry | Mid entry | High entry | Low regime | High regime |
|---|---:|---:|---:|---:|---:|
| **Original Optuna** | 0.36 | 0.42 | 0.48 | 0.60–0.70 | 0.78–0.88 |
| **Genombrott** | 0.25 | 0.28 | 0.32 | 0.45 | 0.55 |
| **Skillnad** | +44% | +50% | +50% | +33% | +60% |

**Konsekvens:** Optuna optimerade fib-gates, exits och risk_map medan ATR-zonerna garanterade få trades (0–34). Därför såg vi identiska dåliga resultat oavsett andra parameterändringar.

**Åtgärd:** `config/optimizer/tBTCUSD_1h_optuna_smoke_loose.yaml` uppdaterad med 5 grid-varianter runt genombrott-värdena (0.20–0.34 entry, 0.38–0.58 regime).

## Nästa steg

- ✅ Uppdatera Optuna-konfig med korrekta ATR-zon-intervall
- Köra ny Optuna-session (80 trials, bootstrap 32) med uppdaterad konfig
- Testa på längre tidsperioder (6–12 månader) för robusthet
- Walk-forward-validering med rullande fönster
- Överväg dynamisk ATR-zon-klassificering för bättre anpassning

## Fil

- Konfiguration: `config/tmp/tmp_user_test.json`
- Backtest: `results/backtests/tBTCUSD_1h_20251113_163809.json`
- Trades: `results/trades/tBTCUSD_1h_trades_20251113_163809.csv`
