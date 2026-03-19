# HANDOFF — RI/R1 vs legacy role-map kickoff

Senast uppdaterad: 2026-03-19

> Detta dokument är en operativ handoff för nästa agent/session. Det är **inte** en governance authority source och får inte överstyra `.github/copilot-instructions.md`, `docs/governance_mode.md`, `docs/OPUS_46_GOVERNANCE.md` eller `AGENTS.md`. Verifiera alltid live branch, HEAD, remote-status och working tree i aktuell arbetskopia innan arbete fortsätter.

## Läs detta först — vad nästa agent måste förstå direkt

Den viktigaste insikten från den senaste sessionen är **inte** bara att RI är en separat strategy family. Den viktigaste insikten är också att den ursprungliga idén med **R1/RI** verkar ha varit:

- **management/filter-lager**
- **overlay-lager**
- **inte en primary entry-driver**

Under implementationen gled arbetet sannolikt bort från den idén utan att det upptäcktes direkt. Det upptäcktes först i efteranalys/brainstorming.

### Kritisk arbetsfråga framåt

Nästa agent ska därför **inte** börja med mer bred parameteroptimering.

Nästa agent ska först fråga:

> **Vilka delar i RI/R1 är egentligen tänkta att vara context/filter/management — och vilka delar har i praktiken börjat bete sig som entry-motor?**

Detta är sannolikt nyckeln till nästa edge.

## Live repo-status vid denna handoff

- **Aktiv branch vid handoff:** `feature/ri-legacy-role-map-2026-03-19`
- **HEAD vid handoff:** `8d5d7d80`
- **Senast pushad commit på master före brancharbete:** `8d5d7d80` — `docs(ri): align strategy-family architecture terminology`
- **Remote-status som observerades:** `origin/master` pekade på samma commit när branchen skapades

## Vad som blev klart precis innan denna handoff

### 1. Strategy-family-separationen är redan landad

Följande är redan infört och ska **inte** återdebatteras som om det vore öppet:

- `strategy_family` är kanoniskt `legacy | ri`
- hybrida ytor fail-closed i stället för att accepteras som tredje family label
- RI behandlas som separat strategy family, inte som legacy-overlay i canonical modellen

### 2. Repo-guidance har just alignats semantiskt

En docs-slice landades för att städa aktiv guidance så att den matchar nuvarande architecture truth:

- `docs/features/feature-regime-intelligence-strategy-family-1.md`
- `docs/governance/regime_intelligence_strategy_family_integration_stub_2026-03-18.md`
- `docs/analysis/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_repo_wide_architecture_alignment_2026-03-19.md`

Den slicen verifierades med riktade STRICT-sentinels och pushades till `master` innan denna nya branch skapades.

## Det viktigaste resonemanget att bevara

### Kärntes

Edge ser just nu mer sannolikt ut att komma från:

- **regime-aware permissioning**
- **continuation bias**
- **no-trade state detection**
- **management / exit intelligence**

…än från bredare parameteroptimering av nuvarande RI-baseline.

### Arbetsantagande

Det är möjligt att RI/R1 har blivit för entry-drivande under implementationen och därmed tappat sin avsedda roll som filter/management-lager.

### Viktig konsekvens

Nästa steg bör därför vara **rollkartläggning**, inte ny Optuna-jakt.

## Hypoteser som nästa agent ska bära vidare

1. **Edge ligger troligen i permissioning, inte i ny entry-logik.**
2. **RI tappade sin design när den började påverka entryytan för mycket.**
3. **Continuation-aware filtering är mer lovande än allmän regime-entry.**
4. **Exit/management kan ge större edge än ytterligare entry-tuning.**
5. **No-trade state detection kan vara mer värdefull än ökad signalaggressivitet.**

## Rekommenderad nästa uppgift — bygg en rollkarta

Nästa agent bör ta fram en **rollkarta för RI/R1 och legacy**.

### Syftet med rollkartan

Att svara på:

- vad ansvarar **legacy** för?
- vad borde **RI/R1** ansvara för?
- vilka intelligence-moduler hör hemma i **context/filter/management**?
- vilka delar har glidit över till att bli **entry-drivare**?

### Rekommenderade ansvarshinkar

Nästa agent bör gruppera allt i åtminstone dessa fyra kategorier:

1. **Context / regime**
   - marknadsläge, struktur, volatilitet, persistence, state
2. **Permission / filtering**
   - trade allowed / not allowed, veto, cooldown, hysteresis, confidence gating
3. **Management**
   - sizing, exits, partials, hold, aggressivitetsjustering
4. **Entry-driving logic**
   - allt som i praktiken skapar eller kraftigt flyttar entry-beteendet

### Kritisk designregel

RI/R1 bör huvudsakligen leva i:

- **Permission / filtering**
- **Management**

…och endast mycket försiktigt i **Entry-driving logic**.

## Konkreta frågor nästa agent bör driva

1. **Vilka indikatorer används faktiskt i legacy vs RI/R1?**
2. **Vilka parametrar finns per modul och vilken roll spelar de egentligen?**
3. **Vilka moduler har testats isolerat, och vilka har bara testats i kluster?**
4. **Vilka moduler är orthogonala, och vilka är bara redundans/komplexitet?**
5. **Vilka delar bör behållas, förenklas, flyttas eller stängas av?**

## Viktigt: börja inte härifrån på fel sätt

Nästa agent ska **inte** börja med att:

- köra ny bred Optuna-kampanj
- öka/minska parametrar blint
- anta att “mer RI” automatiskt är bättre
- behandla alla intelligence-moduler som lika viktiga
- låta overlay-/filter-lagret fortsätta mutera till dold entrymotor

## Bättre arbetsordning

1. **Inventory**
   - lista alla intelligence-moduler + indikatorer + centrala parametrar
2. **Intent audit**
   - var modulen tänkt som filter/management eller beter den sig som entry-driver?
3. **Ablation plan**
   - modul av/på, modul som filter-only, modul som management-only, kombinationspar
4. **Parameter policy först efteråt**
   - diskutera först därefter om något ska upp, ner, frysas eller tas bort

## Filer nästa agent sannolikt bör läsa tidigt

### För arkitektur / definitioner

- `src/core/strategy/family_registry.py`
- `src/core/strategy/families.py`
- `src/core/backtest/intelligence_shadow.py`
- `scripts/validate/validate_optimizer_config.py`

### För styrande/förklarande kontext

- `docs/features/feature-regime-intelligence-strategy-family-1.md`
- `docs/governance/regime_intelligence_strategy_family_integration_stub_2026-03-18.md`
- `docs/analysis/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `docs/analysis/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`

### För test-/guardrail-surface

- `tests/core/strategy/test_families.py`
- `tests/utils/test_validate_optimizer_config.py`
- `tests/governance/test_pipeline_fast_hash_guard.py`
- `tests/governance/test_regime_intelligence_cutover_parity.py`

## Om nästa agent ska skriva något först

Det bästa första artefaktförslaget är **inte kod** utan en tydlig arbetsmatris, till exempel:

- modul / indikator
- tänkt roll
- faktisk observerad roll
- påverkar entry?
- påverkar filtering?
- påverkar management?
- misstanke (behåll / förenkla / flytta / avaktivera)

## Enradig sammanfattning

RI är redan separerad från legacy i canonical modellen, men nästa stora arbete är att återföra RI/R1 till sin sannolika ursprungsroll som **management/filter-lager** genom att först bygga en tydlig **rollkarta för RI/R1 vs legacy** innan mer optimering sker.
