# README — RI/R1 vs legacy analysserie

Datum: 2026-03-20
Status: kort slutöversikt för analysserien

## Syfte

Den här README:n sammanfattar RI/R1-vs-legacy-serien i `docs/analysis/` och pekar ut vilka artefakter som är viktigast att läsa i vilken ordning.

## Rekommenderad läsordning

1. `handoff.md`
   - kickoff och ursprunglig arbetsfråga
   - varför RI/R1 skulle granskas som management/filter snarare än som ren entry-motor

2. `docs/analysis/regime_intelligence_champion_compatibility_findings_2026-03-18.md`
   - visar att champion + authority-only kollapsar
   - etablerar att RI beter sig som separat strategi-topologi, inte som liten overlay

3. `docs/analysis/ri_legacy_role_map_2026-03-20.md`
   - huvudartefakten i serien
   - full rollkarta, evidenskedja, driftattribution och slutsyntes

## Kort slutbild

Den samlade analysen pekar just nu på följande:

- **legacy** är fortfarande den primära entry-motorn
- **RI/R1** hör mest naturligt hemma i:
  - context / regime
  - permission / filtering
  - management / sizing / exits
  - observability
- RI ser inte ut att bli en separat family därför att quality eller en enskild gate råkar justera utfallet
- det tidigaste topologibrottet ser i stället ut att ligga i **authority + calibration**
- för att bli tradebar som sammanhängande yta kräver RI därefter en egen **threshold-/cadence-shape**

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
5. **Quality**
   - familjeintern driftfördelare

## Vad master-diff-reviewn visade

Jämförelsen mot `master` visade att den här branchen i praktiken består av två analysrelaterade spår:

- `handoff.md` — kickoff / arbetsfråga / designriktning
- `docs/analysis/ri_legacy_role_map_2026-03-20.md` — den faktiska slutanalysen

Ingen ytterligare runtime- eller testartefakt i branchdiffen såg ut att saknas för att förstå själva analysserien. Det som saknades var främst en kort index-/summary-yta som binder ihop kickoff, kompatibilitetsfynd och slutlig rollkarta.

## Viktigaste slutsats för framtida arbete

Om nästa steg någon gång återupptas bör första frågan vara:

> Bryter RI/legacy redan vid kandidatunderlaget, eller uppstår driften först senare i threshold-, cadence- eller safety-lagret?

Det håller analysen fokuserad på rätt lager i rätt ordning.

## Relaterade analysdokument i samma mapp

- `regime_intelligence_default_cutover_gap_analysis_2026-03-17.md`
- `regime_intelligence_parity_artifact_matrix_2026-03-17.md`
- `regime_intelligence_champion_compatibility_findings_2026-03-18.md`
- `tBTCUSD_3h_candidate_recommendation_2026-03-18.md`
- `ZERO_TRADE_ANALYSIS.md`

## Enradig slutdom

RI/R1 bör läsas som en separat topologi där **authority/calibration bryter först**, **threshold/cadence gör ytan tradebar**, och **quality huvudsakligen fördelar drift inom redan vald family-yta**.
