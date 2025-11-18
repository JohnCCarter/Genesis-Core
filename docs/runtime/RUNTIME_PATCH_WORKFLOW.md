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
# torrkörning
python scripts/apply_runtime_patch.py --dry-run config/tmp/override_entry_loose.json

# skriv till config/runtime.json
python scripts/apply_runtime_patch.py config/tmp/override_entry_loose.json
```

### Nästa steg
- Dokumentera arbetsflödet även i `AGENTS.md`.
- Lägg till enhetstest för patch-sanitiseraren så framtida ändringar inte bryter filtret.
