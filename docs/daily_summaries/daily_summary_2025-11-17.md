# Daily Summary 2025-11-17 — Fib-dataflöde diagnostik

## Utfört

### Fibonacci-dataflödesundersökning

**Problem:** Champion tBTCUSD 1h gav 0 trades trots återställda parametrar från `run_20251023_141747`.

**Diagnostik genomförd:**
1. Lade till [FIB-FLOW] loggning i `features_asof.py`, `evaluate.py` och `decision.py`
2. Skapade diagnostikskript `scripts/diagnose_fib_flow.py`
3. Spårade dataflödet från feature-extraktion till beslutslogik

### Två kritiska buggar identifierade och fixade

#### Bug #1: Shallow merge i evaluate.py
**Problem:** 
```python
merged_cfg = champion_cfg
merged_cfg.update(configs)  # ← SHALLOW UPDATE
```
Shallow `.update()` ersatte hela `htf_fib`-dict istället för att deep-merga den.

**Fix:**
```python
def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base, recursively merging nested dicts."""
    merged = dict(base)
    for key, value in (override or {}).items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged

# Använd deep merge
merged_cfg = _deep_merge(champion_cfg, configs)
```

#### Bug #2: Signal_adaptation trösklar för höga
**Problem:** 
Championens signal_adaptation hade för höga trösklar (genombrott-problemet från 2025-11-13):
- low: entry 0.36, regime 0.60-0.70
- mid: entry 0.42, regime 0.70-0.80
- high: entry 0.48, regime 0.78-0.88

Detta blockerade ALLA signaler INNAN fib-gates kördes!

**Fix:**
Uppdaterade champion med genombrott-värdena:
- low: entry 0.25, regime 0.45-0.50
- mid: entry 0.28, regime 0.50-0.55
- high: entry 0.32, regime 0.55-0.60

### Resultat efter fixar

✅ **Fibonacci-dataflödet fungerar nu korrekt:**
1. HTF/LTF fibonacci context skapas med `available=True`
2. Context når evaluate_pipeline korrekt
3. Deep merge bevarar htf_fib/ltf_fib konfiguration
4. HTF och LTF gates aktiveras och körs
5. Gates får korrekt metadata med levels, swings, etc.

**Diagnostikloggar bekräftar:**
```
[FIB-FLOW] HTF fibonacci context created: symbol=tBTCUSD timeframe=1h available=True
[FIB-FLOW] LTF fibonacci context created: symbol=tBTCUSD timeframe=1h available=True
[FIB-FLOW] evaluate_pipeline state assembly: htf_available=True ltf_available=True
[FIB-FLOW] HTF gate active: enabled=True available=True
[FIB-FLOW] LTF gate active: enabled=True available=True
```

### Kvarstående: 0 trades

Trots att fib-gates nu körs korrekt får vi fortfarande 0 trades. Detta beror troligen på:
- Fib-gates blockerar alla signaler (för strikta toleranser eller målnivåer)
- Priset når aldrig fibonacci-nivåerna inom tolerans
- Behöver kalibrera `tolerance_atr`, `long_target_levels`, `short_target_levels`

## Filer ändrade

- `src/core/strategy/evaluate.py` - Lade till `_deep_merge` och fixade shallow update
- `src/core/strategy/features_asof.py` - Diagnostikloggning (INFO-nivå)
- `src/core/strategy/evaluate.py` - Diagnostikloggning (INFO-nivå)
- `src/core/strategy/decision.py` - Diagnostikloggning (INFO-nivå)
- `config/strategy/champions/tBTCUSD_1h.json` - Uppdaterade signal_adaptation trösklar
- `scripts/diagnose_fib_flow.py` - Nytt diagnostikskript

## Nästa steg

1. **Kalibrera fib-gates:**
   - Analysera vilka fibonacci-nivåer priset faktiskt rör
   - Justera `tolerance_atr` (nuvarande 0.5 kanske är för snäv)
   - Bredda `long_target_levels` och `short_target_levels`
   - Överväg `missing_policy: pass` för fib-gates initialt

2. **Validera med backtest:**
   - Kör full backtest med uppdaterade inställningar
   - Jämför mot historisk referens (75 trades, PF 3.30)

3. **Regressionstest:**
   - Lägg till tester för deep merge-funktionalitet
   - Testa att fib-metadata når decision.py korrekt
   - Testa att gates aktiveras när enabled=True

4. **Dokumentera lösningar:**
   - Uppdatera AGENTS.md med bugfixar och lösningar
   - Dokumentera fib-dataflöde i separat guide
   - Lägg till troubleshooting-sektion

## Observationer

- **Deep merge är kritiskt:** Shallow `.update()` bryter nested dict-konfiguration
- **Signal_adaptation dominerar:** Proba-trösklar måste passas INNAN andra gates körs
- **Loggning på INFO-nivå:** DEBUG syns inte i normal körning, INFO krävs för diagnostik
- **Champion-struktur:** `cfg.parameters` → extraheras av ChampionLoader korrekt

## Referens

- **AGENTS.md sektion 21:** Genombrott-konfiguration 2025-11-13
- **AGENTS.md sektion 8:** Next steps for hand-off (14 Nov 2025)
- **docs/optuna/BREAKTHROUGH_CONFIG_20251113.md:** Signal_adaptation flaskhals

---

## Runtime-konfigurationsflöde fixat (eftermiddag)

Se även `docs/runtime/RUNTIME_PATCH_WORKFLOW.md` för detaljerad handbok.

### Problem
- Temp-profiler (`config/tmp/*.json`) gick inte att applicera via API/CLI eftersom `ConfigAuthority.propose_update()` krävde redan plattade patchar → fel `non_whitelisted_field` och `config/runtime.json` låg kvar på gamla trösklar.
- `scripts/apply_runtime_patch.py` saknade stöd för champion-format (`cfg.parameters`) och filtrerade inte bort otillåtna nycklar.
- Backtesteren visade inte vilken runtime som faktiskt laddades, så felaktiga tester gick obemärkt.

### Åtgärder
1. **ConfigAuthority**
   - Ny helper `_deep_merge_dicts` ger rekursiv merge när patchar läggs på befintliga värden.
   - `propose_update()` unwrappar nu `cfg` om den finns innan whitelist-checken, så champion- och tmp-profiler accepteras.
2. **CLI – `scripts/apply_runtime_patch.py`**
   - Läser både flacka patchar och champion-profiler; plockar ut `cfg.parameters` automatiskt.
   - Sanitiserar patchar och behåller endast `thresholds`, `gates`, `risk.risk_map`, `ev`, `multi_timeframe`.
   - Har `--dry-run` för diff-koll innan write.
3. **Backtest-synlighet**
   - `scripts/run_backtest.py` loggar nu aktuellt `entry_conf_overall`, zontrösklar och MTF override-switchar direkt efter laddning av runtime (och eventuellt override).

### Resultat
- `config/tmp/override_entry_loose.json` applicerad → runtime version 75 (entry 0.30 + LTF override med tröskel 0.65).
- `config/strategy/champions/tBTCUSD_1h_ltf_override.json` applicerad → runtime version 80 (championens ATR-zoner + hysteresis 2).
- Backtester läser bekräftat de nya värdena (se `[CONFIG:runtime] …` i CLI).

### Nästa steg
- Dokumentera nya arbetsflödet i `AGENTS.md` (hur temp/champion-profiler ska appliceras).
- Lägga till enhetstest för patch-sanitiseraren i CLI:n.
- Fundera på att skriva en kort changelog varje gång CLI:n körs (utöver audit-loggen).
