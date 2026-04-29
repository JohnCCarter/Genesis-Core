# Governance docs index

Den här mappen samlar operativa governance-dokument för Genesis-Core.

`docs/governance/**` är ett komplement till de högre styrlagren. Den här README:n är ett index, inte en egen SSOT.

## SSOT och precedence

Vid konflikt gäller följande:

1. Explicit användarbegäran för aktuell uppgift
2. `.github/copilot-instructions.md`
3. `docs/OPUS_46_GOVERNANCE.md`
4. `AGENTS.md`

För governance mode-resolution och mode-specifika operativa förväntningar gäller `docs/governance_mode.md` som SSOT.

Operativa dokument i `docs/governance/**` är **kompletterande**, inte överstyrande.

## Innehåll

- `concept_evidence_runtime_lane_model_2026-04-23.md` — kanonisk praktisk definition av koncept-, evidens- och runtime-integrations-lanes
- `GENESIS_HYBRID_V1_1.md` — operativt kontrakt (hybridmodell)
- `templates/command_packet.md` — standardmall för start av uppgift
- `runbooks/trivial_fast_lane.md` — snabbspår för triviala ändringar

## Användning (kort)

1. Lös mode deterministiskt från `docs/governance_mode.md`.
2. Klassificera risk (LOW/MED/HIGH) enligt kontraktet.
3. Välj path (Quick/Lite/Full) och lås Scope IN/OUT.
4. Om arbetet är research-/governance-tungt: klassificera vilket arbetslane som gäller enligt `concept_evidence_runtime_lane_model_2026-04-23.md`.
5. Kör gates och producera evidens innan `READY_FOR_REVIEW`.
