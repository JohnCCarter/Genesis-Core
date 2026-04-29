## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH`
- **Risk:** `MED` — why: governance wording in this slice must select the fallback execution-prep path without accidentally granting baseline approval or execution approval
- **Required Path:** `Full`
- **Objective:** Define the execution-prep packet for `RI P1 OFF parity governed baseline reset via parity rerun` under frozen spec `ri_p1_off_parity_v1`, preserving the canonical artifact contract, metadata contract, provenance requirements, and full future gate bundle.
- **Candidate:** `ri p1 off parity governed baseline reset execution prep`
- **Base SHA:** `1c2f38ad`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_p1_off_parity_governed_baseline_reset_execution_prep_2026-03-17.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_baseline_reset_execution_prep_2026-03-17.md`
  - `docs/decisions/regime_intelligence/p1_off_parity/regime_intelligence_p1_off_parity_governed_baseline_reset_execution_prep_2026-03-17.md`
- **Scope OUT:**
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
  - all existing analysis / execution-plan / execution-review docs are reference-only in this slice
- **Expected changed files:** `3`
- **Max files touched:** `3`

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_p1_off_parity_governed_baseline_reset_execution_prep_2026-03-17.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_baseline_reset_execution_prep_2026-03-17.md docs/decisions/regime_intelligence/p1_off_parity/regime_intelligence_p1_off_parity_governed_baseline_reset_execution_prep_2026-03-17.md`
- clean editor diagnostics on the 3 new docs

### Stop Conditions

- Any requirement to execute the rerun in this slice
- Any wording that implies execution approval is granted by this slice
- Any wording that implies baseline approval is granted by this slice
- Any scope drift into existing plan/review docs unless those exact files are first added to Scope IN via fresh review
- Any frozen-spec drift in `window_spec_id`, `symbol`, `timeframe`, `start_utc`, `end_utc`, canonical artifact path, or metadata contract
- Any future gate-bundle drift in named selectors or skill checks without fresh governance review
- Any attempt to relabel March sign-off text, ignored logs, or synthetic `ri_p1_off_parity_v1_ri-20260303-003.json` as recovered baseline provenance
- Any requirement to modify `src/**`, `src/core/config/**`, `config/runtime.json`, or `config/strategy/champions/**`

### Output required

- **Implementation Report**
- **PR evidence template**
- **Execution-prep packet** for the fallback baseline-reset path, preserving the frozen spec and the full future sign-off contract

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- This slice selects the fallback path `governed baseline reset via parity rerun` as the intended next route and retires evidence recovery as the preferred next step.
- This slice does **not** itself grant baseline approval and does **not** authorize execution.
- Allowed future baseline classification path: `newly approved baseline under explicit governance approval`.
- Canonical parity artifact remains `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`.
- Canonical baseline reference path remains `results/evaluation/ri_p1_off_parity_v1_baseline.json`.
- Required future metadata remains locked, including `git_sha`, `window_spec_id`, `run_id`, `symbol`, `timeframe`, `start_utc`, `end_utc`, and `baseline_artifact_ref`.
- Any future PASS may count as governance sign-off only after the full named gate bundle is green and provenance is reviewable.
