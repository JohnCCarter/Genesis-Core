# RI policy router 2023 mixed-year pocket isolation precode packet

Date: 2026-05-06
Branch: `feature/next-slice-2026-05-05`
Mode: `RESEARCH`
Status: `föreslagen / pre-code packet / research-evidence only / read-only annual decomposition / non-authoritative / no behavior change`

This packet opens the next smallest honest question after the current D1 insufficient-evidence line has been re-anchored as a bounded evidence bank with one completed context-clean reread, one completed first fresh external-surface falsifier, and one completed bank-state synthesis.

It does **not** reopen the D1 line by default.
It does **not** reuse March as a primary loop.
It does **not** reuse July `2024` as a primary subject.
It does **not** reuse late-2024 as a recycled external holdout.
It does **not** reopen the closed `2024` versus `2020` control branch.
It does **not** authorize runtime/default/config/policy/promotion work.

Instead it pivots to one fresh read-only annual/pocket question on a repo-visible surface that remains explicitly unresolved in the historical annual evidence:

> on the mixed curated annual `2023` enabled-vs-absent surface, does the year materially concentrate into one late-year low-zone suppression + continuation-displacement pocket anchored by the already-documented December 2023 subject, or is the mixed annual verdict distributed across multiple unrelated months?

This is a new interpretation question.
It is not a continuation of the spent D1 bank loop.
It is not a runtime carrier question.

## COMMAND PACKET

- **Category:** `obs`
- **Mode:** `RESEARCH` — source: live branch `feature/next-slice-2026-05-05`
- **Risk:** `LOW` — why: the slice is read-only, uses one already-materialized annual action-diff file plus already-written analysis notes, and adds only helper/test/docs surfaces without touching runtime/config/default/authority paths.
- **Required Path:** `non-trivial RESEARCH proof path`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the D1 line has been honestly re-anchored and should not be widened cheaply by default, while `2023` remains explicitly mixed in the curated annual evidence and has not yet received a bounded annual pocket-isolation slice.
- **Objective:** determine whether the mixed annual `2023` enabled-vs-absent surface is dominated by one bounded late-year shared-shape pocket or instead remains broadly distributed across multiple months.
- **Candidate:** `2023 mixed-year shared-shape pocket isolation`
- **Base SHA:** `e958bd3e266830ecbc66150d1e5021c0a68df56c`
- **Skill Usage:**
  - `.github/skills/decision_gate_debug.json`
  - `.github/skills/python_engineering.json`

## Why this packet exists

The curated annual enabled-vs-absent evidence already established that `2023` is one of the mixed full years:

- clearly positive full years: `2018`, `2020`, `2022`, `2025`
- clearly negative full years: `2019`, `2021`, `2024`
- mixed full years: `2017`, `2023`

The first negative-year pocket isolation intentionally excluded mixed years.
The later positive-vs-negative pocket comparison still answered only whether the broad low-zone suppression + later continuation-displacement shape is unique to negative years.
It did **not** explain the unresolved status of the mixed `2023` year itself.

At the same time, the repository already contains bounded December 2023 router evidence on the exact fail-B carrier and the later residual diagnostics:

- bounded contribution on `2023-12-01 -> 2023-12-31`
- exact helper-hit proof at `2023-12-20T03:00:00+00:00`
- a documented low-zone no-trade-floor / min-dwell cluster on `2023-12-20`
- a documented later aged-weak continuation guard cluster on `2023-12-28` and `2023-12-30`

That combination means the next honest question is no longer another D1 falsifier.
It is a bounded annual decomposition question:

> is December 2023 merely one remembered local pocket, or is it actually the dominant carrier of the shared annual `2023` mixed-year action-diff mass?

## Exact research question

The later execution slice must answer only this bounded question:

### 2023 mixed-year shared-shape question

On the exact annual `2023` curated enabled-vs-absent action-diff surface, and using only the already-established shared-shape action families from the annual pocket work,
which month carries the largest low-zone shared-shape mass, and does December `2023` rank first on that exact annual surface?

The shared-shape action families are fixed as follows:

1. **suppression rows**
   - absent action = `LONG`
   - enabled action = `NONE`
   - enabled router zone = `low`
   - enabled router `switch_reason` in:
     - `insufficient_evidence`
     - `AGED_WEAK_CONTINUATION_GUARD`
2. **continuation-displacement rows**
   - absent action = `NONE`
   - enabled action = `LONG`
   - enabled router zone = `low`
   - enabled router `switch_reason` = `stable_continuation_state`

For each row $r$ on the fixed annual `2023` action-diff surface, define:

$$
\text{month}(r) = \text{UTC year-month bucket of the row timestamp}
$$

and define the per-month shared-shape mass as:

$$
\text{shared\_shape\_mass}(m) =
\#\{r \in 2023 : \text{month}(r)=m \land r \text{ matches either fixed family above}\}
$$

The later helper must report:

1. the complete month ranking of `shared_shape_mass(m)` for all months present in the annual `2023` diff file,
2. the separate month rankings for suppression rows and continuation-displacement rows,
3. the exact December `2023` rows contributing to the shared-shape mass,
4. whether the already-documented December rows appear on the annual surface,
5. whether December is the top month by combined shared-shape mass.

The later targeted hermetic test must assert the actual research contract rather than only successful execution:

1. deterministic full month ranking on a fixed synthetic annual surface,
2. deterministic December overlap row set,
3. deterministic `is_december_top_month` outcome,
4. fail-closed handling when the fixed `2023` annual surface is absent or malformed.

Allowed final statuses for the later execution slice are:

- `december_is_top_shared_shape_month`
- `december_is_not_top_shared_shape_month`
- `fail_closed_missing_2023_annual_surface`

These statuses are descriptive only.
They do **not** authorize tuning, runtime, transport, or promotion claims.

## Exact allowed input surface

The later helper is fail-closed to the following repo-visible surfaces only:

- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/enabled_vs_absent_all_years_summary.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2023_enabled_vs_absent_action_diffs.json`

Supporting descriptive anchors allowed for packet/note wording only:

- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_curated_annual_evidence_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_negative_year_pocket_isolation_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_positive_vs_negative_pocket_comparison_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_bounded_contribution_evidence_2026-04-28.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `GENESIS_WORKING_CONTRACT.md`

Not allowed:

- raw backtest reruns
- new year mining outside `2023`
- reopening the D1 bank surfaces
- reopening March, July `2024`, late-2024, or the closed `2024` versus `2020` branch
- any runtime/config/default authority surface

## Fixed December anchor rows allowed for descriptive overlap checks only

The later helper may report overlap against these already-documented December 2023 rows if they appear on the annual `2023` surface:

- `2023-12-20T03:00:00+00:00`
- `2023-12-21T18:00:00+00:00`
- `2023-12-22T09:00:00+00:00`
- `2023-12-28T09:00:00+00:00`
- `2023-12-30T21:00:00+00:00`

These rows are descriptive anchors only.
They may not be used to refit the monthly ranking or narrow the annual subject after the result is known.

## Allowed operations

The later helper is allowed to:

1. read the fixed annual summary and exact `2023` annual action-diff file,
2. assert that `2023` exists in the summary and remains a non-partial full year,
3. compute per-month counts for the two fixed shared-shape families,
4. compute a combined per-month shared-shape ranking,
5. emit the exact contributing December rows,
6. record overlap with the fixed December anchor rows,
7. emit one deterministic JSON artifact and one human-readable analysis note.

The later helper is not allowed to:

- widen to `2017` in the same slice,
- search for a better month after seeing the result,
- introduce a new pocket family,
- fit thresholds,
- use payoff-state fields as classifier inputs,
- reopen runtime packets,
- or infer promotion or transport authority from the ranking.

## Success / fail-closed rule

A later execution slice may report either month-ranking outcome only if all of the following remain true:

1. the `2023` annual action-diff file exists and is readable,
2. `2023` remains a full year in the curated annual summary,
3. every counted row matches one of the two pre-registered shared-shape families exactly,
4. the helper reports the full month ranking rather than only December,
5. December overlap rows are reported descriptively only,
6. no new year, no new family, and no threshold search is introduced.

The slice must fail closed if any of the following occurs:

- missing `2023` annual surface,
- missing or malformed router debug fields required for the fixed family definitions,
- widening to additional years,
- attempts to reinterpret the monthly ranking as runtime authority,
- or any drift into runtime/config/default/promotion surfaces.

## Planned output paths

If this packet is approved and executed, the exact output paths should be:

- helper: `scripts/analyze/ri_policy_router_2023_mixed_year_pocket_isolation_20260506.py`
- test: `tests/backtest/test_ri_policy_router_2023_mixed_year_pocket_isolation.py`
- analysis note: `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md`
- JSON artifact: `results/evaluation/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.json`
- drift-anchor update: `GENESIS_WORKING_CONTRACT.md` only if the completed slice changes the truthful next admissible step

Planned JSON artifact retention rule for the later execution slice:

- default posture: treat `results/evaluation/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.json` as **regenerate-on-demand evidence** unless git visibility/staging is explicitly verified on the current checkout,
- required note content: record the verified deterministic rerun SHA256 in the analysis note,
- if git visibility is unexpectedly clean and explicit staging is desired, that decision must be stated in the analysis note rather than assumed.

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_precode_packet_2026-05-06.md`
  - `scripts/analyze/ri_policy_router_2023_mixed_year_pocket_isolation_20260506.py`
  - `tests/backtest/test_ri_policy_router_2023_mixed_year_pocket_isolation.py`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md`
  - `results/evaluation/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.json`
  - `GENESIS_WORKING_CONTRACT.md` only if the completed slice changes the truthful next-step anchor
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `tests/**` other than the one new targeted test file above
  - D1 bank helper/test/docs surfaces
  - March `2021` / March `2025`
  - July `2024`
  - late-2024 external surface reuse
  - the closed `2024` versus `2020` branch
  - runtime/default/policy/family/champion/promotion/readiness surfaces
- **Expected changed files:** `4-6`
- **Max files touched:** `6`

## Validation requirements for a later execution slice

- `get_errors` on all touched files
- `ruff check` on the new helper and test
- targeted `pytest` on the new test file
- one helper run against the fixed `2023` annual action-diff file
- deterministic rerun hash check on the emitted JSON artifact
- smoke selector: `tests/governance/test_import_smoke_backtest_optuna.py`
- determinism selector: `tests/backtest/test_backtest_determinism_smoke.py`
- feature-cache invariance selectors:
  - `tests/utils/test_features_asof_cache.py`
  - `tests/utils/test_features_asof_cache_key_deterministic.py`
- pipeline invariant selector:
  - `tests/governance/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
- `pre-commit run --files` on the touched files
- explicit git-visibility check for the JSON artifact path before any claim of retained evidence:
  - `git status --short --ignored -- "results/evaluation/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.json"`
  - `git check-ignore -v "results/evaluation/ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.json"` if needed
- Opus post-diff audit confirming no scope or authority drift

## Stop conditions

- the slice starts to widen into `2017` or other years,
- the slice starts to behave like a tuning or candidate-selection effort,
- the slice reopens D1 or December runtime packets instead of staying annual/read-only,
- or the fixed family definitions are changed after seeing the data.

## Output required from a later execution slice

- one deterministic JSON artifact giving the month ranking of the fixed shared-shape mass on annual `2023`
- one analysis note stating whether December is or is not the top shared-shape month on that exact surface
- exact December overlap rows, if present
- exact validation outcomes

## What this packet does not authorize

This packet does **not** authorize:

- a `2017` mixed-year slice in the same block
- a new D1 falsifier
- a new runtime helper or packet
- threshold fitting
- promotion of the December 2023 pocket into annual mechanism authority
- runtime/default/policy/config changes

Bottom line for this packet only:

> the next honest move is a fresh read-only annual decomposition asking whether mixed `2023` materially concentrates into one December-anchored shared-shape pocket on the exact annual surface, not another cheap D1 recurrence extension and not a runtime reopening.
