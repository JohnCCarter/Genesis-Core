# RI/R1 vs legacy — första rollkarta

Datum: 2026-03-20
Branch: `feature/ri-legacy-role-map-2026-03-19`
Status: arbetsdokument / analysunderlag / ingen runtime-ändring

## Syfte

Detta dokument fångar en första rollkarta för **legacy** respektive **RI/R1** i Genesis-Core.
Målet är att klargöra:

- vad som faktiskt driver entry i legacy
- vilka RI/intelligence-delar som i första hand verkar vara context/filter/management
- var ansvar blandas eller riskerar att glida
- vilka moduler som bör granskas först i fortsatt ablations-/edge-arbete

Detta är en analysartefakt. Den ändrar inte runtime-beteende, config-authority eller strategy-family-regler.

## Kort slutsats

Den nuvarande kodbilden pekar på följande övergripande ansvarsfördelning:

- **legacy** är fortfarande den tydliga **entry-drivaren**
- **RI/R1/intelligence** ligger främst i **context**, **permission/filtering**, **sizing** och **observability**
- den största arkitekturrisken är inte att RI fullt ut redan tagit över entry, utan att vissa lager blandar **context + permission + management** så att ansvar blir svårare att se och utvärdera

Arbetsantagandet från handoffen består därför:

> Nästa edge bör sökas genom att förtydliga RI/R1 som management/filter-lager och genom att testa dess delar som sådana, innan ny bred parameteroptimering sker.

## Översiktskarta

| Lager                      | Legacy                                                       | RI/R1 / intelligence                                                                       | Bedömning                                                    |
| -------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| **Context / regime**       | `regime_unified.py`, delar av `regime.py`                    | `core.intelligence.regime.authority`, `core.intelligence.regime.htf`, shadow observability | Delat område; RI bidrar främst med alternativ/utökad kontext |
| **Entry-driving logic**    | `prob_model.py`, `decision.py`, `decision_gates.py`          | endast sekundär påverkan via thresholds, calibration och tie-breaks                        | Legacy dominerar tydligt                                     |
| **Permission / filtering** | EV-check, confidence gates, fib-gating, hysteresis, cooldown | regime-aware thresholds, LTF override-history per regime, authority-mode routing           | Här ligger mycket av RI:s verkliga värde idag                |
| **Management / exits**     | risk_map, sizing, HTF exits                                  | `risk_state`, `clarity_score` (när aktiverad), regime multipliers, HTF regime multipliers  | Mest naturliga hemvisten för RI/R1                           |
| **Observability / audit**  | begränsad i legacy-kärnan                                    | `intelligence_shadow.py`, regime contracts, mismatch-observability                         | RI/intelligence är starkt här                                |

## Rollkarta — legacy

### Legacy som tydlig entrymotor

Legacy verkar fortfarande bära den primära beslutskedjan för att skapa en trade-kandidat:

- `src/core/strategy/prob_model.py`
  - buy/sell-probabilities via logistisk modell
- `src/core/strategy/decision.py`
  - den rena beslutsfunktionen som orkestrerar ordningen
- `src/core/strategy/decision_gates.py`
  - candidate selection, thresholding, EV-filter, post-fib-gates
- `src/core/strategy/decision_fib_gating.py`
  - HTF/LTF-structural gates före entry släpps igenom

### Legacy-ansvar enligt denna första karta

| Komponent                | Föreslagen roll                        | Kommentar                                                    |
| ------------------------ | -------------------------------------- | ------------------------------------------------------------ |
| `prob_model.py`          | **Entry-driving**                      | Producerar det egentliga buy/sell-underlaget                 |
| `decision.py`            | **Entry orchestration**                | Gate-ordningen lever här; är navet mellan layers             |
| `decision_gates.py`      | **Permission/filtering nära entry**    | Fortfarande legacy-kärna även när regime påverkar thresholds |
| `decision_fib_gating.py` | **Permission/filtering**               | Strukturveto/override; viktigt före sizing                   |
| `regime_unified.py`      | **Context authority (legacy default)** | Standardauktoritet i default-path                            |
| `htf_exit_engine.py`     | **Management/exits**                   | Position lifecycle, partials, trailing, hold                 |

### Legacy-signatur som bör hållas i minnet

Den verifierade legacy-signaturen i repo/logik/docs är fortfarande ungefär:

- `strategy_family = "legacy"`
- `authority_mode = legacy`
- `atr_period = 28`
- `hysteresis_steps = 2`
- `cooldown_bars = 0`
- legacy-threshold-kluster snarare än RI-kluster

Det betyder att när vi talar om “legacy” i fortsatt rollkarta syftar vi inte bara på gamla docs, utan på en faktisk aktiv entry-topologi.

## Rollkarta — RI/R1 / intelligence

### RI/R1:s mest naturliga hemvist

Kodbilden pekar på att RI/intelligence främst hör hemma i följande roller:

1. **Context / regime enrichment**
2. **Permission / filtering modulation**
3. **Management / sizing / exits**
4. **Observability / shadow audit**

Det är i linje med den återupptäckta grundidén: management/filter-lager snarare än primary entry-driver.

### RI/intelligence-komponenter

| Komponent                                       | Primär roll          | Sekundär roll      | Bedömning                                                           |
| ----------------------------------------------- | -------------------- | ------------------ | ------------------------------------------------------------------- |
| `src/core/intelligence/regime/authority.py`     | Context              | authority seam     | RI-kompatibel authority-boundary, men ska inte själv bli entrylogik |
| `src/core/intelligence/regime/htf.py`           | Context              | confirmation       | HTF-regime som sekundär signal, inte entrymotor                     |
| `src/core/intelligence/regime/clarity.py`       | Management           | permission-support | Mest naturlig som sizing/clarity-justering                          |
| `src/core/intelligence/regime/risk_state.py`    | Management           | risk modulation    | Stark kandidat för kärn-RI snarare än entry                         |
| `src/core/backtest/intelligence_shadow.py`      | Observability        | audit              | Viktig för att mäta utan att injicera decision behavior             |
| regime-aware thresholding i `decision_gates.py` | Permission/filtering | context bridge     | Här finns mycket RI-värde men också ansvarsmix                      |
| regime multipliers i `decision_sizing.py`       | Management           | risk control       | Mycket naturlig RI-yta                                              |

## Första arbetsmatris per område

### 1. Context / regime

| Modul                                   | Tänkt roll                                     | Observerad roll                  | Notering                                |
| --------------------------------------- | ---------------------------------------------- | -------------------------------- | --------------------------------------- |
| `regime_unified.py`                     | Authoritative context                          | Authoritative context            | Legacy-default och fortfarande styrande |
| `regime.py`                             | Alternativ regimeklassificering / richer state | Delvis shadow / delvis stödjande | Viktig att granska för faktisk påverkan |
| `core.intelligence.regime.authority.py` | RI authority boundary                          | Context authority seam           | Ska hållas ren från entryglidning       |
| `core.intelligence.regime.htf.py`       | HTF context                                    | Context/confirmation             | Borde inte ges för stor entrytyngd      |

### 2. Permission / filtering

| Modul                         | Tänkt roll          | Observerad roll          | Risk / möjlighet                                                                 |
| ----------------------------- | ------------------- | ------------------------ | -------------------------------------------------------------------------------- |
| `decision_gates.py`           | Filter/gate         | Filter/gate nära entry   | Hög analysvikt; här blandas mycket ansvar                                        |
| `decision_fib_gating.py`      | Structural veto     | Structural veto/override | Bra kandidat för “trade permission” snarare än alpha                             |
| zone/regime threshold mapping | Regime-aware gating | Regime-aware gating      | Ser fortfarande ut som permission, inte ren entry, men behöver isolerad testning |
| LTF override adaptive         | Filter override     | Filter override          | Kan vara kraftfull men riskerar att bli dold entry-aggressivitet                 |

### 3. Management / exits

| Modul                | Tänkt roll                    | Observerad roll           | Bedömning                                            |
| -------------------- | ----------------------------- | ------------------------- | ---------------------------------------------------- |
| `decision_sizing.py` | Sizing                        | Sizing + RI multipliers   | Naturlig RI-yta                                      |
| `risk_state.py`      | Risk modulation               | Risk modulation           | Stark kandidat att behålla i RI-kärnan               |
| `clarity.py`         | Clarity / strength adjustment | Sizing/clarity modulation | Bör behandlas som management tills motsatsen bevisas |
| `htf_exit_engine.py` | Exit/partials/trailing        | Exit/partials/trailing    | Intressant för framtida RI-as-management-spår        |

### 4. Entry-driving logic

| Modul                                      | Nuvarande roll            | Bör i första hand tillhöra   | Bedömning                                                |
| ------------------------------------------ | ------------------------- | ---------------------------- | -------------------------------------------------------- |
| `prob_model.py`                            | Entry-driving             | Legacy                       | Borde förbli entrymotor tills tydligt annat beslut finns |
| candidate selection i `decision_gates.py`  | Entry-adjacent            | Legacy + permission boundary | Ambivalent men fortfarande mest legacy-kärna             |
| regime tie-breaks                          | Secondary entry influence | Permission/context           | Troligen okej som sekundärt beteende                     |
| regime-aware calibration i `prob_model.py` | Entry-adjacent modulation | Ambivalent                   | Behöver granskas om den börjar bli för styrande          |

## Viktigaste blandzoner att granska först

Det finns några områden där ansvar ser blandat ut och där nästa analys sannolikt ger mest värde.

### A. `decision_gates.py`

Detta är sannolikt den viktigaste filen för nästa steg eftersom den binder ihop:

- regime/context
- probability thresholds
- candidate selection
- EV-filter
- post-fib gates

Det gör den till en naturlig plats där RI kan se ut som “bara filtering” men ändå i praktiken flytta entrybeteende.

**Arbetshypotes:**
`decision_gates.py` bör brytas ner analytiskt i vilka delar som är:

- genuin permissioning
- legacy entry resolution
- dold aggressivitetsstyrning

### B. `decision_sizing.py`

Denna fil verkar vara en stark kandidat för RI:s “rätta hem”.
Den innehåller redan:

- regime multipliers
- HTF regime multipliers
- clarity hooks
- risk state hooks

**Arbetshypotes:**
Om RI ska återföras till management/filter-lager är `decision_sizing.py` och dess närliggande intelligence-moduler sannolikt kärnområdet.

### C. `decision_fib_gating.py` + override-logiken

Fib-gating och LTF override verkar mer som **trade permission** än alpha-generation.
Det gör området mycket intressant eftersom en verklig edge kan ligga i:

- bättre rätt-att-handla-logik
- bättre no-trade states
- bättre confirmation

…inte i fler fria entryparametrar.

## Har vi testat alla intelligence-moduler?

Första svaret är: **inte på det sätt vi nu behöver**.

Det finns test- och bevisytor för delar av RI/intelligence, inklusive:

- authority-mode parity
- clarity on/off legacy parity
- risk state multiplier
- cutover parity / pipeline invariants
- shadow observability

Men det är en annan sak än att ha en ren **modul-för-modul rollkarta + ablationsmatris**.

Det vi ännu verkar sakna är en kompakt översikt som svarar på:

1. vad modulen var tänkt att göra
2. vad den nu faktiskt gör
3. om den påverkar entry, filtering eller management
4. om den är orthogonal eller redundant
5. om den bör behållas, förenklas, flyttas eller stängas av

## Första rekommendationer

### Behåll som sannolik RI-kärna att utvärdera vidare

- `risk_state.py`
- `clarity.py` (som management/sizing-kandidat, inte som entrymotor)
- HTF/secondary regime context
- observability/shadow-spåret
- regime-aware permissioning där den verkligen fungerar som veto/filter

### Granska extra hårt för ansvarsglidning

- `decision_gates.py`
- regime-aware threshold mapping
- LTF override adaptive logic
- eventuell regime-aware calibration i `prob_model.py`

### Utgå inte från att detta ska optimeras bredare ännu

Innan ny Optuna/parameterjakt bör nästa arbete fokusera på:

1. **Inventory**
2. **Intent audit**
3. **Ablation plan**
4. **Först därefter parameter policy**

## Rekommenderad nästa artefakt

Efter detta dokument bör nästa steg vara en ännu mer operativ arbetsmatris, till exempel:

| Modul / indikator | Tänkt roll | Faktisk roll | Entry? | Filter? | Management? | Misstanke | Nästa test |
| ----------------- | ---------- | ------------ | ------ | ------- | ----------- | --------- | ---------- |

Det skulle göra fortsatt arbete mycket mer systematiskt.

## Operativ arbetsmatris — första version

Syftet med matrisen nedan är att göra nästa steg konkret. Den är inte en slutdom över modulerna, utan en arbetsyta för att prioritera:

- vad som ska granskas först
- vad som sannolikt hör hemma i legacy
- vad som sannolikt hör hemma i RI/R1
- vilka delar som riskerar ansvarsglidning

### Matris

| Modul / indikator                        | Tänkt roll                               | Faktisk observerad roll                            | Entry  | Filter | Management | Misstanke                                                                  | Nästa test / analys                                                                     |
| ---------------------------------------- | ---------------------------------------- | -------------------------------------------------- | ------ | ------ | ---------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `prob_model.py`                          | Entrymotor                               | Primär buy/sell-signal                             | Ja     | Nej    | Nej        | Ska sannolikt stanna i legacy-kärnan                                       | Isolera regime-aware calibration mot ren legacy-kalibrering                             |
| `decision.py`                            | Orkestrering                             | Binder ihop gates, fib, sizing                     | Ja     | Ja     | Ja         | Hög ansvarskoncentration, men inte nödvändigtvis fel                       | Dokumentera exakt gate-ordning och vilka inputs som faktiskt påverkar candidate vs size |
| `decision_gates.py`                      | Permission/filtering nära entry          | Filter/gate nära entry + delvis entry resolution   | Delvis | Ja     | Nej        | Största blandzonen i hela systemet                                         | Bryt ned i delsteg: EV, thresholding, candidate selection, tie-break, post-fib-gates    |
| `decision_fib_gating.py`                 | Structural permission                    | HTF/LTF-veto, override, structure-based pass/block | Delvis | Ja     | Delvis     | Ser mer ut som trade permission än alpha                                   | Testa strikt veto-only vs override-aktivt läge                                          |
| `decision_fib_gating_helpers.py`         | Local helper                             | Hjälper override/veto-logik                        | Nej    | Ja     | Nej        | Risk för dold komplexitet om mycket logik ligger här                       | Kartlägg exakt vad som är policy vs helper-implementering                               |
| `regime_unified.py`                      | Legacy authority context                 | Fortfarande default authority path                 | Nej    | Delvis | Delvis     | Bör inte blandas ihop med RI-path bara för att båda är “regime”            | Dokumentera vilka downstream-beslut som faktiskt läser authoritative regime             |
| `regime.py`                              | Alternativ / rikare regimeklassificering | Delvis shadow, delvis stödjande signal             | Nej    | Delvis | Delvis     | Kandidat för begreppsglidning om den uppfattas som live authority överallt | Jämför shadow-resultat mot faktisk decision-input rad för rad                           |
| `core.intelligence.regime.authority.py`  | RI authority boundary                    | Context-seam för authority_mode                    | Nej    | Delvis | Delvis     | Måste hållas ren från att bli entrylogik i smyg                            | Verifiera vilka funktioner som bara normaliserar context vs förändrar decision-input    |
| `core.intelligence.regime.htf.py`        | HTF context / confirmation               | Sekundär kontextsignal                             | Nej    | Delvis | Delvis     | Får inte övervärderas till primär alpha                                    | Testa HTF-context som ren confirmation-signal utan override-effekt                      |
| `decision_sizing.py`                     | Management                               | Sizing + regime/HTF/RI multipliers                 | Nej    | Delvis | Ja         | Stark kandidat för RI:s rätta hemvist                                      | Kör clarity/risk_state av/på utan att ändra candidate outcome                           |
| `core.intelligence.regime.clarity.py`    | Clarity/strength                         | Sizing/clarity modulation                          | Nej    | Delvis | Ja         | Ska sannolikt behandlas som management tills motsatsen bevisas             | Testa clarity on/off och bevisa om endast size/logg ändras                              |
| `core.intelligence.regime.risk_state.py` | Risk modulation                          | Risk modulation / sizing                           | Nej    | Nej    | Ja         | Starkaste kandidaten för “ren RI management”                               | Isolera risk_state-effekt på size och exits utan entry-drift                            |
| `htf_exit_engine.py`                     | Exit/management                          | Partials, trailing, hold                           | Nej    | Nej    | Ja         | Möjlig framtida edge-källa via RI-as-management                            | Testa regime-aware exit-profiler utan entryändring                                      |
| `intelligence_shadow.py`                 | Observability/audit                      | Shadow logging utan decision injection             | Nej    | Nej    | Nej        | Viktig safety rail; bör bevaras                                            | Säkerställ fortsatt `decision_input=False` i observability-bevis                        |

### Prioriteringsordning

Om nästa agent bara hinner granska några få ytor först, bör ordningen vara:

1. `decision_gates.py`
2. `decision_sizing.py`
3. `decision_fib_gating.py`
4. `core.intelligence.regime.risk_state.py`
5. `core.intelligence.regime.clarity.py`
6. `prob_model.py` (främst calibration-frågan, inte full omdesign)

## Kompletterande rollkarta — återstående kärnmoduler i hela kedjan

Efter kodläsningen av de återstående nyckelmodulerna blir helhetskedjan tydligare. Det som först såg ut som “några separata beslutslager” är i praktiken en ganska ren pipeline med tydliga men ibland semantiskt känsliga övergångar.

### Förenklad systemkedja

Den nuvarande pipeline-kedjan kan läsas ungefär så här:

1. `features_asof.py`
2. `regime_unified.py` / authority-path
3. `prob_model.py`
4. `confidence.py`
5. `decision.py`

- `decision_gates.py`
- `decision_fib_gating.py`
- `decision_sizing.py`

6. `evaluate.py`
7. shadow/observability via `meta.observability.shadow_regime`
8. separat forsknings-/ledger-spår via `core/backtest/intelligence_shadow.py`

Det innebär att nästa rollmap inte bara bör tala om “vilka moduler som finns”, utan också om **vilken typ av ansvar som förs vidare från ett lager till nästa**.

### Fullare klassificering av återstående moduler

| Modul                                       | Primär roll               | Sekundär roll                   | Bedömning                                                                                                    |
| ------------------------------------------- | ------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `src/core/strategy/evaluate.py`             | Pipeline-orkestrering     | authority-seam + observability  | Tunn men central kompositör; väljer regime-authority, features, probas, confidence och `decide()`            |
| `src/core/strategy/decision.py`             | Beslutsorkestrering       | state propagation               | Renaste navet mellan candidate, fib-gating, post-gates och sizing                                            |
| `src/core/strategy/prob_model.py`           | Entry-underlag            | regime-aware calibration        | Legacy-kärna, men med RI-adjacent calibration seam när regime-specifik kalibrering används                   |
| `src/core/strategy/confidence.py`           | Confidence-/quality-layer | gate+sizing bridge              | Inte entrymotor i sig, men påverkar både gating och sizing beroende på `quality.apply` och component scopes  |
| `src/core/strategy/regime_unified.py`       | Legacy context authority  | trend/volatility classification | Ser fortfarande ut som canonical legacy-default för authoritative regime                                     |
| `src/core/intelligence/regime/authority.py` | RI authority seam         | normalization/fallback          | Viktig därför att den avgör _vilken_ regime-källa som är auktoritativ, inte därför att den genererar entries |
| `src/core/backtest/intelligence_shadow.py`  | Research/observability    | advisory ledger                 | Stark observability-yta; uttryckligen advisory/shadow, inte decision-input                                   |

### Samlad bedömning av `evaluate.py`

`evaluate.py` ser efter läsningen ut som det tydligaste **pipeline-navet** i hela systemet, men inte som en egen alpha-modul. Den:

- bygger features
- väljer authoritative regime via authority-mode
- kör `predict_proba_for(...)`
- kör `compute_confidence(...)`
- väljer mellan scaled/raw confidence beroende på `quality.apply`
- beräknar HTF-regime
- skickar allt vidare till `decide(...)`
- exporterar shadow-observability där `decision_input=False`

Det viktigaste här är att `evaluate.py` inte själv verkar flytta alfa eller entrylogik, men den **bestämmer vilken väg som används**. Därför bör den klassas som:

- **primärt:** orchestration
- **sekundärt:** authority/observability seam

### Samlad bedömning av `decision.py`

`decision.py` bekräftar den ordning som dokumentet redan antytt, men gör den nu explicit:

1. `select_candidate(...)`
2. `apply_fib_gating(...)`
3. `apply_post_fib_gates(...)`
4. `apply_sizing(...)`
5. state propagation + final reason append

Det gör `decision.py` till den tydligaste **mekaniska orkestreraren av själva beslutsordningen**. Viktig nyans:

- filen skapar inte probas
- filen skapar inte confidence
- filen skapar inte regime

Men den avgör i vilken ordning dessa får påverka slutbeslutet. Därför bör den klassas som:

- **primärt:** entry orchestration
- **sekundärt:** state management

### Samlad bedömning av `prob_model.py`

`prob_model.py` ser fortfarande ut som den renaste **legacy-entry-kärnan** i hela systemet. Den producerar buy/sell/hold-probabilities från model registry + kalibrering.

Det som gör filen semantiskt viktig för RI-rollkartan är dock att `predict_proba_for(...)` stödjer:

- regime-specifik kalibrering via `calibration_by_regime`
- fallback till vanlig default-kalibrering om regime-specifik version saknas

Det betyder att filen bör klassas som:

- **primärt:** entry-driving substrate
- **sekundärt:** regime-aware entry modulation

Viktig observation: här kan RI påverka entry **före gates**, men fortfarande genom kalibrering av proba-underlaget snarare än genom att bli en separat entrymotor.

### Skarpare delkarta — vad i `prob_model.py` flyttar faktiskt entry?

Efter närläsning av koden är det viktigt att inte beskriva hela `prob_model.py` som “en enda entrymotor”. Filen innehåller i praktiken tre olika ansvar:

1. **inläsning av modellsubstrat**
2. **proba-beräkning från vikter/bias/kalibrering**
3. **val av kalibreringsgren beroende på regime**

Det betyder att filen inte väljer `LONG` eller `SHORT` direkt, men den formar det sannolikhetsunderlag som alla senare gates lever på.

| Del i `prob_model.py`                            | Vad koden gör                                                               | Flyttar sannolikhetsytan? | Typisk roll                        | Bedömning för rollkartan                                     |
| ------------------------------------------------ | --------------------------------------------------------------------------- | ------------------------- | ---------------------------------- | ------------------------------------------------------------ |
| `ModelRegistry().get_meta(...)`                  | Hämtar modellmetadata från registry / modellfil                             | Indirekt                  | Model substrate lookup             | Infrastruktur-/substratsteg; viktig men inte i sig RI-logik  |
| `schema` + feature projection                    | Läser features i rätt ordning och fyller saknade värden med `0.0`           | Ja                        | Deterministiskt inference-substrat | Legacy-kärna; utan detta finns ingen meningsfull proba       |
| `buy.w` / `buy.b` / `sell.w` / `sell.b`          | Definierar den råa logistiska scoringytan                                   | Ja                        | Entry substrate                    | Detta är den mest rena legacy-entryytan i filen              |
| Default-kalibrering (`buy.calib` / `sell.calib`) | Skalar/offsetar råscore till kalibrerad buy/sell-proba                      | Ja                        | Entry calibration                  | Fortfarande legacy-nära, men redan ett boundary-shaping steg |
| `calibration_by_regime`-lookup                   | Väljer regimespecifik kalibrering när både `regime` och metadata finns      | Ja                        | Regime-aware entry modulation      | Detta är filens tydligaste RI-adjacent söm                   |
| Fallback från regime-kalibrering till default    | Behåller default-kalibrering när regime-saknas eller saknar specifik branch | Ja                        | Safety / compatibility fallback    | Viktig kompatibilitetsbrygga snarare än ny alpha             |
| `predict_proba(...)`-normalisering till simplex  | Bygger slutlig `{buy, sell, hold}`-fördelning                               | Ja                        | Canonical probability output       | Legacy-inferencekärna; formar allt senare gating läser       |
| `meta_out.versions.regime_aware_calibration`     | Exponerar om regime-aware kalibrering användes                              | Nej                       | Observability                      | Audit-spår, inte beslutslogik                                |
| `meta_out.calibration_used`                      | Exponerar exakt vilka kalibreringsparametrar som användes                   | Nej                       | Observability / evidence           | Mycket värdefullt för ablation och driftanalys               |

### Praktisk split — legacy-substrat vs RI-söm i `prob_model.py`

I praktiken kan filen delas så här:

- **Tydligt legacy-substrat**
  - feature projection enligt `schema`
  - buy/sell-vikter och bias
  - sigmoid + simplex-normalisering

- **Boundary-shaping men fortfarande model-nära steg**
  - default-kalibrering
  - fallbacklogik när regime-specifik kalibrering saknas

- **RI-adjacent söm**
  - valet av `calibration_by_regime` när authoritative regime skickas in från pipeline

Den viktiga nyansen är att RI här inte väljer riktning direkt. I stället kan RI flytta **sannolikhetsgeometrin före gates**, vilket gör sömmen mer känslig än sizing men fortfarande annorlunda från ren candidate selection.

### Konkret evidens — aktiv modellmetadata flyttar proba före gates

Detta är inte bara en teoretisk kodstig. Aktiv modellmetadata i `config/models/tBTCUSD_1m.json` innehåller tydligt olika `a`/`b`-parametrar per regime för både buy och sell. En snabb körning med samma feature-vektor men olika `regime` gav:

| Regime    | Buy        | Sell       | Hold       | Tolkning                               |
| --------- | ---------- | ---------- | ---------- | -------------------------------------- |
| `none`    | `0.425263` | `0.574737` | `0.000000` | Default-kalibrering                    |
| `bull`    | `0.378436` | `0.587149` | `0.034414` | Regime-söm aktiv men måttlig drift     |
| `bear`    | `0.206923` | `0.755708` | `0.037368` | Kraftig topologisk drift före gates    |
| `ranging` | `0.352529` | `0.583218` | `0.064253` | Regime-söm aktiv även i sidledes miljö |

Det stöder två viktiga slutsatser:

1. `prob_model.py` är fortfarande legacy-entry-substratet.
2. regime-aware kalibrering är en **aktiv och meningsfull beslutsgräns före gating**, inte bara dekorativ metadata.

### Tydligare slutsats om `prob_model.py`

Den skarpare läsningen pekar på följande:

- **Filens kärna är fortfarande legacy**
  - vikter, bias, sigmoid och simplex-normalisering

- **Den mest känsliga RI-bryggan i filen är kalibreringsvalet**
  - inte inferencemotorn i sig
  - inte candidate selection
  - utan valet mellan default-kalibrering och regime-specifik kalibrering

- **Detta gör `prob_model.py` till en tidigare och mer strukturell brygga än `decision_gates.py`**
  - `decision_gates.py` formar vilka kandidater som överlever
  - `prob_model.py` kan redan innan dess flytta själva buy/sell/hold-fördelningen som gates läser

Det betyder att om vi vill förstå var RI först börjar bryta loss från legacy-topologin, är `prob_model.py` sannolikt en av de första verkligt känsliga sömmarna i kedjan.

### Befintlig evidens som stödjer denna split

- `tests/integration/test_prob_model_integration.py::test_prob_model_wrapper_applies_calibration_and_meta`
  - stöder att wrappern faktiskt applicerar kalibrering och exporterar metadata
- `tests/utils/test_prob_model_min.py`
  - stöder att basmodellen producerar normaliserad `{buy, sell, hold}`-output utan sidoeffekter
- `docs/analysis/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
  - stöder att authority-/calibration-pathen är den första tydliga topologiska bryggan i RI-familjens avvikelse från legacy

### Samlad bedömning av `confidence.py`

`confidence.py` förtjänar en egen plats i rollkartan, eftersom den inte bara är ett “litet hjälplager”. Efter kodläsning ser den ut som en **quality-aware bridge** mellan entry-underlag och både gating/sizing.

Filen:

- skalar buy/sell-confidence med quality factor
- kan hålla gate och sizing isär via component scopes
- exporterar `buy_scaled` / `sell_scaled` när sizing-faktorn skiljer sig från gate-faktorn

Det gör att `confidence.py` bör klassas som:

- **primärt:** confidence/quality layer
- **sekundärt:** permission + sizing bridge

Viktig observation: detta är inte en RI-modul i snäv mening, men den är en plats där marknadskvalitet kan minska aggressivitet utan att nödvändigtvis ändra direction. Därför är den strategiskt viktig i rollkartan.

### Skarpare delkarta — vad i `confidence.py` flyttar faktiskt beteendet?

Efter närläsning av både `confidence.py`, `evaluate.py` och kontraktstesterna blir bilden skarpare: filen genererar inte direction, men den kan fortfarande flytta **vilka setups som passerar confidence-gates** och/eller **hur stora positioner de får** beroende på konfiguration.

| Del i `confidence.py`                           | Vad koden gör                                                  | Ändrar riktning? | Kan ändra gate-pass?  | Kan ändra storlek? | Typisk roll              | Bedömning                                                          |
| ----------------------------------------------- | -------------------------------------------------------------- | ---------------- | --------------------- | ------------------ | ------------------------ | ------------------------------------------------------------------ |
| `_as_float` / `_clamp01` / `_clamp`             | Normaliserar och säkrar numeriska inputs                       | Nej              | Indirekt              | Indirekt           | Safety / numeric hygiene | Ren stödfunktion, inte semantisk alpha                             |
| `_compute_quality_factor(..., enabled=False)`   | v1-läge: använder bara `data_quality` eller `1.0`              | Nej              | Ja, via absolut nivå  | Ja                 | Basal confidence scaling | Legacy-kompatibel dämpning                                         |
| v2-komponenter: `spread`, `atr`, `volume`       | Straffar quality utifrån marknadskvalitet                      | Nej              | Ja                    | Ja                 | Quality modulation       | Flyttar absolut confidence men inte buy/sell-ordning               |
| `component_scopes`                              | Delar upp komponenter i `gate`, `sizing` eller `both`          | Nej              | Ja, om scope når gate | Ja                 | Gate/sizing routing      | Detta är filens viktigaste beteendesöm                             |
| `q_gate` / `q_size`                             | Bygger separata kvalitetsfaktorer för gating respektive sizing | Nej              | Ja                    | Ja                 | Boundary + sizing bridge | Förklarar varför samma quality-data kan ge olika downstream-effekt |
| `c_buy` / `c_sell` / `overall`                  | Skalar buy/sell lika med gate-faktorn och bevarar rangordning  | Nej              | Ja                    | Indirekt           | Gate-facing confidence   | Direction bevaras men absolut nivå kan stoppa entry                |
| `buy_scaled` / `sell_scaled` / `overall_scaled` | Exponerar separat sizing-confidence när `q_size != q_gate`     | Nej              | Nej direkt            | Ja                 | Sizing-facing confidence | Tydlig brygga till `decision_sizing.py`                            |
| `meta.quality` / `reasons` / `component_scopes` | Exporterar varför confidence reducerades och med vilken scope  | Nej              | Nej                   | Nej                | Observability / audit    | Viktigt bevislager, inte beslutsmotor                              |

### Praktisk split — confidence som direction-bevarande men boundary-flyttande brygga

Det viktigaste att hålla isär här är tre olika påståenden:

1. `confidence.py` **väljer inte riktning**
2. `confidence.py` kan ändå **ändra om ett setup passerar confidence-gaten**
3. `confidence.py` kan också, separat, **bara ändra size**

Denna kombination gör lagret ovanligt viktigt:

- **Direction-bevarande egenskap**
  - buy och sell skalas med samma gate-faktor
  - ordningen mellan buy och sell bevaras
  - filen introducerar därför inte ny long/short-bias i sig

- **Boundary-flyttande egenskap**
  - om `quality.apply = both` i `evaluate.py` används den skalade confidence-bilden direkt i `decide()`
  - då kan samma proba-setup gå från pass till block utan att direction ändras

- **Ren sizing-gemenskap när den explicit konfigureras så**
  - om `quality.apply = sizing_only` använder `evaluate.py` rå confidence för gating
  - samtidigt exporteras `buy_scaled` / `sell_scaled` för sizing
  - då blir lagret i praktiken management/sizing snarare än entry-permission

Detta betyder att `confidence.py` inte bör beskrivas som varken ren management eller ren gate-logik. Det är en **konfigurerbar brygga** vars default-läge kan vara entry-adjacent, medan dess isolerade sizing-läge ligger mycket närmare RI:s tänkta managementroll.

### Tydligare slutsats om `confidence.py`

Den skarpare läsningen pekar på följande:

- **`confidence.py` är inte en direction-motor**
  - den bevarar buy/sell-ordningen
  - den skapar inte nya kandidater

- **`confidence.py` är däremot en verklig boundary-modulator**
  - i default-/`both`-läge kan den påverka vilka setups som överlever gating
  - i `sizing_only`-läge blir den i stället en ren storleksmodulator

- **Detta gör filen till en mer flexibel brygga än `decision_sizing.py`**
  - `decision_sizing.py` är nästan rent post-candidate
  - `confidence.py` kan, beroende på apply/scope, ligga både före och efter den verkliga gating-effekten

Praktiskt betyder det att `confidence.py` bör hållas under extra kontroll i RI-rollkartan: inte därför att den genererar entry, utan därför att den kan flytta entry-gränsen utan att ändra riktning.

### Befintlig evidens som stödjer denna split

- `tests/utils/test_confidence.py::test_compute_confidence_v2_preserves_buy_sell_order_when_not_saturated`
  - stöder att lagret bevarar direction-order och därmed inte själv skapar ny riktning
- `tests/utils/test_confidence.py::test_compute_confidence_v2_component_scope_sizing_only_does_not_affect_gate`
  - stöder att komponentscope kan hålla gating oförändrad men ändå reducera sizing via `buy_scaled` / `sell_scaled`
- `tests/utils/test_decision_edge.py::test_entry_gate_does_not_use_scaled_confidence`
  - stöder att scaled confidence inte får smyga in och skapa entry när rå gate-confidence ligger under threshold
- `tests/utils/test_decision_edge.py::test_sizing_prefers_scaled_confidence_when_present`
  - stöder att scaled confidence faktiskt används i sizing när den väl finns
- `src/core/strategy/evaluate.py`
  - visar explicit att `quality.apply` avgör om confidence-lagret används som `both`-bridge eller som `sizing_only`-bridge

### Runtime-/config-karta — var används `both` respektive `sizing_only`?

Efter repo-sökning över kod, tester och checked-in configfiler framträder en viktig praktisk bild:

| Runtime-/configyta                                                                                               | Observerat läge                       | Evidens                                                                                 | Tolkning                                                                                       |
| ---------------------------------------------------------------------------------------------------------------- | ------------------------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `src/core/strategy/evaluate.py` utan explicit `quality.apply`                                                    | `both` (default)                      | `quality_cfg.get("apply") or "both"`                                                    | Om config inte sätter `apply` används quality-lagret som gate+sizing-brygga                    |
| Checked-in quality-profiler under `config/strategy/champions/`                                                   | ingen explicit `apply`                | profilerna innehåller `quality.components.*.scope` men ingen `apply`-nyckel             | Dessa profiler faller därför tillbaka till runtime-default `both`                              |
| `config/strategy/champions/tBTCUSD_1h_quality_v2_candidate_scoped*.json`                                         | effektivt hybrid under default `both` | `data_quality` + `spread` har `scope: both`, medan `atr` + `volume` har `scope: sizing` | Gating påverkas av vissa quality-komponenter, medan andra bara påverkar sizing                 |
| `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_ri_v2_clarity_on_changes_sizing_only_and_logs` | explicit `sizing_only`                | `cfg_base["quality"] = {"apply": "sizing_only"}`                                        | Testad RI-slice där confidence hålls borta från gating och används för sizing-only             |
| `src/core/strategy/decision_sizing.py` clarity-payload                                                           | `sizing_only`                         | `clarity_payload["apply"] = "sizing_only"`                                              | RI clarity är uttryckligen modellerad som storleks-/management-lager                           |
| Repo-bredd sökning efter explicit `"apply": "sizing_only"` i checked-in config                                   | inga träffar i config                 | `rg` över `config/` gav inga explicita `quality.apply = sizing_only`-konfigurationer    | `sizing_only` framstår som kontrollerat test-/specialläge, inte som standardiserad huvudprofil |

### Praktisk slutsats om skarpa confidence-lägen

Detta ger en mer precis karta än den tidigare allmänna formuleringen:

- **Default i runtime är `both`**
  - om `quality.apply` saknas blir confidence-lagret gate+sizing-brygga
  - detta gäller även checked-in quality-profiler som bara anger komponentscopes

- **Checked-in champion-/candidate-profiler ser ut som hybrider under `both`**
  - `data_quality` och `spread` får påverka gating
  - `atr` och `volume` får bara påverka sizing
  - alltså: inte “ren gate” och inte “ren sizing”, utan en avsiktlig mix

- **`sizing_only` finns tydligt som kontrollerad policy, men främst i testad RI-/clarity-kontext**
  - explicit i pipeline-testen för clarity-slicen
  - explicit i clarity-metadata i `decision_sizing.py`
  - inte observerad som generell checked-in runtime-default i `config/`

Detta betyder att den nuvarande repo-bilden lutar åt att **skarp standardanvändning fortfarande är entry-adjacent via `both`**, medan **RI clarity-spåret redan uttryckligen är placerat i management/sizing-facket via `sizing_only`**.

### Konkret evidens — de faktiska `both`-profilerna ger verklig gate-drift

För att flytta detta från “trolig tolkning” till faktisk evidens kördes `compute_confidence(...)` med den checked-in profilen `config/strategy/champions/tBTCUSD_1h_quality_v2_candidate_scoped.json` och en representativ buy-proba nära defaultgränsen (`buy = 0.33` mot `entry_conf_overall = 0.24`).

Det gav följande bild:

| Fall                  | Gate confidence | Scaled confidence | Gate-pass vid `0.24`? | Slutsats                                                         |
| --------------------- | --------------- | ----------------- | --------------------- | ---------------------------------------------------------------- |
| Clean                 | `0.33`          | `0.33`            | Ja                    | Baslinje                                                         |
| `spread_stress`       | `0.231`         | `0.231`           | Nej                   | `scope: both` på `spread` kan blockera entry                     |
| `data_quality_stress` | `0.231`         | `0.231`           | Nej                   | `scope: both` på `data_quality` kan blockera entry               |
| `atr_stress`          | `0.33`          | `0.231`           | Ja                    | `scope: sizing` på ATR lämnar gating orörd men sänker storlek    |
| `volume_stress`       | `0.33`          | `0.231`           | Ja                    | `scope: sizing` på volume lämnar gating orörd men sänker storlek |

Detta är viktigt därför att det visar att frågan inte längre är om `both`-profiler **kan** flytta gating i teorin, utan att den checked-in scoped-profilen faktiskt gör det på ett mätbart sätt.

### Jämförelse mellan scoped-profilerna — relaxed-size ändrar size, inte gate

Den andra checked-in varianten, `tBTCUSD_1h_quality_v2_candidate_scoped_relaxed_size.json`, visar samma gate-sida men mildare size-straff för de sizing-only-komponenter som öppnats upp:

| Profil             | Fall            | `q_gate` | `q_size`   | Tolkning                                            |
| ------------------ | --------------- | -------- | ---------- | --------------------------------------------------- |
| `candidate_scoped` | `spread_stress` | `0.7`    | `0.7`      | Gate och size sjunker tillsammans via `scope: both` |
| `relaxed_size`     | `spread_stress` | `0.7`    | `0.7`      | Samma gate-ytan kvar                                |
| `candidate_scoped` | `atr_stress`    | `1.0`    | `0.7`      | Gating orörd, size tydligt reducerad                |
| `relaxed_size`     | `atr_stress`    | `1.0`    | `0.892469` | Samma gate, mildare size-straff                     |

Det stöder följande precisering:

- **gate-driften i dessa profiler kommer från `data_quality` och `spread`**
- **skillnaden mellan scoped-profilerna sitter främst i sizing-sidan (`atr` / `volume`)**
- relaxed-size-profilen ser alltså ut att vara en **size-surface-justering**, inte en ny gate-topologi

Detta passar också väl med metadata-noten i den scoped-profilen: målet beskrivs som att behålla gating-fördelarna från W1/W3 men mildra W2-regression via sizing-only-komponenterna.

### Konkret evidens — threshold-lagret kan ensamt flippa samma setup

För att få en jämförbar evidenspunkt mot quality-lagret kördes också samma `probas` och samma `confidence` genom RI-signaturens zontrösklar i `decision_gates.py`:

- `buy = 0.45`
- `sell = 0.20`
- `confidence.buy = 0.45`
- regime = `balanced`

Med en RI-lik signal-adaptation-konfiguration gav det:

| Zon | Aktiv balanced-threshold | Action | Slutsats |
| --- | ------------------------ | ------ | -------- |
| `low` | `0.33` | `LONG` | setup passerar |
| `mid` | `0.51` | `NONE` | samma setup blockeras |
| `high` | `0.57` | `NONE` | samma setup blockeras ännu tydligare |

Detta visar att threshold-lagret i `decision_gates.py` på egen hand kan flytta ett identiskt setup mellan **trade** och **no-trade** utan att probas eller confidence i sig ändras.

### Jämförbar driftstege — calibration vs threshold vs quality

När de tre evidensytorna ställs bredvid varandra blir skillnaden i ansvar tydligare:

| Lager | Fast input | Observerad drift | Typ av drift |
| ----- | ---------- | ---------------- | ------------ |
| `prob_model.py` calibration | samma features, olika regime | `buy` går från `0.425263` (`none`) till `0.206923` (`bear`) och faller då under gate `0.24` | **Upstream probability drift** före all gating |
| `decision_gates.py` thresholding | samma probas/confidence, olika zon | samma setup går från `LONG` (`low`) till `NONE` (`mid/high`) | **Explicit gate-boundary drift** |
| `confidence.py` quality (`both`) | samma probas, olika market-quality | gate confidence går från `0.33` till `0.231` under `spread_stress` / `data_quality_stress` | **Conditional gate drift** via gate-scoped quality-komponenter |
| `confidence.py` quality (`sizing`) | samma probas, olika ATR/volume | gate confidence oförändrad, men scaled confidence sjunker | **Ren size drift** |

### Tydligare slutsats om relativ driftstyrka

Den jämförbara bilden pekar på följande arbetsordning för fortsatt analys:

1. **Calibration** är den tidigaste och mest strukturella bryggan
  - den flyttar själva sannolikhetsytan innan några gates ens läser den

2. **Thresholding** är den tydligaste sena trade/no-trade-brytaren
  - den kan med identiska probas/confidence flippa ett setup mellan `LONG` och `NONE`

3. **Quality** är i nuvarande checked-in profiler en verklig men mer selektiv gate-brygga
  - `data_quality` och `spread` kan blockera entry
  - `atr` och `volume` ligger däremot huvudsakligen i sizing-facket

Det betyder att om målet är att förklara faktisk trade-drift mellan RI- och legacy-topologier, bör nästa viktning sannolikt vara:

- först **calibration-pathen**
- därefter **threshold-/zone-pathen**
- därefter **quality-gating**

...med förbehållet att quality fortfarande kan vara mycket viktig i vissa marknadslägen, men att dess checked-in scoped-profiler just nu ser mer **hybridiska** än primärt topologidrivande ut.

### Samlad bedömning av authority-seamen

Kombinationen av `regime_unified.py` och `core/intelligence/regime/authority.py` gör att regime-authority inte bör beskrivas som “en modul”, utan som en **auktoritetsseam**:

- `regime_unified.py` = legacy-default authoritative context
- `authority.py` = normalize/fallback-seam och RI-path-stöd
- `evaluate.py` = väljer authority-mode och därmed vilken väg som används

Detta stödjer följande klassning:

- **legacy-path:** `regime_unified.py` som canonical authority
- **RI-path:** authority-mode-baserad seam där regime_module kan vinna

Viktig observation: authority-seamen är inte entrylogik, men den kan indirekt påverka både calibration, gating och observability genom att definiera vilket regime som anses sant.

### Samlad bedömning av `core/backtest/intelligence_shadow.py`

`core/backtest/intelligence_shadow.py` ser efter läsningen inte ut som ett latent beslutslager, utan som en **ren advisory/ledger-observability-yta**.

Det viktiga här är att den:

- bygger shadow events från backtest-resultat
- persistar dem till research-ledger
- uttryckligen sätter `decision_drift_observed=False` i summary-payloaden
- arbetar som post-hoc research-/auditlager

Den bör därför klassas som:

- **primärt:** observability / advisory research
- **sekundärt:** audit trail

Detta stärker tesen att shadow/intelligence-spåret i nuvarande form främst är till för förståelse och utvärdering, inte för att injicera runtime-beslut.

## Bevisstatus — vad vi faktiskt vet nu

Rollkartan stöds nu inte bara av kodläsning, utan också av redan existerande högsignaltester.

### Verifierad evidens som stödjer rollkartan

| Fråga                                                           | Befintligt test                                                                                                           | Vad det stöder                                                                                              |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Ändrar clarity bara size/logg?                                  | `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_ri_v2_clarity_on_changes_sizing_only_and_logs`          | Stöder att clarity hör hemma i management/sizing snarare än candidate selection                             |
| Ändrar risk_state action-path eller bara size?                  | `tests/utils/test_decision_scenario_behavior.py::test_decide_risk_state_stress_reduces_size_without_changing_action_path` | Stöder att risk_state är risk/sizing modulation, inte entrymotor                                            |
| Kan adaptive fib override faktiskt flytta block → entry?        | `tests/utils/test_decision_scenario_behavior.py::test_decide_adaptive_htf_override_progression_flips_block_into_entry`    | Stöder att fib-override är en semantiskt känslig permission-brygga                                          |
| Är `confidence.py` direction-bevarande men gate/sizing-känslig? | `tests/utils/test_confidence.py` + `tests/utils/test_decision_edge.py`                                                    | Stöder att confidence bevarar riktning men kan moduleras som gate- eller sizing-brygga                      |
| Ger checked-in `both`-profiler faktisk gate-drift?              | direkt körbar evidens med `tBTCUSD_1h_quality_v2_candidate_scoped*.json`                                                  | Stöder att `data_quality`/`spread` verkligen kan flytta gate-pass, medan `atr`/`volume` främst flyttar size |
| Kan threshold-lagret ensamt flippa samma setup?                 | direkt körbar evidens med RI-zontrösklar i `decision_gates.py`                                                            | Stöder att zone/regime-thresholding är en explicit trade/no-trade-brytare även när probas och confidence hålls fasta |
| Förblir shadow-regime observability advisory?                   | `tests/governance/test_regime_intelligence_cutover_parity.py` och relaterade shadow-observer-tester                       | Stöder att `decision_input=False` hålls i observability-spåret                                              |

### Det viktigaste som fortfarande behöver bevisas bättre

Det som fortfarande är mest värt att isolera i nästa steg är:

1. hur mycket av candidate-drift som kommer från `decision_gates.py` thresholding
2. hur mycket regime-aware calibration i `prob_model.py` faktiskt flyttar outputs relativt legacy-calibration i verkliga RI-/legacy-jämförelser
3. hur stor del av faktisk trade-drift i RI-/legacy-jämförelser som kommer från threshold-lagret jämfört med calibration-lagret när quality hålls konstant

## Föreslagen ablationsordning

För att undvika ännu en “allt på en gång”-situation bör nästa analys/experimentserie vara liten och tydlig.

### Steg A — bevisa vad som är entry vs management

1. **Clarity on/off**

- fråga: ändras bara size/logg, eller ändras faktiskt candidate?

2. **Risk state on/off**

- fråga: påverkar den bara sizing/risk, eller läcker den bakåt in i entrybeslut?

3. **HTF/LTF fib override on/off**

- fråga: är detta ett permission-lager eller en dold entry-aggressionsmotor?

### Steg B — bryt ned `decision_gates.py`

Nästa agent bör gärna skriva en mikro-matris enbart för `decision_gates.py`:

| Delsteg             | Roll idag            | Bör tillhöra                    | Risk   |
| ------------------- | -------------------- | ------------------------------- | ------ |
| EV-filter           | Entry-säkerhet       | Legacy/permission               | låg    |
| Thresholding        | Permission           | RI/permission + legacy boundary | medium |
| Candidate selection | Entry resolution     | Legacy                          | hög    |
| Tie-break           | Context bridge       | Permission/context              | medium |
| Post-fib gates      | Permission/stability | Permission                      | medium |

### Mikromatris — `decision_gates.py`

Filen har två centrala funktioner:

- `select_candidate(...)`
- `apply_post_fib_gates(...)`

Tillsammans utgör de den mest koncentrerade blandzonen mellan legacy-entry och RI-influerad permissioning.

| Del i `decision_gates.py`                      | Vad koden gör                                                | Observerad roll idag                  | Bör främst tillhöra            | Drift-/riskbedömning                                            | Rekommenderad nästa kontroll                                                                |
| ---------------------------------------------- | ------------------------------------------------------------ | ------------------------------------- | ------------------------------ | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Fail-safe på saknade probas                    | Returnerar `NONE` om `probas` saknas/är ogiltiga             | Säkerhetsveto                         | Legacy/permission              | Låg risk; tydlig fail-safe                                      | Behåll som ren safety gate                                                                  |
| EV-beräkning (`ev_long`, `ev_short`, `max_ev`) | Stoppar trade om EV <= 0                                     | Entry-säkerhet                        | Legacy med permission-karaktär | Låg risk; tydligt pre-entry skydd                               | Dokumentera som “entry-safety”, inte RI-logik                                               |
| Event block / risk cap block                   | Stoppar trade vid risk/event conditions                      | Permission/safety                     | Permission                     | Låg risk; korrekt placerat                                      | Bryt eventuellt ut begreppsligt som separat safety-lager i docs                             |
| Regime-baserad long/short-allowance            | `trend_long_only` / `trend_short_only` begränsar riktning    | Context → permission                  | Permission/context             | Medium; kan missläsas som regime-entry                          | Testa fasta probas med växlande regime för att bevisa att detta bara är riktningstillåtelse |
| Bas-threshold (`entry_conf_overall`)           | Sätter default confidence threshold                          | Permission                            | Legacy/permission boundary     | Medium; nära entry men fortfarande gate                         | Dokumentera som canonical gate före candidate resolve                                       |
| ATR-zonval (`low/mid/high`)                    | Väljer zon från ATR + percentiler                            | Volatility context feeding permission | Context → permission           | Medium; behavior-påverkande trots att den inte är regimebaserad | Isolera zonbyte med fasta probas för att se hur thresholds flyttar outcomes                 |
| Zone/regime threshold mapping                  | Väljer regime-specifikt threshold per zon                    | Regime-aware permission               | RI/permission boundary         | Hög analysvikt; här börjar RI flytta beslutsgränser             | Testa threshold-tabellen med fasta inputs och mappa exakt vilka outcomes som ändras         |
| `buy_pass` / `sell_pass`                       | Avgör om respektive sida överlever thresholding              | Permission nära entry                 | Permission                     | Medium; direkt outcome-påverkan                                 | Mät hur stor del av candidate drift som kommer härifrån vs senare steg                      |
| Candidate selection                            | Väljer `LONG`/`SHORT` när en eller båda sidor passerar       | Entry resolution                      | Legacy                         | Hög; detta är tydlig entrylogik                                 | Behandla explicit som legacy-kärna i fortsatt modell                                        |
| Tie-break vid lika probas                      | Använder `last_action` eller regime-bias när p_buy ≈ p_sell  | Context bridge                        | Permission/context             | Medium; liten men semantiskt viktig                             | Testa om tie-break någonsin triggar meningsfullt i riktiga runs                             |
| Confidence gate i `apply_post_fib_gates(...)`  | Kräver att confidence för vald kandidat överstiger threshold | Permission/stability                  | Permission                     | Medium; ytterligare gate nära entry                             | Jämför effekt mot tidigare proba-threshold för att undvika dubbelräkning                    |
| `min_edge`-gate                                | Kräver tillräcklig skillnad mellan buy/sell                  | Entry-säkerhet / permission           | Legacy/permission              | Medium; kan vara bra “no-trade”-mekanism                        | Testa om detta är bättre edge-kandidat än mer proba-tuning                                  |
| Hysteresis-block                               | Kräver flera steg innan action byts                          | Stability filter                      | Permission                     | Medium; starkt beteendepåverkande men inte alpha i sig          | Isolera hur mycket hysteresis skyddar vs försenar bra entries                               |
| Cooldown                                       | Blockerar entry under låsperiod                              | Stability/risk control                | Permission                     | Låg till medium; tydlig anti-chop mekanik                       | Testa som ren no-trade-state mekanism                                                       |

### Samlad bedömning av `decision_gates.py`

Första kodläsningen stödjer följande uppdelning:

- **Tydligt legacy-kärna:**
  - EV-beräkning
  - candidate selection
  - delar av `min_edge`-logiken

- **Tydligt permission/filtering:**
  - confidence thresholds
  - zone/regime threshold mapping
  - hysteresis
  - cooldown
  - event/risk veto

- **Semantiskt känsliga bryggor:**
  - regime-baserad long/short-allowance
  - tie-break via regime / `last_action`

Den viktigaste observationen är att `decision_gates.py` inte ser ut som att RI direkt genererar trades, men filen är absolut ett ställe där RI-liknande signaler kan flytta gränsen för _när_ legacy-entry får passera. Därför bör filen behandlas som den viktigaste blandzonen, inte som ren entrylogik eller ren management.

### Skarpare delkarta — vad i `decision_gates.py` flyttar faktiskt candidate?

Efter närläsning av koden och kontraktstesterna är det användbart att skilja mellan tre olika typer av steg i `decision_gates.py`:

1. steg som **kan skapa eller ändra candidate**
2. steg som **inte ändrar candidate men kan blockera det**
3. steg som **bara förbereder eller flyttar beslutsgränsen**

Detta ger en mycket skarpare bild av var entry faktiskt uppstår.

| Delsteg i `decision_gates.py`                 | Kan skapa/ändra candidate? | Kan bara blockera? | Typisk roll                        | Kommentar                                                                                             |
| --------------------------------------------- | -------------------------- | ------------------ | ---------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Fail-safe på null/ogiltiga probas             | Nej                        | Ja                 | Safety veto                        | Stoppar hela flödet innan någon candidate finns                                                       |
| EV-beräkning / `EV_NEG`                       | Nej                        | Ja                 | Entry-safety                       | Stoppar setup med negativ edge men väljer aldrig riktning                                             |
| Event block / risk cap block                  | Nej                        | Ja                 | Safety / permission                | Hård veto-yta före candidate                                                                          |
| `trend_long_only` / `trend_short_only`        | Indirekt                   | Ja                 | Context → permission               | Ändrar inte proba-order, men kan eliminera ena sidan och därmed påverka vilken candidate som återstår |
| `entry_conf_overall` + threshold-bas          | Nej                        | Nej                | Boundary setup                     | Förbereder gränsen; i sig ingen candidate-effekt                                                      |
| ATR-zonval                                    | Nej                        | Nej                | Context setup                      | Flyttar vilken threshold-tabell som ska gälla                                                         |
| Zone/regime threshold mapping                 | Indirekt                   | Ja                 | Permission boundary                | Ändrar inte kandidat direkt, men flyttar vilka sidor som överlever till candidate-valet               |
| `buy_pass` / `sell_pass`                      | Indirekt                   | Ja                 | Permission outcome                 | Här avgörs vilka riktningar som fortfarande är kandidater                                             |
| Candidate selection                           | Ja                         | Nej                | Entry resolution                   | Det tydligaste stället där `LONG` eller `SHORT` faktiskt väljs                                        |
| Tie-break (`last_action` / regime-bias)       | Ja                         | Nej                | Context-sensitive entry resolution | Kan välja riktning när probas är lika; liten volym men semantiskt viktig                              |
| Confidence gate i `apply_post_fib_gates(...)` | Nej                        | Ja                 | Post-candidate permission          | Kandidaten finns redan; steget kan bara blockera                                                      |
| `min_edge`                                    | Nej                        | Ja                 | Post-candidate entry-safety        | Bevarar eller stoppar vald candidate; skapar ingen ny                                                 |
| Hysteresis                                    | Nej                        | Ja                 | Stability filter                   | Kan bara hålla kvar NONE/pausa byte, inte välja annan riktning                                        |
| Cooldown                                      | Nej                        | Ja                 | No-trade filter                    | Ren blockering efter att candidate redan är känt                                                      |

### Praktisk split — candidate-moving vs candidate-preserving

I praktiken ser `decision_gates.py` ut att ha följande kärnsplit:

- **Candidate-moving steg**
  - candidate selection
  - tie-break
  - indirekt: regime-baserad allowance + threshold-pass/fail eftersom de bestämmer vilka kandidater som över huvud taget får vara kvar i urvalet

- **Candidate-preserving men blockerande steg**
  - EV-gate
  - event/risk veto
  - confidence gate
  - `min_edge`
  - hysteresis
  - cooldown

- **Boundary-forming steg**
  - bas-threshold
  - ATR-zonval
  - zone/regime threshold mapping

Detta är viktigt därför att det visar att mycket av det som först ser ut som “entrylogik” i själva verket bara är **candidate-preserving blockering**. Den verkliga entry-resolutionen är betydligt smalare än filens totala yta antyder.

### Tydligare slutsats om `decision_gates.py`

Den skarpare läsningen pekar på följande:

- **Legacy-entry-kärnan i filen är smalare än man först tror**
  - candidate selection
  - tie-break

- **Den större delen av filen är egentligen permission/safety/boundary management**
  - EV
  - thresholds
  - buy/sell pass
  - confidence
  - edge
  - hysteresis
  - cooldown

- **De mest känsliga RI-adjacent bryggorna är inte där candidate väljs, utan där beslutsgränsen formas**
  - regime-baserad allowance
  - zone/regime threshold mapping
  - threshold-pass/fail

Det betyder att om vi vill förstå om RI håller på att bli entrymotor, bör vi inte främst stirra på `candidate selection`-raden i sig, utan på **vilka boundary-steg som avgör vilka kandidater som ens når dit**.

### Befintlig evidens som stödjer denna split

De nuvarande testerna stödjer redan delar av denna uppdelning:

- `tests/utils/test_decision_gates_contract.py::test_select_candidate_tie_handling_contract`
  - stödjer att tie-break är ett verkligt candidate-moving-steg
- `tests/utils/test_decision_gates_contract.py::test_select_candidate_fail_safe_and_blockers`
  - stödjer att fail-safe, event-block och risk-cap är rena blockerare
- `tests/utils/test_decision_gates_contract.py::test_apply_post_fib_gates_hysteresis_blocks_and_increments_state`
  - stödjer att hysteresis är candidate-preserving blockering
- `tests/utils/test_decision_gates_contract.py::test_apply_post_fib_gates_cooldown_blocks_and_decrements_state`
  - stödjer att cooldown är ren post-candidate blockering
- `tests/utils/test_decision_edge.py::test_min_edge_requirement`
  - stödjer att `min_edge` blockerar ett redan möjligt entry men inte skapar ett nytt

### Mikromatris — `decision_sizing.py`

Första kodläsningen visar att `decision_sizing.py` i praktiken är en enda koncentrerad management-funktion:

- `apply_sizing(...)`

Det mest intressanta här är inte om filen “skapar entries”, utan hur många olika lager av risk/context/RI som får påverka **storleken efter att kandidat redan valts**.

| Del i `decision_sizing.py`                               | Vad koden gör                                             | Observerad roll idag          | Bör främst tillhöra        | Drift-/riskbedömning                                                  | Rekommenderad nästa kontroll                                                         |
| -------------------------------------------------------- | --------------------------------------------------------- | ----------------------------- | -------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `confidence_gate` från vald kandidat                     | Hämtar buy/sell-confidence utifrån redan vald `candidate` | Bridge från entry till sizing | Legacy → management bridge | Medium; beroende av upstream-candidate men ändrar inte kandidat själv | Bekräfta med test att filen aldrig byter action, bara size                           |
| `risk_map` → `size_base`                                 | Mappar confidence till basstorlek                         | Klassisk sizing               | Legacy/management          | Låg; tydlig sizing-kärna                                              | Dokumentera som canonical pre-RI size base                                           |
| `size_scale` via `buy_scaled` / `sell_scaled`            | Skalar size med kalibrerad confidence om sådan finns      | Confidence-aware sizing       | Management                 | Medium; kan misstolkas som extra entryvikt                            | Testa om den bara förändrar storlek och aldrig gate:ar bort trades                   |
| `regime_size_multipliers`                                | Multiplicerar size beroende på regime                     | Regime-aware management       | RI/management              | Låg till medium; naturlig RI-yta                                      | Isolera multipliers med fast candidate och confidence                                |
| `htf_regime_size_multipliers`                            | Läser HTF-regime och modulerar size                       | HTF-aware management          | RI/management              | Låg till medium; tydligt secondary-context-beteende                   | Bekräfta att detta inte läcker bakåt till candidate-path                             |
| `volatility_sizing`                                      | Minskar size i hög ATR-volatilitet                        | Volatility risk control       | Management                 | Låg; ren riskkontroll                                                 | Dokumentera som no-trade-light/risk-lager snarare än alpha                           |
| `risk_state_mult` från `risk_state.py`                   | Modulerar storlek via drawdown/transition-state           | RI risk modulation            | RI/management              | Låg; stark kandidat för ren RI-kärna                                  | Kör on/off-test och bevisa att endast size/state_out ändras                          |
| `min_combined_multiplier`                                | Sätter golv för total multiplikator                       | Safety floor                  | Management/safety          | Låg; skyddar mot nollning/överstraffning                              | Verifiera att golvet är risk-policy, inte dold aggressionsregel                      |
| `clarity_multiplier` från `clarity.py`                   | Applicerar clarity-score på size när RI v2 är aktiv       | RI clarity-based sizing       | RI/management              | Medium; rik signal men fortfarande size-only i denna fil              | Kör clarity on/off och diffa candidate vs size/logg                                  |
| `authority_mode` / `authority_mode_source` i `state_out` | Sparar authority metadata                                 | Observability/traceability    | Observability              | Låg; ingen direkt beslutskraft här                                    | Behåll som audit-spår, inte beslutsmotor                                             |
| `state_out`-telemetri                                    | Skriver ut delmultipliers, clarity och risk_state-data    | Observability                 | Observability              | Låg; mycket värdefullt för ablation                                   | Använd som primär evidensyta i framtida rolltester                                   |
| Regime transition tracking                               | Uppdaterar `last_regime` och `bars_since_regime_change`   | State support för risk_state  | Management/support state   | Medium; liten men viktigt stöd till risk_state                        | Verifiera att detta bara stödjer sizing-logik och inte återkopplas till entry i smyg |

### Samlad bedömning av `decision_sizing.py`

Första kodläsningen stödjer följande uppdelning:

- **Tydligt management-kärna:**
  - `risk_map` → `size_base`
  - regime/HTF multipliers
  - volatility sizing
  - `risk_state_mult`
  - `clarity_multiplier`

- **Tydligt observability / audit-stöd:**
  - `authority_mode`
  - `authority_mode_source`
  - `state_out`-telemetri

- **Semantiskt känsliga bryggor:**
  - `confidence_gate` från redan vald kandidat
  - `size_scale` via scaled confidence
  - regime transition tracking som matar risk_state-stöd

Den viktigaste observationen är att `decision_sizing.py` inte ser ut att vara någon entrymotor alls. Tvärtom ser den ut som den starkaste nuvarande kandidaten för var RI/R1 faktiskt kan få vara “sig själv” utan att bli en dold ersättare för legacy-entry. Om vi vill återföra RI till management/filter-lagret är detta sannolikt ett av de renaste kärnområdena att bygga vidare från.

### Mikromatris — `decision_fib_gating.py` + helpers

Första kodläsningen visar att `decision_fib_gating.py` själv främst är en orkestrerare, medan den verkliga policytyngden ligger i:

- `prepare_override_context(...)`
- `apply_htf_fib_gate(...)`
- `apply_ltf_fib_gate(...)`

Det betyder att denna yta bör läsas som **ett sammanhållet permission-lager**, inte som en ensam wrapper-fil.

| Del i fib-gating-flödet                               | Vad koden gör                                                                | Observerad roll idag                | Bör främst tillhöra                | Drift-/riskbedömning                                       | Rekommenderad nästa kontroll                                                            |
| ----------------------------------------------------- | ---------------------------------------------------------------------------- | ----------------------------------- | ---------------------------------- | ---------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `apply_fib_gating(...)` orchestration                 | Bygger override-context, kör HTF-gate, sedan LTF-gate och sammanfattar debug | Gate orchestration                  | Permission/orchestration           | Låg; främst ordningskontroll                               | Dokumentera tydligt att wrappern inte bär huvudpolicyn själv                            |
| `prepare_override_context(...)`                       | Bygger confidence/history/adaptiv threshold för eventuell override           | Override-prep / adaptive permission | RI/permission                      | Medium till hög; här kan filter bli dold aggressionsmotor  | Testa fasta confidence-serier per regime och mappa hur `effective_threshold` rör sig    |
| Override history (`buy_history` / `sell_history`)     | Sparar historik i `override_state` för percentilbaserad threshold            | Stateful permission support         | Permission/support state           | Medium; statefulness gör beteendet svårare att läsa        | Verifiera om historiken bara stabiliserar eller faktiskt ökar trade-frekvens aggressivt |
| Adaptive threshold via percentil + regime-multipliers | Gör override-threshold dynamisk efter historik och regime                    | Regime-aware permission             | RI/permission boundary             | Hög; tydlig plats där RI kan flytta entry-gränser indirekt | Kör ablation med adaptiv av/på och jämför override-rate                                 |
| HTF gate: context availability / missing-policy       | Blockerar eller passerar beroende på om HTF-context finns                    | Safety + permission                 | Permission/safety                  | Medium; viktig fail-open/fail-closed-policy                | Dokumentera separat vilka lägen som är `pass` vs `block`                                |
| HTF gate: target match / level checks                 | Kräver att pris ligger nära tillåtna HTF-nivåer eller inte bryter nivågräns  | Structural permission               | Permission                         | Medium; tydligt “rätt-att-handla”-lager                    | Isolera target-match vs level-block i analysmatris                                      |
| HTF override (`try_override_htf_block`)               | Tillåter LTF-confidence att häva HTF-block under vissa villkor               | Override bridge                     | Permission med entry-adjacent risk | Hög; här kan filter slå över i entry-aggression            | Testa override-rate, win-rate och om override främst räddar bra eller dåliga trades     |
| `override_confidence` range                           | Tillåter override inom explicit confidence-intervall                         | Fixed override policy               | Permission                         | Medium; enklare och mer läsbar än adaptive path            | Jämför mot adaptive override för att se vilken som driver mest drift                    |
| LTF gate: context availability / missing-policy       | Blockerar eller passerar beroende på om LTF-context finns                    | Safety + permission                 | Permission/safety                  | Medium; samma fail-policyfråga som HTF                     | Säkerställ att HTF och LTF använder konsekvent semantik                                 |
| LTF gate: level checks                                | Stoppar LONG ovan maxnivå / SHORT under minnivå                              | Structural veto                     | Permission                         | Låg till medium; tydligt veto-lager                        | Behandla som canonical permission-regel i rollkartan                                    |
| `fib_gate_summary` / debug payloads                   | Samlar HTF/LTF-debug i `state_out`                                           | Observability/audit                 | Observability                      | Låg; mycket värdefullt för beviskedjan                     | Använd som primär evidensyta i framtida override-ablationer                             |

### Samlad bedömning av `decision_fib_gating.py` + helpers

Första kodläsningen stödjer följande uppdelning:

- **Tydligt permission-kärna:**
  - HTF gate
  - LTF gate
  - structural veto via level checks
  - missing-policy-hantering

- **Tydligt observability / audit-stöd:**
  - `ltf_override_debug`
  - `htf_fib_entry_debug`
  - `ltf_fib_entry_debug`
  - `fib_gate_summary`

- **Semantiskt känsliga bryggor:**
  - adaptive override-threshold
  - regime-multipliers i override-path
  - `try_override_htf_block(...)`

Den viktigaste observationen är att fib-gatingytan inte ser ut som en ren alpha-motor, utan som ett avancerat permission-lager med en potentiellt mycket viktig override-mekanism. Det gör området strategiskt intressant: om RI/R1 ska vara filter/management snarare än entrymotor är detta sannolikt rätt plats att leta edge i form av bättre veto, bättre confirmation och bättre no-trade-state — men också rätt plats att jaga ansvarsglidning om override-logiken blivit för aggressiv.

### Steg C — först därefter parameterpolicy

Först när ansvaren är tydligare bör vi börja märka moduler som:

- **behåll**
- **förenkla**
- **flytta ansvar**
- **stäng av**

## Rekommenderade frågor för nästa session

1. Vilka moduler vill vi uttryckligen definiera som **R1/RI-kärna**?
2. Vilka moduler ska uttryckligen definieras som **legacy-kärna**?
3. Vilka moduler är tillåtna att påverka **candidate selection**?
4. Vilka moduler får endast påverka:

- permission
- size
- exits
- observability

5. Vilket minimum-set av moduler ger mest “ren” RI-identitet utan att bli en ny entrymotor?

## Enradig slutsats

Legacy ser fortfarande ut att vara den verkliga entrymotorn, medan RI/R1/intelligence främst lever i context, filtering, sizing och observability; nästa edge-arbete bör därför fokusera på att förtydliga och testa dessa roller snarare än att direkt optimera fler parametrar.
