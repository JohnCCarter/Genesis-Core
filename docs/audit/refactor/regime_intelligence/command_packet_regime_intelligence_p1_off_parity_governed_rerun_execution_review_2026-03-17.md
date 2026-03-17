## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH`
- **Risk:** `MED` — why: docs-only formal execution review for a governance-sensitive rerun path; inaccurate review wording here could be mistaken for execution approval
- **Required Path:** `Full`
- **Objective:** Perform a formal execution review of the defined `RI P1 OFF parity governed rerun` execution plan, verifying branch/SHA provenance, baseline-provenance status, canonical artifact contract, and sign-off gate bundle without starting the rerun.
- **Candidate:** `ri p1 off parity governed rerun execution review`
- **Base SHA:** `1c2f38ad88723034b819b7844c69d138a7702086`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_p1_off_parity_governed_rerun_execution_review_2026-03-17.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_rerun_execution_review_2026-03-17.md`
  - `docs/governance/regime_intelligence_p1_off_parity_governed_rerun_execution_review_2026-03-17.md`
- **Scope OUT:**
  - all existing execution-plan docs as reference-only
  - `src/**`
  - `src/core/config/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - `tests/**`
  - `scripts/**`
  - `tools/**`
  - `results/**` writes
  - `docs/audit/refactor/regime_intelligence/evidence/**` writes
  - `logs/**`
  - `tmp/**`
  - `artifacts/**`
  - `archive/**`
- **Expected changed files:** `3`
- **Max files touched:** `3`

### Context map

- `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_rerun_execution_review_2026-03-17.md`

### Skill Usage

- Skills referenced:
  - `ri_off_parity_artifact_check`
  - `feature_parity_check`
  - `config_authority_lifecycle_check`
- Skills executed in this docs-only review slice:
  - none
- Future execution skill checks:
  - must remain exactly as named in the reviewed gate bundle
- Skill proposals: none
- Skill updates: none

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_p1_off_parity_governed_rerun_execution_review_2026-03-17.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_rerun_execution_review_2026-03-17.md docs/governance/regime_intelligence_p1_off_parity_governed_rerun_execution_review_2026-03-17.md`

### Stop Conditions

- Any wording that implies the rerun is approved, started, or sign-off-ready without a fresh approval step
- Any claim that baseline provenance for `window_spec_id=ri_p1_off_parity_v1` is verified unless a tracked approved baseline anchor is explicitly identified
- Any attempt to treat `docs/audit/RI_P1_OFF_SIGNOFF_2026-03-04.md` alone as sufficient baseline provenance
- Any attempt to treat `logs/skill_runs.jsonl` or other ignored/local-only files as sufficient provenance by themselves
- Any attempt to use `results/evaluation/ri_p1_off_parity_v1_ri-20260303-003.json` as baseline, candidate, or sign-off evidence
- Any requirement to write into `results/**` or `docs/audit/refactor/regime_intelligence/evidence/**` in this review slice
- Any requirement to modify runtime/config/champion/default-authority surfaces
- Any branch/SHA mismatch between the reviewed execution-plan packet and this execution-review packet

### Output required

- **Implementation Report**
- **PR evidence template**
- **Formal execution-review packet** with explicit execution status

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- This slice performs review only; it does **not** approve baseline provenance, execute the rerun, or approve sign-off
- The review may conclude that the execution plan is structurally complete while still landing in `NOT YET APPROVED FOR EXECUTION`
- Branch under review: `feature/regime-intelligence-cutover-analysis-v1`
- Reviewed HEAD: `1c2f38ad88723034b819b7844c69d138a7702086` (`1c2f38ad`)
