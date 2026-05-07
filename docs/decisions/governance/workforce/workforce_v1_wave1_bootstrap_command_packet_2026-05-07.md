# Workforce v1 wave 1 bootstrap command packet

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Status: `proposed / pre-execution / docs-only operational bootstrap`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-05-06`
- **Category:** `docs`
- **Risk:** `LOW` — operational workforce bootstrap only; no runtime, config-authority, default-authority, family, readiness, or promotion surface is touched.
- **Required Path:** `Quick`
- **Lane:** `Concept` — the cheapest admissible next step is to pin the first workforce wave shape and clean execution surface before any parallel worker starts producing new bounded evidence.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** record the first manual workforce wave, pin its execution base, and formalize the initial worker split so the model can start operating from a clean integration surface.
- **Candidate:** `workforce v1 / wave 1 bootstrap`
- **Base SHA:** `fb25f9b0b487e322c759b0aa103e25706b0cf8e4`

### Lane framing

#### Concept lane

- **Hypotes / idé:** workforce v1 should begin with one clean integration worktree plus one small wave of explicitly bounded workers instead of trying to automate broad parallelism immediately.
- **Varför det kan vara bättre:** this keeps provenance pinned, reduces worktree drift, and proves the control-plane / worker-plane split before broader scaling.
- **Vad skulle falsifiera idén:** if even a three-role manual wave cannot stay isolated, bounded, and easy to integrate, then the current workforce model is still too underspecified for safe execution.
- **Billigaste tillåtna ytor:** `docs/decisions/**`, worktree setup, branch naming, worker envelopes, command packets.
- **Nästa bounded evidence-steg:** open the first inventory-worker envelope from the clean integration surface and require it to produce a shortlist for the first deep-dive slot.

### Scope

- **Scope IN:**
  - `docs/decisions/governance/workforce/workforce_v1_wave1_bootstrap_command_packet_2026-05-07.md`
- **Scope OUT:**
  - `src/**`
  - `config/**`
  - `GENESIS_WORKING_CONTRACT.md`
  - `docs/governance_mode.md`
  - `.github/copilot-instructions.md`
  - `docs/governance/worker_governance_envelope.md`
  - `workforce_roadmap.md`
- **Expected changed files:** `docs/decisions/governance/workforce/workforce_v1_wave1_bootstrap_command_packet_2026-05-07.md`
- **Max files touched:** `1`

### Gates required

- `pre-commit run --files docs/decisions/governance/workforce/workforce_v1_wave1_bootstrap_command_packet_2026-05-07.md`

### Stop Conditions

- Scope drift
- Any attempt to reinterpret governance authority or mode semantics
- Any attempt to open runtime/config/default-authority work
- Any attempt to update shared truth directly from non-integration worker planning

### Output required

- Landed bootstrap packet
- Explicit worker wave shape
- Named clean integration surface
- Next admissible worker-opening step

## Wave 1 execution surface

### Integration surface

- **Integration worktree path:** `C:\gcww1`
- **Integration branch:** `feature/wt/integration-wave1`
- **Pinned base SHA:** `fb25f9b0b487e322c759b0aa103e25706b0cf8e4`
- **Purpose:** hold the clean control-plane / integration-plane surface for the first workforce wave.

### Initial worker split

#### 1. Integration worker

- **Role:** control-plane coordination and truth fan-in
- **Branch:** `feature/wt/integration-wave1`
- **Allowed outputs:** wave dispatch, worker envelopes, integration decisions, later bounded truth updates only when explicitly authorized
- **Must not:** produce runtime claims or broad synthesis by itself

#### 2. Inventory worker (next to open)

- **Planned branch:** `feature/wt/inventory-wave1`
- **Primary question:** produce the next shortlist of candidate slices from already-landed research surfaces
- **Expected output:** bounded shortlist plus recommended next deep-dive candidates
- **Write policy:** docs/artifacts only, no shared truth writes

#### 3. Deep-dive worker (opens only after shortlist exists)

- **Planned branch:** `feature/wt/deepdive-wave1`
- **Primary question:** execute one exact bounded slice chosen from the inventory shortlist
- **Expected output:** packet + analysis note or equivalent bounded evidence artifact
- **Write policy:** scoped repo-write only, no shared truth writes

## Execution rule for wave 1

Wave 1 is considered successful if:

1. the integration surface stays clean and pinned,
2. the inventory worker produces one bounded shortlist,
3. the first deep-dive worker can be opened from that shortlist without scope ambiguity, and
4. integration remains the only path that can later update shared truth.

## Next admissible step

Open the first inventory-worker envelope from `C:\gcww1` using the shared worker-envelope spec and keep the initial question strictly shortlist-oriented.
