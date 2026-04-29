# Microstructure triage — Phase 4 packet

Date: 2026-04-14
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / docs-only / no-runtime-authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `LOW` — why: this slice is a triage decision only; the main risk is wasting bounded research time on a class that still lacks an authorized evidence surface.
- **Required Path:** `Quick`
- **Objective:** Make an explicit yes/no decision on whether structural market microstructure deserves any more bounded-slice time under the current artifact constraints.
- **Candidate:** Phase 4 microstructure triage
- **Base SHA:** `ba1db8ac`

### Scope

- **Scope IN:**
  - `docs/decisions/microstructure_triage_phase4_packet_2026-04-14.md`
  - `docs/analysis/microstructure_triage_phase4_2026-04-14.md`
  - `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`
  - `docs/analysis/structural_market_microstructure_artifact_gap_2026-04-02.md`
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
  - any edits to locked Phase 13–14 artifacts
- **Expected changed files:**
  - `docs/decisions/microstructure_triage_phase4_packet_2026-04-14.md`
  - `docs/analysis/microstructure_triage_phase4_2026-04-14.md`
  - `plan/genesis_driver_identification_master_roadmap_2026-04-14.md`
- **Max files touched:** `3`

### Constraints

- docs-only; no code changes and no new artifact generation
- may use only already tracked evidence and the existing microstructure gap memo
- must finish with exactly one decision from this closed set:
  - `stop / keep unresolved`
  - `future stricter lane only`

### Required memo outcomes

The memo is complete only if it does all of the following:

1. states whether structural market microstructure has any bounded-slice future under the current artifact surface
2. explains why the chosen decision is the most time-efficient option
3. preserves that unresolved is not the same thing as disproven
4. states the next admissible move for the roadmap

### Stop Conditions

- any wording that upgrades unresolved microstructure into an attested mechanism
- any attempt to reopen execution or drift evidence inside this slice
- any scope drift into runtime changes, results regeneration, or unrelated agent/tooling files

### Output required

- one docs-only packet
- one triage memo
- one roadmap update reflecting whether Phase 4 is closed

## Bottom line

This slice exists to decide whether microstructure gets more bounded attention now, or whether it should be explicitly deferred to a future stricter evidence program.
