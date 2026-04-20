# RI advisory environment-fit Phase 3 non-runtime evidence namespace packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / docs-only / non-runtime evidence namespace decision`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — docs-only decision about where a clarity-on RI donor may be frozen as research evidence without becoming runtime-authoritative; no `src/**`, no tests changed, no config artifact created.
- **Required Path:** `Quick`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** decide the admissible non-runtime namespace for preserving `phaseC_oos_trial.json` and its donor `merged_config` as fixed RI research evidence so Phase 3 can proceed without runtime-valid carrier authoring.
- **Candidate:** `RI advisory environment-fit Phase 3 non-runtime evidence namespace`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`

### Scope

- **Scope IN:**
  - `docs/governance/ri_advisory_environment_fit_phase3_non_runtime_evidence_namespace_packet_2026-04-17.md`
  - `docs/analysis/ri_advisory_environment_fit_phase3_non_runtime_evidence_namespace_2026-04-17.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**`
  - any actual artifact freeze or ledger write
  - any runtime-valid carrier creation
  - any capture or baseline implementation
- **Expected changed files:**
  - `docs/governance/ri_advisory_environment_fit_phase3_non_runtime_evidence_namespace_packet_2026-04-17.md`
  - `docs/analysis/ri_advisory_environment_fit_phase3_non_runtime_evidence_namespace_2026-04-17.md`
- **Max files touched:** `2`

### Gates required

- `pre-commit run --files docs/governance/ri_advisory_environment_fit_phase3_non_runtime_evidence_namespace_packet_2026-04-17.md docs/analysis/ri_advisory_environment_fit_phase3_non_runtime_evidence_namespace_2026-04-17.md`

### Allowed evidence inputs

- `docs/analysis/ri_advisory_environment_fit_phase3_strategy_family_bridge_admissibility_2026-04-17.md`
- `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json`
- `src/core/research_ledger/models.py`
- `src/core/research_ledger/service.py`
- `src/core/research_ledger/storage.py`
- `artifacts/`

### Required decision questions

The memo must answer at minimum:

1. what namespace can hold the Phase C donor as fixed RI research evidence without making it runtime-config?
2. how should `strategy_family` be carried in that namespace without mutating runtime `cfg`?
3. should the namespace be ledger-primary, bundle-primary, or both?
4. what exact follow-up slice becomes admissible if this namespace decision is accepted?

### Required boundary statements

The memo must state explicitly that:

- `strategy_family` on a ledger `ArtifactRecord` is descriptive metadata only, not runtime identity for `cfg`
- every ledger entry must reference a concrete frozen payload under `artifacts/**`
- the next admissible implementation slice is scoped IN only to non-runtime evidence under `artifacts/**`
- `config/strategy/candidates/**`, `tmp/**`, and all ConfigAuthority/runtime-consumer paths remain scoped OUT for that follow-up slice

### Stop Conditions

- any wording that treats the chosen namespace as runtime-authoritative
- any wording that implies `config/strategy/candidates/**` is still the intended next surface
- any wording that authorizes capture or baseline implementation from this packet alone
- any wording that conflates ledger metadata with runtime config identity

## Bottom line

This packet authorizes one docs-only decision about a non-runtime evidence namespace and nothing more.
It does not authorize artifact creation, ledger mutation, runtime carrier authoring, or capture v2.
