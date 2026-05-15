# Decision-influencing claim-header boundary packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the compact mandatory claim-header minimum for decision-influencing evidence. It grants no runtime, config-authority, paper/live, promotion, or replay authority by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice tightens provenance wording in existing docs surfaces only and does not modify scripts, tests, results, runtime behavior, or governance precedence
- **Required Path:** `Quick path / docs-only boundary record`
- **Lane:** `Research-evidence` — why: this packet narrows the minimum provenance envelope for decision-influencing evidence without turning all research notes into packet-grade process
- **Objective:** tighten the existing claim-header template and adoption runbook so decision-influencing evidence must name a compact minimum envelope, especially `Input carrier`
- **Base SHA:** `9f5e08098ba2c4035d4b1e101034e20d016b75b3`
- **Related artifacts:** `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md`, `docs/analysis/diagnostics/genesis_core_premortem_feature_evidence_closeout_pilot_2026-05-15.md`, `docs/governance/templates/evidence_claim_header.md`, `docs/governance/runbooks/evidence_claim_adoption.md`, `docs/analysis/diagnostics/decision_influencing_replay_smoke_candidate_selection_2026-05-15.md`

### Scope

- **Scope IN:** this boundary packet; in-place tightening of `docs/governance/templates/evidence_claim_header.md`; in-place tightening of `docs/governance/runbooks/evidence_claim_adoption.md`; queue sync that records Slice 10 as completed and advances the next admissible slice
- **Scope OUT:** all `src/**`; all `tests/**`; all `scripts/**`; all `config/**`; all `registry/**`; all `results/**`; all `artifacts/**`; all `.github/**`; any repo-wide retrofit across existing claim notes; any CI/lint/tooling enforcement; any wording that changes runtime/default/comparison/readiness/promotion/paper-live authority
- **Max files touched:** `4`

### Gates required

For this packet itself:

- targeted docs validation for this packet, template update, runbook update, and queue sync
- manual wording audit that adoption remains trigger-based rather than universal
- manual wording audit that the header refinement does not become a new SSOT or implementation authority

## Purpose

This packet answers one narrow question only:

- what compact claim-header minimum must every decision-influencing evidence note name explicitly?

## What changed in this slice

- `Input carrier` is now explicit in the reusable claim-header template
- the existing runbook now states the mandatory minimum envelope for decision-influencing evidence
- the boundary remains inside the existing template/runbook surfaces rather than creating a parallel framework

## What did not change

- no source, test, results, runtime, or config-authority behavior
- no paper/live, readiness, or promotion semantics
- no requirement to retrofit the full archive

## Governing basis

### Observed

1. The live successor queue names `SHA`, `branch`, `clean/dirty status`, `input carrier`, `env/cache/data-policy`, and `authority level` as the minimum claim-header target for this slice.
2. The branch premortem identifies omitted env/cache/data-policy, missing claim headers for decision-influencing evidence, and remembered-but-unnamed carriers as real branch risks.
3. The existing claim-header template and adoption runbook already provide a strong trigger-based base, but they did not yet standardize `Input carrier` as an explicit header field.
4. The existing runbook explained when to use the header, but it did not yet lock a compact mandatory minimum subset for decision-influencing evidence.
5. Recent claim-bearing notes already record much of the needed envelope — branch, SHA, working-tree status, data-source policy, env flags, cache policy, and authority level — which means the pattern already exists and only needs tightening.

### Inferred

- The smallest admissible fix is to tighten the existing template and runbook in place rather than create a new template family, new SSOT, or tooling gate.
- For decision-influencing evidence, the claim header must now name at minimum: `Branch`, `Runtime base SHA`, `Evidence commit SHA` or explicit non-rerun wording, `Working-tree status`, `Input carrier`, `Data-source policy`, `Env flags`, `Cache policy`, `Authority level`, and a short `Does not authorize` boundary.
- `Config path` and `Config hash` remain mandatory when the note depends on config-bearing meaning, but they are conditional rather than universal.
- Adoption remains trigger-based for decision-bearing notes only; ordinary scratch research remains light.

### Unverified in this packet

- whether later tooling or lint support would ever be worth adding for header completeness
- whether some future runtime-adjacent evidence class will need an even stricter mandatory subset
- whether any older frequently cited notes should later be upgraded for provenance clarity

## Boundary decision

### Current standing conclusion

For **decision-influencing evidence** only, the existing claim-header pattern must now include at minimum:

- `Branch`
- `Runtime base SHA`
- `Evidence commit SHA` or explicit non-rerun wording
- `Working-tree status`
- `Input carrier`
- `Data-source policy`
- `Env flags`
- `Cache policy`
- `Authority level`
- `Does not authorize`

`Config path` and `Config hash` remain required whenever the note depends on config-bearing meaning.

This is a provenance-discipline conclusion only. It is **not** approval to widen runtime authority, retroactively bless existing notes, or turn all RESEARCH notes into packet-grade process.

### Input-carrier interpretation boundary

For this slice, `Input carrier` means the exact artifact/control surface the note depends on, for example:

- one tracked fixture path
- one exact frozen historical artifact path or root
- one retained bundle pointer
- one exact summary artifact when the note is summary-only by construction

It must be named directly rather than left to surrounding prose or worker memory.

## Hard stop and reopen rule

If a future slice needs any of the following, it must stop and reopen as a separate bounded packet:

- repo-wide retrofit across historical notes
- CI, lint, or editor enforcement
- runtime/default/comparison/readiness/promotion/paper-live authority changes
- a claim that the header itself is sufficient governance for high-sensitivity work

## Bottom line

The next useful governance refinement is not more packet volume; it is sharper provenance. Decision-influencing evidence must now name its compact envelope explicitly — especially `Input carrier` — while the broader claim-header regime remains trigger-based, lightweight, and non-authorizing.
