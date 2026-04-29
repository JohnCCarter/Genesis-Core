## COMMAND PACKET

- **Mode:** `RESEARCH` — source: branch mapping `feature/* -> RESEARCH`
- **Risk:** `MED` — why: this slice is docs-only, but governance wording must pin exact execution provenance and operational steps without granting execution or baseline approval
- **Required Path:** `Full`
- **Objective:** Define the docs-only execution runbook for `RI P1 OFF parity governed baseline reset via parity rerun` under frozen spec `ri_p1_off_parity_v1`, including pinned execution provenance, operational command surfaces, metadata contract, baseline/candidate handling, canonical artifact path, and full future sign-off gate bundle.
- **Candidate:** `ri p1 off parity governed baseline reset execution runbook`
- **Base SHA:** `1c2f38ad88723034b819b7844c69d138a7702086`

### Scope

- **Scope IN:**
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_p1_off_parity_governed_baseline_reset_execution_runbook_2026-03-17.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_baseline_reset_execution_runbook_2026-03-17.md`
  - `docs/decisions/regime_intelligence_p1_off_parity_governed_baseline_reset_execution_runbook_2026-03-17.md`
- **Scope OUT:**
  - all existing analysis / execution-prep / execution-plan / execution-review docs are reference-only in this slice
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

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_p1_off_parity_governed_baseline_reset_execution_runbook_2026-03-17.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_p1_off_parity_governed_baseline_reset_execution_runbook_2026-03-17.md docs/decisions/regime_intelligence_p1_off_parity_governed_baseline_reset_execution_runbook_2026-03-17.md`
- clean editor diagnostics on the 3 new docs

### Stop Conditions

- Any requirement to start the rerun in this slice
- Any wording that implies execution approval is granted by this slice
- Any wording that implies baseline approval is granted by this slice
- Any proposal to execute from a dirty working tree
- Any proposal to execute from a SHA other than `1c2f38ad88723034b819b7844c69d138a7702086` unless a fresh execution-approval packet first re-pins and re-reviews that SHA
- Any scope drift into existing docs unless those exact files are first added to Scope IN via fresh review
- Any frozen-spec drift in `window_spec_id`, `symbol`, `timeframe`, `start_utc`, `end_utc`, canonical artifact path, or metadata contract
- Any future compare invocation drift away from the locked comparator surface
- Any requirement to modify `src/**`, `src/core/config/**`, `config/runtime.json`, or `config/strategy/champions/**`
- Any attempt to relabel March sign-off text, ignored logs, or synthetic `ri_p1_off_parity_v1_ri-20260303-003.json` as recovered baseline provenance
- Any evidence chain that would rely only on ignored or untracked local state

### Output required

- **Implementation Report**
- **PR evidence template**
- **Execution runbook packet** for the fallback baseline-reset path, operationally concrete but still prep-only

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- This slice remains docs-only and prep-only.
- The future rerun must be treated as pinned to reviewed branch `feature/regime-intelligence-cutover-analysis-v1` and reviewed commit `1c2f38ad88723034b819b7844c69d138a7702086`.
- If execution is later proposed from a successor SHA, a separate execution-approval packet must re-pin and re-review that SHA before any rerun starts.
- `window_spec_id=ri_p1_off_parity_v1` is a governance-defined frozen execution spec; candidate-row generation materializes the frozen tuple, and the compare step materializes `window_spec_id` into the canonical artifact.
- `results/evaluation/ri_p1_off_parity_v1_baseline.json` remains a reserved canonical reference path only; this runbook does not treat it as a currently verified tracked baseline artifact.
- A future rerun PASS does not itself create, promote, or approve the canonical baseline path.
- `runtime_config_source` must always be recorded, even when `--config-file` is omitted.
- Any future PASS may count as governance sign-off only after the full named gate bundle is green and provenance is reviewable.
