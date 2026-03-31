# Feature Attribution v1 — Phase 6 artifact-report packet

Date: 2026-03-31
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `phase6-proposed / docs-only / research-only / non-authorizing`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: artifact and report language can drift into hidden schema authority or generation authority if not explicitly downgraded.
- **Required Path:** `Quick`
- **Objective:** Define future reviewability minima for attribution artifacts and reports without authorizing artifact creation, report generation, schema authority, or file-format authority.
- **Candidate:** `future Feature Attribution v1 artifact/report minima`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:** one docs-only RESEARCH packet; future artifact matrix minima; future report-section minima; placeholder path discipline; explicit downgrade of all field lists to reviewability minima only; skill/reference anchors as analogy only.
- **Scope OUT:** no source-code changes; no tests; no result or artifact generation; no schema authority; no file-format authority; no runtime/config/result changes; no fib reopening.
- **Expected changed files:** `docs/governance/feature_attribution_v1_phase6_artifact_report_packet_2026-03-31.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/path sanity only
- read-only consistency check against controlling Phase 2, Phase 3, Phase 4, and Phase 5 packets
- manual wording audit that all fields remain documentation minima only
- manual wording audit that no artifact generation or schema authority is created

For interpretation discipline inside this packet:

- neither this packet alone, nor together with the other Feature Attribution v1 packets, authorizes writing any file under `results/research/feature_attribution_v1/`
- all field lists are future reviewability minima only
- placeholder paths remain placeholders only
- artifact/report expectations must remain subordinate to any later separately approved execution packet

### Stop Conditions

- any wording that turns report fields into a canonical schema
- any wording that requires files to be created now
- any wording that creates artifact-generation authority, file-format authority, or runtime result authority
- any wording that imports artifact semantics by reference from another lane

### Output required

- one reviewable Phase 6 RESEARCH artifact/report packet
- one future artifact-matrix minimum field set
- one future report minimum section set
- one placeholder path-discipline statement

## What this packet is

This packet is docs-only, research-only, and non-authorizing.
Neither this packet alone, nor together with the other Feature Attribution v1 packets, authorizes generating artifacts, writing reports, defining schemas, choosing file formats, or producing manifests.

Report field expectations in this packet are documentation minima for future reviewability only.
They do not establish schema authority, file-format authority, or artifact-generation authority.

## Inherited controlling packets

This packet inherits and does not weaken:

- `docs/governance/feature_attribution_v1_phase0_scope_freeze_packet_2026-03-31.md`
- `docs/governance/feature_attribution_v1_phase1_feature_inventory_packet_2026-03-31.md`
- `docs/governance/feature_attribution_v1_phase2_toggle_boundary_packet_2026-03-31.md`
- `docs/governance/feature_attribution_v1_phase3_baseline_metrics_packet_2026-03-31.md`
- `docs/governance/feature_attribution_v1_phase4_runner_boundary_packet_2026-03-31.md`
- `docs/governance/feature_attribution_v1_phase5_classification_policy_packet_2026-03-31.md`

## Future artifact matrix minima

If a later packet ever authorizes execution and evidence retention, a future artifact matrix should record at minimum:

| Field family    | Future minimum contents                                                                             |
| --------------- | --------------------------------------------------------------------------------------------------- |
| provenance      | branch, git SHA, run identifier, controlling packet paths                                           |
| selection       | selected exact Phase 1 row label, selector class, locked baseline anchor                            |
| metrics         | baseline metric snapshot, candidate metric snapshot, delta snapshot under the locked Phase 3 labels |
| contract status | gate bundle status, provenance status, invalid-state status if any                                  |
| interpretation  | descriptive Phase 5 label, explicit limitations, open questions                                     |
| follow-up       | allowed next step under the later post-attribution gate                                             |

These fields are future reviewability minima only.
They do not define a canonical artifact schema.

## Future report minima

If a later packet ever authorizes reporting, a future reviewable report should contain at minimum:

- provenance header
- locked baseline reference section
- selected unit section
- effective-config diff summary section
- baseline vs candidate metric table
- descriptive label section
- limitations and non-authority section
- follow-up section bound to the later post-attribution gate

These are report-section minima only.
They do not authorize report generation now.

## Placeholder path discipline

If a later packet ever separately authorizes artifact retention, placeholder families may include:

- `results/research/feature_attribution_v1/matrices/<run_id>.md`
- `results/research/feature_attribution_v1/reports/<run_id>.md`
- `results/research/feature_attribution_v1/manifests/<run_id>.json`

These paths are placeholders only.
They do not authorize file creation now and they do not define a final storage contract.

## Analogy-only anchors

The following repository surfaces are analogy-only anchors and are not adopted by reference:

- `docs/analysis/regime_intelligence_parity_artifact_matrix_2026-03-17.md` — matrix-style evidence layout only
- `.github/skills/ri_off_parity_artifact_check.json` — artifact-integrity discipline only
- `tools/compare_backtest_results.py` — comparison-result field discipline only

No artifact, schema, or comparison authority is imported by citing them.

## Bottom line

Phase 6 freezes future reviewability minima for Feature Attribution v1 artifacts and reports by stating that:

- field lists are minima only
- report sections are minima only
- placeholder paths are placeholders only
- no schema or artifact-generation authority is created
- cited artifact patterns are analogy-only

This packet describes future reporting hygiene.
It does not create report artifacts.
