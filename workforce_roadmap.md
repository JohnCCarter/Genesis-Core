# Workforce roadmap

## Syfte

Det här dokumentet beskriver den övergripande arbetsmodellen för att köra många parallella research-spår utan att förlora repo-sanning, governance eller spårbarhet.

Det här är **översiktsdokumentet**.

Det här är också en **retained target-model surface** för explicit aktiverade slice-workers.
Det skapar inte stående worker-identiteter och ger inte implicit worker-till-worker-kedjning någon auktoritet.
Den levande terminologin i retained governance-docs beskriver numera editor workers som defaultmodell.
Det i sig ändrar inte runtime-kapabiliteter, automationsgarantier eller authority boundaries.

Det är inte:

- mode-SSOT
- worker-lokalt kontrakt
- detaljspec för manifestfält
- kö- eller dispatch-lista för den aktuella vågen

Worker-facing operativa detaljer finns i:

- [`docs/governance/worker_governance_envelope.md`](docs/governance/worker_governance_envelope.md)

Global mode- och governance-auktoritet finns i:

- [`docs/governance_mode.md`](docs/governance_mode.md)

Aktiv branch-sanning och nuvarande admissible steg hålls i:

- `GENESIS_WORKING_CONTRACT.md`

---

## Kärnprincip

Den bärande regeln är fortfarande denna:

> **Parallellisera evidensproduktionen. Centralisera sanningsintegrationen.**

Det betyder att vi vill ha:

- parallell produktion
- seriell integration
- pinnad provenance
- ren governance

Det betyder också att vi inte vill ha:

- en gigantisk manuell kö
- flera workers som skriver i samma sanningsdokument samtidigt
- kartesisk explosion över alla år, alla signs, alla slices och alla windows

---

## Nästa verkliga flaskhals: integrations-explosion

När många workers returnerar samtidigt är problemet inte främst dispatch.
Problemet är adjudikering:

- duplicat
- överlappande findings
- motsägelser
- stale `base_sha`
- saknad provenance
- outputs som antyder mer än de bevisar

Det betyder att workforce inte ska optimeras för maximal parallellism.
Det ska optimeras för maximal sanningsdensitet per enhet integrationsarbete.

Som huvudregel gäller därför:

- dispatch styrs av integrationsbacklogg, inte bara av lediga workers
- samma fråga ska inte öppnas i flera workers samtidigt
- varje worker ska äga en egen domän, ett eget bounded scope och en egen outputyta
- integration plane måste klassificera varje retur explicit

---

## Arkitekturen i åtta plan

### 1. Control plane

Control plane är styrskiktet. Det avgör:

- vad som är aktivt
- vad som är stängt
- vad som är nästa admissible steg
- vilka workers som får jobba på vad
- vilken `base_sha` och vilken fråga som gäller
- hur mycket integrationsarbete som samtidigt får skapas

Kort sagt: detta är hjärnan.

### 2. Governance compiler

Governance compiler är översättningsskiktet mellan global repo-governance och worker-kontrakt.

Det avgör:

- resolved mode
- authority source
- scope IN / OUT
- förbjudna ytor
- gates, stop conditions och escalation conditions

Som huvudregel ska rutinmässig dispatch börja från `QUICK_REF` och bara läsa tyngre SSOT-dokument när risk, konflikt eller känslig yta kräver det.

Kort sagt: detta är kompilatorn.

### 3. Scheduler / dispatch queue

Scheduler bestämmer vad som får starta nu.

Den väger:

- lane-prioritet
- förväntat research-värde
- kostnad
- beroenden
- contradiction pressure
- integrationsbacklogg
- tillgänglig budget

Kort sagt: detta är tempot.

### 4. Worker plane

Worker plane är allt som kör parallellt.

Varje worker får:

- en editor-attached exekveringsyta (normalt den delade lokala `Genesis-Core`-checkouten på `feature/editor-worker-orchestrator`)
- en egen bounded ownership-tuple / scope
- en exakt fråga
- ett kompilerat kontrakt

En worker ska här förstås som en långlivad worker-identitet.
Den aktiva arbetsenheten är däremot alltid en bounded slice / execution leg.
Samma worker får därför arbeta över flera slices över tid, men aldrig äga mer än en aktiv slice åt gången och aldrig fortsätta utan explicit nästa admissible slice från control / integration plane.

Den normala lokala editor-worker-ytan är den delade `Genesis-Core`-checkouten på `feature/editor-worker-orchestrator`.
Separata worktrees kan användas av control- eller integration plane när explicit isolering krävs, men de är inte defaultmodellen, inte workforce-definitionen och inte en auktoritetssurface.

Kort sagt: detta är muskeln.

### Default worker model

Den operativa defaultmodellen för Genesis editor workers ska vara:

- en editor worker = en **autonomous slice worker**
- de flesta editor workers delar samma grundroll, samma governance-ram och samma returformat
- samma custom agent eller promptyta ska normalt återanvändas över flera editorfönster i samma checkout; skillnaden mellan workers ska uttryckas i deras envelope, bounded scope och slice, inte i olika standardpersonligheter eller separata worktrees som default
- variation ska i första hand ligga i slice-kontraktet: år/window, fråga, scope, inputs, gates och done criteria
- asymmetriska batchroller som `primary`, `corroborative` eller `fallback` får förekomma som daterade dispatch-strategier, men de är inte workforce-definitionen och ska inte behandlas som långsiktiga worker-personligheter

Det betyder att workforce-systemet i normalfallet ska dispatcha samma sorts worker på olika bounded slices, snarare än att uppfinna olika agentpersonligheter för varje år eller uppgift.

### 5. Evidence store

Evidence store innehåller bounded output som ännu inte är repo-sanning.

Exempel:

- shortlistor
- JSON-artifacts
- candidate reports
- draft-notes
- null-resultat
- determinism-hashar

Detta lager får vara produktivt, men ska alltid vara tydligt märkt som exploratory och pending integration.

### 6. Artifact registry

Artifact registry indexerar det som kommer tillbaka.

Det ska kunna hålla reda på:

- artifact-id
- `task_id`
- `base_sha`
- worker-id / branch
- lineage
- claim- eller question-fingerprint
- status i integrationskön

Kort sagt: detta är minnet.

### 7. Review / gate layer

Review / gate layer säkerställer att workers inte bara returnerar output, utan returnerar verifierbar output.

Det innefattar:

- editor diagnostics
- scoped linters och pre-commit
- nödvändiga tester
- determinism- eller hashkontroller när slicen kräver det

Kort sagt: detta är filtret.

### 8. Integration plane

Integration plane är den smala slussen där vi avgör:

- vad som faktiskt blev sant
- vad som ska landa i repo
- vad som ska parkeras
- vad som bara var brus

Som huvudregel är det bara integration plane som får uppdatera shared truth, till exempel:

- `GENESIS_WORKING_CONTRACT.md`
- större synteser
- repo-sanning om “next admissible step”

---

## Jobbfamiljer och worker-klasser

Det är viktigt att skilja på jobbtyp och worker-klass.

Det är också viktigt att skilja på worker-klass och worker-personlighet.
En worker-klass beskriver främst kapabilitets- och permissionsyta.
Den ska inte i normalfallet användas för att skapa flera olika långlivade editor-worker-identiteter när samma grundworker kan dispatchas på olika bounded slices.

### Jobbfamiljer

| Jobbfamilj | Syfte                                                   |
| ---------- | ------------------------------------------------------- |
| Inventory  | bred scan, ranking, harvesting och shortlist-byggande   |
| Deep-dive  | bounded slice som testar eller fördjupar en exakt fråga |
| Synthesis  | sammanför vad som faktiskt ändrat kartan                |

### Worker-klasser

| Worker-klass   | Huvudroll                                               |
| -------------- | ------------------------------------------------------- |
| Inventory      | read-only evidensproduktion                             |
| Deep-dive      | bounded repo-write inom exakt scope                     |
| Integration    | central landing, parkering och shared-truth-uppdatering |
| Runtime/strict | reserverad klass för explicit separat auktorisering     |

Worker-specifika kapabiliteter, precedence-regler och manifestfält hör hemma i den separata envelope-specen.

Som operativ default bör de flesta editor workers i Genesis dispatchas som samma grundläggande slice-worker-modell inom samma kapabilitetsklass, och skiljas åt av sin envelope snarare än av sin identitet.
Inventory-, integration- och runtime/strict-klasserna förblir specialiseringar, inte ett krav på en asymmetrisk worker-flotta.

---

## Branches, checkouts och isolation

Gemensam control-plane-branch i den här vågen är:

- `feature/editor-worker-orchestrator`

Den praktiska starttopologin för branch/worktree-disciplin dokumenteras i:

- [`docs/governance/runbooks/editor_slice_worker_dispatch.md`](docs/governance/runbooks/editor_slice_worker_dispatch.md)

Varje editor worker ska utgå från:

- samma basgren eller auktoriserad integrationsgren
- samma `base_sha` för vågen
- samma lokala checkout om inte separat isolering uttryckligen krävs
- ett eget bounded ownership-scope
- egen issue eller dispatch-brief

Lokala worktrees kan användas av control plane för koordinering eller debugging när en slice kräver branch-isolering, konfliktfri repo-write, destruktiva git-operationer eller PR-förberedelse.
De är däremot inte defaultmodellen, inte workforce-definitionen, inte en separat governance-auktoritet och inte en genväg runt envelope-kontraktet.

Om en slice uttryckligen flyttas till separat branch bör branchnamnet bära mode där det är möjligt, till exempel:

Exemplen nedan är illustrativa.
De definierar inte ett obligatoriskt branchprefix eller ett nytt authority-lager.

- `feature/inventory/...`
- `feature/deepdive/...`
- `research/sign/...`
- `sandbox/probe/...`

Undvik:

- `wt/...` som definition av workforce-modellen

Detaljerad branch- och envelope-disciplin finns i:

- [`docs/governance/worker_governance_envelope.md`](docs/governance/worker_governance_envelope.md)

---

## Hårda regler i roadmap-form

### 1. Allt måste vara pinnat

Varje jobb måste vara bundet till en tydlig `base_sha`, en exakt fråga och ett bounded subject.

### 2. Workers får inte improvisera repo-sanning

En worker får hitta något intressant, men får inte själv uppgradera resultatet till shared truth, readiness eller runtime-auktoritet.

### 3. Shared truth ska ha en smal skrivväg

Delade sanningsdokument ska inte uppdateras direkt från flera workers eller flera parallella PR-spår samtidigt.

### 4. Lokal envelope får bara snäva in

Worker-lokala kontrakt får bara begränsa ytterligare. De får aldrig override:a repo-SSOT.

### 5. Undvik kartesisk explosion

Arbetsflödet ska normalt vara:

1. inventory
2. score
3. shortlist
4. deep-dive
5. synthesis

### 6. Integrationsbacklogg sätter tempot

Frågan är inte hur många workers vi kan starta.
Frågan är hur många returer integration plane kan adjudikera utan att börja parkera, duplicera eller feltolka resultat.

### 7. Session recovery ska vara artefaktdriven

Editor workers ska kunna återuppta från envelope, dispatch-status och registrerade artefakter.
De ska inte kräva full chatthistorik för att förstå sitt uppdrag.

För långlivade workers gäller samma sak mellan slices: continuation ska utgå från explicit retur-/handoff-state, ny envelope och registrerade artefakter, inte från att workern "minns" tidigare chatt eller improviserar nästa steg.

---

## Version 1: enkel men riktig

Version 1 av modellen bör hållas enkel.

### Rekommenderad startnivå

- Aktiva editor workers samtidigt: `1–3`
- Default worker-roll: `autonomous slice worker`
- Dominerande dispatch-mönster: samma worker-roll på olika bounded slices
- Asymmetrisk batchdesign: tillåten som pilot eller när integrationsrisk kräver det, men inte default
- Integration lane: `1`

En bra första batch är därför normalt:

- `1–3` slice-workers med samma grundroll
- distinkta ownership tuples per worker
- en aktiv slice per worker
- explicit integration-lane-kapacitet att ta emot alla returer

Om en asymmetrisk wave används i pilotform ska det vara en uttrycklig dispatch-strategi, inte ett antagande om att workers i sig har olika permanenta roller.

Hård regel:

- en **aktiv slice / execution leg** = en bounded slice = ett explicit ownership-kontrakt i den valda exekveringsytan
- separat branch/PR behövs först när slicen uttryckligen flyttas till en isolerad landing-yta
- en långlivad worker får ta flera execution legs sekventiellt över tid
- samma worker får aldrig äga fler än en aktiv slice samtidigt
- continuation kräver explicit klassificerad retur och refreshed bounded envelope; workern får inte själv välja nästa slice

### Tillåtna deep-dive-domäner just nu

- mixed-year exact-window-frågor
- sign-spår shortlist/falsifier
- bounded negative/positive control subjects

### Förbjudet för vanliga workers

- direkt uppdatering av `GENESIS_WORKING_CONTRACT.md` utanför integration
- runtime/config work utan separat auktorisering
- bred synthesis utan explicit handoff

---

## Vad workers faktiskt ska läsa

Roadmapen är inte den primära körinstruktionen för en worker.

Det workers faktiskt ska arbeta efter är:

- sin envelope / sitt dispatch-kontrakt
- sin pinnade startpunkt
- sina tillåtna inputs
- vid continuation: sin explicit refererade handoff-/returstate från föregående slice

Det är därför den operativa specen nu är bruten ur roadmapen och lagd i:

- [`docs/governance/worker_governance_envelope.md`](docs/governance/worker_governance_envelope.md)

---

## Nästa konkreta förbättringar

När modellen ska skärpas vidare är de viktigaste nästa stegen:

1. **föreslagen:** definiera hur control plane routar från avslutad slice till nästa admissible slice utan self-widening
2. **föreslagen:** definiera slice-bundna access frames för docs / code / config / scripts / backtests / artifacts
3. **föreslagen:** definiera retur-/handoff-state för långlivade workers mellan slices
4. definiera integrationsklassificering för `ignore / park / duplicate / contradicted / deep-dive / integrate`
5. definiera evidence graph med lineage-, contradiction- och supersession-kanter
6. definiera artifact registry och canonical naming
7. definiera scheduler som väger integrationsbacklogg mot nytt research-värde
8. definiera retry/idempotency-regler för editor workers

---

## Slutsats

Poängen med modellen är inte att göra varje worker smartare.

Poängen är att göra varje worker smalare, säkrare och lättare att styra.

Kort slutbild:

- en control-plane-branch
- flera domain-isolerade editor workers med olika bounded scopes i samma checkout som default
- separat branch/worktree bara när explicit isolering behövs
- inventory brett
- deep-dive selektivt
- shared truth bara via integration
- editorn som worker-yta
- lokala worktrees som valfri isoleringsyta, inte som separat governance-lager
- repo som sanningslager
