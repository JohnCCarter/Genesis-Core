# Auditrapport: Konfig & Governance (Genesis-Core)

Datum: 2026-02-21
Branch: feature/composable-strategy-phase2
Scope: `src/core/config/*`, `src/core/governance/registry.py` samt tillhörande schema/validator.

## Sammanfattning
Granskningen identifierar **3 prioriterade risk-/felklasser**:

1) **Två parallella konfig-system** (legacy JSON-schema vs runtime Pydantic) utan tydlig separation → hög risk för felvalidering och felaktiga antaganden.
2) **Runtime update-whitelist** i `ConfigAuthority.propose_update()` är strikt och utesluter fält som runtime-schemat faktiskt stödjer (t.ex. `exit`, `features`) → kan uppfattas som fel/felkonfigurerat API om avsikten är att dessa ska kunna ändras live.
3) **Governance registry** kan ge **falska konflikter** p.g.a. dubbletter vid pack-expansion (`includes_compacts`) → konfliktregler triggas även om det är samma compact.

Utöver detta finns några **förbättringar/edge cases** i validering och diff-verktyg.

## Detaljfynd

### Fynd A — Parallella config-system utan tydlig kontraktgräns
**Filer:**
- `src/core/config/validator.py`
- `src/core/config/schema_v1.json`
- `src/core/config/schema.py`
- `src/core/config/authority.py`

**Observation**
- `validator.py` använder `schema_v1.json` (Draft-07) som endast validerar: `dry_run`, `max_drawdown_pct`, `position_cap_pct`.
- Runtime-schemat (`schema.py`) definierar ett mycket större kontrakt: `thresholds`, `gates`, `risk`, `ev`, `exit`, `multi_timeframe`, `warmup_bars`, `features`, `htf_*` m.m.

**Risk**
- Det är lätt att (felaktigt) använda legacy-validatorn för runtime-config och tro att konfigen är korrekt.
- ”SSOT”-förvirring: flera källor kan uppfattas som ”den riktiga” konfigen.

**Rekommenderad åtgärd**
- Gör separationen explicit:
  - Byt namn på `schema_v1.json` → `legacy_schema_v1.json`.
  - Byt namn på `validate_config` → `validate_legacy_config`.
  - Lägg till tydlig docstring/README i `src/core/config/` om vilket system som används var.

**Severity:** Medium (risk för fel användning och driftincidenter)

---

### Fynd B — `ConfigAuthority` whitelist blockerar runtime-fält som schemat stödjer
**Fil:** `src/core/config/authority.py`

**Observation**
- `propose_update()` accepterar patchar men kör en whitelist som bara tillåter toppnivå:
  - `thresholds`, `gates`, `risk`, `ev`, `multi_timeframe`
- RuntimeConfig innehåller även (minst): `exit`, `warmup_bars`, `features`, `htf_exit_config`, `htf_fib`, `ltf_fib`.

**Risk**
- Om API/ops antar att runtime-config är ”live-uppdaterbar” blir det ett funktionellt fel.
- Drift risk: teams kan göra ändringar som valideras via Pydantic men stoppas i propose-vägen.

**Rekommenderad åtgärd (välj strategi)**
- **B1 (säkerhetsmodell):** behåll whitelist men dokumentera exakt vad som är tillåtet live och varför.
- **B2 (funktionalitet):** utöka whitelist till de runtime-fält som ska få ändras live (t.ex. `exit`, `features`, `warmup_bars`), med underfältsbegränsningar.
- **B3 (rollstyrning):** tillåt fler fält för admin/service-actor.

**Severity:** Medium–High (beroende på avsikt med live-updates)

---

### Fynd C — Governance registry: risk för falska konflikter p.g.a. dubbletter i `active_compacts`
**Fil:** `src/core/governance/registry.py`

**Observation**
- Vid manifestvalidering byggs `active_compacts` av:
  - listade compacts i manifestet
  - plus en nivå expansion av `includes_compacts`
- Listan dedupliceras inte innan conflict-group enforcement.

**Risk**
- Om samma compact inkluderas både direkt och via ett pack kan den hamna två gånger.
- Konfliktregeln triggar då eftersom `len(items) > 1`, även om labels kan vara identiska.

**Rekommenderad åtgärd**
- Deduplicera `active_compacts` på nyckel `(id, version)` före conflict-group-samling.

**Severity:** Medium (kan ge blockerande validering/CI falskt negativ)

---

### Fynd D — `validator.diff_config()` är toppnivå-only och kan missleda
**Fil:** `src/core/config/validator.py`

**Observation**
- `diff_config()` jämför endast toppnivå-nycklar, ingen rekursion.

**Risk**
- Om detta återanvänds för runtime-config missas de flesta relevanta förändringar.

**Rekommenderad åtgärd**
- Antingen:
  - döp om tydligt som legacy/toppnivå-diff, eller
  - implementera rekursiv diff (eller återanvänd `_diff_paths()`-logik i authority).

**Severity:** Low–Medium

---

### Fynd E — Små validerings-edge cases i runtime-schema
**Fil:** `src/core/config/schema.py`

**Observation / Risk**
- `Risk.risk_map`: validerar struktur och float-coercion men inte monotonicitet/bounds (t.ex. storlek > 1 kan smyga in).
- `LTFOverrideAdaptiveConfig.regime_multipliers`: tillåter dict men värdena coerces inte; kan ge runtime-fel senare om icke-numeriska värden smyger in via JSON.

**Rekommenderad åtgärd**
- Lägg till validering:
  - risk_map: enforce `0<=thr<=1` och `0<=size<=1`, samt ev sortering/monotonicitet.
  - regime_multipliers: float-coercion/ValueError vid icke-numeriska värden.

**Severity:** Low

## Rekommenderad prioritering
1) **A (separation)**: minska felanvändning och förvirring snabbt.
2) **C (dedupe i registry)**: enkel fix som förhindrar falska konflikter.
3) **B (whitelist policy)**: besluta och dokumentera (eller utöka) enligt er governance-modell.

## Handoff till nästa agent
### Mål
Implementera små, isolerade förändringar som ökar tydlighet och minskar falska fel utan att ändra runtime-beteende i onödan.

### Föreslagen arbetsordning
1) **Tydliggör legacy vs runtime**
   - Byt namn på `schema_v1.json` och funktioner i `validator.py`.
   - Lägg till kort dokumentation i `src/core/config/README.md` (eller liknande) om SSOT och vilka API:er som använder vad.
   - Uppdatera eventuella tester/imports som förlitar sig på gamla namn.

2) **Deduplicera governance active_compacts**
   - I `validate_registry()`, innan conflict-groups byggs: dedupe på `(id, version)`.
   - Lägg till ett unit test där manifestet inkluderar samma compact direkt + via pack och verifiera att ingen konflikt flaggas.

3) **Konfig-uppdateringar: besluta whitelist-policy**
   - Läs `src/core/server_config_api.py` och se hur propose_update exponeras.
   - Om live update av `exit/features` är önskat: utöka whitelist (minsta säkra uppsättning) + test.
   - Om inte: dokumentera i API-guide och returnera tydligare fel (t.ex. vilket fält som nekas).

### Definition of Done
- Tydlig dokumentation för legacy vs runtime.
- Registry-validering robust mot dubbletter.
- Antingen (a) dokumenterad whitelist-policy eller (b) utökad whitelist + test.
- CI/tests passerar.

---

Ägare/kontext
- `ConfigAuthority` använder repo-root resolution via `pyproject.toml` och skriver `config/runtime.json` + `logs/config_audit.jsonl`.
- Runtime hash-kontrakt: `sha256(canonical_json(cfg))`.

