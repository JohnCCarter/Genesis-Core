# Workforce roadmap

## Syfte

Det här dokumentet beskriver den övergripande arbetsmodellen för att köra många parallella research-spår utan att förlora repo-sanning, governance eller spårbarhet.

Det här är **översiktsdokumentet**.

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

## Arbetsmodellen i fyra lager

### 1. Control plane

Control plane är styrskiktet. Det avgör:

- vad som är aktivt
- vad som är stängt
- vad som är nästa admissible steg
- vilka workers som får jobba på vad
- vilken `base_sha` och vilken fråga som gäller

Kort sagt: detta är hjärnan.

### 2. Worker plane

Worker plane är allt som kör parallellt.

Varje worker får:

- en isolerad checkout eller worktree
- en egen branch
- en exakt fråga
- ett kompilerat kontrakt

Kort sagt: detta är muskeln.

### 3. Evidence plane

Evidence plane innehåller bounded output som ännu inte är repo-sanning.

Exempel:

- shortlistor
- JSON-artifacts
- candidate reports
- draft-notes
- null-resultat
- determinism-hashar

Detta lager får vara produktivt, men ska alltid vara tydligt märkt som exploratory och pending integration.

### 4. Integration plane

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

### Jobbfamiljer

| Jobbfamilj | Syfte                                                   |
| ---------- | ------------------------------------------------------- |
| Inventory  | bred scan, ranking, harvesting och shortlist-byggande   |
| Deep-dive  | bounded slice som testar eller fördjupar en exakt fråga |
| Synthesis  | sammanför vad som faktiskt ändrat kartan                |

### Worker-klasser

| Worker-klass | Huvudroll                                               |
| ------------ | ------------------------------------------------------- |
| Inventory    | read-only evidensproduktion                             |
| Deep-dive    | bounded repo-write inom exakt scope                     |
| Integration  | central landing, parkering och shared-truth-uppdatering |

Worker-specifika kapabiliteter, precedence-regler och manifestfält hör hemma i den separata envelope-specen.

---

## Branches och worktrees

Gemensam integrationsbranch i den här vågen är:

- `feature/next-slice-2026-05-06`

Varje worker ska utgå från:

- samma basgren eller auktoriserad integrationsgren
- samma `base_sha` för vågen
- egen branch
- egen worktree eller isolerad checkout

Branchnamn bör bära mode där det är möjligt, till exempel:

- `feature/wt/...`
- `research/wt/...`
- `sandbox/wt/...`

Detaljerad branch- och envelope-disciplin finns i:

- [`docs/governance/worker_governance_envelope.md`](docs/governance/worker_governance_envelope.md)

---

## Hårda regler i roadmap-form

### 1. Allt måste vara pinnat

Varje jobb måste vara bundet till en tydlig `base_sha`, en exakt fråga och ett bounded subject.

### 2. Workers får inte improvisera repo-sanning

En worker får hitta något intressant, men får inte själv uppgradera resultatet till shared truth, readiness eller runtime-auktoritet.

### 3. Shared truth ska ha en smal skrivväg

Delade sanningsdokument ska inte uppdateras från flera worktrees samtidigt.

### 4. Lokal envelope får bara snäva in

Worker-lokala kontrakt får bara begränsa ytterligare. De får aldrig override:a repo-SSOT.

### 5. Undvik kartesisk explosion

Arbetsflödet ska normalt vara:

1. inventory
2. score
3. shortlist
4. deep-dive
5. synthesis

---

## Version 1: enkel men riktig

Version 1 av modellen bör hållas enkel.

### Rekommenderad startnivå

- Inventory workers: `6–12`
- Deep-dive workers: `2–4`
- Integration worker: `1`

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

Det är därför den operativa specen nu är bruten ur roadmapen och lagd i:

- [`docs/governance/worker_governance_envelope.md`](docs/governance/worker_governance_envelope.md)

---

## Nästa konkreta förbättringar

När modellen ska skärpas vidare är de viktigaste nästa stegen:

1. definiera integrationsmatris för `ignore / park / deep-dive / integrate`
2. definiera evidence-/artifact-klassning
3. definiera dedupe-identitet för jobb
4. definiera dispatch- eller queue-format för aktiva vågor

---

## Slutsats

Poängen med modellen är inte att göra varje worker smartare.

Poängen är att göra varje worker smalare, säkrare och lättare att styra.

Kort slutbild:

- en integrationsgren
- många isolerade worker-worktrees/checkouts
- en branch per worker
- inventory brett
- deep-dive selektivt
- shared truth bara via integration
- molnet som worker-fabrik
- repo som sanningslager
