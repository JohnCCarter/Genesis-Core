# RI policy router insufficient-evidence D1 2023-06 external surface falsifier

Date: 2026-05-07
Branch: `copilot/research-wave1-cloud-dispatch`
Mode: `RESEARCH`
Status: `completed / source_data_unavailable in cloud context / bounded evidence / non-authoritative`

This slice implements the Agent A dispatch contract for the D1 2023-06 external surface
falsifier. The helper reads the committed context-clean artifact for frozen D1 bank ceilings
and attempts to load the 2023 annual action-diff source from the standard regenerate-on-demand
path. In the cloud checkout the source file is absent; the helper emits a deterministic
`source_data_unavailable` result without backfill or rescue.

This slice is observational only, non-authoritative, and does not constitute shared-truth,
promotion, readiness, or runtime authority.

## COMMAND PACKET

- **Mode:** `RESEARCH`
- **Risk:** `LOW`
- **Required Path:** `approved non-trivial RESEARCH helper-backed evidence path`
- **Lane:** `research-evidence`
- **Objective:** transport frozen D1 bank ceilings onto the exact `2023-06` low-zone
  `insufficient_evidence` external surface and record an honest result.
- **Base SHA:** `cf852ad8a559dfd8313405c3c30806fd3ff00e08` (dispatch base)
- **Runner SHA:** `2fb6e9a4824de97934786e6230131ae2008cdc28` (cloud checkout)

## Evidence inputs

- `results/evaluation/ri_policy_router_insufficient_evidence_d1_context_clean_selectivity_falsifier_2026-05-05.json` (committed — used for bank ceilings)
- `results/backtests/ri_policy_router_enabled_vs_absent_all_years_20260428_curated_only/2023_enabled_vs_absent_action_diffs.json` (regenerate-on-demand — **absent in cloud checkout**)

## Frozen D1 bank ceilings (loaded from committed artifact)

These were loaded successfully in the cloud context.

| field | target_bank_ceiling | context_bank_min | descriptive_only |
| --- | --- | --- | --- |
| `action_edge` | `0.033803` | `0.042122` | `False` |
| `confidence_gate` | `0.516902` | `0.521061` | `False` |
| `clarity_raw` | `0.364914` | `0.369952` | `False` |
| `clarity_score` | `36.0` | `37.0` | `True` |

## Exact result

**Status: `source_data_unavailable`**

The 2023 annual action-diff source was not present in the cloud checkout. The helper failed
closed per contract. No transport was performed. No row-lock was materialized.

## Artifact

```
results/evaluation/ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_2026-05-07.json
SHA256: cb7edad5efca58ed2b2e4f290d95d6caa5d6f4ebecef4f43661d9fd3bede8571
```

This artifact is `results/evaluation/**/*.json` (git-ignored by default; force-added for
this slice).

Regenerate-on-demand command (requires the annual diff source to be present locally):

```
python scripts/analyze/ri_policy_router_insufficient_evidence_d1_2023_06_external_surface_falsifier_20260507.py \
    --base-sha <HEAD_SHA>
```

## Observed / Inferred / Unverified separation

### Observed (directly from committed artifacts)

- The committed context-clean artifact (`2026-05-05`) holds the following frozen D1 bank
  ceilings: `action_edge ≤ 0.033803`, `confidence_gate ≤ 0.516902`, `clarity_raw ≤ 0.364914`.
- The cloud checkout does not contain the 2023 annual action-diff artifact
  (`results/backtests/**` is git-ignored).
- The helper correctly emits `source_data_unavailable` and does not attempt backfill or rescue.

### Inferred (from the pocket isolation analysis note — cloud-visible on base branch)

- The 2023 mixed-year pocket isolation note
  (`ri_policy_router_2023_mixed_year_pocket_isolation_2026-05-06.md`) characterizes the June
  `2023` suppression pocket as approximately 19 low-zone suppression rows (with
  `switch_reason in {insufficient_evidence, AGED_WEAK_CONTINUATION_GUARD}`) and 14
  continuation-displacement rows.
- The 2023-vs-2017 shape comparison note confirms that June `2023` is the top suppression
  month in the `2023` mixed-year surface.
- Neither note contains row-level timestamps or field values; they are shape-level
  characterizations only.

### Unverified (requires the annual diff source)

- Whether any of the June `2023` low-zone `insufficient_evidence` rows have
  `action_edge ≤ 0.033803` (D1 bank ceiling).
- Whether any of the June `2023` low-zone `insufficient_evidence` rows have
  `confidence_gate ≤ 0.516902`.
- Whether the D1 bank transport survives or is falsified on the `2023-06` surface.
- Whether `clarity_raw` is present in the annual diff `router_debug` for June `2023` rows
  (expected absent; would remain `not_evaluable` regardless per fail-closed contract).

## What this does not prove

1. This slice does **not** prove that the D1 bank ceilings hold on the `2023-06` surface.
   The surface was never loaded.
2. This slice does **not** prove that the D1 bank ceilings are falsified on the `2023-06`
   surface. The status `source_data_unavailable` is not a transport result.
3. This slice does **not** identify any specific timestamps in the `2023-06` low-zone
   `insufficient_evidence` cohort. The pocket isolation note provides shape counts only.
4. This slice does **not** constitute a search for new thresholds or new feature families.
5. This slice does **not** extend the D1 bank to `2023-06` or claim that `2023-06` matches
   the D1 family shape.
6. This slice does **not** authorize runtime, default, or promotion changes. Nothing
   follows from `source_data_unavailable`.

## Hermetic test coverage

Six hermetic tests were implemented and pass in the cloud context without any dependency on
the annual diff source:

| test | scenario | expected status |
| --- | --- | --- |
| `test_source_data_unavailable_when_annual_diff_missing` | annual diff absent | `source_data_unavailable` |
| `test_external_surface_survivor_when_all_target_rows_pass` | all target rows below ceilings | `external_surface_survivor` |
| `test_external_surface_falsified_when_target_rows_exceed_ceiling` | all target rows above ceilings | `external_surface_falsified` |
| `test_leaky_antitarget_causes_falsification` | antitarget leaks through ceiling | `external_surface_survivor` (partial) |
| `test_row_lock_records_exact_surface` | row-lock metadata | pass |
| `test_non_june_rows_excluded` | non-June rows excluded | target_count correct |

## fail_closed_contract (verbatim from artifact)

> The helper reads only the frozen D1 context-clean artifact for bank ceilings and the 2023
> annual diff artifact for the external surface. If the annual diff source is absent it emits
> source_data_unavailable without backfill or rescue. clarity_raw is always not_evaluable on
> this surface because annual diff router_debug does not carry clarity_raw. clarity_score is
> descriptive-only with no PASS/FAIL authority.

## Next admissible move

If this slice is extended beyond the cloud-only context, the only admissible next step is:

1. Run the 2023 annual diff backtest locally to regenerate the source artifact.
2. Re-execute the helper with the source present.
3. Record the honest transport result in a follow-up evidence note.

What is **not** justified by this slice alone:

- Any claim about the `2023-06` surface D1 compatibility.
- New threshold or feature-family search.
- Widening the surface to include non-June rows.
- Any promotion, readiness, or runtime change.

## Overlap avoidance

- Agent B ownership tuple: `{window=2017-06, question class=D1 packet-first corroborative}` — no overlap.
- Agent C ownership tuple: `{window=2023-04, question class=D1 dormant fallback}` — no overlap.
- This slice remains within the Agent A ownership tuple: `{window=2023-06, question class=D1 external falsifier}`.
