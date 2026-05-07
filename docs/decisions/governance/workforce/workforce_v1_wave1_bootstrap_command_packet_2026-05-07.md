# Workforce v1 wave 1 bootstrap command packet

Date: 2026-05-07
Branch: `feature/next-slice-2026-05-06`
Status: `corrected draft / docs-only operational bootstrap / no behavior change`

> Correction: earlier local-worktree wording in this draft reflected a mistaken control-plane assumption.
> The intended worker model is isolated cloud-agent execution.
> Local worktrees are optional operator convenience only; they are not the workforce definition, authority surface, or required execution substrate.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-05-06`
- **Category:** `docs`
- **Risk:** `LOW` — operational workforce bootstrap only; no runtime, config-authority, default-authority, family, readiness, or promotion surface is touched.
- **Required Path:** `Quick`
- **Lane:** `Concept` — the cheapest admissible next step is to pin the first workforce wave shape and cloud dispatch model before any parallel worker starts producing new bounded evidence.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** record the first cloud-workforce wave, pin its execution base, and formalize the initial worker split so the model can start operating from a clean control plane without confusing local operator surfaces for real workers.
- **Candidate:** `workforce v1 / wave 1 bootstrap`
- **Base SHA:** `fb25f9b0b487e322c759b0aa103e25706b0cf8e4`

### Lane framing

#### Concept lane

- **Hypotes / idé:** workforce v1 should begin with one clean control plane plus one small cloud batch of explicitly bounded workers instead of confusing local operator worktrees with the workforce itself.
- **Varför det kan vara bättre:** this keeps provenance pinned, reduces overlap, and treats integration explosion as the real bottleneck rather than maximizing raw parallelism.
- **Vad skulle falsifiera idén:** if even a small domain-isolated cloud batch cannot return artifacts that are easy to classify without overlap, contradiction drift, or integration backlog blow-up, then the current workforce model is still too underspecified for safe execution.
- **Billigaste tillåtna ytor:** `docs/decisions/**`, dispatch briefs, branch/check-out naming, worker envelopes, command packets.
- **Nästa bounded evidence-steg:** compile the first cloud-agent dispatch briefs with exact domain, scope IN/OUT, allowed inputs, forbidden surfaces, and output contracts.

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
- Named clean control-plane surface
- Next admissible cloud-dispatch step

## Wave 1 execution surface

### Control-plane surface

- **Control-plane branch:** `feature/next-slice-2026-05-06`
- **Pinned base SHA:** `fb25f9b0b487e322c759b0aa103e25706b0cf8e4`
- **Purpose:** hold the clean control-plane / integration-plane surface that compiles envelopes, opens dispatches, and adjudicates returned findings.

Lokala worktrees eller checkouts får användas som operatörskonveniens för koordinering och debugging, men de är uttryckligen sekundära till cloud-agent-modellen.

### Initial worker split

#### 1. Control / integration lane

- **Role:** compile envelopes, manage dispatch queue, classify returned evidence, and own the narrow shared-truth write path
- **Allowed outputs:** wave dispatch, worker envelopes, integration decisions, later bounded truth updates only when explicitly authorized
- **Must not:** pretend that local operator surfaces are the workforce itself

#### 2. Primary cloud worker

- **Primary question:** execute the top-ranked bounded slice in one exact domain
- **Expected output:** one bounded packet/analysis/helper/test family in its own branch and PR
- **Write policy:** scoped repo-write only, no shared truth writes

#### 3. Corroborative or packet-only cloud worker

- **Primary question:** open one separate bounded slice or fallback packet in a non-overlapping domain
- **Expected output:** corroborative evidence or a packet-only fallback in its own branch and PR
- **Write policy:** exact-scope repo-write only; no shared truth writes

## Execution rule for wave 1

Wave 1 is considered successful if:

1. the control plane stays pinned and clean,
2. each cloud worker owns one bounded domain only,
3. returned artifacts carry usable provenance and `base_sha`,
4. integration classifies duplicate / park / deep-dive / integrate explicitly before any truth update, and
5. dispatch volume stays below the integration backlog the system can honestly adjudicate.

## Next admissible step

Compile the first cloud-agent dispatch briefs with exact domain boundaries, scope IN/OUT, allowed inputs, forbidden surfaces, and output contracts, then launch a small domain-isolated cloud batch.
