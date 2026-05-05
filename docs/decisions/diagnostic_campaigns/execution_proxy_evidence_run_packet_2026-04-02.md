# Execution proxy evidence run — packet

Date: 2026-04-02
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / run-only / no-runtime-authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `MED` — why: this slice executes new read-only research tooling against locked traces and must preserve proxy-only interpretation boundaries.
- **Required Path:** `Lite`
- **Objective:** Run the additive execution-proxy evidence lane against the locked `baseline_current` trace and materialize deterministic proxy artifacts in a new output root without modifying runtime code, trace producers, or locked Phase 10–14 artifacts.
- **Candidate:** `baseline_current` execution proxy artifact run
- **Base SHA:** `220fde3b`

### Scope

- **Scope IN:**
  - `docs/decisions/diagnostic_campaigns/execution_proxy_evidence_run_packet_2026-04-02.md`
  - `results/research/fa_v2_adaptation_off/trace_baseline_current.json`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence/execution_proxy_evidence.json`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence/execution_proxy_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence/audit_execution_proxy_determinism.json`
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - all files under `scripts/`
  - any runtime/config authority changes
  - any edits to locked Phase 10–14 artifacts
  - any rerun or regeneration of baseline traces
  - `config/strategy/champions/**`
- **Expected changed files:**
  - `docs/decisions/diagnostic_campaigns/execution_proxy_evidence_run_packet_2026-04-02.md`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence/execution_proxy_evidence.json`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence/execution_proxy_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence/audit_execution_proxy_determinism.json`
- **Max files touched:** `4`

### Constraints

- run-only; no code edits
- outputs must remain proxy-only and must not be summarized as realized execution authority
- input trace is read-only and fixed at `trace_baseline_current.json`
- output root is fixed at `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence/`
- deterministic replay must match within the script-generated audit output

### Gates required

- CLI run of `scripts/analyze/execution_proxy_evidence.py`
- audit file must report `match = true`
- output file set must equal:
  - `execution_proxy_evidence.json`
  - `execution_proxy_summary.md`
  - `audit_execution_proxy_determinism.json`

### Stop Conditions

- any attempt to overwrite locked Phase 10–14 artifacts
- any proxy run failure on the locked baseline trace
- any determinism mismatch in the generated audit output
- any need to mutate runtime or trace-production surfaces

### Output required

- materialized proxy artifacts in the fixed output root
- short execution note of first findings and residual limits

## Bottom line

This slice materializes the new execution-proxy lane on locked artifacts only.
It does not upgrade proxy evidence into realized execution authority.
