# Batch 033 RI experiment-map candidate/boundary historical framing audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only status/framing audit / non-authorizing / docs-only / no behavior change`

> This file is a bounded audit for two retained RI experiment-map decision records.
> It does **not** reopen a current candidate-surface decision, a current packet-boundary decision,
> current pre-code sequencing authority, launch/execution authority, runtime authority, or promotion meaning.

## Scope boundary

Primary candidates in scope:

- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_regime_definition_candidate_surface_packet_2026-03-30.md`
- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_regime_definition_packet_boundary_2026-03-30.md`

Supporting anchors in scope:

- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_signal_segmentation_direction_packet_2026-03-30.md`
- `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_phase5_precode_binding_note_2026-03-30.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_experiment_map_post_binding_roadmap_2026-03-30.md`

Out of scope in this batch:

- editing same-family direction, Phase 5 binding, or post-binding roadmap files
- rewriting any body content below each target file's framing block, including chosen surface, packet-boundary decision, relation to admissibility, explicit non-authorization boundary, and bottom-line language
- changing any runtime, config, test, script, tmp, or results surface named in the retained files
- editing `docs/CURRENT_AUTHORITY_INDEX.md`
- editing `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
- editing locally modified prior audit files, including Batch 028, Batch 029 if drifted, Batch 030, Batch 031, Batch 032, and locally modified SCPE audit files 020-025

## Method

Checked in this slice:

- full read of both retained experiment-map decision records
- read of the already historicalized same-family direction record, the already historicalized same-family Phase 5 binding record, and the already historicalized post-binding roadmap for bounded current-use context only
- top-of-file status/current-use framing check for the two target files only
- targeted diff review requirement confirming each target file changes only in the top framing block and that the preserved body remains verbatim from `## COMMAND PACKET` downward

Immutability boundary used for proof:

- candidate-surface file body begins at `## COMMAND PACKET`
- packet-boundary file body begins at `## COMMAND PACKET`
- this audit verifies top-block reframing only and does **not** reopen the underlying candidate-surface or packet-boundary decision

Skill coverage note:

- no suitable repo-local skill was identified or invoked for this bounded claim-bearing historical-framing slice
- no skill-backed process coverage is claimed beyond this manual bounded audit
- any future reusable skill coverage for this exact audit pattern remains `föreslagen`, not `införd`

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch033_ri_experiment_map_candidate_boundary_framing_evidence.json`

## Observed

### Both targets are claim-bearing historical decision records

Observed supporting context:

- the candidate-surface file records the earlier Phase 3 narrowing to `multi_timeframe.regime_intelligence.regime_definition.*`
- the packet-boundary file records the earlier Phase 4 conclusion that the next admissible step, if work continues, may only be a separate bounded pre-code packet
- same-family direction and Phase 5 binding files are already historicalized in current branch context
- the post-binding roadmap already treats this chain as historical/documentary rather than current authority

### Both target tops still read like active decisions

Observed pre-change drift:

- `regime_intelligence_experiment_map_reselection_regime_definition_candidate_surface_packet_2026-03-30.md`
  begins with `candidate-surface-selected / planning-only / no authorization`
- `regime_intelligence_experiment_map_reselection_regime_definition_packet_boundary_2026-03-30.md`
  begins with `packet-boundary-defined / planning-only / no authorization`

Observed skim-risk pattern:

- without a historical/current-use note at the top, later readers can over-read the retained files as the current active candidate-surface and packet-boundary authorities rather than as the exact earlier branch/state decision records
- the stale effect is concentrated at the top; both bodies below should remain verbatim historical records in this slice

## Inferred

- both files are safe historical-framing candidates in one same-family bounded batch
- the safe patch shape in this batch is:
  - replace the stale top status label in each target with historical/current-use framing only
  - add one narrow current-status note to each target stating that the retained text below records the exact earlier branch/state decision only
  - explicitly deny current candidate-surface authority, current packet-boundary authority, current pre-code sequencing authority, launch/execution authority, runtime authority, and promotion meaning at the top
  - preserve every body section below the framing block verbatim

## UNRESOLVED

- `UNRESOLVED:` whether any later RI family outside this experiment-map chain should receive additional historical-framing passes after this same-family closeout is stabilized

## Batch result summary

- Candidates reviewed: `2`
- `YELLOW_NEEDS_REVIEW`: `2`
- `KEEP_AS_IS`: `0`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate                                                                                                                                                   | Observed role                                              | Drift signal                                                                        | Classification        | Safe batch action                                |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------------------------------- | --------------------- | ------------------------------------------------ |
| `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_regime_definition_candidate_surface_packet_2026-03-30.md` | historical earlier branch/state candidate-surface decision | stale `candidate-surface-selected / planning-only / no authorization` reads current | `YELLOW_NEEDS_REVIEW` | replace top framing and add historical note only |
| `docs/decisions/regime_intelligence/experiment_map/regime_intelligence_experiment_map_reselection_regime_definition_packet_boundary_2026-03-30.md`          | historical earlier branch/state packet-boundary decision   | stale `packet-boundary-defined / planning-only / no authorization` reads current    | `YELLOW_NEEDS_REVIEW` | replace top framing and add historical note only |

## What changed vs. what did not change

This audit supports changing:

- only the top framing block of the two retained experiment-map decision records

This audit does **not** support changing:

- same-family direction, Phase 5 binding, or post-binding roadmap files
- the earlier chosen surface, the earlier packet-boundary decision, or any body section below the framing block in either target
- any runtime/config/test/script/tmp/results surface named in the retained files

## Bottom line

Batch 033 is a bounded historical-framing closeout for the remaining claim-bearing experiment-map decision records in the March 30 chain.

The top framing blocks may be updated to remove present-tense authority ambiguity, while the retained bodies remain verbatim as the historical records of the earlier candidate-surface and packet-boundary decisions and continue to carry no launch, execution, runtime, or promotion authority.
