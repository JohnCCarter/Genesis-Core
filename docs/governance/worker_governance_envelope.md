# Worker governance envelope

## Syfte

Det här dokumentet definierar den worker-facing operativa specen för parallella workers.

Det är här den kompilerade governance-envelope:n beskrivs: alltså det kontrakt som control plane ger till en worker så att workern kan arbeta säkert utan att själv behöva tolka hela repo-governance-stacken.

Det här dokumentet är **inte** ett nytt governance-SSOT.

Auktoritativa källor förblir:

- `docs/governance_mode.md`
- `.github/copilot-instructions.md`
- `AGENTS.md`

`workforce_roadmap.md` beskriver systemet på hög nivå. Det här dokumentet beskriver vad en worker faktiskt ska få och följa.

---

## Designregel

Den viktigaste designregeln är följande:

> Roadmapen förklarar systemet. Envelope:n instruerar workern.

En worker ska inte behöva läsa flera styrdokument och själv försöka härleda vad som gäller. Om workern måste göra det har governance inte kompilerats tillräckligt långt.

Som huvudregel ska en worker kunna arbeta säkert med bara:

- `base_sha`
- sin envelope / sitt dispatch-kontrakt
- sina tillåtna inputs

---

## Auktoritet och precedence

### Global governance är alltid auktoritativ

Repo-governance förblir alltid överordnad worktree-lokala dokument eller dispatch-filer.

Det betyder att en lokal envelope:

- får återge resolved mode
- får snäva in scope
- får lägga till extra förbud
- får specificera outputs, gates och stop conditions

Den får inte:

- byta mode
- öppna globalt förbjudna ytor
- sänka gate-krav
- ge write-rätt till shared truth om global governance inte tillåter det
- omtolka strict-only surfaces

### Konfliktregel

Vid konflikt gäller följande:

- global governance vinner alltid
- lokal envelope får bara **narrow**, aldrig override:a
- om envelope:n motsäger eller försöker bredda global governance ska resultatet vara **fail-closed**

Praktiskt:

- effektiva tillåtna ytor = globalt tillåtet ∩ envelope-tillåtet
- effektiva förbjudna ytor = globalt förbjudet ∪ envelope-förbud
- review och gates följer alltid den striktare regeln

### Mode bestäms inte lokalt

Resolved mode bestäms via `docs/governance_mode.md`, inte via worktree-lokal fil.

Envelope:n ska därför bära med sig:

- `resolved_mode`
- `mode_source`
- `authority_source`

Den får däremot inte själv ändra dem.

---

## Branch- och worktree-disciplin

Varje worker ska utgå från:

- samma integrationsgren eller samma auktoriserade basgren
- samma `base_sha` för den aktuella dispatch-vågen
- egen branch
- egen worktree eller isolerad checkout

### Branchnamn ska bära mode där det är möjligt

Eftersom `docs/governance_mode.md` använder branchmappning ska worker-brancher bära mode i namnet.

Exempel:

- `feature/wt/mixed/2017-2023-chronology`
- `feature/wt/inventory/annual-scan-batch-a`
- `research/wt/sign/insufficient-evidence-holdout`
- `sandbox/wt/probe/example-x`

Undvik:

- `wt/...`

Anledningen är att `wt/...` inte matchar `feature/*`, `research/*`, `sandbox/*` eller `spike/*` och därför riskerar att falla tillbaka till `STRICT`.

### Hårda branchregler

- samma branch ska inte checkas ut aktivt i flera worktrees samtidigt
- en worker får inte själv byta branchkonvention mitt under ett jobb
- worktree-lokala filer får aldrig användas för att override:a resolved mode

---

## Worker-klasser och kapabiliteter

| Worker-klass | Repo-write? | Commit allowed? | Shared truth write? | Typiska outputs | Kommentar |
| --- | --- | --- | --- | --- | --- |
| Inventory | Normalt nej | Normalt nej | Nej | shortlist, ranking, artifacts, summary | read-only med hårda gränser |
| Deep-dive | Ja, inom exakt scope | Ja | Nej | packet, analysis note, ev. explicit tillåten helper/test | bounded repo-write i egen branch |
| Integration | Ja | Ja | Ja | re-anchor, synthesis, integration decisions | enda normala vägen för shared truth |
| Runtime/strict | Endast via explicit separat auktorisering | Endast via explicit separat auktorisering | Endast när uttryckligen tillåtet | strikt styrda ändringar | inte standardklass för parallella workers |

Den viktigaste regeln är att ingen worker själv får uppgradera betydelsen av sitt resultat.

En worker får hitta något intressant, men får inte själv besluta att resultatet nu är:

- repo-sanning
- readiness
- promotion-underlag
- runtime-auktoritet

Det sker i integration plane.

---

## Fält som varje envelope minst ska innehålla

| Fält | Syfte |
| --- | --- |
| `task_id` | unik identifierare för jobbet |
| `worker_class` | vilken kapabilitetsklass workern tillhör |
| `base_branch` | basgren för dispatch-vågen |
| `base_sha` | pinnad startpunkt |
| `worker_branch` | worker-specifik branch |
| `resolved_mode` | mode som redan lösts av control plane |
| `mode_source` | varför mode blev som det blev |
| `authority_source` | vilken SSOT som gav mode/auktoritet |
| `change_class` | t.ex. `docs-only`, `tooling`, `runtime-touching` |
| `lane` | arbetslane, t.ex. `research-evidence` |
| `question` | exakt fråga som ska besvaras |
| `subject` | avgränsat subject för jobbet |
| `scope_in` | vad workern får röra |
| `scope_out` | vad workern uttryckligen inte får röra |
| `allowed_inputs` | godkända datakällor och artefakter |
| `allowed_output_types` | vilka outputtyper workern får producera |
| `forbidden_surfaces` | ytor som alltid ska behandlas som förbjudna |
| `repo_write_allowed` | om worker får skriva till repo över huvud taget |
| `commit_allowed` | om worker får göra commits |
| `shared_truth_write` | om worker får uppdatera shared truth |
| `review_required` | om review krävs innan landing |
| `gates_required` | vilka gates som måste köras |
| `done_criteria` | vad som räknas som klar output |
| `stop_conditions` | när workern måste stoppa direkt |
| `escalation_conditions` | när workern ska lämna tillbaka jobbet till control plane |

Om något av de här fälten är oklart ska workern inte gissa. Den ska stoppa eller eskalera.

---

## Minimal manifestmall

```yaml
task_id: mixed-2017-2023-cadence
worker_class: deep-dive
base_branch: feature/next-slice-2026-05-06
base_sha: <PINNED_SHA>
worker_branch: feature/wt/mixed/2017-2023-cadence
resolved_mode: RESEARCH
mode_source: branch:feature/wt/mixed/2017-2023-cadence
authority_source: docs/governance_mode.md
change_class: docs-only
lane: research-evidence
question: "Compare internal cadence inside the fixed dominant windows for 2017-03 and 2023-12"
subject:
  kind: year-pair
  value: [2017, 2023]
scope_in:
  - docs/decisions/**
  - docs/analysis/**
scope_out:
  - src/**
  - config/**
  - GENESIS_WORKING_CONTRACT.md
allowed_inputs:
  - results/evaluation/<artifact>.json
allowed_output_types:
  - packet
  - analysis_note
forbidden_surfaces:
  - runtime
  - default-authority
  - promotion
repo_write_allowed: true
commit_allowed: true
shared_truth_write: false
review_required: false
gates_required:
  - pre-commit_docs
done_criteria:
  - packet_created
  - analysis_note_created
  - scoped_validation_green
stop_conditions:
  - touching_forbidden_path
  - widening_subject
  - implying_runtime_authority
escalation_conditions:
  - touching_strict_only_surface
  - envelope_conflicts_with_global_governance
  - shared_truth_update_needed
```

---

## Outputkontrakt från worker tillbaka till control plane

Varje worker ska lämna minst följande:

- `status`: `pass | null | blocked | fail-closed`
- artifacts
- kort summary
- `what_this_does_not_prove`
- `recommended_next_step`
- `recommended_integration_class`

Tillåtna värden för `recommended_integration_class`:

- `ignore`
- `park`
- `deep-dive`
- `integrate`

Envelope:n ska göra det möjligt att bedöma output utan att kontrollplanet måste gissa vad workern egentligen trodde att uppdraget var.

---

## Stoppa vs eskalera

### Typiska stop conditions

Arbetet ska stoppa direkt om workern:

- rör förbjuden path eller förbjuden surface
- breddar subject utanför envelope
- börjar implicera runtime/default/readiness/promotion-auktoritet
- saknar kritiskt input som envelope:n uttryckligen kräver

### Typiska escalation conditions

Arbetet ska lämnas tillbaka till control plane om workern ser att:

- strikt yta behöver röras
- envelope:n krockar med global governance
- shared truth egentligen behöver uppdateras
- frågan inte längre är bounded
- nytt jobb behöver öppnas för att slutsatsen ska bli ärlig

Stop betyder: gör inte mer.

Eskalera betyder: fortsätt inte på eget initiativ, men lämna tillbaka ett tydligt problem och ett rekommenderat nästa steg.

---

## Livscykel

### 1. Control plane kompilerar envelope:n

Control plane löser först:

- mode
- risk/path-klassning
- scope IN / OUT
- förbjudna ytor
- required gates
- om review krävs

### 2. Worker exekverar inom envelope:n

Worker får ett smalt kontrakt och ska hålla sig inom det.

### 3. Integration plane klassar resultatet

Integration plane avgör om resultatet ska:

- ignoreras
- parkeras
- bli nästa deep-dive
- integreras i shared truth

Worker producerar bounded evidens. Integration plane avgör vad evidensen betyder i den större kartan.

---

## Praktisk tumregel

Om en worker behöver läsa roadmapen, SSOT:n och flera andra dokument för att förstå sitt uppdrag, då är envelope:n ännu inte tillräckligt bra kompilerad.

Målet är att worker-kontraktet ska vara så tydligt att workern främst behöver:

- sitt envelope
- sin pinnade startpunkt
- sina tillåtna inputs

Det är då modellen börjar bli robust på riktigt.
