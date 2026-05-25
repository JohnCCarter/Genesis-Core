# Batch 028 RI upstream candidate-authority direction historical framing audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only status/framing audit / non-authorizing / docs-only / no behavior change`

> This file is a bounded audit for one retained RI upstream candidate-authority direction packet.
> It does **not** reopen a current active direction, slice-opening authority, launchable lane,
> runtime authority, or promotion meaning by itself.

## Scope boundary

Primary candidate in scope:

- `docs/decisions/regime_intelligence/upstream_candidate_authority/regime_intelligence_upstream_candidate_authority_direction_packet_2026-03-30.md`

Supporting anchors in scope:

- `docs/decisions/regime_intelligence/upstream_candidate_authority/regime_intelligence_upstream_diagnostic_path_closeout_2026-03-30.md`
- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_hypothesis_direction_packet_2026-03-27.md`
- `docs/audit/ri_upstream_candidate_authority_diagnostics_historical_framing_audit_batch_026.md`
- `docs/audit/ri_signal_direction_superseded_pointer_audit_batch_027.md`

Out of scope in this batch:

- editing the upstream diagnostic closeout packet
- editing the earlier SIGNAL direction packet
- editing any upstream precode packet or analysis summary
- rewriting any body content below the target file's top framing block, including the narrow
  supersession clause, chosen hypothesis label, meaning-of-decision sections, qualitative
  improvement signature, falsification condition, and explicit non-authorization boundary
- changing any runtime, config, test, script, tmp, results, or artifact surface named in the retained packet
- editing `docs/CURRENT_AUTHORITY_INDEX.md`
- editing `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
- editing the locally modified Batch 020, Batch 021, Batch 022, Batch 023, Batch 024, Batch 025, Batch 026, or Batch 027 audit files

## Method

Checked in this slice:

- full read of the retained upstream candidate-authority direction packet
- read of the current locally drifted Batch 026 and Batch 027 audits as neighboring historical-framing context
- read of the upstream diagnostic closeout packet and earlier SIGNAL direction packet for bounded historical/current-use context only
- top-of-file status/current-use framing check for the target file only
- targeted diff review confirming the target file changed only in the top framing block and that the preserved body remained verbatim from `## COMMAND PACKET` downward

Skill coverage note:

- no suitable repo-local skill was identified for this bounded docs-only historical-framing slice
- any future reusable skill coverage for this exact historical-framing audit pattern remains `föreslagen`, not `införd`

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch028_ri_upstream_candidate_authority_direction_framing_evidence.json`

## Observed

### The target is a claim-bearing historical direction-selection record

Observed supporting context:

- the retained packet records the then-active forward direction selection on 2026-03-30
- the closeout packet already frames the fixed upstream diagnostic path as closed in current tracked state
- the earlier SIGNAL direction packet has already been historicalized as an earlier direction record only

### The retained upstream direction packet top still reads like the current active direction

Observed pre-change drift:

- `regime_intelligence_upstream_candidate_authority_direction_packet_2026-03-30.md` begins with
  `direction-selected / non-launch-authoritative / no slice opened`

Observed skim-risk pattern:

- without a top historical/current-use note, later readers can over-read the retained packet as
  the current active branch direction rather than as an exact earlier branch/state direction-selection record
- the stale effect is concentrated at the top; the body below should remain a verbatim historical
  direction-selection record in this slice

## Inferred

- the safe correction is a **top-framing plus historical/current-use note only** patch
- the safe patch shape in this batch is:
  - replace the stale top status label with historical/current-use framing only
  - add one narrow note stating that the chosen direction below records the exact earlier
    branch/state forward selection only
  - explicitly state that the narrow supersession clause below is historical to that earlier state
  - explicitly deny current active-direction status, slice-opening authority, launchable-lane
    status, runtime authority, and promotion meaning at the top
  - preserve every body section below the framing block verbatim

## UNRESOLVED

- `UNRESOLVED:` whether the adjacent upstream closeout packet should later receive its own historical-framing pass or remain as the present current-state anchor

## Batch result summary

- Candidates reviewed: `1`
- `YELLOW_NEEDS_REVIEW`: `1`
- `KEEP_AS_IS`: `0`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate                                                                                                                        | Observed role                                    | Drift signal                                                           | Classification        | Safe batch action                                 |
| -------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------- | --------------------- | ------------------------------------------------- |
| `docs/decisions/regime_intelligence/upstream_candidate_authority/regime_intelligence_upstream_candidate_authority_direction_packet_2026-03-30.md` | historical direction-selection record            | stale `direction-selected / non-launch-authoritative / no slice opened` reads current | `YELLOW_NEEDS_REVIEW` | replace top framing and add historical note only |

## What changed vs. what did not change

This audit supports changing:

- only the top framing block of the retained upstream candidate-authority direction packet

This audit does **not** support changing:

- the narrow supersession clause, chosen hypothesis label, or any body section below the framing block
- the upstream closeout packet or the earlier SIGNAL direction packet
- any runtime/config/test/script/tmp/results/artifacts surface named in the retained packet

## Bottom line

Batch 028 is a bounded historical-framing correction for one claim-bearing retained upstream
candidate-authority direction-selection surface.

The classification applies to header framing only; the body remains a verbatim historical direction
record and is not re-audited here for current active-direction status, slice-opening authority,
runtime authority, or promotion meaning.
