# RI vs legacy — rollkarta som två strategy families

Datum: 2026-03-20
Branch: `feature/ri-legacy-role-map-2026-03-19`
Status: arbetsdokument / analysunderlag / ingen runtime-ändring

## Syfte

Detta dokument reframar RI och legacy utifrån den kod och evidens som nu finns i repot.

Den tidigare läsningen — att **legacy** är den egentliga strategin och att **RI** främst är ett context-/filter-/management-lager ovanpå — är för svag givet nuvarande repo-kontrakt och kodvägar.

Arbetsmodellen i detta dokument är därför i stället:

- `strategy_family ∈ {"legacy", "ri"}`
- **legacy** och **RI** ska behandlas som två **separata strategy families**
- båda familjerna realiseras genom samma övergripande runtime-orkestrering (`evaluate -> decide`)
- men de använder olika **family-signaturer**, olika **authority/calibration-paths** och olika **threshold/gating/cadence/sizing-surfaces**

Detta dokument beskriver alltså **inte** två fysiskt duplicerade runtime-motorer. Det beskriver två fullständiga strategiytor som körs genom samma orkestreringskedja men divergerar på family-kritiska sömmar.

## Repo-kodens nuvarande family-premiss

Repo-koden uttrycker redan en explicit family-modell:

- `src/core/strategy/family_registry.py`
  - definierar `legacy` och `ri` som de enda tillåtna strategy families
  - förbjuder hybridlägen där legacy försöker bära RI-signatur eller där RI saknar canonical RI-kluster
- `tests/core/strategy/test_families.py`
  - bekräftar att RI kräver ett sammanhängande kluster av authority, ATR-period, gates och thresholds
  - bekräftar att legacy med `regime_module` eller RI-signaturmarkörer ska avvisas

Det gör följande formulering legitim och nödvändig:

> **RI är en separat strategy family, inte ett lager ovanpå legacy.**

## Delad orkestrering, två fullständiga strategiytor

Den kodmässiga huvudkedjan är delad:

1. `src/core/strategy/evaluate.py`
2. `src/core/strategy/prob_model.py`
3. `src/core/strategy/confidence.py`
4. `src/core/strategy/decision.py`
   - `decision_gates.py`
   - `decision_fib_gating.py`
   - `decision_sizing.py`
5. exit-/livscykelytor, inklusive `src/core/backtest/htf_exit_engine.py`

Men familjebeteendet är inte delat bara för att orkestreringen är det. Family-separationen realiseras i de parametrar, authority-val och beslutsytor som matas genom denna kedja.

Det mest korrekta sättet att läsa systemet är därför:

- **en delad orkestreringspipeline**
- **två kompletta strategy families** ovanpå den

## Kodförankrad evidensbas

Följande ytor bär huvudevidensen för family-spliten:

- `src/core/strategy/family_registry.py`
  - legacy- och RI-definitioner
- `tests/core/strategy/test_families.py`
  - canonical RI-signatur och hybridförbud
- `src/core/strategy/evaluate.py`
  - authority-val, regime-detektion, family-konditionerad confidence-applicering, vidarekoppling till `decide(...)`
- `src/core/strategy/prob_model.py`
  - default-kalibrering och `calibration_by_regime`
- `src/core/strategy/decision_gates.py`
  - thresholding, candidate selection, hysteresis, cooldown, `min_edge`
- `src/core/strategy/decision_fib_gating.py`
  - HTF/LTF-gating, override-prep och survival-logik
- `src/core/strategy/decision_sizing.py`
  - regime-multipliers, HTF-multipliers, `risk_state`, `clarity`

Den starkaste evidensen för family-separation i denna artefakt ligger **uppströms** i authority, calibration, threshold, cadence och sizing. Exit-lagret behandlas här som del av den fulla strategilivscykeln, men inte som den primära bevisytan för family-spliten.

## LEGACY PIPELINE

Legacy ska läsas som en **full strategy family**, inte bara som en rå entry-motor.

### Steg 1 — family-signatur och config-kontrakt

- `strategy_family = "legacy"`
- authority får **inte** vara `regime_module`
- legacy får **inte** bära RI:s canonical signaturmarkörer

Det betyder att legacy är en sammanhängande family-surface, inte bara ett restläge när RI är avstängt.

### Steg 2 — features och authoritative context

- `evaluate.py` bygger features via `extract_features_live(...)` eller `extract_features_backtest(...)`
- authoritative regime går via legacy-path när authority inte är `regime_module`
- detta context är en del av legacy-pipelinen, inte ett externt overlay-lager

### Steg 3 — probability generation och kalibrering

- `predict_proba_for(...)` i `prob_model.py` hämtar modellmetadata
- samma funktion bygger `{buy, sell, hold}`-ytan för båda families
- i legacy-läget är default-kalibrering den canonical family-basen

Legacy har alltså en egen probability surface även om den kodmässigt produceras av samma modul som RI använder.

### Steg 4 — thresholding och candidate resolution

- `select_candidate(...)` i `decision_gates.py`
- EV-kontroll
- risk/event-veto
- zone/threshold-val
- candidate selection och tie-break

Detta är inte “bara gating”. Det är en del av legacy-familjens fulla survival-pipeline.

### Steg 5 — structural gating och survival

- `apply_fib_gating(...)`
- HTF-block
- LTF-gating
- override-policy

Fib-lagret är en del av hur legacy-familjen överlever från kandidat till faktisk trade, inte bara kosmetisk filtrering efteråt.

### Steg 6 — cadence och post-gates

- `apply_post_fib_gates(...)`
- confidence-threshold efter kandidat
- `min_edge`
- hysteresis
- cooldown

I denna analys läses cadence och post-gates som family-konstitutiva för legacy, inte som löst hängande stabiliserare utanför strategin.

### Steg 7 — sizing

- `apply_sizing(...)`
- `risk_map`
- confidence-driven size-base
- volatilitetsskalning

Sizing är del av legacy-familjens kompletta strategiuttryck, även när RI-specifika multipliers inte används.

### Steg 8 — exits och livscykel

- exit-livscykeln fortsätter via exit-/backtestytor, inklusive `htf_exit_engine.py`

I denna analys används exits främst som del av den fulla strategilivscykeln. Den starkaste legacy-vs-RI-separationen i evidensen ligger dock tidigare i kedjan.

## RI PIPELINE

RI ska också läsas som en **full strategy family**, inte som ett sekundärt lager ovanpå legacy.

### Steg 1 — family-signatur och config-kontrakt

Canonical RI kräver enligt `family_registry.py` och `test_families.py`:

- `strategy_family = "ri"`
- `multi_timeframe.regime_intelligence.authority_mode = regime_module`
- `thresholds.signal_adaptation.atr_period = 14`
- `gates.hysteresis_steps = 3`
- `gates.cooldown_bars = 2`
- canonical RI-threshold-kluster

Detta är inte en liten overlay-konfiguration. Det är en explicit family-signatur.

### Steg 2 — features och authoritative context

- `evaluate.py` väljer authority-path
- när authority är `regime_module` blir RI-pathen authoritative för regime-inputen
- family-spliten börjar därför redan innan sannolikheter och gates används fullt ut

### Steg 3 — probability generation och regime-aware calibration

- RI använder samma `predict_proba_for(...)`
- men när regime-aware kalibrering aktiveras används en annan calibration-branch
- det kan flytta eller vända kandidatunderlaget innan senare gates alls får säga sitt

Detta gör RI:s probability surface family-specifik trots att inferensmotorn delas kodmässigt.

### Steg 4 — RI-threshold surface

- RI kräver sitt canonical threshold-kluster
- samma proba/confidence kan därför passera i legacy men blockeras i RI, eller tvärtom

Threshold-surface är därmed inte bara “finjustering”. Den är en del av RI-familjens kärnidentitet.

### Steg 5 — RI survival-pipeline via structural gating

- `decision_fib_gating.py` används även för RI
- override-prep, HTF-/LTF-gating och adaptiva trösklar blir del av RI-familjens survival-logik

Här finns en viktig family-poäng: RI är inte bara en annan probability-yta. RI kräver också en sammanhängande passage genom en annan survival-surface.

### Steg 6 — RI cadence

- canonical RI-gates är `3/2`
- det ger en annan bytesprofil än legacy
- i evidensen syns detta som skillnader i när giltiga kandidatbyten får realiseras

Cadence är därför en family-formgivare i RI, inte bara en sen stabiliseringsdetalj.

### Steg 7 — RI sizing

- `decision_sizing.py` aktiverar family-känsliga ytor via regime multipliers, HTF-multipliers, `risk_state` och `clarity`
- RI-v2 clarity är uttryckligen modellerad som `sizing_only`
- `risk_state` och clarity ändrar inte nödvändigtvis action-path, men de är fortfarande del av RI-familjens fulla strategiuttryck

Detta betyder inte att RI “bara är sizing”. Det betyder att sizing-surface är en family-bärande del av RI-pipelinen.

### Steg 8 — exits och livscykel

- även RI måste fullbordas genom exit-/livscykelytorna
- den aktuella artefaktens starkaste bevisläge för RI-family-split ligger dock inte i exit-wiringen, utan tidigare i authority/calibration/threshold/cadence/sizing

## Divergenspunkter mellan families

| Lager                   | Legacy family                               | RI family                                   | Varför detta är family-separerande                   |
| ----------------------- | ------------------------------------------- | ------------------------------------------- | ---------------------------------------------------- |
| **Family-signatur**     | `strategy_family=legacy`, ingen RI-signatur | `strategy_family=ri` + canonical RI-kluster | Family-registry förbjuder hybrider                   |
| **Authority**           | legacy authority-path                       | `regime_module` authoritative path          | avgör vilken regime-input som är sann                |
| **Probability surface** | default family-calibration                  | regime-aware calibration-branch             | kan ändra kandidatunderlaget före gating             |
| **Threshold surface**   | legacy-cluster                              | canonical RI-thresholds                     | samma setup kan ge olika trade/no-trade              |
| **Cadence**             | legacy-gates                                | RI `3/2` cadence                            | samma kandidatbyte kan släppas eller hållas tillbaka |
| **Structural survival** | fib-gating på legacy-surface                | fib-gating på RI-surface                    | överlevnadsvillkoren följer family-ytan              |
| **Sizing**              | legacy risk-map + basmultipliers            | RI regime/HTF/clarity/risk_state-surface    | full family skiljer sig även efter candidate         |
| **Exits/lifecycle**     | full strategi kräver exits                  | full strategi kräver exits                  | starkaste splitbeviset ligger dock uppströms         |

## Family-konditionerade moduler

Följande moduler beter sig inte som “RI-moduler” eller “legacy-moduler” i isolation. De beter sig som **delade moduler med family-konditionerad semantik**.

| Modul                    | Gemensam eller family-konditionerad?       | Vad som skiftar mellan families                                                         |
| ------------------------ | ------------------------------------------ | --------------------------------------------------------------------------------------- |
| `family_registry.py`     | family-definierande                        | avgör vad som ens får kallas legacy respektive RI                                       |
| `evaluate.py`            | delad orkestrering, family-konditionerad   | authority-val, regime-input, confidence-applicering och väg in i `decide(...)`          |
| `prob_model.py`          | delad inferensmotor, family-konditionerad  | default-kalibrering vs regime-aware calibration                                         |
| `confidence.py`          | delad brygga, family-konditionerad         | om quality påverkar gate+sizing eller sizing-only i family-surface                      |
| `decision_gates.py`      | delad gate-motor, family-konditionerad     | threshold-cluster, zone-surface, candidate survival, cadence                            |
| `decision_fib_gating.py` | delad survival-motor, family-konditionerad | override-thresholds, HTF/LTF-permission och structural survival                         |
| `decision_sizing.py`     | delad sizing-motor, family-konditionerad   | regime multipliers, HTF multipliers, `risk_state`, `clarity`                            |
| `htf_exit_engine.py`     | del av full livscykel                      | evidensen här är svagare för family-split, så exits kvalificeras snarare än överbevisas |

## Projekt- och rollkarta

Om hela projektet läses på en högre nivå blir rollerna tydligare om de grupperas i fyra lager snarare än i enskilda filer.

### 1. Family- och kontraktslager

Detta lagers jobb är att avgöra **vilken strategi-family som över huvud taget får existera**.

- `src/core/strategy/family_registry.py`
- `tests/core/strategy/test_families.py`

Roll:

- definierar `legacy` respektive `ri`
- förbjuder hybrider
- låser RI till canonical authority-/threshold-/cadence-signatur

Detta är projektets tydligaste **kontraktsroll**.

### 2. Delad runtime-orkestrering

Detta lagers jobb är att bära den gemensamma exekveringskedjan, oavsett family.

- `src/core/strategy/evaluate.py`
- `src/core/strategy/decision.py`

Roll:

- bygger features
- väljer authority-path
- kopplar probability, confidence och decision-funktionerna
- driver ordningen mellan candidate, gating, cadence och sizing

Detta är projektets tydligaste **backbone-roll**.

### 3. Family-konditionerade beslutsytor

Detta lagers jobb är att ge samma backbone **olika strategibeteende beroende på family**.

- `src/core/strategy/prob_model.py`
- `src/core/strategy/confidence.py`
- `src/core/strategy/decision_gates.py`
- `src/core/strategy/decision_fib_gating.py`
- `src/core/strategy/decision_sizing.py`

Roll:

- formar probability surface
- formar threshold surface
- formar survival / gating
- formar cadence
- formar sizing surface

Detta är projektets viktigaste **family-differentierande roll**.

### 4. Livscykel, exits och observability

Detta lagers jobb är att fullborda strategin efter att family-ytan redan valts.

- `src/core/backtest/htf_exit_engine.py`
- shadow-/observability-spår som stöder analys och uppföljning

Roll:

- fullbordar position lifecycle
- gör family-beteendet granskbart
- stödjer analys utan att i sig bära huvudbeviset för family-spliten

Detta är projektets tydligaste **livscykel- och granskningsroll**.

### Praktisk projektläsning

Om vi fortsätter med projektet utan att fastna i diagram bör den praktiska läsordningen nu vara:

1. **Vilken family tillåts?**
2. **Vilken delad backbone kör?**
3. **Vilka family-konditionerade ytor formar utfallet?**
4. **Hur fullbordas strategin i sizing, exits och observability?**

Det gör att projektet inte längre behöver beskrivas som “legacy plus RI-lager”, utan som:

> **ett gemensamt strategiramverk med två separata strategy families och tydligt delade roller mellan kontrakt, orkestrering, family-ytor och livscykel.**

### Kompakt ansvarsmatris för projektet

| Lager / roll                      | Primärt ansvar                                       | Huvudmoduler                                   | Delad eller family-konditionerad? | Praktisk nyckelfråga                                                                        |
| --------------------------------- | ---------------------------------------------------- | ---------------------------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------- |
| **Family- och kontraktslager**    | Definiera vilka strategy families som är giltiga     | `family_registry.py`, `test_families.py`       | **Family-definierande**           | Vilken family är tillåten, och är configen hybridfri?                                       |
| **Backbone / orkestrering**       | Bära den gemensamma runtime-kedjan                   | `evaluate.py`, `decision.py`                   | **Delad**                         | I vilken ordning kopplas features, authority, proba, confidence och beslut ihop?            |
| **Probability surface**           | Forma sannolikhetsunderlaget                         | `prob_model.py`                                | **Family-konditionerad**          | Är det default-kalibrering eller regime-aware calibration som styr ytan?                    |
| **Threshold / candidate surface** | Avgöra om kandidat överlever till tradebar action    | `decision_gates.py`                            | **Family-konditionerad**          | Är det threshold-klustret eller cadence/post-gates som stoppar eller öppnar setupet?        |
| **Structural survival**           | Tvinga passage genom HTF/LTF-veto och override-logik | `decision_fib_gating.py`                       | **Family-konditionerad**          | Är detta ett legitimt survival-lager eller finns ansvarsglidning mot dold entry-aggression? |
| **Sizing surface**                | Översätta kandidat till faktisk riskexponering       | `decision_sizing.py`, delar av `confidence.py` | **Family-konditionerad**          | Är drift i första hand en sizing-fråga eller började den tidigare i family-ytan?            |
| **Livscykel / exits**             | Fullborda trade efter vald family-surface            | `htf_exit_engine.py`                           | **Delvis delad**                  | Hur mycket av family-skillnaden lever faktiskt vidare in i exit-lagret?                     |
| **Observability / audit**         | Göra family-beteendet spårbart och granskbart        | shadow-/observability-spår                     | **Delad stödroll**                | Kan vi bevisa family-drift utan att injicera nytt runtime-beteende?                         |

Denna matris är avsedd som **arbetsyta för fortsatt projektstyrning**. Den svarar inte bara på vad modulerna gör, utan också på **vilken typ av fråga** varje lager bör bära i fortsatt analys eller implementation.

## Prioriterad fortsatt arbetsordning

Om projektet fortsätter härifrån bör arbetet inte drivas som “allting samtidigt”, utan i en fast ordning från högst semantisk risk till lägst.

### Prioritet 1 — skydda family-kontraktet

Det första som alltid bör hållas stabilt är family- och kontraktslagret.

Primära ytor:

- `family_registry.py`
- `test_families.py`

Frågor att bära här:

- Är legacy- och RI-signaturerna fortfarande tydligt separerade?
- Har någon hybridglidning uppstått i config eller testantaganden?
- Har family-begreppet börjat tunnas ut i docs eller implementation?

Praktisk regel:

> **Ingen senare analys eller implementation bör accepteras om den först gör family-kontraktet otydligt.**

### Prioritet 2 — håll backbone tunn och tydlig

Det andra som bör skyddas är den delade runtime-orkestreringen.

Primära ytor:

- `evaluate.py`
- `decision.py`

Frågor att bära här:

- Är ordningen mellan features, authority, proba, confidence och beslut fortsatt tydlig?
- Har backbone börjat bära policy som egentligen hör hemma i family-ytorna?
- Går det fortfarande att peka ut var family-separationen faktiskt uppstår?

Praktisk regel:

> **Backbone ska orkestrera, inte smyga in ny family-policy.**

### Prioritet 3 — analysera family-drift där den faktiskt uppstår

Det tredje arbetet bör ligga i de ytor där evidensen redan visar att family-spliten faktiskt formas.

Primära ytor:

- `prob_model.py`
- `decision_gates.py`
- `decision_fib_gating.py`
- `decision_sizing.py`

Föreslagen intern ordning:

1. **Probability surface**

- authority + calibration

2. **Threshold / candidate surface**

- threshold-kluster, candidate survival, cadence

3. **Structural survival**

- HTF/LTF-veto, override-logik

4. **Sizing surface**

- regime-/HTF-multipliers, `risk_state`, `clarity`

Praktisk regel:

> **Om drift syns tidigt i family-ytan ska den inte förklaras bort som ett sent sizing- eller exitfenomen.**

### Prioritet 4 — behandla exits som viktig men senare livscykelyta

Exit-lagret är viktigt, men bör inte vara första platsen där family-frågan avgörs.

Primär yta:

- `htf_exit_engine.py`

Frågor att bära här:

- Vilken del av skillnaden mellan families lever faktiskt vidare in i exit-lagret?
- Vad är verklig family-drift och vad är allmän livscykellogik?

Praktisk regel:

> **Exits ska användas för att fullborda family-analysen, inte för att ersätta tidigare family-bevis.**

### Prioritet 5 — använd observability som verifieringsyta, inte som strategi

Observability ska bära bevis, inte ny policy.

Primära ytor:

- shadow-/observability-spår

Frågor att bära här:

- Kan vi spåra family-drift utan att injicera nytt runtime-beteende?
- Har analysbeviset god täckning över authority, probability, gating, cadence och sizing?

Praktisk regel:

> **Observability ska göra skillnaden synlig, inte skapa skillnaden.**

### Rekommenderad arbetssekvens för nästa fas

Om arbetet fortsätter i ännu en fas bör sekvensen vara:

1. säkra family-kontraktet
2. bekräfta att backbone fortfarande är ren orkestrering
3. analysera probability- och threshold-surface
4. analysera structural survival och sizing
5. först därefter gå vidare till exits och bredare uppföljning

Detta minskar risken att projektet åter glider tillbaka till ett otydligt språk där legacy antas vara “huvudstrategin” och RI ett sent lager ovanpå.

## Riskzoner för fortsatt implementation

Om arbetet senare går från analys till implementation finns några särskilt känsliga zoner där family-gränser lätt kan bli otydliga igen.

### Riskzon 1 — hybridglidning i family-kontraktet

Den första risken är att `legacy` och `ri` börjar blandas i namn, config eller testlogik utan att det sägs rakt ut.

Typiska varningssignaler:

- legacy-config som börjar bära RI-signaturmarkörer
- RI-config som tappar canonical authority-/threshold-/cadence-kluster
- docs eller tester som börjar tala om “nästan-RI legacy” eller “legacy med lite RI på toppen”

Varför zonen är farlig:

- den upplöser hela family-begreppet
- den gör senare drift omöjlig att tolka rent

### Riskzon 2 — policy läcker in i backbone

Den andra risken är att `evaluate.py` eller `decision.py` börjar bära family-policy som egentligen borde ligga i family-ytorna.

Typiska varningssignaler:

- ny family-specifik logik göms i ordningsstyrning eller routing
- backbone börjar fatta policybeslut i stället för att bara orkestrera
- det blir svårt att peka ut om drift uppstår i authority, calibration, thresholds eller cadence

Varför zonen är farlig:

- det suddar ut separationen mellan ramverk och strategi
- det gör framtida refaktorering betydligt farligare än nödvändigt

### Riskzon 3 — tidig family-drift feltolkas som sen effekt

Den tredje risken är att drift som börjar i authority, calibration eller threshold surface förklaras bort som ett senare sizing- eller exitfenomen.

Typiska varningssignaler:

- diskussioner som hoppar direkt till `risk_state`, `clarity` eller exits
- tuning av size/exits innan probability- och threshold-surface är förstådd
- buggrapporter där candidate-drift och size-drift blandas ihop

Varför zonen är farlig:

- den leder analysen till fel lager
- den riskerar att skapa kosmetiska fixar på fel ställe

### Riskzon 4 — override-logik börjar uppträda som dold entrymotor

Den fjärde risken sitter i structural survival-lagret, särskilt där override-logik kan börja fungera som dold aggressionsreglering i stället för legitim survival-policy.

Nuvarande kod- och testläsning skärper bilden:

- `decision.py` väljer kandidat före fib-gating, så override byter inte riktning utan kan bara rädda eller stoppa en redan vald kandidat.
- `tests/utils/test_decision.py::test_htf_override_preserves_debug_payload_and_history` visar en hög-confidence-override där HTF-block släpper igenom en redan vald LONG utan att hoppa över senare gates.
- `tests/utils/test_decision_scenario_behavior.py::test_decide_adaptive_htf_override_progression_flips_block_into_entry` visar samtidigt att adaptiv threshold-sänkning över tid kan flytta samma scenario från `NONE` till `LONG`.
- `tests/utils/test_decision_scenario_behavior.py::test_decide_ltf_entry_range_override_remains_static_across_history` visar däremot att den fasta `ltf_entry_range`-vägen inte driver samma historikbaserade glidning: samma historik propagateras, men acceptansgränsen ligger kvar oförändrad.

Arbetsregel just nu:

- **Legitim survival-policy** när override endast återöppnar passage för en redan vald kandidat, fortfarande kräver hög/tydlig confidence och fortfarande låter post-fib-gates + sizing bära resten av beslutskedjan.
- **Risk för dold entryaggression** när adaptiv threshold gör att tidigare blockerade medelstarka setups systematiskt börjar passera, så att fib-lagret i praktiken flyttar trade/no-trade-gränsen snarare än bara skyddar mot falska block. Den fasta `ltf_entry_range`-vägen ser efter nuvarande scenarioyta mer ut som en statisk policygräns än en historikdriven aggressionsmotor.

Typiska varningssignaler:

- HTF/LTF override används för att systematiskt rädda svaga setups
- veto-lager börjar beskrivas som “smart entry-förbättring”
- permission-lagret blir svårare att skilja från alpha-generation

Varför zonen är farlig:

- det döljer var entry egentligen uppstår
- det kan återinföra precis den rollförvirring som rapporten försöker städa bort

### Riskzon 5 — observability går från spegel till policy

Den femte risken är att shadow-/observability-spår börjar användas som beslutsdrivare i stället för som verifieringsyta.

Typiska varningssignaler:

- observability-data används som direkt runtime-input utan tydlig family-förankring
- advisory-/shadow-spår börjar styra i stället för att mäta
- analysartefakter används som om de vore policykontrakt

Varför zonen är farlig:

- den suddar ut gränsen mellan bevis och beslut
- den gör systemets verkliga kausalitet svårare att läsa

### Praktisk riskregel

Om en framtida ändring gör det svårare att svara på följande fyra frågor, då ligger den sannolikt i en riskzon:

1. vilken family körs?
2. vilken authority-path är authoritative?
3. i vilket lager uppstår drift först?
4. är detta policy, orkestrering, survival eller observability?

Om svaret på någon av dessa blir otydligare efter en ändring, bör den ändringen betraktas som högrisk även om diffen ser liten ut.

## Beslutschecklista för nästa ändring

Innan en framtida implementation eller refaktor accepteras bör följande checklista kunna besvaras kort och tydligt.

### A. Family-frågor

- Vilken strategy family berörs: `legacy`, `ri` eller båda?
- Är ändringen family-definierande, backbone-relaterad eller bara en lokal yta?
- Riskerar ändringen att skapa ett hybridläge mellan families?

### B. Kausalitet

- I vilket lager uppstår den avsedda effekten först?
  - authority
  - calibration
  - threshold/candidate
  - survival/cadence
  - sizing
  - exits
- Finns risk att man försöker fixa en sen effekt fast problemet börjar tidigare?

### C. Rollrenhet

- Ligger ändringen i rätt lager?
- Bör den höra hemma i backbone, eller borde den vara en family-konditionerad yta?
- Bör den höra hemma i observability i stället för i runtime-policy?

### D. Evidens

- Vilken befintlig evidens stöder att detta är rätt lager att ändra?
- Vilken verifiering krävs för att visa att family-separationen inte blivit otydligare?
- Är resultatet lättare eller svårare att förklara efter ändringen?

### Kort beslutsregel

> **En bra nästa ändring gör family-gränser, backbone-roller och den kausala driftordningen tydligare — inte mer sammanblandade.**

## Verifieringskarta per lager

För att rapporten ska kunna användas som arbetsunderlag i praktiken behöver varje lager också ha en tydlig verifieringsyta. Tabellen nedan är inte en fullständig testinventering, utan en styrkarta för **vilka bevis som hör till vilket ansvar**.

| Lager                               | Vad som ska bevisas                                                                        | Primära bevisytor                                                                                           |
| ----------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
| **Family- och kontraktslager**      | att `legacy` och `ri` fortfarande är tydligt separerade och hybridfria                     | `family_registry.py`, `tests/core/strategy/test_families.py`                                                |
| **Backbone / orkestrering**         | att den gemensamma kedjan fortfarande bara orkestrerar och inte smyger in ny family-policy | `evaluate.py`, `decision.py`, `tests/backtest/test_evaluate_pipeline.py`, pipeline-hash-/cutover-parity-yta |
| **Authority + probability surface** | att authority-path och calibration verkligen är tidiga family-sömmar                       | `prob_model.py`, authority-/cutover-parity-bevis, prob-model integration-/kontraktytor                      |
| **Threshold / candidate surface**   | att trade/no-trade och candidate resolution sker i rätt lager                              | `decision_gates.py`, decision-gates contract-/edge-/scenario-ytor                                           |
| **Structural survival**             | att HTF/LTF-veto och override beter sig som survival-policy snarare än dold entrymotor     | `decision_fib_gating.py`, scenario-/behavior-tester kring override och block/pass                           |
| **Sizing surface**                  | att drift i size inte förväxlas med tidigare candidate-drift                               | `decision_sizing.py`, `confidence.py`, clarity-/risk_state-/sizing-relaterade pipeline- och scenarioytor    |
| **Livscykel / exits**               | att exits fullbordar strategin utan att överta family-beviset                              | `htf_exit_engine.py`, exit-engine tester och backtestytor                                                   |
| **Observability / audit**           | att drift kan mätas utan att observability blir policy                                     | shadow-/observability-spår, cutover-parity-/shadow-bevis                                                    |

### Praktisk användning av verifieringskartan

Kartans poäng är enkel:

- om en ändring påstår sig röra **family-kontraktet**, ska beviset inte börja i exits
- om en ändring påstår sig röra **threshold surface**, ska beviset inte gömmas i sizing-telemetri
- om en ändring påstår sig röra **observability**, ska den inte beskrivas som ny strategi

Det vill säga: **beviset bör ligga i samma lager som anspråket**.

### Minsta bevisdisciplin för framtida arbete

När projektet går vidare bör minst följande princip gälla:

1. påstådd family-drift ska ha bevis i rätt family-lager
2. påstådd backbone-förenkling ska visa att backbone blivit renare, inte smartare
3. påstådd sizing-fix ska visa att den inte döljer tidigare candidate-drift
4. observability ska användas för att bekräfta, inte för att uppfinna, family-skillnad

## Nästa kandidatytor för fortsatt fas

Om arbetet fortsätter utan att öppna en bred refaktor eller ny parameterjakt, är följande kandidatytor de mest rimliga att ta i turordning.

### Kandidatyta A — `prob_model.py`

Varför först:

- calibration-seamen är den tidigaste tydliga family-brytaren
- här går det att isolera authority/calibration utan att direkt röra senare lager

Vad nästa fas bör svara på:

- hur mycket family-drift uppstår redan före thresholding?
- vilka delar är ren inferens och vilka delar är family-shaping calibration?

### Kandidatyta B — `decision_gates.py`

Varför därefter:

- threshold- och candidate-surface är den tydligaste sena trade/no-trade-brytaren
- här ligger också cadence och flera av de mest synliga family-skillnaderna

Vad nästa fas bör svara på:

- vilka steg är boundary-forming, vilka är candidate-moving och vilka är bara blockerande?
- hur mycket av driftbilden kommer från threshold-surface jämfört med calibration?

### Kandidatyta C — `decision_fib_gating.py`

Varför som tredje steg:

- structural survival är semantiskt känsligt
- override-logik är den tydligaste platsen där permission riskerar att glida mot dold aggressionsstyrning

Nuvarande kodläsning (2026-03-24):

- `decision.py` väljer kandidat före `apply_fib_gating(...)`, vilket betyder att fib-lagret inte initierar LONG/SHORT utan granskar om en redan vald kandidat får överleva vidare i kedjan.
- `decision_fib_gating.py` beter sig därför primärt som **permission-/survival-lager**: det kan stoppa en kandidat genom att returnera `"NONE"`, eller låta den passera vidare till post-fib-gates och sizing.
- Den semantiskt känsliga delen ligger i `prepare_override_context(...)` och `try_override_htf_block(...)`, där confidence, historik, percentiler och regime-multipliers kan rädda en annars blockerad setup.
- Arbetsdomen just nu bör därför vara: **delad survival-motor med family-konditionerad permission-logik**, men ännu inte slutligt frikänd från risken att override börjar fungera som dold entryförstärkning.

Vad nästa fas bör svara på:

- när är override legitim survival-policy?
- när börjar override fungera som dold entryförstärkning?

Nuvarande preliminära dom:

- override är **inte** kandidatursprung, eftersom riktningen väljs tidigare i `decision.py`
- override är **mer än passiv observability**, eftersom testytan visar att ett HTF-block faktiskt kan vändas till entry när thresholden justeras
- den avgörande gränsen går därför inte mellan "override eller inte", utan mellan **snäv räddningspolicy för stark kandidat** och **återkommande threshold-förskjutning som i praktiken skapar ny aggression**
- den separata `ltf_entry.entry.override_confidence` / `ltf_entry_range`-vägen har nu explicit riktad evidens både på kontraktnivå i `tests/utils/test_decision_fib_gating_contract.py` och på full `decide(...)`-integrationsnivå i `tests/utils/test_decision.py`, för både `LONG` och `SHORT`; kvarvarande fråga är därför inte om vägen existerar, utan hur ofta den bör tolkas som legitim survival-policy jämfört med dold aggressionsförskjutning

### Kandidatyta D — `decision_sizing.py`

Varför efter survival-lagret:

- sizing är viktig, men bör läsas efter att tidig family-drift redan separerats ut
- här blir skillnaden mellan candidate-drift och size-drift särskilt viktig

Nuvarande kodläsning (2026-03-24):

- `apply_sizing(...)` tar en redan vald `candidate` och returnerar endast `size` + `conf_val_gate`; den producerar inte ny action och kan inte i sig byta LONG/SHORT/NONE.
- `tests/utils/test_decision_scenario_behavior.py::test_decide_risk_state_stress_reduces_size_without_changing_action_path` visar att RI risk_state kan reducera storlek utan att ändra action-path.
- `tests/utils/test_decision_scenario_behavior.py::test_decide_stacked_sizing_penalties_reduce_size_without_changing_entry_path` visar dessutom att staplade sizing-signaler (regime multiplier + HTF-regime multiplier + RI risk_state + clarity) fortfarande lämnar samma `ENTRY_LONG`-path intakt medan endast storleken pressas ned.
- `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_ri_v2_clarity_on_changes_sizing_only_and_logs` visar att clarity v2 påverkar storlek och state/exporter, men inte entry-reasons eller vald action.
- `tests/utils/test_decision_edge.py::test_regime_size_multiplier_scales_size_only` visar samma sak för regime-multipliers: samma LONG, annan size.
- `tests/utils/test_confidence.py::test_compute_confidence_v2_component_scope_sizing_only_does_not_affect_gate` är viktig därför att den skiljer gate-confidence från sizing-confidence via `buy_scaled` / `sell_scaled`; annars riskerar man att misstolka en sizing-penalty som tidig candidate-drift.

Arbetsdomen just nu bör därför vara: **sizing-surface är huvudsakligen post-candidate och family-konditionerad**, där RI främst uttrycker sig genom clarity-, risk_state- och regime-/HTF-multipliers snarare än genom att skapa kandidaten från början.

Vad nästa fas bör svara på:

- vilka effekter är verkligt post-candidate?
- vilka family-skillnader ligger i regime-/HTF-/clarity-/risk_state-surface snarare än tidigare i kedjan?

Nuvarande preliminära dom:

- family-drift som syns här är i första hand **riskexponering efter vald kandidat**, inte första uppkomst av kandidat
- den största tolkningsrisken är att blanda ihop `confidence`-penalty i gating med `buy_scaled` / `sell_scaled` i sizing och därmed felaktigt tro att sizing-lagret skapade en trade/no-trade-skillnad
- sizing-fasen framstår därför som tillräckligt ren för att läsas efter threshold/survival, inte före

### Kandidatyta E — exits och observability

Varför sist:

- de fullbordar och verifierar strategin
- de bör inte vara första platsen där family-frågan avgörs

Nuvarande kodläsning (2026-03-24):

- `src/core/backtest/htf_exit_engine.py` arbetar på en redan öppnad position med fryst `exit_ctx`, HTF-fibnivåer, partials, trailing och structure-breaks; den väljer inte strategy family och skapar inte entry-kandidat.
- `tests/backtest/test_htf_exit_engine_selection.py` visar främst motorval mellan ny och legacy exit-engine via config/env, inte family-separation.
- `tests/backtest/test_htf_exit_engine_htf_context_schema.py` och `tests/backtest/test_htf_exit_engine_components.py` visar schema-, partial-, trailing- och structure-break-kontrakt för exitmotorn, men de bevisar framför allt korrekt livscykel efter entry.
- `tests/backtest/test_backtest_applies_htf_exit_config.py` visar att exit-konfiguration faktiskt appliceras i backtestmotorn, vilket stärker exit-lagret som runtime-livscykel snarare än som family-definierare.
- `tests/backtest/test_regime_shadow_artifacts.py` och `tests/core/intelligence/regime/test_contracts.py::test_shadow_regime_observability_roundtrip_preserves_shape` visar att shadow-/observability-lagret bevarar en stabil payload-shape, håller `decision_input` som observability-only och skriver evidensartefakter endast i explicit opt-in-läge.

Arbetsdomen just nu bör därför vara: **exit-lagret fullbordar och kvalificerar den redan valda family-surface**, men utgör inte den primära evidensen för family-spliten mellan legacy och RI.

Vad nästa fas bör svara på:

- hur mycket av family-skillnaden lever faktiskt vidare efter sizing?
- vilka observability-ytor ger bäst bevis utan att skapa ny policy?

Nuvarande preliminära dom:

- exits verkar huvudsakligen vara **livscykellogik nedströms candidate + sizing**, inte ett eget family-breaker-lager
- family-frågan här handlar därför mer om **hur tidigare vald surface fullbordas** än om var den först uppstår
- om exit-lagret börjar bära huvudbeviset för family-split har analysen sannolikt redan flyttat sig för långt nedströms
- observability-/shadow-lagret framstår som **spegel och kontraktsbärare**, inte som policykälla: det ska göra mismatch och evidens synliga utan att själv bli beslutsdrivare
- closure-fasen kan därför läsas som tillräckligt ren när exits + observability bekräftar tidigare lager utan att omdefiniera dem

## Selector- och evidensplan per kandidatyta

För att nästa fas inte ska börja med att "leta test" bör varje kandidatyta ha en liten minimiuppsättning selectors redan innan första diffen skrivs.

### A. `prob_model.py` — rekommenderad minsta evidens

Primär selectors:

- `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_returns_meta`
- `tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode`
- `tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_pipeline_hash_stability`

Bra komplettering om calibration-/probability-seamen öppnas tydligare:

- `tests/backtest/test_evaluation.py`

Praktisk läsning:

- börja med selectors som visar att sannolikhets- eller authority-drift faktiskt syns uppströms thresholding
- använd bredare calibration-tester som kompletterande stöd, inte som ensam family-dom

### B. `decision_gates.py` — rekommenderad minsta evidens

Primär selectors:

- `tests/integration/test_golden_trace_runtime_semantics.py::test_signal_adaptation_zone_overrides_base_thresholds`
- `tests/core/strategy/test_families.py::test_resolve_strategy_family_rejects_declared_ri_with_wrong_gates`
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

Bra komplettering när threshold-shape eller gating-gränser rörs:

- `tests/governance/test_config_schema_backcompat.py`

Praktisk läsning:

- om ändringen sägs vara threshold-relaterad ska minst en selector visa faktisk threshold-/candidate-effekt
- pipeline-hash ska fungera som skydd mot att en "liten" gate-ändring i själva verket flyttar backbone-ordning

### C. `decision_fib_gating.py` — rekommenderad minsta evidens

Primär selectors:

- `tests/utils/test_decision_fib_gating_contract.py`
- `tests/utils/test_decision.py::test_htf_override_preserves_debug_payload_and_history`
- `tests/utils/test_decision_scenario_behavior.py::test_decide_adaptive_htf_override_progression_flips_block_into_entry`
- `tests/utils/test_decision_scenario_behavior.py::test_decide_ltf_entry_range_override_remains_static_across_history`
- `tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode`
- `tests/backtest/test_evaluate_regime_precomputed_index.py`
- `tests/core/strategy/test_families.py::test_cross_family_promotion_requires_override_and_signoff`

Bra komplettering om HTF/LTF-fib-samspelet påverkas:

- `tests/utils/test_features_asof_context_bundle.py`

Praktisk läsning:

- override/survival-logik behöver bevisas som permission- eller survival-policy, inte smygväg för ny aggression
- därför bör samma ändring helst ha både replay-bevis och ett kontraktsbevis mot otillåten override-glidning

### D. `decision_sizing.py` — rekommenderad minsta evidens

Primär selectors:

- `tests/backtest/test_evaluate_pipeline.py::test_evaluate_pipeline_ri_v2_clarity_on_changes_sizing_only_and_logs`
- `tests/utils/test_decision_scenario_behavior.py::test_decide_risk_state_stress_reduces_size_without_changing_action_path`
- `tests/utils/test_decision_scenario_behavior.py::test_decide_stacked_sizing_penalties_reduce_size_without_changing_entry_path`
- `tests/utils/test_decision_edge.py::test_regime_size_multiplier_scales_size_only`
- `tests/utils/test_confidence.py::test_compute_confidence_v2_component_scope_sizing_only_does_not_affect_gate`
- `tests/governance/test_regime_intelligence_cutover_parity.py::test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode`
- `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`

Bra komplettering när regime-/clarity-/risk-state-surface öppnas:

- `tests/core/intelligence/regime/test_clarity.py`
- `tests/core/intelligence/regime/test_contracts.py`

Praktisk läsning:

- sizing-ytan ska visa post-candidate-effekt, inte maskera tidigare drift
- om clar​ity eller risk_state påverkar size men inte candidate, ska beviset säga just det och inte mer

### E. exits och observability — rekommenderad minsta evidens

Primär selectors:

- `tests/backtest/test_htf_exit_engine_selection.py`
- `tests/backtest/test_htf_exit_engine_htf_context_schema.py`
- `tests/backtest/test_backtest_applies_htf_exit_config.py`
- `tests/backtest/test_htf_exit_engine_components.py`

Bra komplettering när evidensartefakter eller shadow-spår rörs:

- `tests/backtest/test_regime_shadow_artifacts.py`
- `tests/core/intelligence/regime/test_contracts.py::test_shadow_regime_observability_roundtrip_preserves_shape`

Closure-dom just nu:

- exits och observability bekräftar family-bilden **nedströms** men definierar den inte
- det stärker huvudtesen att family-separationen ska bevisas i authority/calibration/threshold/survival/sizing, medan closure-lagret främst ska göra samma bild granskningsbar och reproducerbar

Praktisk läsning:

- exits och observability ska bekräfta family-bilden nedströms, inte definiera den uppströms
- om en ändring bara kan försvaras via shadow-artifacts men inte via family-/candidate-lager, är evidensen sannolikt felplacerad

### Kort arbetsregel för nästa fas

Före första implementation på någon av kandidatytorna bör nästa slice skriva ned exakt:

1. vilken av selectors ovan som är **minimikrav**
2. vilken selector som är **driftvakt** mot scope-glidning
3. vilken extra selector som bara körs om ändringen faktiskt öppnar ett bredare lager

Det gör att nästa fas kan starta med en liten, explicit evidensdisciplin i stället för att uppfinna sin verifiering halvvägs genom diffen.

## Minimal arbetsmall för nästa slice

Om nästa fas öppnar en av kandidatytorna ovan bör arbetet kunna beskrivas i följande miniformat redan innan första kodändringen.

### 1. Slice-definition

- **Kandidatyta:** vilken fil eller family-surface som öppnas
- **Family-anspråk:** `legacy`, `ri` eller delad backbone med family-konditionerad effekt
- **Första driftlager:** authority, calibration, threshold, survival, sizing eller exits
- **Uttryckligt icke-mål:** vilket lager som inte ska ändras i samma slice

### 2. Minsta evidenspaket

- **Minimikrav-selector:** den viktigaste selector som måste passera
- **Driftvakt:** selector som fångar scope-glidning eller backbone-drift
- **Kompletterande selector:** körs bara om ändringen faktiskt öppnar bredare semantik

### 3. Tolkningsregel

- om minimikravet faller är hypotesen om rätt lager sannolikt fel
- om driftvakten faller har ändringen sannolikt blivit bredare än avsett
- om bara kompletterande selector faller måste man först avgöra om slicen i praktiken öppnade ett större lager än planerat

### 4. Kort beslutsrad som bör kunna fyllas i

Nästa pass bör kunna börja med en enda rad i stil med:

> **Vi öppnar `decision_gates.py` för RI/legacy threshold surface; första driftlager antas vara candidate/threshold; `test_signal_adaptation_zone_overrides_base_thresholds` är minimikrav, pipeline-hash är driftvakt och config-schema-backcompat körs endast om threshold-shape öppnas.**

Poängen med denna mall är enkel: nästa arbete ska kunna uttryckas som **ett litet lageranspråk + ett litet bevispaket**, inte som en bred diffus ambition.

## Vad denna reframing uttryckligen säger

1. **RI är en separat strategy family, inte ett lager.**
2. **Legacy är också en full strategy family, inte bara “rå entry”.**
3. **Båda families realiseras genom samma övergripande orkestreringskedja.**
4. **Family-separationen sitter i signatur, authority, calibration, threshold, cadence, survival och sizing.**

## Vad denna reframing uttryckligen inte säger

- den säger **inte** att RI och legacy använder två helt separata fysiska runtime-pipelines
- den säger **inte** att RI ersätter legacy helt
- den säger **inte** att exits redan är den starkast bevisade splitpunkten
- den säger **inte** att behavior ska ändras eller retunas

## Samlad family-dom

Den starkaste, kodförankrade slutdomen är nu:

> **Legacy och RI ska beskrivas som två separata strategy families som realiseras genom samma `evaluate -> decide`-orkestrering men med olika family-signaturer, authority/calibration-paths och family-konditionerade threshold/gating/cadence/sizing-surfaces. RI är därför inte ett lager ovanpå legacy, utan en separat strategy family.**

## Praktisk läsregel för fortsatt arbete

När framtida analys eller implementation frågar “är detta legacy eller RI?” bör frågan inte längre besvaras med “vem gör entry och vem gör filtering?”.

Rätt fråga är i stället:

1. vilken **family-signatur** bär konfigurationen?
2. vilken **authority-path** är authoritative?
3. vilken **calibration-/threshold-/cadence-surface** används?
4. vilken **survival- och sizing-surface** fullbordar strategin?

Om dessa svar ligger på RI-ytan, då är det RI-strategin som körs — inte legacy med ett smart lager ovanpå.
