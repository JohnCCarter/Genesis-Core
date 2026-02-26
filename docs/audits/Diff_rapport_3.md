diff --git a/docs/audit/BACKTEST_ENGINE_AUDIT.md b/docs/audit/BACKTEST_ENGINE_AUDIT.md
new file mode 100644
index 0000000..8f4b1ad
--- /dev/null
+++ b/docs/audit/BACKTEST_ENGINE_AUDIT.md
@@ -0,0 +1,162 @@
+# Auditrapport: Backtest/Engine (Genesis-Core)

- +Datum: 2026-02-21
  +Branch: feature/composable-strategy-phase2
  +Scope (kärnlogik):
  +- `src/core/backtest/engine.py`
  +- `src/core/backtest/composable_engine.py`
  +- `src/core/backtest/position_tracker.py`
- +Fokus: determinism (repro), lookahead-bias, robusthet vid databrister, korrekt state-isolering och prestanda.
- +## Sammanfattning
  +Jag har identifierat **5 prioriterade risk-/felklasser** i backtest-motorn:
- +1) **HTF-exit policy kräver tydlig dokumentation**: new vs legacy HTF exit-engine styrs explicit av env/konfig-policy; utan tydlig kommunikation kan detta ge förväntansglapp mellan runner och manuella körningar.
  +2) **Konfig muteras per bar** (`configs["_global_index"] = i`) och används över många anrop → kräver strikt defensiv kopiering (ni gör deepcopy, bra), men ökar risk för läckage om någon återanvänder dict.
  +3) **Tyst återanvändning av on-disk precompute-cache** kan ge driftande resultat om cache-nyckeln inte fullt ut representerar feature-spec + dataidentitet (ni har förbättrat nyckeln, men det finns kvar edge cases runt config-hash och schema-version bump).
  +4) **Per-bar exceptions hanteras “soft” i loopen men leder till hard fail efteråt** (samlar errorcount och raise) → OK för test/hårdhet men kan överraska om man förväntar robust backtest.
  +5) **Exit-logik blandar flera källor till HTF-context** (precomputed mapping vs meta från pipeline) och kan ge inkonsistens, särskilt om `_global_index` är None/invalid eller mapping saknas delvis.
- +Utöver detta finns förbättringar kring timestamp-typer, regime-strängar, och datakvalitet i parquet-laddning.
- +---
- +## Detaljfynd
- +### Fynd A — HTF exit engine selection är en policy trade-off +**Fil:** `src/core/backtest/engine.py` (`_init_htf_exit_engine`)
- +**Observation**
  +- Policy:
- - Om `GENESIS_HTF_EXITS` är satt: "1" => new engine annars legacy.
- - Annars: `use_new_engine = isinstance(htf_exit_config, dict) and bool(htf_exit_config)`.
    +- `run()` anropar `_init_htf_exit_engine(configs.get("htf_exit_config"))` efter champion-merge.
    +- Detta är en avsiktlig trade-off för att minska mismatch mellan runner/manuell körning när `htf_exit_config` är tydligt satt.
- +**Risk**
  +- Förväntansglapp: manuell backtest med `htf_exit_config={}` (tom dict) kan hamna i legacy trots att användaren tänkte "new".
  +- Operativ otydlighet: runner som injectar non-empty `htf_exit_config` kan ge "new" utan att policyn uppfattats som explicit.
- +**Rekommenderad åtgärd**
  +- Dokumentera policyn explicit i runtime/backtest-guiden (env auktoritativt; annars auto-opt-in via icke-tom config).
  +- Behåll beslutloggning (env_flag, config_present, engine_selected) för spårbarhet och felsökning.
- +**Severity:** Medium
- +---
- +### Fynd B — Config mutation per bar: kräver strikt isolering +**Fil:** `src/core/backtest/engine.py` (`run`)
- +**Observation**
  +- `configs = copy.deepcopy(configs) if configs else {}` görs (bra).
  +- Men därefter muteras configs varje bar: `configs["_global_index"] = i`.
- +**Risk**
  +- Om någon anropar `run()` med en configs-dict och förväntar sig att den är oförändrad: deepcopy skyddar.
  +- Men om någon kringgår deepcopy (t.ex. i framtida refaktor) får man svåra, stateful buggar.
- +**Rekommenderad åtgärd**
  +- Behåll deepcopy (viktigt) och lägg ett kort kontrakt i docstring: "configs muteras internt".
  +- Alternativ: bygg en separat `runtime_cfg = {**configs, "_global_index": i}` per iteration (dyrare men isolerat).
- +**Severity:** Medium
- +---
- +### Fynd C — Precompute cache: nyckel bra, men edge cases kvar +**Fil:** `src/core/backtest/engine.py` (`_precompute_cache_key`, `_precompute_cache_key_material`)
- +**Observation**
  +- Ni inkluderar schema-version + spec-digest + symbol/timeframe + len + start/end timestamp ns.
  +- Ni kan dessutom namespace:a via `GENESIS_PRECOMPUTE_CONFIG_HASH` (hashad och trunkerad).
- +**Risk**
  +- Om feature-implementation ändras utan att spec/schema-version uppdateras, kan fel cache återanvändas.
  +- `GENESIS_PRECOMPUTE_CONFIG_HASH` är valfritt; om det inte sätts kan två körningar med olika strategikonfig (men samma data) dela cache.
- +**Rekommenderad åtgärd**
  +- Dokumentera tydligt: när man måste bumpa `PRECOMPUTE_SCHEMA_VERSION`.
  +- Överväg att alltid inkludera en deterministic hash av relevant config-subset (t.ex. fib_cfg + indicator periods) istället för en env-var.
- +**Severity:** Medium
- +---
- +### Fynd D — Error policy: “continue on error” i loop men raise efteråt +**Fil:** `src/core/backtest/engine.py` (`run`)
- +**Observation**
  +- Exceptions i per-bar evaluate fångas, loggas (ibland), men loopen fortsätter.
  +- Efter loopen: om `per_bar_error_count > 0` så `raise RuntimeError(...)`.
- +**Risk**
  +- Detta kan överraska användare: de ser en backtest som “kör klart” men kraschar i slutet.
  +- Samtidigt är det bra för att undvika tysta fel i metrics.
- +**Rekommenderad åtgärd**
  +- Gör policyn explicit via parameter/konfig:
- - `fail_fast=True` (raise direkt)
- - `fail_on_any_error=True` (nuvarande)
- - `best_effort=True` (returnera resultat + errors)
- +**Severity:** Medium
- +---
- +### Fynd E — HTF-context källa kan divergera (precomputed mapping vs meta) +**Fil:** `src/core/backtest/engine.py` (`_check_htf_exit_conditions`)
- +**Observation**
  +- Vid idx+precomputed: bygger `htf_fib_context` från `_precomputed_features["htf_fib_*"]`.
  +- Annars: tar från `meta["features"]["htf_fibonacci"]`.
- +**Risk**
  +- Om mapping finns men idx saknas/är fel (eller arrays kortare) faller man tillbaka och kan få annan HTF-context → exit-beteende ändras.
  +- `compute_htf_fibonacci_mapping` fyller NaN med 0.0 i vissa kolumner; 0.0 kan misstolkas som giltig nivå.
- +**Rekommenderad åtgärd**
  +- Standardisera: om precomputed HTF mapping är enabled, använd den konsekvent och markera `available=False` om nivåer är 0/NaN.
  +- Lägg explicit validering: swing_high/low > 0 och nivåer > 0 innan `available=True`.
- +**Severity:** Medium
- +---
- +### Fynd F — Timestamp-typer: blandning av pandas.Timestamp och numpy-dtypes +**Fil:** `src/core/backtest/engine.py` (`run`)
- +**Observation**
  +- I fast-path: `timestamp = pd.Timestamp(self._np_arrays["timestamp"][i])`
  +- I else-path: `timestamp = timestamps_array[i]` (kan vara numpy datetime64)
- +**Risk**
  +- Små skillnader i typ kan påverka serialisering (`isoformat`) och jämförelser.
- +**Rekommenderad åtgärd**
  +- Normalisera timestamp till `pd.Timestamp(..., tz="UTC")` eller konsekvent `datetime`.
- +**Severity:** Low
- +---
- +## Rekommenderad prioritering
  +1) **A/E**: tydlig och deterministisk HTF-exit/HTF-context policy.
  +2) **D**: gör error policy explicit (så användare vet vad som händer).
  +3) **C**: gör cache-kontraktet tydligt och svårare att göra fel.
  +4) **B/F**: fortsätt hårdna isolering/typer.
- +---
- +## Handoff till nästa agent
  +### Mål
  +Stabilisera backtest-resultat mellan körningar och minska “surprise behavior” kring exits, cache och error-policy.
- +### Föreslagen arbetsordning
  +1) **HTF exit-engine selection**
- - Inför `htf_exit_config["enabled"]` (eller liknande) och välj engine baserat på det.
- - Lägg enhetstest: tom dict vs enabled=false/true ska ge förväntad engine.
- +2) **HTF-context validering**
- - När ni bygger precomputed htf_fib_context: markera `available=False` om nivåer/swing är 0/invalid.
- - Lägg test där precomputed innehåller 0.0 och verifiera att exit-engine inte kör på "fake" nivåer.
- +3) **Error policy**
- - Lägg parameter `error_policy` och returnera `errors` i resultat vid best_effort.
- +4) **Cache kontrakt**
- - Dokumentera bump-policy för `PRECOMPUTE_SCHEMA_VERSION`.
- - Överväg att inkludera relevant config-subset hash i key utan env-var.
- +### Definition of Done
  +- Samma data+config ger samma resultat oavsett runner/manual.
  +- HTF exits körs bara när HTF-context är faktiskt giltig.
  +- Backtest felhantering är explicit och testad.
-
