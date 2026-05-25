# Research experiment infrastructure inventory contract

Status: `bounded usage contract / derivative / non-authorizing`

> Routing status (2026-05-25, `feature/research-experiment-lane-operating-contract`): detta dokument inventerar befintliga research-/experiment-ytor och definierar hur agenter får läsa och återanvända dem utan authority leakage. Dokumentet är derivativt och citation-bound. Det skapar inte ny governance-, runtime-, readiness- eller promotion-authority och ersätter inte `docs/CURRENT_AUTHORITY_INDEX.md`, `docs/knowledge/KNOWLEDGE_AUTHORITY_RULES.md` eller `docs/governance_mode.md`.

## Syfte

Detta dokument svarar på en begränsad fråga för denna slice:

- vilken research-/experiment-infrastruktur finns redan i repot
- vad dessa ytor får användas till
- vad dessa ytor uttryckligen inte får auktorisera
- hur agenter ska läsa och använda dem utan att observations- eller evidensytor glider över i current authority
- när researcharbete måste eskalera till promotion-packet eller annan current authority path

Detta dokument gör **inte** historisk cleanup, utökar inte lineage-kartor och introducerar inte en ny research-lane eller ett nytt governance-mode.

## Scope boundary

### Scope IN

- inventera befintliga `research_ledger`-ytor
- inventera befintliga `research_orchestrator`-ytor
- inventera befintliga `research_findings`-, findings-bundle- och findings-index-ytor
- klassificera dessa som återanvändbar icke-runtime research-infrastruktur, historisk packet-proveniens eller derivativa icke-auktoriserande outputs
- definiera agentregler och no-leakage-gränser för dessa ytor
- definiera eskaleringsgräns till promotion/current authority path

### Scope OUT

- runtimekod
- configbeteende
- teständringar
- schemaändringar
- artifactändringar
- nya entity types
- ny research-infrastruktur
- research-lineage-expansion
- historisk cleanup utanför de direkt inventerade ytorna
- ny governance-mode
- promotion-, readiness- eller runtime-authority claims

## Läsmodell för denna slice

Använd följande etiketter strikt:

- **Observed**: direkt verifierat i nuvarande repo genom befintliga filer, exporter, inline-notes eller README-/schema-text.
- **Inferred**: försiktig tolkning från observerad repoform plus redan citerade authority-/routingytor.
- **Unverified**: sådant denna slice uttryckligen inte klassificerar uttömmande.

Om stöd saknas eller glider utanför den inventerade ytan ska materialet behandlas som `NON_AUTHORIZING` eller `UNRESOLVED` enligt de högre styrlagren, inte som implicit current authority.

## Inventering av befintlig research-/experiment-infrastruktur

### Återanvändbar icke-runtime research-infrastruktur

#### `research_ledger`

**Observed**

- Paketet finns i `src/core/research_ledger/` med följande nuvarande filer:
  - `enums.py`
  - `indexes.py`
  - `models.py`
  - `queries.py`
  - `service.py`
  - `storage.py`
  - `validators.py`
  - `__init__.py`
- `src/core/research_ledger/__init__.py` exporterar observerat både lagrings-/query-/validator-ytor och record-/enumtyper, inklusive bland annat:
  - `ResearchLedgerService`
  - `LedgerStorage`
  - `LedgerQueries`
  - `validate_record`
  - `ArtifactRecord`
  - `ExperimentRecord`
  - `HypothesisRecord`
  - `PromotionRecord`
  - `GovernanceDecisionRecord`
  - `ChampionRecord`
  - `ProposalRecord`

**Inferred**

- Paketet är en befintlig file-backed research substrate för researchidentitet, lagring, queries, validering och artifact/provenance-hantering.
- Det är återanvändbar research-infrastruktur, men inte i sig en current authority path.

**Unverified**

- Denna slice klassificerar inte varje downstream-konsument av ledger-records.
- Denna slice avgör inte om varje recordtyp används aktivt i nuvarande operativt flöde.

**Agenter får använda ytan till**

- läsa struktur, recordformer, lagringsmönster och query-/validatorgränser
- förstå hur research artifacts och identiteter representeras
- återanvända etablerad terminologi för research records när en slice redan ligger inom research/evidence-ytor
- referera till ledgern som provenance- eller strukturstöd för researcharbete

**Ytan får inte användas för att auktorisera**

- runtimebeteende eller default-semantik
- readiness eller promotion
- governance verdicts eller current operational truth
- tolkningen att en recordtyp med namn som `PromotionRecord`, `GovernanceDecisionRecord` eller `ChampionRecord` i sig innebär att en promotion eller governance-beslut är gällande

#### `research_orchestrator`

**Observed**

- Paketet finns i `src/core/research_orchestrator/` med följande nuvarande filer:
  - `families.py`
  - `family_decisions.py`
  - `models.py`
  - `orchestrator.py`
  - `workflow.py`
  - `__init__.py`
- `src/core/research_orchestrator/__init__.py` exporterar observerat bland annat:
  - `DeterministicResearchOrchestrator`
  - `ResearchTask`
  - `ResearchResult`
  - `ResearchStageOutputs`
  - `orchestrate_research_task`
  - `FamilyResearchTask`
  - `FamilyParameterBatch`
  - `FamilyStatusRecord`
  - `FamilyComparisonInput`
  - `FamilyComparisonResult`
  - `evaluate_family_promotion`
  - `build_family_status_records`

**Inferred**

- Paketet är en befintlig research coordination-yta för deterministiska research tasks och family-orienterade researchhjälpare.
- Orchestratorn är bredare än det äldre, smalare historiska packet-språket antydde; därför ska den i denna slice läsas som nuvarande researchkoordination, inte som endast ett historiskt förslag.

**Unverified**

- Denna slice gör ingen full downstream-audit av alla konsumenter av `research_orchestrator`.
- Denna slice avgör inte om varje family-orienterad helper används i nuvarande operativa beslutsflöden.

**Agenter får använda ytan till**

- läsa hur research tasks, stage outputs och deterministisk researchkoordination är strukturerade
- återanvända researchlokala jämförelse- och batchtermer i research slices
- referera till family-orienterade helpers som research analysis surfaces när repoformen uttryckligen visar dem

**Ytan får inte användas för att auktorisera**

- family admission
- promotionstatus
- readiness
- current runtime policy
- governance override
- slutsatsen att namn som `evaluate_family_promotion`, `ComparisonDecision` eller `FamilyStatusRecord` i sig skapar repo-gällande promotion- eller policy-authority

#### `research_findings`-infrastruktur

**Observed**

- Följande read-only helperytor finns i repot:
  - `scripts/preflight/findings_preflight_lookup.py`
  - `scripts/preflight/findings_packet_starter.py`
- Följande verifieringsytor finns i repot:
  - `tests/utils/test_findings_preflight_lookup.py`
  - `tests/utils/test_findings_packet_starter.py`
- Följande committed formyta finns i repot:
  - `artifacts/bundles/findings/schema/research_findings_bundle_v1.schema.json`
- Schemat anger observerat att findings bundles är `Research-only, non-runtime` och kräver `runtime_authority` med konstant värde `none`.
- `finding_outcome` beskrivs observerat i schemat som research-only evidensriktning och uttryckligen inte som governance verdict eller runtime-/promotion-/readiness-authority.
- `scripts/preflight/findings_preflight_lookup.py` beskriver sig observerat som `Read-only preflight lookup over the research findings bank`.
- Samma helper anger observerat att `--fail-on-blocking-match` är `Research convenience only; not governance authority.`
- `scripts/preflight/findings_packet_starter.py` genererar observerat advisory-only starterinnehåll och markdownoutputen säger uttryckligen `Advisory only` samt att outputen inte skapar governance-, runtime-, readiness- eller promotion-authority.

**Inferred**

- Findings-sidan är en befintlig research evidence-reuse layer för lookup, advisory preflight och packet-starter-stöd.
- De committed helpers och schemat utgör återanvändbar icke-runtime research-infrastruktur.

**Unverified**

- Denna slice gör ingen uttömmande revision av varje findings-bundle eller varje möjlig framtida findings-konsument.

**Agenter får använda ytan till**

- slå upp tidigare positiva, negativa eller direction-lock findings
- undvika upprepning genom `do_not_repeat`, `next_admissible_step` och referensytor
- bygga advisory packet starter-utkast för manuell vidarebearbetning
- validera att ett materialiserat findings-index matchar committed projection när detta görs inom research-evidence-ramen

**Ytan får inte användas för att auktorisera**

- governance gates
- readiness gates
- promotion grants
- runtime- eller defaultbeteende
- current canon
- tolkningen att helperns exit code eller `blocking`-språk i sig är repo-gällande beslutskraft

### Historisk packet-proveniens endast

Följande ytor ska i denna slice läsas som historisk proveniens, inte som current authority:

- `docs/audit/research_ledger/context_map_research_ledger_v1_merge_readiness_2026-03-16.md`
- `docs/audit/research_ledger/command_packet_research_ledger_v1_merge_readiness_2026-03-16.md`
- `docs/audit/research_orchestrator/context_map_research_orchestrator_v1_2026-03-17.md`
- `docs/audit/research_orchestrator/command_packet_research_orchestrator_v1_2026-03-17.md`
- `docs/decisions/research_findings/research_findings_bank_repo_native_packet_2026-04-24.md`
- `docs/decisions/research_findings/research_findings_bank_seed_implementation_packet_2026-04-24.md`
- `docs/decisions/research_findings/research_findings_preflight_lookup_implementation_packet_2026-04-24.md`
- `docs/decisions/research_findings/research_findings_packet_starter_implementation_packet_2026-04-24.md`
- `docs/decisions/research_findings/slice_scout_preflight_bootstrap_packet_2026-04-24.md`
- `docs/decisions/research_findings/slice_evidence_handoff_bootstrap_packet_2026-04-24.md`
- `docs/analysis/recommendations/research_findings_bank_repo_native_structure_2026-04-24.md`

**Observed**

- Dessa filer finns i nuvarande repo och bär packet-, audit- eller recommendations-framing.

**Inferred**

- De är användbara som proveniens för tidigare scope, stop conditions, designavsikt och implementation history.
- De är inte i sig current authority bara för att de är detaljerade, nyare än äldre arkiv eller skrivna i packet-form.

**Unverified**

- Denna slice gör ingen bred klassificering av alla andra historiska packetkedjor utanför den direkt inventerade researchytan.

**Agenter får använda ytan till**

- förstå tidigare begränsningar, historiska stop conditions och tidigare slice-intention
- spåra varför en nuvarande committed yta sannolikt ser ut som den gör

**Ytan får inte användas för att auktorisera**

- current live instruction
- runtime- eller promotionbeslut
- inferred supersession eller lineage bara på grund av kronologi, mappnamn eller packet-format

### Derivativa icke-auktoriserande outputs

#### Findings bundles, findings index och artifact records

**Observed**

- `artifacts/research_ledger/indexes/findings_index.json` finns committed i repot.
- Indexet säger observerat att det är `derived`, `rebuildable`, att `runtime_authority` är `none`, och att det `is not a governance gate, runtime surface, readiness surface, or promotion surface.`
- Findings bundles finns committed under `artifacts/bundles/findings/**`.
- Findings-kopplade artifact records finns committed under `artifacts/research_ledger/artifacts/ART-*.json`.

**Inferred**

- Dessa ytor är evidence-/projection-outputs som får stödja återanvändning, observation och candidate reasoning.
- De är inte självständiga authority-ytor.

**Unverified**

- Denna slice uttalar sig inte om varje artifact under `artifacts/` utanför findings-kopplade ytor.

**Agenter får använda ytan till**

- hitta tidigare findings och deras evidensreferenser
- läsa återanvändbara observationer och negativa/direction-lock-hinder
- stödja smalare nästa slice eller packet-scope

**Ytan får inte användas för att auktorisera**

- policy- eller governance-pass/fail
- runtime semantics
- readiness eller promotion
- current truth genom existens, recency, densitet eller mappplacering

#### Research outputs under `results/research/**`

**Observed**

- `results/research/README.md` anger att denna yta är för reproducerbara experimentbundlar och uttryckligen `inte` är governance-SSOT eller authority-signal för runtime, readiness eller promotion.

**Inferred**

- Research outputs under denna zon får användas som evidens eller observation när de är relevanta för en bounded slice.
- De ska läsas som framåtriktade researchbundlar, inte som current policy eller decision authority.

**Unverified**

- Denna slice klassificerar inte varje enskild bundle under `results/research/**`.

**Agenter får använda ytan till**

- läsa reproducerbara observationsbundlar
- återanvända manifest-, artifacts- och summaryreferenser som research evidence
- koppla vidare till längre mänskliga synteser där sådan routing redan finns

**Ytan får inte användas för att auktorisera**

- policybeslut
- current canon
- readiness eller promotion
- tolkningen att en välorganiserad bundle automatiskt är en current authority surface

## Hur agenter ska läsa och använda dessa ytor

1. Börja med current authority path, inte med research outputs.
   - För governance mode, authority-ordning och promotionsgränser gäller först de högre styrlagren.
   - Denna kontraktsyta styr endast hur de redan existerande researchytorna får läsas och återanvändas.

2. Läs `research_ledger` som struktur och proveniens, inte som beslutskraft.
   - Ledgern får användas för att förstå records, artifacts och researchspårbarhet.
   - Ledgern får inte läsas som att recordnamn i sig etablerar current status.

3. Läs `research_orchestrator` som researchkoordination, inte som policy-motor.
   - Orchestratorn får användas för att förstå research tasks, resultatformer och family-orienterade researchhjälpare.
   - Namn med `promotion`, `decision` eller `status` måste läsas som researchlokala former tills en current authority path uttryckligen adopterar dem.

4. Läs findings helpers och findings index som advisory reuse, inte som gates.
   - Helpers får användas för lookup, packet starter-stöd och återanvändning av negativa/positiva/direction-lock findings.
   - Index, bundles och helper-exit-codes får inte läsas som governance gate eller readiness gate.

5. Läs `results/research/**` och andra research outputs som evidensbundlar.
   - De får stödja observation, återanvändning och candidate reasoning.
   - De får inte tyst prometeras till canon, policy eller runtime-authority.

6. Märk claims ärligt.
   - När en claim bygger direkt på committed filer eller text: märk den som **Observed**.
   - När en claim är en försiktig tolkning av observerad repoform: märk den som **Inferred**.
   - När en claim kräver bredare lineage, downstream-audit eller nuvarande operativ adoption som inte verifierats här: märk den som **Unverified** och stoppa där.

## Vad som räknas som authority leakage

Följande är authority leakage i denna slice:

- att behandla historiska packets eller audits som current authority enbart för att de är detaljerade eller ligger nära nuvarande kod
- att behandla `findings_index.json`, findings bundles eller findings-linked artifact records som governance gate, readiness gate eller promotion grant
- att behandla `--fail-on-blocking-match` eller annan helper-output som repo-gällande beslutskraft i stället för advisory research convenience
- att behandla namn som `PromotionRecord`, `GovernanceDecisionRecord`, `evaluate_family_promotion` eller `ComparisonDecision` som bevis för current operativ status utan explicit promotion/adoption
- att behandla artifactvolym, recency, välorganiserad mappstruktur eller reuse-frekvens som authority-signal
- att citera research outputs som om de redan vore current canon, readiness eller runtime/default-semantik
- att använda denna kontraktsyta som ny SSOT eller som ersättning för current authority path

## När research måste eskalera till promotion/current authority path

Researcharbete måste sluta vara endast research/evidence-reuse och eskalera när det vill göra något av följande:

- hävda current canon eller current operational truth
- hävda readiness
- hävda promotion, family admission eller champion-status
- hävda runtimebeteende, default-semantik eller configtolkning
- behandla en research finding som mer än advisory reuse
- flytta en observation från evidensyta till aktiv policy- eller governance-ytans beslut
- ändra högre styrlager eller annan current authority surface
- korsa in i strict-only surfaces eller annan yta som enligt `docs/governance_mode.md` kräver skärpt hantering

Fram till dess gäller följande begränsning:

- research bundles, findings, packets, indexes och outputs får stödja observation, återanvändning, scoped reasoning och nästa kandidatformulering
- de får inte själva skapa canon, readiness, promotion, runtime-authority eller governance-authority

## Risker och kvarvarande öppna gränser

### Observed risk

- `research_ledger` och `research_orchestrator` exporterar namn med `promotion`, `decision`, `governance`, `champion` och `status`. Dessa namn ökar risken för feltolkning om de läses utan current authority path.

### Inferred risk

- Eftersom `research_orchestrator` nu är bredare än de äldre orchestrator-packeten antydde, finns risk att historisk packet-framing undersäljer nuvarande repoform eller att nuvarande repoform övertolkas som current policy.

### Unverified boundary

- Denna slice klassificerar inte varje downstream-konsument, varje artifact under `artifacts/**`, varje bundle under `results/research/**` eller hela research-lineage-kedjan. Sådana frågor kräver en separat bounded slice om de behöver avgöras.

## Citerade stödytor för denna kontraktsläsning

- `.github/copilot-instructions.md`
- `docs/governance_mode.md`
- `docs/CURRENT_AUTHORITY_INDEX.md`
- `docs/knowledge/KNOWLEDGE_AUTHORITY_RULES.md`
- `docs/contracts/README.md`
- `results/research/README.md`
