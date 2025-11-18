# Optuna vs Backtest - Konfigurationsskillnad

## Datum: 2025-11-14

## Problem

Backtest med manuell config kan ge bra resultat (PF 1.32, +8.41%), men när samma parametrar testas via Optuna ger de dåliga resultat. Varför?

## Orsak: Strukturskillnad mellan config-filer

### 1. Backtest-config (tmp_user_test.json)

```json
{
  "cfg": {                          ← "cfg" wrapper krävs!
    "thresholds": {
      "entry_conf_overall": 0.32,
      "signal_adaptation": {
        "zones": {
          "low": {"entry_conf_overall": 0.25, ...}
        }
      }
    },
    "exit": {...},
    "risk": {...}
  }
}
```

**Användning:**

```python
# scripts/run_backtest.py (rad 168-174)
override_payload = json.loads(args.config_file.read_text())
override_cfg = override_payload.get("cfg")  # ← Hämtar "cfg"-blocket
merged_cfg = _deep_merge(cfg, override_cfg)
```

### 2. Optuna trial-config (trial_XXX_config.json)

```json
{
  "cfg": {                          ← "cfg" wrapper läggs till automatiskt
    "thresholds": {...},
    "exit": {...},
    "risk": {...}
  }
}
```

**Skapande:**

```python
# src/core/optimizer/runner.py (rad 583-594)
authority = ConfigAuthority()
default_cfg = authority.get()[0].model_dump()
transformed_params, _ = transform_parameters(trial.parameters)
merged_cfg = _deep_merge(default_cfg, transformed_params)
config_payload = {"cfg": merged_cfg}  # ← Wrapper läggs till här
```

### 3. YAML Optuna-spec (tBTCUSD_1h_optuna_smoke_loose.yaml)

```yaml
parameters:
  thresholds:                       ← Ingen "cfg" wrapper i spec
    entry_conf_overall:
      type: float
      low: 0.28
      high: 0.44
    signal_adaptation:
      type: grid
      values:
        - atr_period: 14
          zones:
            low: {entry_conf_overall: 0.25, ...}
```

## Skillnader i parameterflöde

### Backtest-körning med config-fil

```
tmp_user_test.json (med "cfg")
    ↓
override_cfg = payload.get("cfg")      ← Extraherar "cfg"
    ↓
_deep_merge(default_cfg, override_cfg)
    ↓
BacktestEngine.run(configs=merged_cfg)
```

### Optuna trial

```
YAML parameters (utan "cfg")
    ↓
_suggest_parameters() → dict
    ↓
transform_parameters() → transformed dict
    ↓
_deep_merge(default_cfg, transformed)
    ↓
{"cfg": merged_cfg} wrappas            ← Wrapper läggs till
    ↓
BacktestEngine.run(configs=merged_cfg)
```

## Kritiska skillnader

### 1. Top-level trösklar vs signal_adaptation

**I manual backtest-config:**

- `cfg.thresholds.entry_conf_overall` och `cfg.thresholds.regime_proba` finns
- `cfg.thresholds.signal_adaptation.zones` finns också
- **Beslutslogiken använder signal_adaptation.zones när de finns definierade**

**I Optuna:**

- YAML-specen har båda (`thresholds.entry_conf_overall` och `signal_adaptation`)
- Men när `signal_adaptation.zones` finns används **endast zones**, inte top-level trösklar
- **Om signal_adaptation har för höga trösklar spelar top-level entry_conf_overall ingen roll**

### 2. Risk map transformation

**I manual backtest-config:**

```json
"risk": {
  "risk_map": [[0.45, 0.015], [0.55, 0.025], [0.65, 0.045]]  // Direkt värden
}
```

**I Optuna:**

```yaml
risk:
  risk_map_deltas:
    type: dict
    conf_0: {type: float, low: -0.15, high: 0.15}
    size_0: {type: float, low: -0.015, high: 0.015}
```

→ Transform via `_build_risk_map_from_deltas(deltas)`
→ Baserad på BASE_RISK_MAP = [(0.45, 0.015), (0.55, 0.025), (0.65, 0.035)]

**Problem:** Om champion använder risk_map [[0.45, 0.015], [0.55, 0.025], [0.65, 0.045]],
men Optuna-deltas begränsas till ±0.015, kan den aldrig nå 0.045!

### 3. Exit-konfiguration

**Tidigare bug (FIXAD 2025-11-13):**

```python
# engine.py läste fel nyckel:
exit_cfg = configs.get("cfg", {}).get("exit", {})  # ← WRONG
# Skulle vara:
exit_cfg = configs.get("exit", {})  # ← CORRECT
```

Detta gjorde att exit-inställningar ignorerades i både Optuna och manuella backtester.

## Lösningar

### ✅ 1. Signal_adaptation är den primära kontrollen

**Före genombrott (2025-11-13):**

- Optuna-spec hade `signal_adaptation` fixerat till höga trösklar (low 0.36, mid 0.42, high 0.48)
- Oavsett hur mycket vi justerade `entry_conf_overall` (0.28-0.44) användes den **aldrig**
- Resultat: Konsekvent 34 trades, PF 0.92

**Efter genombrott:**

- Upptäckte att `signal_adaptation.zones` styr entry-logiken när de finns
- Uppdaterade Optuna-spec med 5 grid-varianter runt optimala värden (low 0.25, mid 0.28, high 0.32)
- Resultat: Trial med rätt signal_adaptation gav PF 1.32, +8.41%

### ✅ 2. Risk map ska täcka champions intervall

**Före:**

```python
BASE_RISK_MAP = [(0.45, 0.015), (0.55, 0.025), (0.65, 0.035)]
deltas: ±0.015 → max size = 0.035 + 0.015 = 0.050
```

**Champion använder:**

```json
[[0.45, 0.015], [0.55, 0.025], [0.65, 0.045]]  // 0.045 > 0.050 (OK)
```

**Kontrollera att:**

- BASE_RISK_MAP + max_delta >= champion.risk_map
- Alternativt: Inkludera championens exakta risk_map som ett grid-val

### ✅ 3. Verifiera att exit-logiken är konsekvent

**Test:**

1. Kör backtest med manual config → spara resultat
2. Konvertera manuell config till Optuna-parametrar
3. Kör Optuna med exakt dessa parametrar (1 trial)
4. Jämför resultat → ska vara **identiskt** (samma trades, PF, return)

**Om skillnad finns:**

- Kontrollera att Optuna-wrappingen (`{"cfg": merged_cfg}`) fungerar
- Kontrollera att `transform_parameters()` inte ändrar semantiken
- Kontrollera att `_deep_merge()` inte överskrider fel nycklar

## Checklista innan Optuna-körning

- [ ] **Champion-parametrar i sökrymden?**
  - `signal_adaptation.zones` täcker champions värden
  - `risk_map` (via deltas eller grid) kan nå champions värden
  - Exit-parametrar (fib_threshold_atr, trail_atr_multiplier, etc.) täcker champions intervall

- [ ] **Smoke-test med champions exakta parametrar:**

  ```bash
  # 1. Kör manual backtest
  python scripts/run_backtest.py --symbol tBTCUSD --timeframe 1h \
    --config-file config/strategy/champions/tBTCUSD_1h.json
  
  # 2. Konvertera till Optuna-spec och kör 1 trial
  # 3. Jämför resultat
  ```

- [ ] **Preflight-validering:**

  ```bash
  python scripts/validate_optimizer_config.py config/optimizer/<config>.yaml
  ```

- [ ] **Verifiera att top-level trösklar INTE används när signal_adaptation.zones finns:**
  - Om du justerar `entry_conf_overall` 0.28→0.44 men får samma resultat, betyder det att `signal_adaptation.zones` styr
  - Fokusera på att optimera zones, inte top-level trösklar

## Sammanfattning

**Varför backtest kan ge bra resultat men Optuna dåliga:**

1. **signal_adaptation.zones är primär kontroll** → Om Optuna-spec har för höga zone-trösklar spelar allt annat mindre roll
2. **Risk map transformation** → Deltas kanske inte når champions värden
3. **Config-struktur** → Backtest läser `cfg`-wrapper, Optuna lägger till den automatiskt
4. **Exit-bug (fixad)** → Tidigare lästes exit-config från fel nyckel

**Lösning:**

- Uppdatera Optuna-spec med signal_adaptation-grid runt genombrott-värden ✅
- Verifiera att risk_map kan nå champions värden ✅
- Kör smoke-test med champions exakta parametrar för att bekräfta paritet ✅
- Dokumentera skillnader mellan manual backtest och Optuna trial-flow ✅
