# RI advisory environment-fit Phase 3 reliability exact-label-authority preflight

Date: 2026-04-17
Mode: RESEARCH
Packet: `docs/decisions/ri_advisory_environment_fit_phase3_reliability_exact_label_authority_preflight_packet_2026-04-17.md`

## Slutsats

- top-level outcome: `NOT_RECOVERED`
- exact label authority recovered: `False`
- reliability axis remains advisory-only: `True`
- transition promotion: `False`
- phase4 opening: `False`
- runtime readiness: `False`

Bottom line: den låsta baseline-vs-candidate-kedjan kunde replayas deterministiskt, men den exakta Phase 2-radytan kunde inte materialiseras tillbaka på capture-v2-ytan i tillräcklig omfattning för att återställa exact-label authority.

## Vad som faktiskt lyckades

Preflight-slicen verifierade att den enda tillåtna authority-kedjan gick att köra direkt från låsta källor:

- `tmp/current_atr_900_env_profile_20260416.py`
- baseline config `tBTCUSD_3h_bull_high_persistence_override_min_size_001_vol_mult_090_vol_thr_75_cfg.json`
- candidate config `candidate_900_cfg.json`
- capture-v2 join-kontraktet `normalize(entry_time)|side`

Den replayade ytan var också deterministisk mellan två körningar:

- join hash: `883177652f96b17cea1600641a94bf3e3c2f107ea9be0b0f5777eb9f8222754a`
- label hash: `c4dd3132661ad60ebaf34b157fda3a7ae73192c100299f70e681fdc3d4a9465f`
- rows hash: `e441bf2a72d51ce54e9b3a97b5b030559ee64bd0719763236fec8b5c7fde043e`

Det betyder att misslyckandet inte är ett determinismproblem eller ett heuristikproblem. Det är ett overlap-/admissibility-problem.

## Varför authority inte återställdes

`join_audit.json` och `label_authority_audit.json` visar samma fail-closed bild:

- capture-v2 rows: `146`
- shared comparison rows from locked chain: `90`
- shared comparison rows matched back to capture-v2: `7`
- unmatched shared comparison rows: `83`
- active uplift rows on capture-v2: `54`
- supportive rows: `1`
- hostile rows: `2`
- non-evaluable rows: `143`

Det kritiska felet är alltså inte att `pnl_delta` saknas i authority-kedjan — den saknas inte där — utan att den exakta shared-comparison-populationen nästan inte överlappar capture-v2-ytan när joinen låses till `normalize(entry_time)|side`.

Den enda tillåtna recovery-regeln krävde exakt 1:1-materialisering tillbaka till capture-v2 för den relevanta authority-ytan. Den regeln faller här, eftersom endast `7 / 90` shared-comparison-rows återfinns på capture-v2-ytan och `83 / 90` inte gör det.

## Vad den materialiserade radenytan säger

Den genererade filen `materialized_exact_label_rows.ndjson` visar att ytan i huvudsak blir fail-closed:

- majoriteten av raderna får `exact_phase2_row_state = non_evaluable_context`
- `authority_source = absence_in_locked_comparison_chain` dominerar
- endast tre capture-v2-rader fick exact authoritative outcome-state från den låsta kedjan

Den rad som tydligast visar ett verkligt positivt exact-authority-fall är:

- `2024-07-05T06:00:00|LONG` → `supportive_context_outcome`
- `baseline_pnl = 97.12989266400017`
- `candidate_pnl = 107.92210296000019`
- `pnl_delta = 10.792210296000022`
- `active_uplift_cohort_membership = true`

Detta visar att metoden fungerar lokalt där den låsta comparison-kedjan faktiskt överlappar capture-v2. Men det räcker inte för att återställa authority på hela reliability-ytan.

## Beslut

Den enda tillåtna domen för denna slice är därför:

- `NOT_RECOVERED`

Och följande förblir stängt:

- ingen transition-axis promotion
- ingen Phase 4-öppning
- ingen runtime score implementation
- ingen uppgradering av dirty-research heuristics till authority

## Boundary / fail-closed

Följande gränser hölls:

- dirty-research heuristics användes inte som authority-input
- exact authority hämtades endast från den låsta baseline-vs-candidate-kedjan
- `pnl_delta` kom från locked comparison surface, inte från `total_pnl`-tecken
- `active_uplift_cohort_membership` härleddes från samma låsta comparison-kedja
- output-dir containment blev `PASS`
- deterministic replay blev `PASS`

## Nästa smala steg

Det här resultatet öppnar inte nästa fas i roadmapen automatiskt. Om arbetet ska fortsätta måste nästa slice hålla sig advisory-only och utgå från att exact Phase 2 label authority **inte** är återställd på capture-v2-ytan.

Den mest rimliga fortsättningen är därför inte promotion, utan en ny smal admissibility-fråga: om reliability-spåret ska fortsätta måste det ske utifrån explicit `NOT_RECOVERED` och utan att låtsas att capture-v2 nu bär exact-authority på radnivå.
