# Ignored-artifact dependency inventory

## Claim header

- **Date:** `2026-05-15`
- **Branch:** `feature/evidence-closeout-pilot`
- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Lane:** `Research-evidence` — why: this note inventories decision-influencing dependency families that still rely on ignored or local-only inputs and records only bounded observational findings about their current carrier posture
- **Status:** `observational / diagnostics inventory`
- **Authority level:** `bounded research-evidence`
- **Claim status:** `observed`
- **Objective:** inventory the smallest current set of decision-influencing dependency families that still depend on ignored `results/**`, cache posture, or workstation-local artifacts, and rank the next admissible follow-ups behind them
- **Baseline reference(s):** `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md`, `docs/analysis/diagnostics/genesis_core_premortem_feature_evidence_closeout_pilot_2026-05-15.md` (`local-only / untracked / historical reference only / not repository-tracked authority`), `docs/governance/runbooks/evidence_claim_adoption.md`, `docs/governance/templates/evidence_claim_header.md`, `docs/governance/runbooks/editor_slice_worker_dispatch.md`
- **Candidate / comparison surface:** `family-level inventory across Phase 10 historical-trace notes, SCPE replay-root derived notes, volatility-policy env-profile notes, and router-replay execution summaries`
- **Input carrier:** `tracked docs and cited historical notes only; no underlying replay/backtest evidence was rerun in this slice`
- **Runtime base SHA:** `06aafa872099402a1df70a822b66d93340f71192`
- **Evidence commit SHA:** `not rerun in this slice; inventory derived from tracked docs and cited historical notes`
- **Working-tree status:** `dirty` — one unrelated untracked premortem note remains in the working tree outside this slice
- **Config path:** `not applicable`
- **Config hash:** `not applicable`
- **Symbol / timeframe:** `not applicable` — this note inventories dependency families rather than executing one market subject
- **Window:** `not applicable`
- **Warmup:** `not applicable`
- **Data-source policy:** `tracked docs and cited historical notes only`
- **Symbol mode:** `not applicable`
- **Env flags:** `no additional env flags were set for this docs-only slice`
- **Cache policy:** `no cache reads or writes were performed in this slice; cache dependence is recorded only when cited notes name it explicitly`
- **Artifact path(s):**
  - `docs/analysis/diagnostics/ignored_artifact_dependency_inventory_2026-05-15.md`
  - `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md`
- **Artifact hash(es):** `not applicable`
- **What changed:** `one bounded diagnostics inventory note ranks four representative dependency families that still rely on ignored or local-only inputs`
- **What did not change:** `no source/test/runtime/config-authority/results/cache surface changed; no carrier decision was implemented in this slice`
- **Does not authorize:** `runtime changes, carrier implementation, replay portability claims, paper/live conclusions, or archive-wide note retrofits`

## Inventory boundary

This note inventories dependency **families**, not every sibling file that mentions `results/**`.

Selection rule used in this slice:

- include only notes or packets likely to carry decision weight outside scratch context
- group siblings by the dependency root they actually rely on
- stop once the next admissible follow-up ranking becomes clear

## Observed inventory

| Rank | Dependency family                                                                      | Representative decision-influencing note(s)                                                                                                                                                                                                                                            | Dependency type                                                                                                                                      | Current carrier status             | Smallest next admissible follow-up                                                                        |
| ---: | -------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------- |
|    1 | SCPE / Phase C mixed replay family                                                     | `docs/analysis/scpe_ri_v1/scpe_ri_v1_selected_defensive_transition_window_audit_report_2026-04-20.md`; `docs/analysis/scpe_ri_v1/scpe_ri_v1_router_replay_script_promotion_report_2026-04-20.md`                                                                                       | tracked `results/research/scpe_v1_ri/**` plus ignored `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/**` | `mixed / partially commit-safe`    | one bounded carrier decision or explicit non-portable classification for the Phase C capture dependency   |
|    2 | Volatility-policy result-root + cache family                                           | `docs/decisions/volatility_policy/current_atr_900_env_profile_packet_2026-04-16.md`                                                                                                                                                                                                    | ignored `results/research/fa_v2_adaptation_off/**` output root plus explicit `cache/precomputed/` containment watch                                  | `local-only / cache-sensitive`     | exact carrier or same-local-only classification for the `current_atr >= 900` environment-profile outputs  |
|    3 | Router-replay execution-summary family                                                 | `docs/analysis/regime_intelligence/router_replay/ri_router_replay_defensive_transition_backtest_execution_summary_2026-04-23.md`                                                                                                                                                       | emitted `results/backtests/**` decision rows plus workstation-local interpreter path and explicit env/cache posture                                  | `same-local-checkout only`         | explicit launch-surface carrier classification rather than implied clean-checkout portability             |
|    4 | Phase 10 historical-trace family (`execution_proxy_evidence`, `edge_origin_isolation`) | `docs/analysis/diagnostics/decision_influencing_replay_smoke_candidate_selection_2026-05-15.md`; `docs/decisions/governance/execution_proxy_replay_claim_level_boundary_packet_2026-05-15.md`; `docs/decisions/governance/edge_origin_isolation_carrier_decision_packet_2026-05-15.md` | ignored historical traces under `results/research/fa_v2_adaptation_off/**` behind now-separated bounded carrier strategies                           | `mixed / bounded carrier selected` | keep current claims below historical-trace-level unless a separate retained-trace carrier slice is opened |

## Observed family notes

### 1. SCPE / Phase C mixed replay family remains the highest unresolved dependency root

The current SCPE-derived line is no longer a missing-manifest problem, but it is still not one clean carrier story.

Observed from the cited reports:

- the tracked replay-root promotion report treats `results/research/scpe_v1_ri/**` as a frozen replay root and records one commit-safe summary artifact under `results/evaluation/**`
- the selected-defensive transition-window audit still depends on ignored Phase C entry rows under `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/**`
- the newer `defensive_probe` carrier packet intentionally narrowed only one exact local pocket and did **not** promote the broader mixed-root chain into a portable replay claim

That leaves a real mixed-root dependency family: partly tracked, partly ignored, and therefore easy to remember more cleanly than it really is.

### 2. Volatility-policy environment profiling remains local-output and cache-aware

The current ATR 900 environment-profile packet is decision-bearing enough to matter, but its packeted surface still lives under ignored `results/research/**` and explicitly watches `cache/precomputed/` as a containment surface.

That means the observational conclusion can be useful while the artifact chain remains non-portable by default.

### 3. Router-replay execution summaries remain bounded launch evidence, not clean-checkout portability proof

The paired backtest execution summary is careful and honest, but it still depends on:

- emitted `results/backtests/**` decision-row files
- explicit local interpreter paths under `C:/Users/.../.venv/...`
- explicit env/cache posture such as `GENESIS_PRECOMPUTE_CACHE_WRITE=0`

This is valuable same-local-checkout execution evidence, but it is not the same thing as a commit-safe reproducibility carrier.

### 4. Phase 10 historical traces are still the buried dependency behind the newly bounded carrier lines

The branch already reduced risk here:

- `execution_proxy_evidence` is pinned to `fixture-level`
- `edge_origin_isolation` has one bounded minimal-fixture carrier strategy

But the older historical traces under `results/research/fa_v2_adaptation_off/**` still sit behind any stronger historical-trace portability claim. So this family is reduced, not closed.

## Inferred

- The branch has reduced one dependency class at a time, but it has **not** yet eliminated ignored/local-only dependency risk across all decision-bearing chains.
- The most urgent unresolved follow-up is the **SCPE / Phase C mixed replay family**, because its tracked replay-root surfaces can hide the still-ignored Phase C carrier dependency.
- The next-highest unresolved family after that is the **volatility-policy result-root + cache family**, because it combines ignored result roots with explicit cache posture and could later be remembered as more portable than it is.
- The **router-replay execution-summary family** needs explicit same-local-checkout classification before anyone casually upgrades it into broader reproducibility language.
- The **Phase 10 historical-trace family** should remain parked at its current bounded labels unless a later slice explicitly needs stronger historical-trace or full-chain portability claims.

## Unverified

- This note does **not** prove that these four families are the only ignored/local-only dependency families in the repo.
- This note does **not** rerun any underlying replay, backtest, or evidence script.
- This note does **not** choose or implement the next carrier decision by itself; it only ranks the follow-up candidates.
- This note does **not** settle queue-freshness policy; that remains Slice 12.

## Why this note matters

Slice 10 made the provenance envelope explicit.

Slice 11 asks the natural next question: where are the biggest remaining dependency roots that can still make a decision-bearing note look more portable than it really is?

The answer is not "every file that mentions `results/**`". The answer is a short ranked family list that points to the next honest carrier questions.

## Bottom line

The current branch has improved claim discipline, carrier discipline, and header discipline, but ignored/local-only dependency risk still exists in a few concentrated families. The highest unresolved root is the **SCPE / Phase C mixed replay family**, followed by the **volatility-policy result-root + cache family**, then the **router-replay execution-summary family**, while the **Phase 10 historical-trace family** is partially reduced but still below stronger portability labels. That ranking is enough to choose future carrier work without pretending this note is a full repo audit.
