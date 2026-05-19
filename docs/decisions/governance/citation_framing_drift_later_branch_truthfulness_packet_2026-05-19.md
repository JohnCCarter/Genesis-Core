# Citation-framing drift later-branch truthfulness packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `implemented / docs-only / truthfulness-correction`

This packet records one bounded docs-only truthfulness correction for baseline finding `#3`. It does not change governance precedence, reopen the broader evidence-to-authority drift family, or authorize any runtime, config, paper/live, promotion, or carrier work.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice corrects one stale current-branch reading using already-corrected tracked docs and does not touch runtime/test/config surfaces
- **Required Path:** `Quick` — why: two docs files only, no behavior change, no dependency/schema/env/default changes
- **Lane:** `Research-evidence` — why: this slice narrows one governance/docs truthfulness seam without reopening a broader queue or evidence lane
- **Skill usage:** `none required` — bounded docs-only truthfulness correction
- **Objective:** record that the exact three-doc citation-framing seam underlying baseline `#3` was later corrected in tracked docs, and add a dated later-branch note to the baseline without rewriting its 2026-05-18 historical framing
- **Related artifacts:** `docs/analysis/diagnostics/premortem_delta_reanchor_feature_evidence_closeout_pilot_2026-05-18.md`, `docs/decisions/governance/queue_status_freshness_guard_packet_2026-05-15.md`, `docs/decisions/governance/decision_influencing_claim_header_boundary_packet_2026-05-15.md`, `docs/analysis/diagnostics/ignored_artifact_dependency_inventory_2026-05-15.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`

### Scope

- **Scope IN:** this packet; one later-branch truthfulness note in `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` limited to finding `#3` under the Governance / docs-integrity section
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `artifacts/**`, and `results/**`; any edit to the already-corrected three source docs; any repo-wide historical-note normalization; any wording that claims the broader `#1` evidence-to-authority drift family is solved
- **Expected changed files:** `docs/decisions/governance/citation_framing_drift_later_branch_truthfulness_packet_2026-05-19.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Max files touched:** `2`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual wording audit that the 2026-05-18 baseline remains historical and the new note is explicitly later-branch truthfulness
- manual wording audit that `#3` truthfulness correction is not misread as closure of the broader `#1` evidence-to-authority drift family
- contradiction self-review against `docs/analysis/diagnostics/premortem_delta_reanchor_feature_evidence_closeout_pilot_2026-05-18.md` and the three corrected tracked docs

## Purpose

This packet answers one narrow question only:

- what is the smallest honest current-branch correction for baseline finding `#3` now that the exact three-doc tracked-vs-local-only citation seam was later corrected in tracked docs?

## What changed in this slice

- one new docs-only truthfulness packet records the evidence boundary for `#3`
- the 2026-05-18 baseline now carries a dated later-branch note clarifying that the specific three-doc citation-framing seam named there is no longer open on this checkout
- the historical baseline wording remains preserved as a 2026-05-18 assessment rather than being silently rewritten away

## What did not change

- no runtime, test, config, or queue behavior changed
- no governance precedence changed
- no source docs beyond the baseline note and this packet were edited
- no claim is made that citation drift is impossible everywhere or that the broader evidence-to-authority family is closed

## Governing basis

### Observed

1. `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` still records `#3` as an identified-but-not-closed residual seam.
2. `docs/analysis/diagnostics/premortem_delta_reanchor_feature_evidence_closeout_pilot_2026-05-18.md` now carries a later status note stating that the tracked-vs-local-only citation seam named there was later corrected in the affected tracked docs.
3. That same re-anchor identifies the exact three-doc seam as:
   - `docs/decisions/governance/queue_status_freshness_guard_packet_2026-05-15.md`
   - `docs/decisions/governance/decision_influencing_claim_header_boundary_packet_2026-05-15.md`
   - `docs/analysis/diagnostics/ignored_artifact_dependency_inventory_2026-05-15.md`
4. Those three tracked docs now describe `docs/analysis/diagnostics/genesis_core_premortem_feature_evidence_closeout_pilot_2026-05-15.md` as a repository-tracked historical diagnostics/risk-framing note rather than a local-only or branch-current authority surface.
5. The broader Governance / docs-integrity section of the baseline still separately records `#1` as a broader evidence-to-authority drift family.

### Inferred

- the exact `#3` seam identified on 2026-05-18 is now stale for the current branch
- the smallest honest correction is a dated later-branch truthfulness note, not a new rewrite of the already-corrected source docs
- closing the specific `#3` seam does not by itself close the broader `#1` family, which remains about per-citation evidence-to-authority drift more generally

### Unverified

- whether new docs added later could reintroduce similar citation-framing drift elsewhere
- whether broader evidence-to-authority drift is adequately controlled outside the corrected three-doc seam
- whether any future governance slice should add stronger prevention beyond current wording discipline

## Applied correction

The baseline now carries a dated note stating that on `feature/risk-hardening-wave2`:

- the exact three-doc tracked-vs-local-only citation seam named by the 2026-05-18 re-anchor should not be treated as still open
- the affected tracked docs now use repository-tracked historical framing rather than local-only/current-authority wording
- this narrows current-branch truthfulness for `#3` only and leaves the broader `#1` family explicitly untouched

## Bottom line

For the current branch, baseline `#3` overstates what remains open. The smallest honest move is therefore a docs-only truthfulness reconcile: preserve the historical 2026-05-18 reading, add a dated later-branch note, and make clear that only the exact three-doc seam is narrowed — not the broader evidence-to-authority risk family.
