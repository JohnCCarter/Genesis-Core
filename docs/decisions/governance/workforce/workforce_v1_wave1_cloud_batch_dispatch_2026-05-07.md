# Workforce v1 wave 1 cloud batch dispatch

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `dispatch-ready / docs-only / non-authoritative`
Skill usage: no suitable repository skill identified for this bounded docs/operational slice.

## Syfte

Det här dokumentet beskriver den första riktiga cloud-agent-batchen för workforce v1.

Det här dokumentet är **dispatch-ready only**.
Det är inte ett nytt governance-SSOT, inte en merge- eller truth-authority-surface och inte en automatisk godkännandeväg för senare implementation.

Batchen ärver och ändrar inte:

- `workforce_roadmap.md`
- `docs/governance/worker_governance_envelope.md`
- `docs/decisions/governance/workforce/workforce_v1_wave1_bootstrap_command_packet_2026-05-07.md`

Workers får producera bounded evidence, packet drafts eller branch-lokala kandidatändringar.
Endast control / integration lane får promotera resultat till backlog, roadmap, beslut eller merge-auktoritativt tillstånd.

## Batch-pins

- **Base branch:** `feature/next-slice-2026-05-06`
- **Base SHA:** `cf852ad8a559dfd8313405c3c30806fd3ff00e08`
- **Controller:** control / integration lane på aktuell feature-branch
- **Resolved mode:** `RESEARCH`
- **Primary objective:** öppna en liten cloud-batch som producerar användbar bounded evidence utan att skapa mer integrationsbörda än systemet kan adjudikera ärligt

## Cloud-visible input rule

För just denna dispatch-våg gäller:

- cloud workers får bara använda inputs som är commitade i repo:t och synliga på den dispatchade branchens remote
- lokala, `gitignored` eller ännu inte pushade artefakter är inte admissible cloud inputs i denna våg
- om en analysis note nämner ett regenerate-on-demand JSON är markdown-filen den cloud-visible evidence anchor; JSON-filen är inte required input om den inte finns på base branch

## Integrationsregel

Batchen får inte optimeras för maximal parallellism.
Batchen får bara köras så länge integrationsbackloggen är mindre än vad control / integration lane kan klassificera explicit.

Som huvudregel gäller:

- inga tysta merges
- inga direkta shared-truth writes från workers
- ingen worker får äga fler än en slice samtidigt
- om två workers börjar konvergera mot samma ownership tuple ska den senare workern stoppa och eskalera

## Ownership matrix

| Agent | Window | Question class | Output class | Activation state | Proposed branch |
| --- | --- | --- | --- | --- | --- |
| Agent A | `2023-06` | `D1 external falsifier` | `implementation-prepared deep-dive` | `primary` | `feature/cloud/deepdive/d1-2023-06-falsifier` |
| Agent B | `2017-06` | `corroborative packet framing` | `packet-first bounded prep` | `secondary` | `feature/cloud/deepdive/d1-2017-06-corroborative` |
| Agent C | `2023-04` | `fallback packet framing` | `packet-only` | `dormant until activated` | `feature/cloud/deepdive/d1-2023-04-fallback` |

Varje agent äger en distinkt tuple av:

- window
- question class
- output class
- activation state

Om arbete konvergerar mot en annan agents tuple måste workern stoppa och eskalera i stället för att duplicera, superseda eller omtolka den andra lane:n.

## Global off-limits för hela batchen

- `GENESIS_WORKING_CONTRACT.md`
- `docs/governance_mode.md`
- `.github/copilot-instructions.md`
- runtime/default/config-authority
- shared truth writes
- roadmap/backlog/decision promotion från worker själv
- March som primär loop
- July `2024` som primär subject
- late-2024 som återöppnad transport-loop

## Dispatch order

### 1. Agent A

Agent A är batchens primära deep-dive-lane.
Den får vara implementation-prepared, men bara inom sitt bounded dispatch-kontrakt.

### 2. Agent B

Agent B är corroborative och packet-first.
Den får inte börja imitera Agent A:s output class eller hypotesform.

### 3. Agent C

Agent C är fallback-only och ska vara dormant tills control plane uttryckligen aktiverar den.

## Review / return route

Varje agent måste returnera minst:

- `status`
- artifact paths eller packet paths
- `summary`
- `observed`
- `inferred`
- `unverified`
- `what_this_does_not_prove`
- `recommended_next_step`
- `recommended_integration_class`
- `base_sha_confirmed`
- `scope_adherence_report`

Det här är inte en automatisk integrationsväg.
Control / integration lane måste klassificera varje retur explicit som till exempel `ignore`, `park`, `deep-dive`, `duplicate`, `contradicted` eller `integrate`.

## Briefs in this batch

- `docs/decisions/governance/workforce/workforce_v1_wave1_agent_a_d1_2023_06_cloud_dispatch_2026-05-07.md`
- `docs/decisions/governance/workforce/workforce_v1_wave1_agent_b_d1_2017_06_cloud_dispatch_2026-05-07.md`
- `docs/decisions/governance/workforce/workforce_v1_wave1_agent_c_d1_2023_04_cloud_dispatch_2026-05-07.md`
