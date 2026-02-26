## Runtime Patch Workflow (2025-11-17)

## Agent Codex

### Bakgrund

- **Symptom:** Ändringar i `config/tmp/*.json` gav identiska backtest-resultat.
- **Orsak:** `ConfigAuthority.propose_update()` accepterade endast redan avskalade patchar och avvisade profiler som låg under `cfg`/`parameters` → `config/runtime.json` uppdaterades aldrig.

### Åtgärder

1. **ConfigAuthority (`src/core/config/authority.py`)**
   - `_deep_merge_dicts` infördes för att applicera patchar rekursivt utan att tappa syskonfält.
   - `propose_update()` unwrappar nu `cfg` innan whitelist-kontrollen så att champion/tmp-profiler accepteras direkt.
2. **CLI-verktyg (`scripts/apply_runtime_patch.py`)**
   - Läser både flacka patchar och champion-profiler (`cfg.parameters`).
   - Sanitiserar patchar och behåller bara `thresholds`, `gates`, `risk.risk_map`, `ev`, `multi_timeframe`.
   - Har `--dry-run` och visar vilka fält som ändras innan `config/runtime.json` skrivs.
3. **Synlighet i backtester (`scripts/run_backtest.py`)**
   - Loggar aktivt `entry_conf_overall`, zontrösklar och MTF override-lägen direkt efter att runtime laddats.

### Resultat

- Runtime version 75 – `config/tmp/override_entry_loose.json` (entry 0.30, LTF override on).
- Runtime version 80 – champion `tBTCUSD_1h_ltf_override.json` (ATR-zoner + hysteresis 2).
- Backtester visar `[CONFIG:runtime] …` så man ser direkt vilka trösklar som används.

### Rekommenderad användning

```powershell
# torrkörning (visar endast diff)
python scripts/apply_runtime_patch.py --dry-run config/tmp/override_entry_loose.json

# applicera whitelistade fält (säkert läge)
python scripts/apply_runtime_patch.py config/tmp/override_entry_loose.json

# applicera ALLA fält (experiment-läge, använd med försiktighet)
python scripts/apply_runtime_patch.py --full config/tmp/balanced.json

# kombinera --dry-run och --full för att se alla ändringar först
python scripts/apply_runtime_patch.py --dry-run --full config/tmp/balanced.json
```

### Whitelist-filter (säkerhetsläge)

I standardläge filtreras patchar så att endast dessa fält appliceras:

- `thresholds.*` (alla trösklar och signal_adaptation)
- `gates.*` (cooldown, hysteresis)
- `risk.risk_map` (endast risk map, ej andra risk-fält)
- `ev.*` (expected value-parametrar)
- `multi_timeframe.*` (HTF/LTF override-inställningar)

**Filtreras bort:** `exit`, `htf_exit_config`, `ltf_fib`, `htf_fib`, `warmup_bars` m.fl.

### Full-läge (experiment)

Med `--full` flaggan appliceras ALLA fält från patch-filen utan whitelist-check. Detta är användbart för:

- 🔬 Experimenterande och optimering (hitta rätt nivåer)
- 🧪 Snabba tester av kompletta konfigurationer
- 📊 A/B-testning mellan olika profiler

⚠️ **Varning:** Full-läge kan överskriva kritiska runtime-fält. Använd `--dry-run` först för att granska ändringar.

### Nästa steg

- ✅ `--full` flagga implementerad för experiment-fas (2025-11-18)
- Dokumentera arbetsflödet även i `AGENTS.md`
- Lägg till enhetstest för patch-sanitiseraren så framtida ändringar inte bryter filtret
- Efter optimering: ta bort `--full` eller gör den till developer-only feature
