# Batch 030 RI experiment-map reselection direction historical framing audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only status/framing audit / non-authorizing / docs-only / no behavior change`

> This file is a bounded audit for one retained RI experiment-map reselection direction packet. It
> does **not** reopen a current active direction, slice-opening authority, launchable lane,
> runtime authority, or promotion meaning by itself.

## Scope boundary

Primary candidate in scope:

- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_signal_segmentation_direction_packet_2026-03-30.md`

Supporting anchors in scope:

- `docs/analysis/regime_intelligence/core/regime_intelligence_experiment_map_reselection_roadmap_2026-03-30.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_experiment_map_post_binding_roadmap_2026-03-30.md`
- `docs/audit/ri_upstream_candidate_authority_direction_historical_framing_audit_batch_028.md`

Out of scope in this batch:

- editing either experiment-map roadmap file
- editing any experiment-map candidate-surface, packet-boundary, or later binding note
- rewriting any body content below the target file's top framing block, including chosen class,
  3h anchor, non-reopen boundary, candidate classes under decision, and explicit non-authorization boundary
- changing any runtime, config, test, script, tmp, results, or artifact surface named in the retained packet
- editing `docs/CURRENT_AUTHORITY_INDEX.md`
- editing `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
- editing the locally modified Batch 020, Batch 021, Batch 022, Batch 023, Batch 024, Batch 025, Batch 026, Batch 027, or Batch 028 audit files

## Method

Checked in this slice:

- full read of the retained experiment-map reselection direction packet
- read of the two already historicalized roadmap anchors for bounded current-use context only
- top-of-file status/current-use framing check for the target file only
- targeted diff review confirming the target file changed only in the top framing block and that the preserved body remained verbatim from `## COMMAND PACKET` downward

Skill coverage note:

- no suitable repo-local skill was identified for this bounded docs-only historical-framing slice
- any future reusable skill coverage for this exact historical-framing audit pattern remains `föreslagen`, not `införd`

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch030_ri_experiment_map_reselection_direction_framing_evidence.json`

## Observed

### The target is a claim-bearing historical direction-selection record

Observed supporting context:

- the retained packet records the then-chosen experiment-map reselection class on 2026-03-30
- the adjacent roadmap chain is already historicalized/archived and no longer framed as an active
  sequencing surface on later branches
- the target body is explicitly planning-only and non-authorizing, but still reads like an active
  class-selection record at the file top

### The retained experiment-map direction packet top still reads like the current active direction

Observed pre-change drift:

- `regime_intelligence_experiment_map_reselection_signal_segmentation_direction_packet_2026-03-30.md`
  begins with `direction-selected / planning-only / no authorization`

Observed skim-risk pattern:

- without a top historical/current-use note, later readers can over-read the retained packet as the
  current active experiment-map direction rather than as an exact earlier branch/state direction-selection record
- the stale effect is concentrated at the top; the body below should remain a verbatim historical
  direction record in this slice

## Inferred

- the safe correction is a **top-framing plus historical/current-use note only** patch
- the safe patch shape in this batch is:
  - replace the stale top status label with historical/current-use framing only
  - add one narrow note stating that the chosen class below records the exact earlier branch/state
    direction-selection only
  - explicitly deny current active-direction status, slice-opening authority, launchable-lane
    status, runtime authority, and promotion meaning at the top
  - preserve every body section below the framing block verbatim

## UNRESOLVED

- `UNRESOLVED:` whether any later experiment-map candidate-surface or binding-note packet should
  receive its own more sensitive historical-framing pass after this direction record is stabilized

## Batch result summary

- Candidates reviewed: `1`
- `YELLOW_NEEDS_REVIEW`: `1`
- `KEEP_AS_IS`: `0`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate                                                                                                                                            | Observed role                                    | Drift signal                                                   | Classification        | Safe batch action                                 |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | -------------------------------------------------------------- | --------------------- | ------------------------------------------------- |
| `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_signal_segmentation_direction_packet_2026-03-30.md` | historical direction-selection record            | stale `direction-selected / planning-only / no authorization` reads current | `YELLOW_NEEDS_REVIEW` | replace top framing and add historical note only |

## What changed vs. what did not change

This audit supports changing:

- only the top framing block of the retained experiment-map reselection direction packet

This audit does **not** support changing:

- either roadmap file
- the chosen class, 3h anchor, non-reopen boundary, or any body section below the framing block
- any runtime/config/test/script/tmp/results/artifacts surface named in the retained packet

## Bottom line

Batch 030 is a bounded historical-framing correction for one claim-bearing retained experiment-map
reselection direction surface.

The classification applies to header framing only; the body remains a verbatim historical direction
record and is not re-audited here for current active-direction status, slice-opening authority,
runtime authority, or promotion meaning.
