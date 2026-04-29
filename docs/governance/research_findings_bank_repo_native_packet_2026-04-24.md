# Research findings bank repo-native packet

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / findings tracking structure decision`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only decision about how findings should be tracked across research/evidence slices using the existing ledger and artifact substrate; no `src/**`, `tests/**`, `registry/**`, or runtime config surfaces changed.
- **Required Path:** `Quick`
- **Lane:** `Concept` — the cheapest admissible step is to define the tracking structure before any schema, ledger-write, or derived-index implementation is attempted.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** define a repo-native findings bank that can preserve verdicts, mechanisms, key timestamps, evidence refs, and next admissible steps without introducing a separate database or new runtime authority.
- **Candidate:** `research findings bank repo-native index`
- **Base SHA:** `47a54c3645fe38cc6c1f34806f6c7133224f0bb0`

### Scope

- **Scope IN:**
  - `docs/governance/research_findings_bank_repo_native_packet_2026-04-24.md`
  - `docs/analysis/research_findings_bank_repo_native_structure_2026-04-24.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `registry/**`
  - `config/**`
  - `artifacts/**` mutation of any kind
  - any ledger write, index build, schema creation, or external database setup
  - any runtime consumer or promotion/champion authority change
- **Expected changed files:**
  - `docs/governance/research_findings_bank_repo_native_packet_2026-04-24.md`
  - `docs/analysis/research_findings_bank_repo_native_structure_2026-04-24.md`
- **Max files touched:** `2`

### Gates required

- editor validation for the two markdown files (`Problems` clean)

### Allowed evidence inputs

- `src/core/research_ledger/models.py`
- `src/core/research_ledger/service.py`
- `src/core/research_ledger/storage.py`
- `docs/analysis/ri_advisory_environment_fit_phase3_non_runtime_evidence_namespace_2026-04-17.md`
- `docs/governance/ri_policy_router_weak_pre_aged_release_failset_evidence_2026-04-24.md`
- `docs/governance/ri_policy_router_weak_pre_aged_release_cooldown_displacement_diagnosis_2026-04-24.md`
- `artifacts/`

### Required decision questions

The memo must answer at minimum:

1. where should findings identity live if the repository already has `research_ledger` and artifact bundles?
2. how should candidate identity, finding identity, and artifact identity stay separate?
3. what fields must every finding carry so negative and positive results are equally traceable?
4. what is the smallest admissible implementation slice after this packet?

### Required boundary statements

The memo must state explicitly that:

- the findings bank is **non-runtime** and descriptive only
- a finding must not become executable strategy/config authority merely because it is indexed
- candidate identity, finding identity, and artifact identity are related but not interchangeable
- the first implementation should prefer artifact-backed finding bundles plus a deterministic derived index before introducing any new dedicated ledger entity type or separate database

### Stop Conditions

- any wording that makes the findings bank sound runtime-authoritative
- any wording that assumes a separate DB is required before the repo-native substrate is tried
- any wording that conflates archived candidate lifecycle metadata with evidence-level findings tracking
- any wording that authorizes code or schema changes from this packet alone

## Bottom line

This packet authorizes one docs-only structure decision for a repo-native findings bank and nothing more.
It does not authorize ledger mutation, schema changes, runtime integration, registry changes, or external database setup.
