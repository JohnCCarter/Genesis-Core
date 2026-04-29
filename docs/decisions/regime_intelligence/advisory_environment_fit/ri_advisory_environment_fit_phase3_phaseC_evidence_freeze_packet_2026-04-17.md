# RI advisory environment-fit Phase 3 phaseC evidence freeze packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `active / bounded implementation / non-runtime evidence freeze only`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded creation of one non-runtime evidence bundle and one ledger artifact record under `artifacts/**`; no runtime/config/test surfaces touched.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** create the first fixed Phase 3 non-runtime evidence object for `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json` using the approved ledger-primary / bundle-secondary namespace.
- **Candidate:** `RI advisory environment-fit Phase 3 phaseC evidence freeze`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`
- **Repo skills invoked:** `python_engineering` (generic quality only)
- **Domain skill coverage note:** no repo-local skill currently exists specifically for inert artifact freeze / research-ledger evidence materialization.
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

### Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_phaseC_evidence_freeze_packet_2026-04-17.md`
  - `artifacts/bundles/ri_advisory_environment_fit/phase3_phasec_evidence_freeze_2026-04-17/phaseC_oos_evidence_bundle.json`
  - `artifacts/research_ledger/artifacts/ART-2026-0001.json`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `tmp/**`
  - `results/**`
  - `config/strategy/candidates/**`
  - any ConfigAuthority/runtime-consumer path
  - any donor mutation
  - any capture-v2 or baseline implementation
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_phaseC_evidence_freeze_packet_2026-04-17.md`
  - `artifacts/bundles/ri_advisory_environment_fit/phase3_phasec_evidence_freeze_2026-04-17/phaseC_oos_evidence_bundle.json`
  - `artifacts/research_ledger/artifacts/ART-2026-0001.json`
- **Max files touched:** `3`

### Hard invariants

1. donor is locked to `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json`
2. donor `merged_config` must be copied unchanged under an inert evidence payload key
3. bundle must not contain any top-level `cfg` or other carrier-like runtime key
4. ledger `strategy_family` metadata is descriptive classification only, not runtime identity authoring
5. ledger record must reference a concrete frozen payload under `artifacts/bundles/...`
6. no file under `config/**` may be created or changed

### Gates required

- `pre-commit run --files docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_phaseC_evidence_freeze_packet_2026-04-17.md artifacts/bundles/ri_advisory_environment_fit/phase3_phasec_evidence_freeze_2026-04-17/phaseC_oos_evidence_bundle.json artifacts/research_ledger/artifacts/ART-2026-0001.json`
- Python validation that:
  - loads donor artifact and created bundle
  - asserts bundle `evidence_payload.merged_config` deep-equals donor `merged_config`
  - asserts bundle provenance fields match donor `trial_id`, `runtime_version`, and source path
  - asserts bundle has no top-level `cfg`
  - loads ledger artifact via `record_from_dict(...)`
  - asserts `artifact_kind == evidence_bundle`
  - asserts ledger `path` points under `artifacts/bundles/`
  - asserts ledger metadata carries descriptive `strategy_family = ri`
- changed-files review confirming only docs + `artifacts/**` changed

### Stop Conditions

- any need to mutate donor `merged_config`
- any need to inject `strategy_family` into donor payload
- any bundle shape that resembles runtime carrier/config authority input
- any change outside docs + `artifacts/**`

### Output required

- one governance packet
- one frozen non-runtime evidence bundle
- one ledger artifact record referencing that bundle
- verification evidence that the object is inert and donor-faithful

## Bottom line

This slice authorizes one inert evidence freeze and nothing more.
It does not authorize runtime carrier creation, capture v2, baseline authoring, or any ConfigAuthority path.
