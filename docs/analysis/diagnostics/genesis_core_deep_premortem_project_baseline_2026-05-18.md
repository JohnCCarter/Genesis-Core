# Genesis-Core deep premortem — project baseline (2026-05-18)

> Status note: This is a **fristående bred projekt-baseline-premortem**, inte en delta mot
> 2026-05-15-kedjan eller mot evidence-closeout-piloten. Den 2026-05-18-re-anchor som klassar
> premortem-lanen som "explicitly closed for now" är respekterad: detta dokument reopens lanen
> bara med en ny bounded anchor-fråga (se nedan) och förändrar inte status, queue eller
> auktoritet i någon befintlig premortem-doc.
> Den lane-lokala closeout-läsningen ovan betyder därför inte "projektet är klart" eller att alla
> risker är eliminerade; den betyder bara att fortsatt arbete måste öppnas explicit som nya bounded
> frågor i stället för att ärvas från gammal premortem-prosa.
>
> Detta dokument är `historical-trace-level` — det är en frusen ögonblicksbild av branchens
> risk-yta som helhet, syntetiserad från tracked governance/audit-docs och tracked code-state.
>
> Reader-routing note (2026-05-19): Treat this note as the **broader project-baseline sweep**.
> For the branch-specific implementation-time risk frame, read
> `docs/analysis/diagnostics/genesis_core_premortem_feature_evidence_closeout_pilot_2026-05-15.md`.
> For the later branch-state re-anchor of that premortem chain, read
> `docs/analysis/diagnostics/premortem_delta_reanchor_feature_evidence_closeout_pilot_2026-05-18.md`.

## Claim header

- **Date:** `2026-05-18`
- **Branch:** `feature/evidence-closeout-pilot`
- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Lane:** `Research-evidence` — why: bounded projektomspännande failure-mode-syntes; ingen runtime/queue/auktoritet rör
- **Status:** `observational / premortem diagnostics / non-authorizing`
- **Authority level:** `bounded research-evidence`
- **Claim status:** `observed + inferred`
- **Checkout scope / portability label:** `historical-trace-level` — ögonblicksbild av tracked-docs + tracked-code; portability stannar vid den frusna träd-snittet HEAD `0812bd605b`
- **Objective:** identifiera de mest sannolika och mest impactful failure-modes som kan slå mot Genesis-Core som helhet i ett 0–6 månaders horisontfönster, oberoende av aktuell branch-scope, utan att reopen-a tidigare premortem-kedjor eller skapa runtime-auktoritet
- **Baseline reference(s):** `CLAUDE.md` (projekt + user-level), `docs/governance/concept_evidence_runtime_lane_model_2026-04-23.md`, `docs/governance/templates/evidence_claim_header.md`, `docs/audit/CONFIG_GOVERNANCE_AUDIT.md`, `docs/audit/BACKTEST_ENGINE_AUDIT.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_feature_evidence_closeout_pilot_2026-05-15.md`, `docs/analysis/diagnostics/premortem_delta_reanchor_feature_evidence_closeout_pilot_2026-05-18.md`
- **Candidate / comparison surface:** Genesis-Core som helhet — alla pelare i `CLAUDE.md` (ConfigAuthority, BacktestEngine, Optimizer, Strategy decision, Intelligence/RI, IO/Bitfinex, Risk guards) plus governance/docs-integritet, determinism, och boundary I/O
- **Input carrier:** tracked docs (governance, audit, analysis) + tracked code under `src/core/` + git metadata; inga local-only roots, inga rerun-results, inga ignored artifacts
- **Runtime base SHA:** `0812bd605ba9f2ea9e08867dec568b1c6afb57de`
- **Evidence commit SHA:** `not rerun in this slice; synthesis derived from tracked docs and code at HEAD 0812bd605ba9f2ea9e08867dec568b1c6afb57de`
- **Working-tree status:** `clean`
- **Config path:** `not applicable`
- **Config hash:** `not applicable`
- **Symbol / timeframe:** `not applicable`
- **Window:** projekt-baseline som helhet; 0–6 månaders prospektiv horisont
- **Warmup:** `not applicable`
- **Data-source policy:** tracked docs och tracked code endast
- **Symbol mode:** `not applicable`
- **Env flags:** ingen env-state använd som evidence i denna doc
- **Cache policy:** inga cache-läsningar eller -skrivningar utförda
- **Artifact path(s):** `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Artifact hash(es):** `not applicable`
- **What changed:** en ny bounded tracked premortem-syntes täcker projektets risk-yta som helhet
- **What did not change:** ingen befintlig premortem-doc redigeras; ingen queue reopens; inga runtime, config, test, results, artifact, eller governance-precedence-ytor påverkas
- **Does not authorize:** runtime changes, config-whitelist edits, promotion, readiness, champion, family-rule edits, gate-tuning, paper→live transitions, schema-version-bumps, demote/pause-status-edits på existerande docs, queue reopen, eller reopen av 2026-05-15-premortem-kedjan

## Mode proof

Aktiv branch `feature/evidence-closeout-pilot` löser deterministiskt till `RESEARCH` under
`docs/governance_mode.md`. RESEARCH tillåter en bounded tracked diagnostics-syntes som inte
ändrar runtime-default, queue-status, paper/live-execution, promotion, readiness, champion, eller
family-rule-auktoritet. Detta dokument håller sig strikt inom den ramen.

## Anchor & scope

**Anchor-fråga:** Vilka är de mest sannolika och mest impactful failure-modes som kan slå mot
Genesis-Core som helhet, oavsett aktuell branch, i ett 0–6 månaders horisontfönster?

**Scope IN:**

- alla namngivna pelare i `CLAUDE.md`: ConfigAuthority/SSOT, BacktestEngine, Optimizer, Strategy decision, Intelligence/RI, IO/Bitfinex, Risk guards
- governance och docs-integritet på repo-nivå (citation-framing, demote/pause-discipline, lane-mapping)
- determinism och reproducibility-yta (seeds, schema-version, cache-keys)
- boundary I/O (Bitfinex REST/WS, paper/live-isolation, symbol-mode)

**Scope OUT:**

- branch-specifika evidence-closeout-pilot-frågor (täcks av 2026-05-15-kedjan och 2026-05-18-re-anchor)
- ny strategi-familje-design (per lane-modellen: ska inte introduceras spekulativt)
- konkreta runtime-promotion-frågor eller readiness-claims (per `Does not authorize`)
- frågor som kräver `same-local-checkout`-evidence eller `fixture-level`-carrier (ingen ny carrier öppnas här)

## Method

- **Ranking:** `score = likelihood (1–5) × impact (1–5)`, range 1–25
- **Likelihood-skala:**
  - 1 = endast hypotes utan kod- eller doc-signal
  - 2 = strukturell möjlighet, ingen observerad incident
  - 3 = sannolikt under realistiska arbetsmönster
  - 4 = observerat eller dokumenterat öppet ≥ 1 gång
  - 5 = redan inträffat och kvar som öppen risk-yta
- **Impact-skala:**
  - 1 = lokal irritation, lätt fixad
  - 2 = bortkastat arbete, ingen permanent skada
  - 3 = silent felaktighet i ett bounded surface
  - 4 = silent felaktighet som propagerar till downstream-beslut
  - 5 = silent corruptness eller skapar felaktig auktoritet på runtime/promotion
- **Evidence-nivå per mode:**
  - **A** = öppet dokumenterat i tracked audit/governance-doc eller direkt observerbart i kod
  - **B** = kod-signal observerad men ej formellt dokumenterad
  - **C** = strukturell hypotes utan direkt signal
- Endast modes med `score ≥ 6` listas i huvudtabellen. Lägre modes hamnar i **Long tail** för
  reader-traceability.

## Ranked failure modes

|   # | Mode                                                                                               | Pelare                |   L |   I |  Score | Ev  | Signal                                                                                                                                                          | Mitigation-pekare                                                                                                |
| --: | -------------------------------------------------------------------------------------------------- | --------------------- | --: | --: | -----: | :-: | --------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
|   1 | Evidence-to-authority drift: "observational" docs cited as approval                                | Governance            |   4 |   5 | **20** |  A  | 2026-05-15 deep premortem rank 1 + 2026-05-18 re-anchor recommendation                                                                                          | Claim-header `Does not authorize` enforcement; lane-mappning                                                     |
|   2 | Precompute cache silent stale-reuse vid feature-impl-change utan `PRECOMPUTE_SCHEMA_VERSION`-bump  | BacktestEngine        |   3 |   5 | **15** |  A  | `BACKTEST_ENGINE_AUDIT.md` Fynd C; `GENESIS_PRECOMPUTE_CONFIG_HASH` är valfritt                                                                                 | Bump-policy docstring; deterministic hash av config-subset i key                                                 |
|   3 | Citation-framing drift: tracked vs local-only mislabel                                             | Governance/docs       |   4 |   3 | **12** |  A  | 2026-05-18 re-anchor identifierar 3 docs som kvarstår som residual seam                                                                                         | Bounded docs-only citation-alignment slice (re-anchor föreslår denna men öppnar den ej)                          |
|   4 | Stale control-plane-pointer survives demote (GENESIS_WORKING_CONTRACT, active_lane_index)          | Governance            |   3 |   4 | **12** |  A  | 2026-05-15 deep premortem rank 2; pointers refererar `feature/editor-worker-orchestrator`                                                                       | Branch-truth-verifiering före re-anchor; queue/status freshness guard                                            |
|   5 | Paused-but-retained doc (editor-worker model) misread som current default workflow                 | Governance            |   3 |   4 | **12** |  A  | `worker_governance_envelope.md` + `editor_slice_worker_dispatch.md` pausade 2026-05-18                                                                          | Eksplicit status-banner; CLAUDE.md-pekare till aktuellt workflow                                                 |
|   6 | Premortem closeout misread som project closeout / "vi är klara"                                    | Governance            |   3 |   4 | **12** |  A  | 2026-05-18 re-anchor explicit: "closed for now" ≠ "all risk eliminated"                                                                                         | Denna doc + bottom-line-discipline                                                                               |
|   7 | Whitelist↔schema-mismatch i ConfigAuthority: validerade fält ej live-updatable                     | ConfigAuthority       |   4 |   3 | **12** |  A  | `CONFIG_GOVERNANCE_AUDIT.md` Fynd B; whitelist `authority.py:223-230` exkluderar `exit`, `warmup_bars`, `features`, `htf_exit_config` som RuntimeConfig stödjer | B1 (säkerhetsmodell) eller B2 (utöka whitelist) per audit                                                        |
|   8 | HTF exit-engine `{}` empty-dict-selection-inkonsistens runner vs manual                            | BacktestEngine        |   3 |   4 | **12** |  A  | `BACKTEST_ENGINE_AUDIT.md` Fynd A; `_init_htf_exit_engine` valselogik                                                                                           | Eksplicit `htf_exit_config["enabled"]` opt-in; logga engine-decision                                             |
|   9 | HTF-context divergens: precomputed mapping vs `meta["features"]["htf_fibonacci"]`                  | BacktestEngine        |   3 |   4 | **12** |  A  | `BACKTEST_ENGINE_AUDIT.md` Fynd E; 0.0-fyllning kan misstolkas som giltig nivå                                                                                  | Validering `swing_high/low > 0` innan `available=True`                                                           |
|  10 | Off-sample / contradiction-year validation tyst skippas vid data-saknad                            | Optimizer             |   3 |   4 | **12** |  B  | Test-skip-mönster på "Data not available" maskerar gates                                                                                                        | Eksplicit fail-on-missing-data i promotion-väg                                                                   |
|  11 | RI policy-router exact-window overreach: findings drift till general-claim-språk                   | Strategy/RI           |   3 |   4 | **12** |  A  | 2026-05-15 deep premortem rank 9; transport/falsifier-boundary-packet är parkerad                                                                               | Parked-bank-syntes-discipline; "exact-subject only"-vokabulär                                                    |
|  12 | PyArrow feature-cache `schema_version=1` utan bump-enforcement vid schema-ändring                  | Determinism           |   3 |   4 | **12** |  A  | Samma rot som #2 men separat angreppsvektor (feature-cache vs precompute-cache)                                                                                 | Bump-policy docstring; CI-gate som triggar vid feature-schema-diff                                               |
|  13 | Regime-detection lookahead-leak under `GENESIS_FAST_WINDOW=1` eller precompute-reorder             | Strategy/Intelligence |   2 |   5 | **10** |  C  | Strukturell — fast-path + precompute-reorder är båda canonical default, ingen explicit lookahead-test sett                                                      | Property-test som jämför slow-path vs fast-path-resultat per bar                                                 |
|  14 | Decision-coercion crash på `None`/string input till `decide()`                                     | Strategy              |   3 |   3 |  **9** |  C  | Ingen fuzz/property-test sett i `tests/`; pydantic v2 strict-mode inte universellt tillämpad                                                                    | Hypothesis-baserad property-test för decision input-shape                                                        |
|  15 | `engine.py` 1522 rader → change-blast-radius vid refactor                                          | BacktestEngine        |   3 |   3 |  **9** |  B  | Verifierad `wc -l` 2026-05-18; MEMORY.md visar pågående split-arbete på separat worktree                                                                        | Slice-modularisering (pågår på `worktree-engine-modul-split`); behåll deepcopy-isolering                         |
|  16 | `runner.py` 1463 rader + `runner_optuna_orchestration.py` 1113 rader → orchestration fragmentation | Optimizer             |   3 |   3 |  **9** |  B  | Verifierad `wc -l`; två stora orchestration-filer utan tydlig kontrakt-gräns                                                                                    | Sektionsrubrik-discipline; ev. delning per Optuna-fas                                                            |
|  17 | Legacy validator misuse: `validate_config` (schema_v1.json) kallas på runtime-config               | ConfigAuthority       |   3 |   3 |  **9** |  A  | `CONFIG_GOVERNANCE_AUDIT.md` Fynd A; legacy validerar bara 3 fält                                                                                               | Rename per Fynd A (`legacy_schema_v1.json`, `validate_legacy_config`)                                            |
|  18 | Backtest error-policy: "continue on error" i loop men `raise` efteråt överraskar caller            | BacktestEngine        |   3 |   3 |  **9** |  A  | `BACKTEST_ENGINE_AUDIT.md` Fynd D; `per_bar_error_count > 0 ⇒ RuntimeError`                                                                                     | Eksplicit `error_policy` parameter (fail_fast / fail_on_any_error / best_effort)                                 |
|  19 | Parallella premortem-kedjor (2026-05-15 + 2026-05-18 + denna) konkurrerar om canonical anchor      | Governance            |   3 |   3 |  **9** |  A  | Tre tracked premortem-docs efter dagens skrivning; readers måste välja rätt                                                                                     | Eksplicit cross-link med portability-labels; bottom-line säger "denna är project-baseline, inte branch-specific" |
|  20 | Nonce-error-detection via string-match (`"nonce"`, `"10114"`) bräcklig vid Bitfinex-format-ändring | IO/Bitfinex           |   3 |   3 |  **9** |  B  | `exchange_client.py:142` — `if "nonce" in text.lower() or "10114" in text`                                                                                      | Strukturerad fel-mappning baserad på Bitfinex error-koder; smoke-test mot ändrade meddelandeformat               |
|  21 | Single-retry på signed REST → cascading failure vid burst-rate-limit                               | IO/Bitfinex           |   3 |   3 |  **9** |  B  | `exchange_client.py:115-129`; `_sleep_jitter` använder `base_delay=0.0, max_backoff=0.3`                                                                        | Exponential backoff med beräknad budget; bounded retry-count med metric                                          |
|  22 | Konfig-bypass via direkt fil-edit av `config/runtime.json` (ingen teknisk block, bara konvention)  | ConfigAuthority       |   2 |   4 |  **8** |  B  | `authority.py` skriver via `_persist_atomic` men inget hindrar utomstående skrivning                                                                            | File-watch / hash-mismatch-detect i `ConfigAuthority`-init; tydlig README                                        |

**Total i huvudtabell: 22 modes.** Score-distribution: 1 mode ≥ 20, 11 modes 12–15, 7 modes 9–10, 3 modes 6–8.

## Per-pelare djupare läsning

### Governance / docs-integritet (#1, #3, #4, #5, #6, #19)

Den genomgående tråden här är inte att Genesis-Core saknar discipline-ytor — det har många,
och de är välskrivna. Risken är att **disciplin-ytorna själva blir det som missförstås**:

- mode #1 (evidence-to-authority drift) är öppet erkänd som branchens rank-1 risk i 2026-05-15-djup-premortem. Den är **inte mitigerad** av denna doc; den är bara dokumenterad oftare. Mitigationen sker per-citation, inte per-doc.
- mode #3 (citation-framing drift) är redan identifierad i 2026-05-18-re-anchor som "den enda residual seam värd en bounded slice". Den är klassad som **identified but not yet closed**.

  Later-branch truthfulness note (2026-05-19, `feature/risk-hardening-wave2`): the exact `#3` seam above should not be read as still open current-branch work for this checkout. `docs/analysis/diagnostics/premortem_delta_reanchor_feature_evidence_closeout_pilot_2026-05-18.md` already records that the tracked-vs-local-only citation seam was later corrected in the affected tracked docs, and the three cited surfaces — `docs/decisions/governance/queue_status_freshness_guard_packet_2026-05-15.md`, `docs/decisions/governance/decision_influencing_claim_header_boundary_packet_2026-05-15.md`, and `docs/analysis/diagnostics/ignored_artifact_dependency_inventory_2026-05-15.md` — now describe `docs/analysis/diagnostics/genesis_core_premortem_feature_evidence_closeout_pilot_2026-05-15.md` as a repository-tracked historical diagnostics / historical risk-framing note rather than a local-only or current-authority surface. This narrows current-branch truthfulness for the exact `#3` seam only and does not claim that the broader `#1` evidence-to-authority drift family is solved. See `docs/decisions/governance/citation_framing_drift_later_branch_truthfulness_packet_2026-05-19.md`.

- modes #4 och #5 är båda **partially mitigated** — pointers/docs har fått status-banners ("historical reference only", "paused"), men en lazy reader kan fortfarande tolka dem som current om de hoppar över status-bannern.
- mode #6 är subtil och är delvis orsakad av denna doc själv (att skriva en ny premortem efter en re-anchor som sa "closed" kan tolkas som motsägelse). Re-anchor-doc:en sa explicit att "if a new bounded question reopens it" är acceptabel reopen-shape — denna doc använder den exit-klausul.

  Later-branch truthfulness note (2026-05-19, `feature/risk-hardening-wave2`): the `closed for now` verdict above should be read as closeout of the inherited premortem lane only, not as `all risk eliminated`, `project complete`, or `vi är klara`. The honest current-branch reading is: the old lane no longer stays open by implication, but broader project-baseline risks and later bounded hardening slices may still exist and must be reopened explicitly.

- mode #19 (parallella premortem-kedjor) blir mätbart värre med varje ny premortem-doc om de inte cross-linkas och labelas tydligt. Denna doc cross-linkar 2026-05-15 + 2026-05-18 i baseline references och deklarerar sig själv project-baseline.

### ConfigAuthority / SSOT (#7, #17, #22)

ConfigAuthority är en av de mest disciplin-täta ytorna i repot:

- `_persist_atomic` (rad 91–212) gör temp-file + fsync + audit-log med rotation
- `propose_update` (rad 212+) kör en whitelist innan validering

Men whitelist-mismatch (mode #7) är **öppet dokumenterad** sedan 2026-02-21 (Fynd B i
CONFIG_GOVERNANCE_AUDIT.md) och har valbar policy:

- B1: behåll whitelist men dokumentera explicit varför `exit`/`features`/`warmup_bars` ej är live
- B2: utöka whitelist till de runtime-fält som ska få ändras live
- B3: rollstyrning för admin/service-actor

Inget av dessa har en current branch-decision (per audit-doc); det är fortfarande "decide and
document" i handoff. Detta är inte en bug — det är en **öppen policy-fråga som ser ut som en
bug** för en användare som försöker live-uppdatera ett valid runtime-fält och får
`non_whitelisted_field`.

Mode #17 (legacy validator misuse) har en konkret rename-fix föreslagen i Fynd A — `schema_v1.json`
→ `legacy_schema_v1.json`, `validate_config` → `validate_legacy_config`. Den fixen är inte
landad. Risk-toppen är att en framtida agent kallar `validate_config` på en runtime-config och
får PASS för att legacy-schemat bara validerar 3 fält.

Mode #22 är **strukturell**: ConfigAuthority är konvention, inte teknisk gate. Inget hindrar att
en mänsklig operatör eller en off-path-script skriver direkt till `config/runtime.json` och
bumpar hash utan audit-trail. Mitigationen är detektion (hash-mismatch-warning vid init), inte
prevention.

### BacktestEngine (#2, #8, #9, #15, #18)

Engine-pelaren har **mest öppet dokumenterad risk**:

- mode #2 (precompute cache silent stale-reuse) är Fynd C i BACKTEST_ENGINE_AUDIT.md. Cache-key inkluderar schema-version + spec-digest + symbol/timeframe + längd + start/end ns. Men `GENESIS_PRECOMPUTE_CONFIG_HASH` är **valfritt**, vilket innebär att två körningar med olika strategi-konfig kan dela cache. Konsekvensen är inte test-fel — det är **olika resultat utan att någon larmar**.
- mode #8 + #9 (HTF-relaterade) handlar båda om att samma logiska intent (kör HTF-exits) realiseras via olika kod-paths beroende på empty-dict vs explicit-enabled vs precomputed-mapping. Audit-rekommendationen är `htf_exit_config["enabled"]` opt-in.

  Later-branch truthfulness note (2026-05-19, `feature/risk-hardening-wave2`): the broad `#8` carry-forward reading should not be repeated unchanged for this checkout. Current `src/core/backtest/engine.py` no longer routes the general env-unset + config-present case to legacy: existing selectors in `tests/backtest/test_htf_exit_engine_selection.py` and `tests/governance/test_dead_code_tripwires.py` show that, with `GENESIS_HTF_EXITS` unset, a non-empty `htf_exit_config` selects the `NEW` engine, while only the empty-config case preserves legacy behavior; optimizer-side flows in `src/core/optimizer/runner.py` and `src/core/optimizer/runner_trial_backtest.py` further reduce one historical runner/manual drift path by setting `GENESIS_HTF_EXITS=1` when HTF exits are requested. This narrows the older subclaim rather than closing Finding A. The broader residual risk remains open because engine selection still depends on explicit env override else `bool(htf_exit_config)`, so `{}` versus non-empty config still changes behavior without an explicit `htf_exit_config["enabled"]` contract. See `docs/decisions/governance/htf_exit_engine_selection_partial_reclassification_packet_2026-05-19.md`.

- mode #15 (`engine.py` 1522 rader) är **partially mitigated** — MEMORY.md visar att en engine-modul-split pågår på separat worktree (slice 1 + slice 2 landade där, slice 3 planerad). Men på `feature/evidence-closeout-pilot` är `engine.py` fortfarande 1522 rader, och split-arbetet är inte mergat hit.

  Later-branch truthfulness note (2026-05-19, `feature/risk-hardening-wave2`): the `#15` sentence above remains a historical 2026-05-18 observation and should not be read as current tracked branch evidence for this checkout. The current review on `feature/risk-hardening-wave2` did not identify a tracked `MEMORY.md` carrier for that claim; current tracked `htf_exit*` split artifacts are a different seam and do not by themselves resolve `src/core/backtest/engine.py`. See `docs/decisions/governance/backtest_engine_split_track_reconcile_packet_2026-05-19.md`.

- mode #18 (error-policy continue+raise) är öppet erkänd som "kan överraska användare" i Fynd D. Korrekt mitigation är explicit `error_policy` parameter, inte hide-the-error.

### Optimizer (#10, #16)

Optimizer-pelaren har **två risk-vektorer som korrelerar**:

- mode #16 (1463 + 1113 rader orchestration) är ren komplexitets-risk. Det finns ingen audit-doc specifikt för optimizer — det är ett tomrum i tracked diagnostics som borde nämnas.
- mode #10 (off-sample / contradiction-year tyst skippable) är allvarligare i intent: gates som ska blocka promotion kan tyst skippas om data inte finns. Test-skip-mönster (`pytest.skip("Data not available")`) är legitimt på CI men problematiskt om samma mönster läcker in i promotion-väg.

### Strategy / Intelligence (#11, #13, #14)

- mode #11 (RI policy-router overreach) är dokumenterat öppet i 2026-05-15-djup-premortem rank 9. Det har **partial mitigation** — exact-subject-vokabulären + transport/falsifier-boundary-packet — men risken är att exact-subject-findings drifte till general-claim-språk när det berättas senare.

  Later-branch partial reclassification note (2026-05-19, `feature/risk-hardening-wave2`): the exact `#11` reading above should now be narrowed on current branch-visible evidence. The repo already carries tracked exact-subject and bank-state re-anchor surfaces for the current D1 line — including `docs/analysis/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_topline_subject_triad_synthesis_2026-05-04.md`, `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_four_surface_synthesis_2026-05-05.md`, `docs/analysis/regime_intelligence/policy_router/ri_policy_router_insufficient_evidence_d1_bank_state_synthesis_2026-05-06.md`, and `docs/decisions/governance/ri_policy_router_d1_transport_falsifier_evidence_boundary_packet_2026-05-15.md`. This means the honest current residual is later retelling drift into broader claim language, not a still-missing parked-bank / exact-subject / transport-boundary frame for the current D1 chain. See `docs/decisions/governance/ri_policy_router_exact_window_overreach_partial_reclassification_packet_2026-05-19.md`.

- mode #13 (lookahead-leak under `GENESIS_FAST_WINDOW=1`) är **strukturell hypotes** (C). `GENESIS_FAST_WINDOW=1` är canonical default per CLAUDE.md, och precompute-features är också canonical default (`GENESIS_PRECOMPUTE_FEATURES=1`). Båda har potentiella ordning-känsligheter. Ingen tracked test sett som verifierar slow-path vs fast-path identitet per bar.
- mode #14 (decision-coercion crash) är också C — ingen fuzz/property-test sett för `decide()`-input. Pydantic v2 ger viss skydd, men `decide()` tar dict-baserade inputs i delar av call-graph.

### IO / Bitfinex (#20, #21)

- mode #20 (nonce string-match) är en konkret bräcklighet på `exchange_client.py:142`. Detection-strängarna `"nonce"` och `"10114"` är hårdkodade. Om Bitfinex ändrar error-format (vilket tredjeparts-APIer gör utan förvarning) tappar retry-logiken sin trigger.
- mode #21 (single-retry signed REST) är öppet erkänd i koden (`_sleep_jitter` använder `base_delay=0.0, max_backoff=0.3, jitter 100-300ms`). Det är **inte exponential backoff** — det är en jitter-baserad engångs-fördröjning. Under burst-rate-limit räcker det inte.

  Later-branch truthfulness note (2026-05-19, `feature/risk-hardening-wave2`): the `#21` sentence above remains a historical 2026-05-18 baseline assessment and should not be read as current branch evidence for this checkout. Current `src/core/io/bitfinex/exchange_client.py` defines `_MAX_SIGNED_REQUEST_ATTEMPTS = 3`, retries nonce / retryable-status / transient request errors inside `signed_request(...)`, and routes `_sleep_jitter(...)` through `exponential_backoff_delay(...)` with `base_delay=0.05`, `max_backoff=0.4`, and jitter `100-300ms`; `tests/utils/test_exchange_client.py` provides focused proof for structured nonce retry and retry-through-third-attempt behavior. This narrows current-branch truthfulness only and does not prove burst-rate-limit sufficiency or preclude a later reopen on retry budget / operational evidence. See `docs/decisions/governance/bitfinex_signed_rest_retry_truthfulness_packet_2026-05-19.md`.

Båda är begränsade till en boundary-yta (inte spridda över repot), vilket gör dem
hanterbara — men det är **inga tracked tester sett som simulerar Bitfinex burst-fel-flöde**.

### Determinism (#12)

Mode #12 separeras från #2 även om de delar struktur eftersom de träffar olika cache-ytor:

- #2 är `_precompute_cache_key` i backtest-engine
- #12 är PyArrow feature-cache `schema_version=1` på disk

Båda har samma rot-orsak (no enforcement at schema-bump time) men olika blast-radius. Feature-cache
mister kan drabba flera körnings-modes (backtest, optimizer, paper) samtidigt.

## Cross-cutting themes

### Tema 1: "Narrowing remembered as authorization" (G1 + G3 + G5)

Den enskilda tråden som binder governance-modes är att **bounded korrekta uttalanden retold
som bredare auktoritet**. Det är inte ett bug-tema utan ett **berättelse-tema**: docs blir aldrig
fel, de bara berättas annorlunda nästa gång de citeras. 2026-05-18-re-anchor använde redan
frasen "precision loss after partial success" för detta. Project-baseline-tråden bekräftar att
risken är inte branch-specifik — den är repo-strukturell.

### Tema 2: "Silent stale-reuse" (#2 + #12 + delvis #15)

Tre olika cache-ytor (precompute-cache, PyArrow feature-cache, deepcopy-isolering i `run()`) har
samma struktur: korrekt nyckel idag, ingen garanti att nyckeln bumpas vid impl-ändring imorgon.
Mitigation är inte tekniska — det är **process-discipline + CI-gate vid schema-yta-diff**.

### Tema 3: "Two valid code-paths, one logical intent" (#8 + #9 + #13)

HTF-exits, HTF-context, fast-path vs slow-path: tre par av code-paths som ska producera samma
logiska resultat men gör det via olika datakällor. Risk-yta är **divergens som inte upptäcks
i existerande tester** för att tester ofta exerciserar en path i taget, inte par.

### Tema 4: "Hot-file change-blast-radius" (#15 + #16)

Tre filer över 1100 rader (`engine.py` 1522, `runner.py` 1463, `runner_optuna_orchestration.py`
1113). Refactor på dessa är dyr per definition. Mitigation pågår partiellt (engine-modul-split
på separat worktree), men kostnaden är fortfarande hög på huvudbranchen.

### Tema 5: "Data-dependency-skip maskerar regressions" (#10 + B4 från 2026-05-15)

Tester som skippas på "Data not available" är **olika** från tester som xfail-as. De skippade
testerna är inte misslyckade, men de är inte heller bevis. När promotion-väg använder samma
skip-mönster glider gates tyst.

### Tema 6: "Convention is not enforcement" (#22 + delvis #11)

ConfigAuthority är konvention, inte teknisk block. Exact-subject-vokabulär är konvention,
inte teknisk block. Båda fungerar tills de inte gör det. Mitigation är **detektion av brott**
(hash-mismatch, language-drift-grep), inte prevention.

## Long tail (score < 6, ej i huvudtabell)

| Mode                                                                       | Pelare          |   L |   I | Score |     Ev     | Anledning lågt                                                                         |
| -------------------------------------------------------------------------- | --------------- | --: | --: | ----: | :--------: | -------------------------------------------------------------------------------------- |
| LT1. Legacy `diff_config` toppnivå-only kan missleda vid runtime-bruk      | ConfigAuthority |   2 |   2 |     4 | A (Fynd D) | Endast lokal irritation om upptäckt; recursive `_diff_paths` finns redan i authority   |
| LT2. Schema `risk_map` validerar struktur men ej monotonicity/bounds       | ConfigAuthority |   2 |   2 |     4 | A (Fynd E) | Edge-case som kräver explicit bad input för att utlösa                                 |
| LT3. Timestamp-typ-mixing (pandas.Timestamp vs numpy datetime64) i `run()` | BacktestEngine  |   2 |   1 |     2 | A (Fynd F) | Påverkar serialisering/jämförelser men inte resultat-värden                            |
| LT4. WebSocket reconnect saknar circuit-breaker                            | IO/Bitfinex     |   2 |   2 |     4 |     B      | Har exponential backoff (max 10s); reconnect-storm-risk finns men begränsad av backoff |
| LT5. `SYMBOL_MODE` implicit på CI (synthetic) vs explicit på dev           | Reproducibility |   2 |   2 |     4 |     A      | Dokumenterat i CLAUDE.md; sannolikt fångad av symbol-mode-banner                       |
| LT6. Audit-log-rotation under concurrent write                             | ConfigAuthority |   1 |   3 |     3 |     C      | Skrivning är serialiserad via ConfigAuthority single-process-antagande                 |
| LT7. Governance registry dubblett-konflikt (Fynd C)                        | Governance      |   2 |   2 |     4 |     A      | Begränsad till manifest-validering; explicit fix föreslagen i audit                    |

## Open bounded follow-up questions

Dessa är **inte queue-items** — de är formulerade så att en framtida bounded slice kan plocka upp
dem utan att reopen-a hela premortem-lanen:

1. Ska whitelist↔schema-mismatch (mode #7) lösas med B1 (dokumentera) eller B2 (utöka)? Detta är en policy-fråga som varit öppen sedan 2026-02-21 audit och behöver en bounded decision-packet, inte mer audit.
2. Ska `PRECOMPUTE_SCHEMA_VERSION`-bump-policy formaliseras som en gate (CI-check vid feature-schema-diff) eller förbli docstring-konvention (modes #2 + #12)?
3. Finns en bounded test-yta som kan jämföra slow-path vs fast-path identitet per bar för att stänga mode #13 från C till A eller B?
4. Vad är minsta admissible reopen-shape för citation-framing drift seam som 2026-05-18-re-anchor identifierade (mode #3)?
5. Ska engine-modul-split-arbetet på `worktree-engine-modul-split` (slice 1+2 landade, slice 3 planerad) mergas tillbaka till master efter slice 3, eller fortsätta som separat track?
6. Finns en bounded fuzz/property-test-slice som kan stänga mode #14 (decision-coercion) utan att kräva runtime-changes?
7. Behöver Bitfinex retry/nonce-logik (modes #20 + #21) en strukturerad fel-mappning baserad på dokumenterade Bitfinex error-koder, eller är string-match-fragiliteten acceptabel given dagens trafik-mönster?

## Does not authorize

Detta dokument är `bounded research-evidence / observational only`. Det auktoriserar **inte**:

- runtime changes, config-whitelist-edits, eller config-schema-bumps
- promotion, readiness, champion, eller family-rule-edits
- gate-tuning, paper→live transitions, eller live-execution
- demote/pause-status-edits på existerande premortem-docs (2026-05-15 + 2026-05-18 förblir intakta)
- queue reopen eller reopen av 2026-05-15-premortem-kedjan
- carrier-upgrades, portability-label-changes, eller cross-chain inheritance
- ändringar i `.github/agents/`, `.claude/agents/`, eller andra agent-customization-ytor

Varje punkt i tabellen är en **risk-observation**, inte en remediation-task. Att flytta en
observation till remediation kräver separat bounded packet med explicit Scope IN/OUT och
relevant lane (typiskt runtime-integration för konkreta fix-slices).

## Bottom line

Genesis-Core är i ett strukturellt sundare läge än 2026-05-15-djup-premortem-baseline. De flesta
identifierade risker är **partially mitigated** (status-banners, demotes, paused docs) snarare
än lösta. De återstående topp-3-riskerna är samma som branchen redan medger:

1. **Evidence-to-authority drift** är fortfarande rank-1, oavsett hur många bounded boundary-packets som landar (mode #1)
2. **Silent stale-reuse** över cache-ytor är obrytt: precompute-cache och PyArrow feature-cache delar samma rot-orsak och samma saknade enforcement (modes #2 + #12)
3. **Whitelist↔schema-policy** har varit öppen i tre månader utan decision (mode #7); det är inte en bug, det är en obesvarad policy-fråga

Om Genesis-Core misslyckas i 0–6-månaders-horisonten är det mest sannolika scenariot **inte**
att en specifik subsystem-bug aktiveras. Det är att **en bounded korrekt evidence-claim
överlagras till en bredare auktoritet i ett senare beslut**, och att det beslutet sedan
används som bas för ett ännu senare beslut. Den failure-modellen är **tema-1** ovan, och den
är inte stängbar genom denna doc.

Den vassaste enskilda mitigationen från detta sweep är **inte** att fixa något i tabellen.
Det är att **göra branch-truth-verifiering och claim-header-discipline obligatorisk vid varje
re-anchor**, vilket är vad 2026-05-18-re-anchor redan rekommenderar. Detta dokument är en
project-baseline-bekräftelse av samma slutsats, breddad utanför evidence-closeout-pilotens scope.

---

_Cross-links:_

- _2026-05-15 deep premortem (branch-scoped):_ `docs/analysis/diagnostics/genesis_core_deep_premortem_feature_evidence_closeout_pilot_2026-05-15.md` — `historical-trace-level`
- _2026-05-18 delta re-anchor:_ `docs/analysis/diagnostics/premortem_delta_reanchor_feature_evidence_closeout_pilot_2026-05-18.md` — `bounded diagnostics / non-authorizing`
- _Denna doc:_ project-baseline sweep — `historical-trace-level`, ej en delta mot ovanstående utan en fristående bredare syntes
