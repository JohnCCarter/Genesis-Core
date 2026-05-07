# Worker governance envelope

## Syfte

Det här dokumentet definierar den worker-facing operativa specen för parallella cloud workers och andra isolerade branch/checkouts.

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
- sin output- och artifact-kontraktversion

En worker ska inte behöva full chatthistorik eller hela governance-stacken för att förstå vad som gäller.
Om den behöver det har control plane inte kompilerat governance tillräckligt långt.

---

## Auktoritet och precedence

### Global governance är alltid auktoritativ

Repo-governance förblir alltid överordnad worker-lokala dokument, checkout-lokala filer eller dispatch-filer.

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

Resolved mode bestäms via `docs/governance_mode.md`, inte via lokal checkout-fil, worker-prompt eller worktree-lokal fil.

Envelope:n ska därför bära med sig:

- `resolved_mode`
- `mode_source`
- `authority_source`

Den får däremot inte själv ändra dem.

---

## Branch-, checkout- och dispatch-disciplin

Varje worker ska utgå från:

- samma integrationsgren eller samma auktoriserade basgren
- samma `base_sha` för den aktuella dispatch-vågen
- egen branch
- egen isolerad checkout
- egen dispatch-instans

Molnexecution ska därför förstås som:

- en worker = en isolerad branch/checkout
- en worker = en bounded fråga
- en worker = ett eget outputkontrakt

Lokala worktrees kan användas av control plane för koordinering eller debugging, men de är bara en operatörskonveniens.
De är inte workforce-definitionen, inte ett krav för cloud execution och inte en auktoritetssurface.

### Branchnamn ska bära mode där det är möjligt

Eftersom `docs/governance_mode.md` använder branchmappning ska worker-brancher bära mode i namnet.

Exempel:

- `feature/cloud/mixed/2017-2023-chronology`
- `feature/cloud/inventory/annual-scan-batch-a`
- `research/cloud/sign/insufficient-evidence-holdout`
- `sandbox/cloud/probe/example-x`

Undvik:

- `wt/...`

Anledningen är att `wt/...` inte matchar `feature/*`, `research/*`, `sandbox/*` eller `spike/*` och därför riskerar att falla tillbaka till `STRICT`.

### Hårda branchregler

- samma branch ska inte checkas ut aktivt i flera workers samtidigt
- en worker får inte själv byta branchkonvention mitt under ett jobb
- checkout-lokala filer får aldrig användas för att override:a resolved mode
- workers får inte dela muterbart tillstånd med varandra
- session recovery ska utgå från envelope, dispatch-status och artefaktregister, inte från att tidigare chatthistorik råkar finnas kvar

---

## Worker-klasser och kapabiliteter

| Worker-klass   | Repo-write?                               | Commit allowed?                           | Shared truth write?              | Typiska outputs                                          | Kommentar                                |
| -------------- | ----------------------------------------- | ----------------------------------------- | -------------------------------- | -------------------------------------------------------- | ---------------------------------------- |
| Inventory      | Normalt nej                               | Normalt nej                               | Nej                              | shortlist, ranking, artifacts, summary                   | read-only med hårda gränser              |
| Deep-dive      | Ja, inom exakt scope                      | Ja                                        | Nej                              | packet, analysis note, ev. explicit tillåten helper/test | bounded repo-write i egen branch         |
| Integration    | Ja                                        | Ja                                        | Ja                               | re-anchor, synthesis, integration decisions              | enda normala vägen för shared truth      |
| Runtime/strict | Endast via explicit separat auktorisering | Endast via explicit separat auktorisering | Endast när uttryckligen tillåtet | strikt styrda ändringar                                  | reserverad klass, normalt avstängd i MVP |

Den viktigaste regeln är att ingen worker själv får uppgradera betydelsen av sitt resultat.

En worker får hitta något intressant, men får inte själv besluta att resultatet nu är:

- repo-sanning
- readiness
- promotion-underlag
- runtime-auktoritet

Det sker i integration plane.

---

## Fält som varje envelope minst ska innehålla

| Fält                    | Syfte                                                              |
| ----------------------- | ------------------------------------------------------------------ |
| `task_id`               | unik identifierare för jobbet                                      |
| `dispatch_id`           | identifierare för själva dispatch-instansen                        |
| `worker_class`          | vilken kapabilitetsklass workern tillhör                           |
| `base_branch`           | basgren för dispatch-vågen                                         |
| `base_sha`              | pinnad startpunkt                                                  |
| `worker_branch`         | worker-specifik branch                                             |
| `resolved_mode`         | mode som redan lösts av control plane                              |
| `mode_source`           | varför mode blev som det blev                                      |
| `authority_source`      | vilken SSOT som gav mode/auktoritet                                |
| `change_class`          | t.ex. `docs-only`, `tooling`, `runtime-touching`                   |
| `lane`                  | arbetslane, t.ex. `research-evidence`                              |
| `question`              | exakt fråga som ska besvaras                                       |
| `question_fingerprint`  | stabil identitet för frågan så att duplicat/överlapp kan upptäckas |
| `subject`               | avgränsat subject för jobbet                                       |
| `scope_in`              | vad workern får röra                                               |
| `scope_out`             | vad workern uttryckligen inte får röra                             |
| `allowed_inputs`        | godkända datakällor och artefakter                                 |
| `input_artifact_hashes` | låsta referenshashar för kritiska inputs när slicen kräver det     |
| `allowed_output_types`  | vilka outputtyper workern får producera                            |
| `artifact_contract`     | vilken artifact-familj och naming-regel som workern ska följa      |
| `output_schema_version` | version av outputformatet som måste följas                         |
| `envelope_hash`         | kontrollhash för det kompilerade kontraktet                        |
| `forbidden_surfaces`    | ytor som alltid ska behandlas som förbjudna                        |
| `repo_write_allowed`    | om worker får skriva till repo över huvud taget                    |
| `commit_allowed`        | om worker får göra commits                                         |
| `shared_truth_write`    | om worker får uppdatera shared truth                               |
| `review_required`       | om review krävs innan landing                                      |
| `gates_required`        | vilka gates som måste köras                                        |
| `done_criteria`         | vad som räknas som klar output                                     |
| `stop_conditions`       | när workern måste stoppa direkt                                    |
| `escalation_conditions` | när workern ska lämna tillbaka jobbet till control plane           |

Om något av de här fälten är oklart ska workern inte gissa. Den ska stoppa eller eskalera.

---

## Minimal manifestmall

```yaml
task_id: mixed-2017-2023-cadence
dispatch_id: mixed-2017-2023-cadence-run-001
worker_class: deep-dive
base_branch: feature/next-slice-2026-05-06
base_sha: <PINNED_SHA>
worker_branch: feature/cloud/mixed/2017-2023-cadence
resolved_mode: RESEARCH
mode_source: branch:feature/cloud/mixed/2017-2023-cadence
authority_source: docs/governance_mode.md
change_class: docs-only
lane: research-evidence
question: "Compare internal cadence inside the fixed dominant windows for 2017-03 and 2023-12"
question_fingerprint: qfp_mixed_2017_2023_cadence_v1
envelope_hash: <COMPILED_ENVELOPE_HASH>
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
input_artifact_hashes:
  - <ARTIFACT_SHA256>
allowed_output_types:
  - packet
  - analysis_note
artifact_contract:
  family: research-evidence
  naming: deterministic
output_schema_version: 1
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
- summary
- observed
- inferred
- unverified
- `what_this_does_not_prove`
- `contradictions_found`
- `assumptions_rejected`
- `recommended_next_step`
- `recommended_integration_class`
- provenance
- `base_sha_confirmed`
- `scope_adherence_report`

Epistemisk separation är hård:

- `observed` = direkt stödbara utsagor från returnerade artefakter
- `inferred` = tolkning som fortfarande kräver integration-plane-bedömning
- `unverified` = öppna hypoteser, luckor eller osäkerheter

Worker outputs förblir alltid proposals/evidence only.
De blir inte authoritative truth, merge approval eller runtime-authority utan kontrollplansgranskning.

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

- upptäcker att envelope:n är ofullständig eller självmotsägande
- ser `base_sha`- eller branch-mismatch
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
- output skulle kräva tolkning utanför `observed`-nivån för att verka meningsfull

Stop betyder: gör inte mer.

Eskalera betyder: fortsätt inte på eget initiativ, men lämna tillbaka ett tydligt problem och ett rekommenderat nästa steg.

---

## Livscykel

### 1. Control plane löser mode och pinnad startpunkt

Control plane fastställer först:

- mode
- `base_branch`
- `base_sha`
- om dispatchen över huvud taget är redo att öppnas

### 2. Governance compiler kompilerar envelope:n

Governance compiler låser sedan:

- risk/path-klassning
- scope IN / OUT
- förbjudna ytor
- required gates
- om review krävs

Envelope:n ska efter detta betraktas som immutabel under körning.

### 3. Worker validerar envelope innan exekvering

Workern ska bekräfta:

- `base_sha`
- branch/check-out
- required inputs
- outputschema
- att inga förbjudna ytor behövs

### 4. Worker exekverar inom envelope:n

Worker får ett smalt kontrakt och ska hålla sig inom det.

### 5. Integration plane klassar resultatet

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
- sitt outputschema och artifact-kontrakt

Det är då modellen börjar bli robust på riktigt.
