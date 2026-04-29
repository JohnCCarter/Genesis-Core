# Structural market microstructure residual hypothesis — packet

Date: 2026-04-02
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / docs-only / no-runtime-authority`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `obs`
- **Risk:** `MED` — why: the residual class `structural_market_microstructure` can easily be overclaimed from generic structural language or underclaimed as if `UNATTESTED` meant `REJECTED`; this slice must remain observational and fail closed on the absence of a packet-authorized microstructure surface.
- **Required Path:** `Quick`
- **Objective:** Freeze the next admissible lane for the residual class `structural_market_microstructure` by documenting exactly what the current locked artifact surface says about the class, what it does not say, and what minimum future evidence would be needed before stronger market-microstructure claims become admissible.
- **Candidate:** `baseline_current` residual structural-market-microstructure lane
- **Base SHA:** `132b6ee3b3e83e99a275a50178c403c4e3027bc8`

### Scope

- **Scope IN:**
  - `docs/governance/structural_market_microstructure_residual_packet_2026-04-02.md`
  - `docs/analysis/structural_market_microstructure_artifact_gap_2026-04-02.md`
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - all files under `scripts/`
  - all files under `results/`
  - any runtime/config authority changes
  - any new backtest or trace reruns
  - any edits to locked Phase 13–14 artifacts
- **Expected changed files:**
  - `docs/governance/structural_market_microstructure_residual_packet_2026-04-02.md`
  - `docs/analysis/structural_market_microstructure_artifact_gap_2026-04-02.md`
- **Max files touched:** `2`

### Constraints

- docs-only; no code changes
- no new evidence claims beyond the currently locked artifact surface
- no weakening of the current Phase 13 `UNATTESTED` status for `structural_market_microstructure`
- no weakening of the current Phase 14 boundary that `UNATTESTED` is distinct from `REJECTED`
- this slice may define the next admissible microstructure lane, but may not pretend that lane is already implemented

### Packet-authorized source surface

The memo may cite only these already locked artifact facts:

- `GENESIS-CORE-POST PHASE-9-ROADMAP.md`
- `docs/governance/edge_classification_phase13_packet_2026-04-02.md`
- `results/research/fa_v2_adaptation_off/phase13_edge_classification/edge_classification.json`
- `results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md`

### Required memo outcomes

The memo is complete only if it does all of the following:

1. states exactly why `structural_market_microstructure` remains `UNATTESTED`
2. distinguishes clearly between:
   - the roadmap class being available as a possible category
   - an attested mechanism on the locked artifact surface
3. explains that the current locked surface does not include a packet-authorized market-microstructure artifact lane
4. lists what minimum future evidence would be needed before stronger microstructure claims become admissible
5. defines the next admissible lane in one of two forms:
   - a continued docs-only closeout if the user wants to keep the class unresolved, or
   - a future stricter evidence lane if the user wants to resolve the class

### Stop conditions

- any need to touch `src/`, `tests/`, `config/`, `scripts/`, or `results/`
- any claim that `structural_market_microstructure` is already supported or rejected on the current surface
- any claim that the current locked traces already prove spread, order-book, queue-position, or fill-priority effects
- any softening of the locked Phase 13 or Phase 14 wording
- any widening beyond the locked artifact set above

### Output required

- one docs-only governance packet
- one short analysis memo freezing the current microstructure gap and the next admissible lane

## Bottom line

This slice does not try to solve `structural_market_microstructure`.
It freezes the exact reason the class remains unresolved and defines the smallest safe next step.
