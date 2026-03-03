# Governance docs index

Den här mappen samlar operativa governance-dokument för Genesis-Core.

## SSOT och precedence

Vid konflikt gäller följande ordning:

1. `AGENTS.md`
2. `docs/governance_mode.md`
3. `.github/copilot-instructions.md`
4. Operativa dokument i `docs/governance/**`

`docs/governance/**` är **kompletterande**, inte överstyrande, i förhållande till SSOT.

## Innehåll

- `GENESIS_HYBRID_V1_1.md` — operativt kontrakt (hybridmodell)
- `templates/command_packet.md` — standardmall för start av uppgift
- `runbooks/trivial_fast_lane.md` — snabbspår för triviala ändringar

## Användning (kort)

1. Lös mode deterministiskt från `docs/governance_mode.md`.
2. Klassificera risk (LOW/MED/HIGH) enligt kontraktet.
3. Välj path (Quick/Lite/Full) och lås Scope IN/OUT.
4. Kör gates och producera evidens innan `READY_FOR_REVIEW`.
