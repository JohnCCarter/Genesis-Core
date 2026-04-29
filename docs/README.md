# Documentation taxonomy

Den här README:n är den praktiska kartan över dokumentytorna i Genesis-Core.
Den är **inte** en egen SSOT och ändrar inte authority-precedence.

## Kärnregel

Separera alltid följande roller:

- **governance** — regler, constraints och authority
- **contracts** — stabila former och gränssnitt mellan världar
- **decisions** — slice-bundna beslut, packets, signoffs och closeouts
- **analysis** — mänskliga synteser, diagnosis och findings
- **research artifacts** — reproducerbara experimentbundlar och råa evidensytor

Historiska dokument kan fortfarande ligga i äldre mappar.
Den här taxonomin definierar fortfarande **framåtriktad placering**, men för `docs/decisions/` och `docs/analysis/` är root-tunga historiska korpusar nu redan migrerade till domändrivna undermappar.

## Rekommenderade ytor

### `docs/governance/`

Använd för styrande dokument och governance-specifik referensyta.
Här hör sådant hemma som definierar regler, mode, constraints eller operativa governance-modeller.

Typiska exempel:

- `docs/governance_mode.md`
- `docs/OPUS_46_GOVERNANCE.md`
- governance-lane-modeller
- governance-runbooks och mallar

Lägg **inte** nya slice-packets, signoffs eller lokala evidensnoter här om dokumentet inte själv är governance-policy.

### `docs/contracts/`

Använd för stabila former som binder ihop governance, kod och research.
Detta är den dokumenterade interfacenivån mellan världar.

Typiska exempel:

- state-/snapshot-kontrakt
- policy- eller router-beslutsformer
- veto-/label-/provenance-kontrakt
- artifact- eller manifestformer som flera ytor ska läsa likadant

### `docs/decisions/`

Använd för beslutsspår kring en viss slice.
Detta är platsen för dokument som förklarar _vad som beslutades nu_, under vilken authority och med vilket scope.
Rooten används nu främst för zon-guide och taxonomi/meta-packets; huvuddelen av beslutskorpusen ligger i domändrivna undermappar som beskrivs i `docs/decisions/README.md`.

Typiska exempel:

- precode-/command-packets
- launch- eller authorization-noter
- signoff-sammanfattningar
- closeout- och disposition-noter

### `docs/analysis/`

Använd för mänskligt läsbara synteser och diagnoser.
Här hör tolkning, sammanfattning och begreppsarbete hemma — inte governance-SSOT och inte råa experimentbundlar.
Rooten används nu främst för zon-guide; huvuddelen av analyskorpusen ligger i grova, domändrivna undermappar som beskrivs i `docs/analysis/README.md`.

Typiska exempel:

- findings-synteser
- jämförelsenoter
- architecture-/behavior-diagnoser
- narrativ sammanfattning av en forskningsserie

### `results/research/`

Använd för reproducerbara experimentbundlar och faskörningar.
Här ska maskinläsbara artefakter, manifest, tabeller, traces och råa jämförelser ligga nära sin experimentyta.

Typiska exempel:

- programmappar som `results/research/<program>/`
- `phase_*`-undermappar
- `manifest.json`, `artifacts.json`, `summary.md`, `tables/`, `traces/`

### `results/evaluation/`

Använd för kuraterade, commit-säkra, maskinläsbara sammanfattningar som andra docs kan peka på utan att dra in en hel forskningsbundle.

## Snabb placeringsguide

| Fråga                                                     | Rätt yta              |
| --------------------------------------------------------- | --------------------- |
| Är detta en regel eller authority-definition?             | `docs/governance/`    |
| Är detta en stabil form som andra ytor måste följa?       | `docs/contracts/`     |
| Är detta ett slice-beslut, packet eller closeout?         | `docs/decisions/`     |
| Är detta en tolkning eller syntes för mänsklig läsning?   | `docs/analysis/`      |
| Är detta reproducerbar experimentoutput eller rå evidens? | `results/research/`   |
| Är detta en liten kuraterad summary för vidare referens?  | `results/evaluation/` |

## Viktig försiktighetsregel

Existensen av ett dokument eller en bundle innebär inte i sig authority, promotion, readiness eller runtime-godkännande.
Läs alltid innehållet i rätt lagerordning:

1. governance
2. contracts
3. decisions
4. analysis / research artifacts
