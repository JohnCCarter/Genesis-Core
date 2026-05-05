# Documentation contracts

Den här mappen är avsedd för stabila dokumenterade gränssnitt mellan governance, kod och research.
Fokus här är **form**, **invarians** och **tolkningsstabilitet** — inte slice-journalföring.

## Syfte

Använd `docs/contracts/` när ett dokument beskriver en varaktig struktur som flera ytor behöver läsa eller implementera likadant.

Typiska kontraktstyper:

- state-/snapshot-former
- policy-, router- eller veto-beslutsformer
- label- och taxonomi-kontrakt
- provenance-, manifest- eller artifact-former
- dokumenterade invariants mellan kod och evidensytor

## Hit hör inte

- tillfälliga packets eller launch-noter
- enskilda experimentsammanfattningar
- governance-SSOT bara för att något känns viktigt
- råa tabeller, traces eller ad hoc-diagnoser

## Kvalitetsribba

Ett kontraktsdokument här bör normalt vara:

- namnstabilt
- tydligt avgränsat
- explicit om fält, invariants och konsumenter
- tydligt med versionering eller backcompat-krav om formen kan utvecklas

## Arbetsregel

Om ett dokument främst svarar på frågan **"vilken form måste andra följa?"** hör det sannolikt hemma här.
Om det i stället svarar på **"vad beslutade vi i den här slicen?"** hör det sannolikt hemma i `docs/decisions/`.
