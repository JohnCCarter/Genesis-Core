# Optuna Fix – signal_adaptation ATR-zoner 2025-11-13

## Problem

Optuna-körningar gav konsekvent dåliga resultat (0 trades, låg PF) oavsett andra parameterändringar.

## Grundorsak

`signal_adaptation` var fixerat till **extremt höga trösklar** i alla Optuna-konfigurationer:

```yaml
# Gamla värden (original Optuna-konfig)
signal_adaptation:
  type: fixed
  value:
    zones:
      low:  {entry: 0.36, regime: 0.60-0.70}
      mid:  {entry: 0.42, regime: 0.70-0.80}
      high: {entry: 0.48, regime: 0.78-0.88}
```

Dessa värden är **44–60% högre** än genombrott-konfigurationen som ger 176 trades med PF 1.32.

## Lösning

Uppdaterad `config/optimizer/tBTCUSD_1h_optuna_smoke_loose.yaml` med 5 grid-varianter:

1. **Genombrott-baseline:** entry 0.25/0.28/0.32, regime 0.45/0.50/0.55
2. **Aggressiv:** entry 0.23/0.26/0.30, regime 0.42/0.47/0.52
3. **Konservativ:** entry 0.27/0.30/0.34, regime 0.48/0.53/0.58
4. **Asymmetrisk:** entry 0.25/0.28/0.32, regime ranging högre än bull/bear
5. **Maximal:** entry 0.20/0.24/0.28, regime 0.38/0.43/0.48

## Förväntad effekt

- Optuna kan nu utforska ATR-zon-rummet runt bevisade arbetsvärden
- Kombinera ATR-zoner med fib-gates, exits och risk_map för optimal prestanda
- 80 trials × 5 grid-varianter = 400 totala kombinationer att testa

## Relaterade filer

- Fix: `config/optimizer/tBTCUSD_1h_optuna_smoke_loose.yaml`
- Genombrott-analys: `BREAKTHROUGH_CONFIG_20251113.md`
- Backtest-konfig: `config/tmp/tmp_user_test.json`
