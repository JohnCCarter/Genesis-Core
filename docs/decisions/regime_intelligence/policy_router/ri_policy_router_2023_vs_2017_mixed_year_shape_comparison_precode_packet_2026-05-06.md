# RI policy router 2023 vs 2017 mixed-year shape comparison precode packet

Date: 2026-05-06
Branch: `feature/next-slice-2026-05-06`
Mode: `RESEARCH`
Status: `föreslagen / pre-code packet / research-evidence only / read-only annual comparison / non-authoritative / no behavior change`

This packet opens the next smallest honest annual follow-up after the completed `2023` mixed-year pocket-isolation slice.

It does **not** reopen the spent D1 line.
It does **not** reopen the closed continuation-release monthly bench.
It does **not** widen into runtime/default/config/policy/promotion work.
It does **not** search across many years after seeing results.

Instead it asks one bounded cross-year comparison question on the already materialized curated annual surfaces:

> when the fixed shared-shape families are counted on the exact mixed full-year annual surfaces for `2023` and `2017`, is the completed `2023` composition read — December-led combined mass, December-led continuation displacement, but June-led suppression — actually distinctive, or does the other mixed full year show a materially similar month-shape profile?

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-05-06`
- **Risk:** `LOW` — why: the slice remains read-only, uses already materialized annual action-diff files, and does not touch runtime/config/default/authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the `2023` annual decomposition is already complete, and the next honest question is a bounded comparison against the only other mixed full year on the curated annual surface rather than a runtime or wider historical reopen.
- **Objective:** compare the fixed shared-shape month composition of annual `2023` versus annual `2017` on the exact curated enabled-vs-absent action-diff surfaces.
- **Candidate:** `2023 vs 2017 mixed-year shape comparison`
- **Base SHA:** `0d8b665cf8d16b76b7c22775fd2a159130ad463e`
- **Skill Usage:** `python_engineering` is explicitly invoked for this bounded helper/test/docs evidence landing; `decision_gate_debug` remains supporting context only, and no runtime/config-authority skill is required because Scope OUT excludes `src/**`, `config/**`, and runtime/default/authority surfaces.

### Research-evidence lane framing

- **Baseline / frozen references:**
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- **Candidate / comparison surface:**
  - `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2017_enabled_vs_absent_action_diffs.json`
  - `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2023_enabled_vs_absent_action_diffs.json`
- **Vad ska förbättras:** move from one-year decomposition to one bounded mixed-year control comparison on the exact annual surface.
- **Vad får inte brytas / drifta:**
  - no widening beyond `2017` and `2023`
  - no new families after seeing the data
  - no runtime/config/default/promotion drift
  - no retelling of `2023` as if the remembered five-row December anchor set had already been annualized
- **Reproducerbar evidens som måste finnas:** deterministic helper output, hermetic targeted test, exact month rankings for both years, one true two-pass determinism replay that emits two distinct temporary JSON outputs and confirms identical SHA256, and one analysis note stating only observational conclusions.

## Why this packet exists

The curated annual evidence already classifies the full years as follows:

- clearly positive: `2018`, `2020`, `2022`, `2025`
- clearly negative: `2019`, `2021`, `2024`
- mixed: `2017`, `2023`

The completed `2023` slice now says something narrower and more truthful than the remembered local December story:

- December is the top combined month in annual `2023`
- December is the top continuation month in annual `2023`
- suppression peaks in June, not December
- only one remembered December anchor survives as annual overlap

That leaves one clean next question:

> is this split composition peculiar to `2023`, or is it simply what a mixed annual surface looks like on the same fixed shared-shape families?

The cheapest honest comparison is `2017`, because it is the only other mixed **full** year already named in the curated annual note.

## Exact research question

Use the same fixed family definitions from the completed `2023` slice:

1. **suppression**
   - absent action = `LONG`
   - enabled action = `NONE`
   - zone = `low`
   - switch reason in `{insufficient_evidence, AGED_WEAK_CONTINUATION_GUARD}`
2. **continuation displacement**
   - absent action = `NONE`
   - enabled action = `LONG`
   - zone = `low`
   - switch reason = `stable_continuation_state`

For each fixed year $y \in \{2017, 2023\}$ and each month bucket $m$ on that annual action-diff surface, define:

$$
\text{shared\_shape\_mass}(y,m) =
\#\{r : r \text{ belongs to year } y \land \text{month}(r)=m \land r \text{ matches either fixed family}\}
$$

The later execution slice must answer only this bounded comparison:

1. what is the full combined month ranking for `2017` and `2023`?
2. what are the separate suppression and continuation month rankings for `2017` and `2023`?
3. is `2023` still December-led on the combined and continuation sides when compared with `2017`?
4. is the June-led suppression shape unique to `2023`, or does `2017` show the same top suppression month?
5. do the two mixed years share the same top combined month, or do they diverge materially at the month-ranking level?

The later helper must report the full ranking tables for both years rather than only the top month.

## Allowed final statuses for the later execution slice

- `mixed_year_shape_differs_between_2017_and_2023`
- `mixed_year_shape_overlaps_between_2017_and_2023`
- `fail_closed_missing_mixed_year_surface`

These statuses are descriptive only.
They do **not** authorize runtime/default/config/policy/promotion claims.

## Exact allowed input surface

The later helper is fail-closed to these repo-visible files only:

- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/enabled_vs_absent_all_years_summary.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2017_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2023_enabled_vs_absent_action_diffs.json`

Supporting wording anchors allowed for note context only:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md`
- `GENESIS_WORKING_CONTRACT.md`

Not allowed:

- widening to positive or negative years in the same slice
- new backtest reruns
- ad hoc threshold fitting
- reopening D1 or continuation-release runtime lanes
- importing new families after the comparison result is known

## Allowed operations

The later helper is allowed to:

1. verify that both `2017` and `2023` exist as full annual surfaces in the summary
2. load only the fixed `2017` and `2023` annual action-diff files
3. compute combined/suppression/continuation month rankings for each year
4. compute exact top-month counts and shares for each year
5. emit one deterministic JSON artifact and one analysis note

The later helper is not allowed to:

- search for a better comparison year after seeing the result
- reinterpret the result as transport-clean or runtime authority
- widen to cross-family or Legacy framing
- change the fixed family definitions

## Planned output paths for a later approved execution slice

- helper: `scripts/analyze/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_20260506.py`
- test: `tests/backtest/test_ri_policy_router_2023_vs_2017_mixed_year_shape_comparison.py`
- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.md`
- JSON artifact: `results/evaluation/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_2026-05-06.json`
- drift-anchor update: `GENESIS_WORKING_CONTRACT.md` only if the completed comparison changes the truthful next admissible step

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_precode_packet_2026-05-06.md`
  - `GENESIS_WORKING_CONTRACT.md` for live branch and next-step re-anchor only
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**`
  - `scripts/**`
  - all D1 helper/test/note surfaces
  - all continuation-release runtime surfaces
  - widening beyond `2017` and `2023`
- **Expected changed files:** `2`
- **Max files touched:** `2`

## Gates required for this docs-only start step

- `pre-commit run --files GENESIS_WORKING_CONTRACT.md docs/decisions/regime_intelligence/policy_router/ri_policy_router_2023_vs_2017_mixed_year_shape_comparison_precode_packet_2026-05-06.md`

## Stop conditions

- scope drift into implementation before a later governed execution step
- widening beyond the fixed `2017` and `2023` mixed-year pair
- any claim that the packet itself proves a result
- any drift into runtime/config/default/promotion surfaces

## Output required from this start step

- one new bounded precode packet for the `2023` vs `2017` mixed-year comparison
- one live-anchor update in `GENESIS_WORKING_CONTRACT.md`

Bottom line for this packet only:

> the next honest move is a fresh read-only mixed-year comparison asking whether the completed `2023` December-led / June-suppression composition is distinctive relative to the only other mixed full year `2017`, while keeping runtime, config-authority, and promotion work explicitly out of scope.
