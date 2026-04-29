# Residual drift separation — Phase 3 packet

Date: 2026-04-14
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / docs-only / no-runtime-authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `MED` — why: this slice is docs-only, but it can still overclaim drift if the residual pattern is mistaken for mechanism proof rather than residual compatibility.
- **Required Path:** `Quick`
- **Objective:** Re-read the residual drift question after the execution-proxy partition and sizing-chain synthesis to determine whether drift remains merely unresolved or whether drift-compatibility is now more strongly supported as the residual interpretation.
- **Candidate:** Phase 3 residual drift separation
- **Base SHA:** `ba1db8ac`

### Scope

- **Scope IN:**
  - `docs/decisions/residual_drift_separation_phase3_packet_2026-04-14.md`
  - `docs/analysis/residual_drift_separation_phase3_2026-04-14.md`
  - `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`
  - `docs/analysis/regime_independent_drift_artifact_gap_2026-04-02.md`
  - `docs/analysis/execution_proxy_partition_phase1_2026-04-14.md`
  - `docs/analysis/sizing_chain_synthesis_phase2_2026-04-14.md`
  - `results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md`
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - all files under `scripts/`
  - all files under `results/`
  - `.github/agents/Codex53.agent.md`
  - any runtime/config authority changes
  - any trace regeneration or backtest reruns
  - any edits to locked Phase 9–14 artifacts
- **Expected changed files:**
  - `docs/decisions/residual_drift_separation_phase3_packet_2026-04-14.md`
  - `docs/analysis/residual_drift_separation_phase3_2026-04-14.md`
  - `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`
- **Max files touched:** `3`

### Constraints

- docs-only; no code changes and no new artifact generation
- may use only already tracked evidence and the completed Phase 1 / Phase 2 memos
- must preserve that drift is not attested unless the current bounded evidence genuinely supports that leap
- must finish with exactly one verdict from this closed set:
  - `drift remains unattested`
  - `drift compatibility strengthened`
  - `drift-specific stricter lane justified`

### Required memo outcomes

The memo is complete only if it does all of the following:

1. states how the Phase 1 and Phase 2 closeouts affect the residual drift reading
2. explains whether drift gains plausibility as a residual interpretation or merely remains untouched
3. preserves the difference between residual compatibility and attested mechanism
4. selects exactly one packet-authorized verdict from the closed set above
5. states the next admissible move for the roadmap

### Stop Conditions

- any wording that upgrades residual compatibility into drift proof
- any attempt to reopen execution or sizing as runtime lanes inside this slice
- any scope drift into runtime changes, results regeneration, or unrelated agent/tooling files

### Output required

- one docs-only packet
- one residual drift memo
- one roadmap update reflecting whether Phase 3 is closed

## Bottom line

This slice exists to decide whether drift is now the cleanest remaining residual interpretation on the bounded surface, or whether it still lacks enough separation to matter even as a residual read.
