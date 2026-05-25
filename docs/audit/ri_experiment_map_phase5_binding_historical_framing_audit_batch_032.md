# Batch 032 RI experiment-map Phase 5 binding historical framing audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only status/framing audit / non-authorizing / docs-only / no behavior change`

> This file is a bounded audit for one retained RI experiment-map Phase 5 binding note.
> It does **not** reopen a current active binding, current pre-code-reference authority,
> launch authority, execution authority, runtime authority, or promotion meaning.

## Scope boundary

Primary candidate in scope:

- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_phase5_precode_binding_note_2026-03-30.md`

Supporting anchors in scope:

- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_signal_segmentation_direction_packet_2026-03-30.md`
- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_regime_definition_candidate_surface_packet_2026-03-30.md`
- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_regime_definition_packet_boundary_2026-03-30.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_experiment_map_reselection_roadmap_2026-03-30.md`
- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_regime_definition_slice1_precode_command_packet_2026-03-27.md`

Out of scope in this batch:

- editing any same-family direction, candidate-surface, packet-boundary, roadmap, or pre-code reference packet
- rewriting any body content below the target file's top framing block, including selected future pre-code reference, compatibility statement, historical status preserved, explicit non-authorization boundary, and bottom line
- changing any runtime, config, test, script, tmp, or results surface named in the retained note
- editing `docs/CURRENT_AUTHORITY_INDEX.md`
- editing `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
- editing locally modified prior audit files, including Batch 020, Batch 021, Batch 022, Batch 023, Batch 024, Batch 025, Batch 028, Batch 029 if drifted, and Batch 030

## Method

Checked in this slice:

- full read of the retained Phase 5 binding note
- read of same-family direction, candidate-surface, packet-boundary, roadmap, and referenced pre-code packet anchors for bounded current-use context only
- top-of-file status/current-use framing check for the target file only
- targeted diff review requirement confirming the target file changes only in the top framing block and that the preserved body remains verbatim from `## COMMAND PACKET` downward

Skill coverage note:

- no suitable repo-local skill was identified for this bounded claim-bearing historical-framing slice
- any future reusable skill coverage for this exact audit pattern remains `föreslagen`, not `införd`

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch032_ri_experiment_map_phase5_binding_framing_evidence.json`

## Observed

### The target is a claim-bearing historical binding record

Observed supporting context:

- the retained note records the then-current Phase 5 resolution that bound the March 30 reselection chain to one already existing 2026-03-27 bounded pre-code packet
- same-family direction history is already historicalized in current branch context
- neighboring same-family candidate-surface and packet-boundary files still retain earlier live-looking top statuses, which increases skim-risk if this Phase 5 binding note also keeps a present-tense top status

### The target top still reads like an active binding decision

Observed pre-change drift:

- `regime_intelligence_experiment_map_reselection_phase5_precode_binding_note_2026-03-30.md`
  begins with `phase5-resolved / planning-only / no authorization`

Observed skim-risk pattern:

- without a historical/current-use note at the top, later readers can over-read the retained note as the current active pre-code reference binding rather than as the exact earlier branch/state binding record
- the stale effect is concentrated at the top; the body below should remain a verbatim historical Phase 5 binding record in this slice

## Inferred

- the safe correction is a **top-framing plus historical/current-use note only** patch
- the safe patch shape in this batch is:
  - replace the stale top status label with historical/current-use framing only
  - add one narrow note stating that the retained binding below is the exact earlier branch/state reference-binding record only
  - explicitly deny current active binding authority, current pre-code-reference authority, launch/execution authority, runtime authority, and promotion meaning at the top
  - preserve every body section below the framing block verbatim

## UNRESOLVED

- `UNRESOLVED:` whether the same-family candidate-surface and packet-boundary records should later receive their own separate historical-framing passes after this Phase 5 binding record is stabilized

## Batch result summary

- Candidates reviewed: `1`
- `YELLOW_NEEDS_REVIEW`: `1`
- `KEEP_AS_IS`: `0`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate                                                                                                                                      | Observed role                          | Drift signal                                                         | Classification        | Safe batch action                                 |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- | -------------------------------------------------------------------- | --------------------- | ------------------------------------------------- |
| `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_phase5_precode_binding_note_2026-03-30.md` | historical Phase 5 reference-binding record | stale `phase5-resolved / planning-only / no authorization` reads current | `YELLOW_NEEDS_REVIEW` | replace top framing and add historical note only |

## What changed vs. what did not change

This audit supports changing:

- only the top framing block of the retained experiment-map Phase 5 binding note

This audit does **not** support changing:

- same-family direction, candidate-surface, packet-boundary, roadmap, or referenced pre-code packet files
- the selected future pre-code reference or any body section below the framing block
- any runtime/config/test/script/tmp/results surface named in the retained note

## Bottom line

This audit concludes that the target document now functions in current branch context as a historical earlier branch/state Phase 5 binding record.

The top framing block may be updated to remove present-tense binding ambiguity, while the retained body remains verbatim as the historical record of the earlier binding and continues to carry no launch, execution, runtime, or promotion authority.
