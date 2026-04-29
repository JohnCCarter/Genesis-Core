# Governance docs index

Den här mappen samlar governance-specifika dokument och indexytor för Genesis-Core.

`docs/governance/**` är ett komplement till de högre styrlagren. Den här README:n är ett index, inte en egen SSOT.

## Roll i dokumenttaxonomin

Framåt ska `docs/governance/` användas för material som verkligen hör till governance-ytan, till exempel:

- mode-resolution och governance-regler
- governance-specifika lane- eller authority-modeller
- governance-runbooks, mallar och referensindex

Följande ska **normalt inte** nyförfattas här om dokumentet inte själv är governance-policy:

- slice-packets och andra beslutsspår
- signoffs eller closeouts
- långa evidenssynteser eller ad hoc-diagnoser
- råa researchbundlar

Framåtriktad placering för sådant material är i stället:

- `docs/decisions/` för packets, signoffs och closeouts
- `docs/contracts/` för stabila dokumenterade gränssnitt
- `docs/analysis/` för mänskliga synteser
- `results/research/` för reproducerbara experimentbundlar

Den stora historiska root-migreringen är nu genomförd för de root-dokument i `docs/governance/` som inte hörde till governance-kärnan.
Kvar här ska i normalfallet främst vara governance-core, modeller, runbooks, mallar och andra verkligt governance-specifika ytor.

## SSOT och precedence

Vid konflikt gäller följande:

1. Explicit användarbegäran för aktuell uppgift
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

För governance mode-resolution och mode-specifika operativa förväntningar gäller `docs/governance_mode.md` som SSOT.

Operativa dokument i `docs/governance/**` är **kompletterande**, inte överstyrande.

## Innehåll just nu

- `concept_evidence_runtime_lane_model_2026-04-23.md` — kanonisk praktisk definition av koncept-, evidens- och runtime-integrations-lanes
- `GENESIS_HYBRID_V1_1.md` — operativt kontrakt (hybridmodell)
- `templates/command_packet.md` — standardmall för start av uppgift
- `runbooks/trivial_fast_lane.md` — snabbspår för triviala ändringar

Historiska packet-, signoff- och closeout-dokument som låg direkt i governance-roten har flyttats till `docs/decisions/` eller `docs/analysis/` enligt faktisk dokumentroll.
Äldre material i andra ytor ska fortfarande läsas med respekt för innehållets faktiska roll, inte enbart efter mappnamnet.

## Användning (kort)

1. Lös mode deterministiskt från `docs/governance_mode.md`.
2. Klassificera risk (LOW/MED/HIGH) enligt kontraktet.
3. Välj path (Quick/Lite/Full) och lås Scope IN/OUT.
4. Om arbetet är research-/governance-tungt: klassificera vilket arbetslane som gäller enligt `concept_evidence_runtime_lane_model_2026-04-23.md`.
5. Lägg nya slice-beslut i rätt framåtriktad yta (`docs/decisions/`, `docs/contracts/`, `docs/analysis/`, `results/research/`) i stället för att reflexmässigt lägga allt under governance.
6. Kör gates och producera evidens innan `READY_FOR_REVIEW`.
