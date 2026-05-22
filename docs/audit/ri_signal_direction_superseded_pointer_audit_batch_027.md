# Batch 027 RI SIGNAL direction superseded-pointer audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only status/pointer audit / non-authorizing / docs-only / no behavior change`

> This file is a bounded audit for one retained RI SIGNAL direction packet. It does **not** reopen
> a current active direction, launchable lane, runtime authority, or promotion meaning by itself.

## Scope boundary

Primary candidate in scope:

- `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_hypothesis_direction_packet_2026-03-27.md`

Supporting anchors in scope:

- `docs/decisions/regime_intelligence/upstream_candidate_authority/regime_intelligence_upstream_candidate_authority_direction_packet_2026-03-30.md`
- `docs/decisions/regime_intelligence/upstream_candidate_authority/regime_intelligence_upstream_diagnostic_path_closeout_2026-03-30.md`
- `docs/audit/ri_upstream_candidate_authority_diagnostics_historical_framing_audit_batch_026.md`

Out of scope in this batch:

- editing the later upstream candidate-authority direction packet
- editing the upstream closeout packet
- editing any precode, analysis, or runtime/config/test/script surface named in the retained packet
- rewriting any body content below the target file's top framing block
- editing `docs/CURRENT_AUTHORITY_INDEX.md`
- editing `docs/knowledge/DOCUMENTATION_PROVENANCE_LINEAGE_MAP.md`
- editing the locally modified Batch 020, Batch 021, Batch 022, Batch 023, Batch 024, or Batch 025 audit files

## Method

Checked in this slice:

- full read of the retained SIGNAL direction packet
- read of the later upstream candidate-authority direction packet and closeout packet for bounded
  supersession/current-use context only
- top-of-file status/current-use pointer check for the target file only

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch027_ri_signal_direction_superseded_pointer_evidence.json`

## Observed

### A later direction packet already narrows supersession of this file's active forward role

Observed supporting context:

- the 2026-03-30 upstream candidate-authority direction packet explicitly says it narrowly
  supersedes the 2026-03-27 SIGNAL direction packet only as the active forward direction selection
- the later upstream closeout and Batch 026 audit confirm that this adjacent family is now being
  read through historical/current-use framing rather than as a live direction chain

### The retained SIGNAL direction packet still reads as the currently selected direction

Observed pre-change drift:

- `regime_intelligence_optuna_signal_hypothesis_direction_packet_2026-03-27.md` begins with
  `direction-selected / SIGNAL only / phases 3–8 deferred pending authority resolution`

Observed skim-risk pattern:

- without a top historical/current-use note, later readers can over-read the retained SIGNAL
  packet as the current active direction rather than as an earlier forward-direction record
- the stale effect is concentrated at the top; the body below should remain a verbatim historical
  direction record in this slice

## Inferred

- the safe correction is a **top-framing plus later-status pointer only** patch
- the safe patch shape in this batch is:
  - replace the stale top status label with historical/current-use framing only
  - add one narrow later-status note pointing readers to the later upstream candidate-authority
    direction packet
  - explicitly deny current active-direction status, launchable-lane status, runtime authority, and
    promotion meaning at the top
  - preserve every body section below the framing block verbatim

## UNRESOLVED

- `UNRESOLVED:` whether the later upstream candidate-authority direction packet should receive its
  own more sensitive historical-framing pass after this cheaper superseded-pointer slice

## Batch result summary

- Candidates reviewed: `1`
- `READY_SUPERSEDED_POINTER`: `1`
- `KEEP_AS_IS`: `0`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate                                                                                                                      | Observed role                       | Drift signal                                                                                              | Classification             | Safe batch action                              |
| ------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------- | ---------------------------------------------- |
| `docs/decisions/regime_intelligence/optuna/signal/regime_intelligence_optuna_signal_hypothesis_direction_packet_2026-03-27.md` | historical earlier direction record | stale `direction-selected / SIGNAL only / phases 3–8 deferred pending authority resolution` reads current | `READY_SUPERSEDED_POINTER` | replace top framing and add later pointer only |

## What changed vs. what did not change

This audit supports changing:

- only the top framing block of the retained SIGNAL direction packet
- one narrow pointer to the later upstream candidate-authority direction packet

This audit does **not** support changing:

- the later upstream candidate-authority direction packet
- any runtime/config/test/script/tmp/results/artifacts surface named in the retained packet
- any body section, selected hypothesis text, or deferred-blocker text below the framing block

## Bottom line

Batch 027 is a bounded superseded-pointer correction for one retained RI SIGNAL direction packet.

The classification applies to header framing and one narrow later-status pointer only; the body
remains a verbatim historical direction record and is not re-audited here for current active-
direction status, runtime authority, or promotion meaning.
