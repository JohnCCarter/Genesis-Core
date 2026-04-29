# Decision records

Den här mappen är den framåtriktade ytan för beslutsspår i Genesis-Core.
Den är **inte** governance-SSOT och den är **inte** den primära platsen för råa research-artefakter.

## Syfte

Här dokumenteras vad som beslutades i en avgränsad slice:

- vilket problem som adresserades
- vilken authority och vilket mode som gällde
- vilket scope som var låst
- vilka constraints och stop conditions som användes
- hur slicen stängdes eller parkerades

## Hit hör

- command-/precode-packets
- launch- eller authorization-noter
- signoff-sammanfattningar
- closeout- och disposition-noter
- ADR-liknande dokument för ett konkret vägval

## Hit hör inte

- governance-SSOT eller mode-definitioner
- stabila kontrakt eller formella interfaces
- råa experimentbundlar och tabellutskrifter
- långa findings-synteser som främst är analys

## Namngivning

Behåll repo-native namn när det hjälper spårbarheten, till exempel:

- `*_packet_YYYY-MM-DD.md`
- `*_authorization_YYYY-MM-DD.md`
- `*_signoff_YYYY-MM-DD.md`
- `*_closeout_YYYY-MM-DD.md`

Om ett dokument både innehåller beslut och evidens bör evidensen refereras ut till `results/research/` eller en syntes i `docs/analysis/` i stället för att bära hela bevismassan här.

## Historisk not

Den historiska root-migreringen från `docs/governance/` är nu genomförd för packet-, signoff-, closeout- och närliggande beslutsdokument som tidigare låg där direkt.
Den här mappen är därför både framåtriktad standard och nuvarande hemvist för den större rotmängden av historiska beslutsspår.
