## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH`
- **Risk:** `MED` — why: this slice is docs-only, but governance wording must prepare a reviewable approval candidate without implying that execution approval or baseline approval has already been enacted
- **Required Path:** `Full`
- **Objective:** Define the docs-only execution-approval candidate packet for `RI P1 OFF parity governed baseline reset via parity rerun` under frozen spec `ri_p1_off_parity_v1`, preserving pinned execution provenance, baseline-reset classification path, candidate/baseline provenance contract, canonical artifact path, artifact metadata contract, and full future sign-off gate bundle.
- **Candidate:** `ri p1 off parity governed baseline reset execution approval packet`
- **Base SHA:** `1c2f38ad88723034b819b7844c69d138a7702086`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_p1_off_parity_governed_baseline_reset_execution_approval_packet_2026-03-17.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_baseline_reset_execution_approval_packet_2026-03-17.md`
  - `docs/decisions/regime_intelligence_p1_off_parity_governed_baseline_reset_execution_approval_packet_2026-03-17.md`
- **Scope OUT:**
  - all existing analysis / execution-prep / execution-runbook / execution-plan / execution-review docs are reference-only in this slice
  - `src/**`
  - `src/core/config/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - `tests/**`
  - `scripts/**`
  - `tools/**`
  - `results/**` writes in this slice
  - `docs/audit/refactor/regime_intelligence/evidence/**` writes in this slice
  - `logs/**`
  - `tmp/**`
  - `artifacts/**`
  - `archive/**`
- **Expected changed files:** `3`
- **Max files touched:** `3`

### Skill Usage

- Skills referenced:
  - `ri_off_parity_artifact_check`
  - `feature_parity_check`
  - `config_authority_lifecycle_check`
- Skills executed in this docs-only slice:
  - none
- Future execution skill checks:
  - must remain exactly as named in the locked gate bundle
- Skill proposals: none
- Skill updates: none

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_p1_off_parity_governed_baseline_reset_execution_approval_packet_2026-03-17.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_baseline_reset_execution_approval_packet_2026-03-17.md docs/decisions/regime_intelligence_p1_off_parity_governed_baseline_reset_execution_approval_packet_2026-03-17.md`
- clean editor diagnostics on the 3 new docs

### Stop Conditions

- Any wording that implies execution approval is granted by this slice merely because the packet exists
- Any wording that implies baseline approval or baseline promotion is already enacted in this slice
- Any baseline classification written as already-approved present fact instead of a requested / allowed future approval path
- Any proposal to execute from a dirty working tree
- Any proposal to execute from a SHA other than `1c2f38ad88723034b819b7844c69d138a7702086` unless a fresh governance review first re-pins and re-approves that SHA
- Any scope drift into existing docs unless those exact files are first added to Scope IN via fresh review
- Any attempt to describe the canonical artifact or evidence outputs as already produced in this slice
- Any attempt to describe a future rerun `PASS` as auto-promoting `results/evaluation/ri_p1_off_parity_v1_baseline.json`
- Any frozen-spec drift in `window_spec_id`, `symbol`, `timeframe`, `start_utc`, `end_utc`, canonical artifact path, metadata contract, or gate bundle
- Any requirement to modify `src/**`, `src/core/config/**`, `config/runtime.json`, or `config/strategy/champions/**`
- Any attempt to relabel March sign-off text, ignored logs, or synthetic `ri_p1_off_parity_v1_ri-20260303-003.json` as recovered baseline provenance
- Any provenance claim that relies only on ignored or untracked local state

### Output required

- **Implementation Report**
- **PR evidence template**
- **Execution-approval packet** prepared as an approval candidate for later governance review

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- This slice remains docs-only and preparation-only.
- Status inside the packet must be framed as `approval-candidate / ready_for_governance_review / execution not approved by this slice`.
- Pinned execution provenance must match the runbook:
  - branch `feature/regime-intelligence-cutover-analysis-v1`
  - SHA `1c2f38ad88723034b819b7844c69d138a7702086`
  - clean working tree
- Allowed / requested future baseline classification for this path: `newly approved baseline under explicit governance approval`.
- `results/evaluation/ri_p1_off_parity_v1_baseline.json` remains a reserved canonical reference path only.
- Canonical artifact path remains `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`.
- Metadata requirements and full gate bundle may be defined in this slice, but are not fulfilled by this slice.
- Any future `PASS` may count as governance sign-off only after explicit governance disposition, full green gates, and reviewable provenance.
