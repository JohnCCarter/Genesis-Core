# README — analysis zone guide

Datum: 2026-03-20
Status: zon-guide med bevarad historisk RI/R1-serieöversikt

## Syfte för mappen

`docs/analysis/` är den framåtriktade ytan för mänskligt läsbara synteser, diagnoser och findings i Genesis-Core.
Mappen är till för tolkning och sammanhang — inte för governance-SSOT, slice-packets eller råa researchbundlar.

Efter den breda dokumenttaxonomimigreringen rymmer mappen också historiska root-dokument som tidigare låg under `docs/governance/` men vars faktiska roll var analys, evidenssyntes eller assessment.

## Hit hör

- findings-synteser
- jämförelse- och diagnosnoter
- narrativ sammanfattning av en forskningsserie
- mänskligt orienterade läsguider till större evidenspaket

## Hit hör inte

- governance-mode eller andra SSOT-regler
- command-/precode-packets, signoffs eller closeouts
- stabila kontraktsdefinitioner
- hela experimentbundlar med tabeller/traces som bör leva under `results/research/`

## Nuvarande subfolder-topologi

Rooten används nu bara för zon-guiden. Analyskorpusen ligger i grova,
domändrivna undermappar:

- `regime_intelligence/`
  - `advisory_environment_fit/`
  - `policy_router/`
  - `core/`
  - `optuna/challenger_family/`
  - `role_map/`
  - `router_replay/`
  - `upstream_candidate_authority/`
- `scpe_ri_v1/`
- `diagnostics/`
- `recommendations/`

`regime_intelligence/core/` är reserverad för corpusnivåmaterial som inte hör
hemma i en smalare RI-ström. Den är inte en generell overflow-bucket.
Om fler optuna-analysserier tillkommer ska de växa under
`regime_intelligence/optuna/` i stället för att skapa parallella namnspår.

`recommendations/` är avsedd för fristående slutsats- och rekommendationsnoter,
inte för stora kampanjserier som bör hållas samlade under sin egen domängren.

## Historisk serie: RI/R1 vs legacy

Den här README:n sammanfattar samtidigt den äldre RI/R1-vs-legacy-serien i `docs/analysis/` och pekar ut vilka artefakter som är viktigast att läsa i vilken ordning.

## Rekommenderad läsordning

1. `handoff.md`
   - kickoff och ursprunglig arbetsfråga
   - varför family-separationen behövde granskas explicit innan vidare implementation

2. `docs/analysis/regime_intelligence/core/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
   - visar att champion + authority-only kollapsar
   - etablerar att RI beter sig som separat strategi-topologi, inte som liten overlay

3. `docs/analysis/regime_intelligence/role_map/ri_legacy_role_map_2026-03-20.md`
   - huvudartefakten i serien
   - beskriver legacy och RI som två fullständiga strategy families över delad orkestrering

## Kort slutbild

Den samlade analysen pekar nu på följande:

- **legacy** och **RI** ska behandlas som två separata **strategy families**
- båda families använder samma övergripande runtime-orkestrering (`evaluate -> decide`)
- family-separationen sitter i:
  - family-signatur
  - authority-val
  - calibration/probability surface
  - threshold surface
  - cadence
  - structural survival
  - sizing-surface
- RI är därför **inte** ett management-/filter-lager ovanpå legacy, utan en egen family-yta

## Sammanfattad lagerordning för drift

Nuvarande evidens stöder denna arbetsmodell:

1. **Authority + calibration**
   - första topologisöm / family-breaker
2. **Threshold-surface**
   - primär kompatibilitetsyta
3. **Cadence**
   - family-shape / timingprofil
4. **Post-gates / safety**
   - sekundära förstärkare / stabiliserare
5. **Quality / sizing-surface**
   - family-intern driftfördelare när family-ytan redan valts

## Vad master-diff-reviewn visade

Jämförelsen mot `master` visade att den här branchen i praktiken består av analysrelaterade artefakter som nu bör läsas som ett sammanhängande family-reframe-paket:

- `handoff.md` — kickoff / arbetsfråga / designriktning
- `docs/analysis/regime_intelligence/role_map/ri_legacy_role_map_2026-03-20.md` — huvudanalysen med explicit family-reframe

Den tidigare Mermaid-sammanfattningen har tagits bort för att undvika begreppsglidning innan RI- och legacy-rollerna är slutligt fastställda. Runtime- och testartefakter finns fortsatt som underliggande evidens, men behöver inte läsas först för att följa reframingen.

## Viktigaste slutsats för framtida arbete

Om nästa steg någon gång återupptas bör första frågan vara:

> Vilken strategy family körs faktiskt här — legacy eller RI — och på vilken authority/calibration/threshold/cadence/sizing-surface realiseras den?

Det håller analysen fokuserad på family-gränserna i stället för på äldre overlay-språk.

## Nästa prioriterade analysyta

Den mest rimliga fortsättningen i rollmap-arbetet är nu:

- `src/core/strategy/decision_fib_gating.py`
- `src/core/strategy/decision_fib_gating_helpers.py`

Kärnfrågan för nästa slice är:

> När beter sig HTF/LTF-veto + adaptive override som legitim survival-/permission-policy, och när börjar det fungera som dold entrymotor?

## Relaterade analysdokument i samma mapp

- `docs/analysis/regime_intelligence/core/regime_intelligence_default_cutover_gap_analysis_2026-03-17.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_parity_artifact_matrix_2026-03-17.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `docs/analysis/recommendations/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`
- `docs/analysis/recommendations/ZERO_TRADE_ANALYSIS.md`

## Enradig slutdom

Legacy och RI ska läsas som två separata strategy families som körs genom samma övergripande orkestrering men divergerar i family-signatur, authority/calibration, threshold, cadence och sizing-surfaces.
