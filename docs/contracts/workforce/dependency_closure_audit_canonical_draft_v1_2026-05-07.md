# Dependency closure audit canonical draft v1

Status: `proposed / non-authoritative / manual-draft`
Scope: `docs-only`
Runtime authority: `none`
Dispatch authority: `none`
Promotion authority: `none`
Skill usage: no suitable repository skill identified for this docs-only workforce manifest-draft slice.

This file is a draft, non-authoritative manual proposal for a candidate canonical workforce dependency-closure audit form. It is not SSOT, not operational authority, and does not by itself approve cloud dispatch or prove dependency completeness.

## Purpose

The dependency-closure audit is the human-readable companion to manifest files.
It exists to answer one bounded question:

> What exact dependency closure did control plane believe a cloud worker needed, which parts were satisfied by repo-visible state, which parts were missing, and why must the system stop or fail closed?

The audit is descriptive, not authoritative.
It explains the closure state, but it does not itself make dispatch legal.

## Required sections

A canonical audit draft should contain at least:

1. **metadata block**
   - date
   - branch
   - mode
   - status
2. **non-authoritative banner**
   - explicit statement that the audit is docs-only and does not authorize dispatch
3. **command packet**
   - mode
   - risk
   - required path
   - lane
   - objective
   - base SHA
4. **scope**
   - scope in
   - scope out
5. **reference case / source set**
   - dispatch brief(s)
   - worker envelope
   - tracked repo-visible anchors
6. **observed dependency inventory**
   - satisfied repo-visible inputs
   - missing from cloud closure
   - operational state requirements or absence thereof
7. **closure verdict**
   - `dispatch_allowed`
   - block reason
   - required worker behavior
8. **epistemic separation**
   - observed
   - inferred
   - unverified
9. **recommended next step**
10. **what this audit does not prove**

## Optional sections

- skill usage note
- produced draft artifacts
- explicit capture recommendation for missing artifacts
- storage-class recommendation
- short fidelity note linking to populated example manifests

## Allowed enum values

### Status

- `manual-draft`
- `dispatch-blocked`

Positive dispatch authorization states remain outside this docs-only landing and require a separately reviewed runtime-integration slice.

### Closure verdict

- `dispatch_allowed: false`

Any positive dispatch authorization state remains outside this docs-only landing and requires a separately reviewed runtime-integration slice.

### Worker behavior if unfixed

- `blocked`
- `fail-closed`

## Hash policy

- Every repo-visible input cited as satisfied should be traceable to a pinned SHA256 in a companion manifest.
- Missing local-only dependencies may carry SHA256 when they exist locally, but the audit must not treat that hash as proof of cloud visibility.
- The audit may summarize hashes rather than inlining all of them when the canonical example manifests already contain the full values.

## Cloud visibility policy

- Local existence does not imply cloud visibility.
- Cloud visibility requires either:
  - tracked repo state on the target branch, or
  - explicit artifact-store / bundle capture with pinned identity.
- If a required input is local-only and uncaptured, the audit must say so directly.

## Missing dependency behavior

If a required input is missing or remote-invisible, the audit should record that:

- dispatch remains blocked
- worker must not guess
- worker must not substitute
- worker must not search the local filesystem ad hoc
- any deterministic fail-closed result is still a limitation, not a successful closure

## Fail-closed conditions

The audit should explicitly mark fail-closed or blocked status when:

- a required dependency is missing from cloud closure
- repo visibility cannot be proven for a required input
- a pinned hash cannot be confirmed for a required satisfied input
- continuing would require undeclared input access

## Agent A 2023-06 populated example

The first concrete reference case is:

- `docs/decisions/governance/workforce/dependency_closure/agent_a_2023_06_dependency_closure_audit_2026-05-07.md`
- `docs/decisions/governance/workforce/dependency_closure/agent_a_2023_06_dependency_manifest_2026-05-07.yaml`
- `docs/decisions/governance/workforce/dependency_closure/agent_a_2023_06_repo_snapshot_manifest_2026-05-07.yaml`
- `docs/decisions/governance/workforce/dependency_closure/agent_a_2023_06_missing_dependency_report_2026-05-07.yaml`

That case establishes the key rule this draft form is built around:

> local file exists
> but not tracked
> therefore not cloud-visible
> therefore `dispatch_allowed: false`

### Minimal populated example summary from Agent A

- worker slice: `2023-06` external falsifier
- tracked and cloud-visible inputs: dispatch briefs, worker envelope, analysis anchors, and context-clean evaluation JSON
- missing required input: annual diff file under `results/backtests/**`
- local existence: `true`
- tracked: `false`
- remote visible: `false`
- correct closure verdict: `dispatch_allowed: false`
- correct worker posture: `blocked` or deterministic `fail-closed`

## What this audit does not prove

This audit draft does **not** prove:

- that the dependency closure is complete in all future slices
- that the missing artifact is reproducible or safe to ship
- that artifact-store policy is finalized
- that any runtime, promotion, readiness, or shared-truth authority follows from the audit
- that the draft form is active SSOT

## Recommended next step

Use this audit draft together with the three YAML draft forms to normalize the next closure case, then compare whether a second worker slice can be expressed without introducing format drift.
