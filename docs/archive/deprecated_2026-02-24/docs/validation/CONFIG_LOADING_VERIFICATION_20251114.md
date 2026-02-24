# Konfigurationsladdning - Verifiering 2025-11-14

## Sammanfattning

Verifiering av hur konfigurationen laddas i både backtest och Optuna för att säkerställa att allt fungerar korrekt.

## Konfigurationsladdning - Flöde

### 1. Modell (vikter, schema)

- **Fil:** `config/models/tBTCUSD_1h.json`
- **Laddas via:** `ModelRegistry.get_meta(symbol, timeframe)`
- **Baseras på:** symbol + timeframe
- **Innehåller:** vikter (`w`), bias (`b`), schema, calibration

### 2. Konfiguration (thresholds, exits, risk, gates)

#### Backtest flöde

1. `scripts/run_backtest.py`:
   - `ConfigAuthority.get()` → baseline (runtime defaults)
   - Om `--config-file` finns: `_deep_merge(baseline, override_cfg)`
   - `engine.run(policy=policy, configs=cfg)`

2. `src/core/backtest/engine.py`:
   - `engine.run()` skickar `configs` till `evaluate_pipeline()`

3. `src/core/strategy/evaluate.py`:
   - `champion = champion_loader.load_cached(symbol, timeframe)`
   - `champion_cfg = dict(champion.config or {})`
   - `merged_cfg = champion_cfg`
   - `merged_cfg.update(configs)` ← **SKICKAD CONFIG OVERRIDE:AR CHAMPION**

**Resultat:** `--config-file` override:ar champion config ✅

#### Optuna flöde

1. `src/core/optimizer/runner.py` (`run_trial`):
   - `ConfigAuthority.get()` → baseline (runtime defaults)
   - `transform_parameters(trial.parameters)`
   - `_deep_merge(baseline, transformed_params)`
   - Skapar config-fil: `{"cfg": merged_cfg}`
   - Kör backtest med `--config-file` (trial_XXX_config.json)

2. `scripts/run_backtest.py` (samma som ovan):
   - `ConfigAuthority.get()` → baseline
   - `_deep_merge(baseline, trial_config_cfg)`
   - `engine.run(policy=policy, configs=cfg)`

3. `src/core/strategy/evaluate.py` (samma som ovan):
   - `champion_cfg.update(configs)` ← **TRIAL CONFIG OVERRIDE:AR CHAMPION**

**Resultat:** Trial parameters override:ar champion config ✅

## Merge-ordning

**Prioritet (högst → lägst):**

1. Trial parameters / `--config-file` (högst)
2. Champion config (mellan)
3. Baseline defaults (lägst)

I `evaluate_pipeline`:

```python
merged_cfg = champion_cfg  # Start med champion
merged_cfg.update(configs)  # Override med skickad config
```

✅ Detta är **KORREKT** - skickad config override:ar champion.

## Potentiellt problem: Shallow merge

### Problem

I `evaluate_pipeline` används `update()` (shallow merge) istället för `_deep_merge()`:

```python
merged_cfg = champion_cfg
merged_cfg.update(configs)  # Shallow merge!
```

Om `configs` har `{"thresholds": {"entry_conf_overall": 0.25}}` och champion har:

```python
{
  "thresholds": {
    "entry_conf_overall": 0.35,
    "regime_proba": {...},
    "signal_adaptation": {...}
  }
}
```

Så ersätts hela `champion["thresholds"]` dict, inte mergad. Detta betyder att `regime_proba` och `signal_adaptation` från champion försvinner om de inte finns i `configs`.

### Verifiering

Test visar att i nuvarande fall fungerar det eftersom:

- Både champion och `tmp_v4_test.json` har `signal_adaptation` definierad
- Shallow merge använder `tmp_v4_test.json`'s version, vilket är korrekt

**MEN:** Om `tmp_v4_test.json` INTE hade `signal_adaptation`, skulle champion's version försvinna p.g.a. shallow merge.

### Rekommendation

1. **Kortsiktigt:** Dokumentera att champion config måste ha samma struktur som trial config för att merge ska fungera korrekt.
2. **Långsiktigt:** Använd `_deep_merge()` i `evaluate_pipeline` istället för `update()` för att säkerställa att nested dicts mergas korrekt.

## KRITISK BUG: Champion-fil laddades inte korrekt

### Problem (2025-11-14)

Champion-filen `config/strategy/champions/tBTCUSD_1h.json` har strukturen:

```json
{
  "cfg": {
    "parameters": {...}
  }
}
```

Men `_validate_champion` letade bara efter `payload.get("parameters")` eller `payload.get("config")` på top-level, vilket inte fanns.

### Konsekvenser

- ❌ Champion config användes **ALDRIG** i tidigare tester
- ❌ Alla tester använde baseline defaults istället
- ❌ Champion's `signal_adaptation`, `risk_map`, `exit config` etc. ignorerades
- ❌ Detta kan förklara varför resultaten var konstanta/dåliga

### Fix

Uppdaterade `_validate_champion` att också kolla `payload.get('cfg', {}).get('parameters')` för att stödja wrapped format.

**Status:** ✅ Fixad 2025-11-14

## Slutsats

✅ **Backtest:** `--config-file` override:ar champion korrekt
✅ **Optuna:** Trial parameters override:ar champion korrekt
✅ **Champion-fil:** Laddas nu korrekt (fixad 2025-11-14)
✅ **Modell:** Samma modell (v4) laddas i både backtest och Optuna via `ModelRegistry.get_meta()`
⚠️ **VARNING:** Shallow merge i `evaluate_pipeline` kan orsaka problem med nested dicts om champion och trial har olika strukturer.

I nuvarande fall fungerar det eftersom både champion och trial configs har samma struktur, men detta är en potentiell bug som bör fixas för robusthet.

## Verifiering 2025-11-14

Kör `scripts/verify_config_loading.py` för att verifiera att allt laddas korrekt:

- ✅ Baseline config laddas korrekt (ConfigAuthority)
- ✅ Champion config laddas korrekt (ChampionLoader)
- ✅ Model laddas korrekt (ModelRegistry) - v4 från `config/models/tBTCUSD_1h.json`
- ✅ Merge-ordning fungerar som förväntat

**Viktigt:** Om resultaten skiljer sig mellan körningar beror det på konfigurationsskillnader, inte på laddningsfel. Alla komponenter laddas korrekt.
