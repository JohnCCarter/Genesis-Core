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

## Nuvarande subfolder-topologi

Rooten används nu bara för zon-guiden och explicita taxonomi-packets.
Övriga beslutsspår ligger i domändrivna undermappar:

- `regime_intelligence/`
  - `advisory_environment_fit/`
  - `policy_router/`
  - `router_replay/`
  - `p1_off_parity/`
  - `experiment_map/`
  - `upstream_candidate_authority/`
  - `optuna/challenger_family/`
  - `optuna/decision/`
  - `optuna/signal/`
  - `core/`
- `feature_attribution/`
  - `v1/`
  - `post_phase14/`
- `scpe_ri_v1/`
- `volatility_policy/`
- `diagnostic_campaigns/`
- `research_findings/`

## Buckets med snäv betydelse

- `regime_intelligence/core/` är reserverad för corpusnivåmaterial som inte
  hör hemma i en smalare RI-ström som `policy_router`, `router_replay` eller
  `optuna`. Den är **inte** en allmän overflow-bucket.
- `research_findings/` lagrar endast beslutsspår för syntetiserade findings och
  preflight/bootstrap-linjer. Rå evidens, scratch-artefakter och genererade
  outputs hör hemma någon annanstans.

## Namngivning

Behåll repo-native namn när det hjälper spårbarheten, till exempel:

- `*_packet_YYYY-MM-DD.md`
- `*_authorization_YYYY-MM-DD.md`
- `*_signoff_YYYY-MM-DD.md`
- `*_closeout_YYYY-MM-DD.md`

Om ett dokument både innehåller beslut och evidens bör evidensen refereras ut till `results/research/` eller en syntes i `docs/analysis/` i stället för att bära hela bevismassan här.

## Historisk not

Den historiska root-migreringen från `docs/governance/` är nu genomförd för packet-, signoff-, closeout- och närliggande beslutsdokument som tidigare låg där direkt.
Den här mappen är därför både framåtriktad standard och nuvarande hemvist för den större historiska beslutskorpusen, nu uppdelad i domändrivna undermappar i stället för en enda rotmängd.
