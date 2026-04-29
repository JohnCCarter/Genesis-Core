# RI router replay defensive-transition candidate-gate carrier pre-code packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code-defined / widened-surface-defined / no implementation authorization`

This packet records a **föreslagen** widened carrier hypothesis after the bounded `decision_sizing.py` slice was inspected and found insufficient under its own stop conditions.

It does **not** authorize implementation, does **not** authorize execution, and does **not** widen runtime-default, family, readiness, or promotion authority by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: this packet is docs-only and narrows the next honest widened carrier surface after the prior single-file seam was falsified by runtime inspection.
- **Required Path:** `Quick`
- **Objective:** define one bounded pre-code hypothesis for the smallest honest runtime carrier surface, if any, that could later express `defensive_transition_state mandate/confidence 2` after the `decision_sizing.py` seam proved insufficient.
- **Candidate:** `defensive-transition candidate-gate carrier`
- **Base SHA:** `2dc6df79`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Hypothesis-only / non-authorizing`
- `Previous single-file sizing hypothesis remains historical evidence, not active implementation authority`
- `No runtime-default / family-rule / promotion reopening`
- `Future code slice requires separate approval`

### Skill Usage

- **Applied repo-local skill:** none in this packet
- **Reason:** this artifact is docs-only and does not execute an implementation workflow.
- **Reserved for any later code slice:** `python_engineering`, `decision_gate_debug`
- **Deferred to any later runnable backtest step:** `backtest_run`, `genesis_backtest_verify`
- **Not claimed:** no skill coverage is claimed as completed by this packet.

### Scope

- **Scope IN:**
  - one docs-only pre-code packet for one honest widened carrier hypothesis after the `decision_sizing.py` seam proved insufficient
  - explicit localization of the next runtime carrier question to upstream candidate formation and, if needed, explicit config-authority/schema support for a default-off research leaf
  - explicit preferred target surfaces and explicit preserve-not-repurpose surfaces
  - re-anchor `GENESIS_WORKING_CONTRACT.md` to this widened carrier-precode state
- **Scope OUT:**
  - no code changes
  - no `src/**` edits
  - no `tests/**` edits
  - no `config/**` file edits
  - no launch authorization
  - no actual baseline or candidate execution
  - no runtime integration / paper / readiness / cutover / promotion widening
  - no family-rule changes
  - no champion/default-authority changes
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_candidate_gate_carrier_precode_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- no sentence may authorize code changes
- no sentence may claim that `decision_gates.py` is already proven sufficient
- no sentence may claim that a new config leaf is already approved or already harmless
- no sentence may repurpose `decision_sizing.py` or `risk_state.py` into a mandate-ranking surface
- no sentence may imply that a later widened code slice can skip a fresh implementation packet and review

### Stop Conditions

- any wording that treats the widened carrier as already safe or already approved
- any wording that treats the prior `decision_sizing.py` packet as still active implementation authority after its seam-insufficiency finding
- any wording that silently widens from candidate formation into generic post-fib/sizing rewrites
- any wording that implies launch/backtest authorization
- any need to modify files outside the two scoped docs files

### Output required

- reviewable widened carrier pre-code packet
- explicit preferred runtime carrier seam
- explicit config-authority support surfaces if an explicit research leaf becomes necessary
- explicit proof requirements before any later implementation slice may proceed

## Purpose

This packet records a **föreslagen** widened carrier hypothesis for a later separately governed code slice.

The problem it isolates is no longer:

- whether `src/core/strategy/decision_sizing.py` can carry the semantics by itself

That question has already been bounded and inspected.

The problem it isolates is now:

- what is the smallest honest repo-visible runtime surface, if any, that can carry `defensive_transition_state mandate/confidence 2` once the sizing seam has already proved insufficient?

Fail-closed interpretation:

> Preferred hypothesis: if a bounded runtime carrier exists after the failed sizing-seam attempt, it should be sought first in upstream candidate formation inside `src/core/strategy/decision_gates.py::select_candidate(...)`. If an explicit default-off research leaf is required for honest activation, that widening must be treated explicitly through `src/core/config/schema.py` and `src/core/config/authority.py`, not smuggled in as an undocumented config convention. If that proof is incomplete or fails, no implementation is authorized under this packet.

## Upstream governed basis

This packet is downstream of the following tracked documents:

- `docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_semantics_packet_2026-04-23.md`
- `docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`
- `docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_backtest_setup_only_packet_2026-04-23.md`
- `docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_candidate_carrier_precode_packet_2026-04-23.md`
- `docs/decisions/regime_intelligence/router_replay/ri_router_replay_defensive_transition_candidate_carrier_implementation_packet_2026-04-23.md`

Carried-forward meaning from that chain:

1. the replay-local finding remains semantically local to `defensive_transition_state`
2. the first bounded backtest subject is already fixed
3. the baseline run is repo-visible on current surfaces
4. the prior bounded implementation attempt against `decision_sizing.py` was governance-approved but runtime-insufficient under its own stop conditions

This packet does **not** change any of those already-recorded conclusions.

## Exact target surfaces under discussion

### Preferred primary runtime carrier seam

The preferred later runtime target hypothesized by this packet is:

- `src/core/strategy/decision_gates.py::select_candidate(...)`

Why this seam is now preferred:

- the research-side router expresses `defensive_transition_state mandate/confidence 1 -> 2` as a **pre-stability / pre-veto candidate-formation** question
- the runtime path already localizes pre-fib candidate formation in `select_candidate(...)`
- `decision_gates.py` already owns threshold-pass, candidate/no-candidate formation, research-only override patterns, and decision-state debug payloads
- unlike `decision_sizing.py`, this seam can see threshold state, probability gap, ATR-zone context, and pre-fib candidate formation without repurposing downstream sizing semantics

### Explicit support surfaces if an explicit research leaf is needed

If the later code slice needs an explicit default-off research leaf, the smallest honest support surfaces appear to be:

- `src/core/config/schema.py`
- `src/core/config/authority.py`

Why these support surfaces matter:

- current runtime config authority already whitelists and canonicalizes existing research-only leaves under `multi_timeframe`
- a new research leaf for defensive-transition candidate formation would therefore be a **deliberate config-authority widening**, not a simple config-file tweak
- treating that widening explicitly is safer than silently relying on unknown nested fields or undocumented config behavior

### Preferred in-scope test surfaces for any later implementation slice

If a later code slice is proposed against this widened hypothesis, the leading in-scope tests are expected to include:

- `tests/utils/test_decision_gates_contract.py`
- `tests/utils/test_decision_scenario_behavior.py`
- `tests/governance/test_config_schema_backcompat.py`

Likely gate-only but not necessarily edited unless needed:

- `tests/utils/test_decision.py`
- relevant disabled/default parity selectors under `tests/integration/test_golden_trace_runtime_semantics.py`

### Preserve-not-repurpose surfaces

The following surfaces are explicitly to be preserved, not repurposed, unless a later packet says otherwise:

- `src/core/strategy/decision.py`
- `src/core/strategy/decision_sizing.py`
- `src/core/intelligence/regime/risk_state.py`
- `scripts/run/run_backtest.py`
- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

## Problem statement

The prior widened evidence chain established that:

- the baseline run is expressible today
- the candidate run is not expressible as a bounded config/CLI-only command
- the first approved single-file runtime attempt in `decision_sizing.py` was stopped honestly because no runtime `defensive_transition_state` or mandate-level signal was actually present there

Current repo-visible evidence narrows the carrier question further:

1. the research-side router models `defensive_transition_state` at raw candidate-formation time, before stability control and far before sizing
2. `src/core/strategy/decision_gates.py::select_candidate(...)` is the nearest runtime seam that already owns candidate/no-candidate formation plus research-only override patterns
3. a new explicit research leaf would not be config-only; it would require schema/authority support because the whitelist and canonical dump paths are enforced in runtime config code
4. `decision_sizing.py` and `risk_state.py` remain downstream consumers and are therefore poor places to smuggle mandate semantics after the fact

Therefore the bounded question becomes:

- is the smallest honest next carrier a multi-surface slice rooted in `decision_gates.py::select_candidate(...)`, with explicit config-authority/schema support only if a default-off research leaf is truly required, or does even that seam prove insufficient and force a larger runtime concept?

## Preferred widened carrier hypothesis

The preferred widened hypothesis is:

- a later separately governed code slice may be proposed first against `src/core/strategy/decision_gates.py::select_candidate(...)`
- that slice should preserve `decision.py`, post-fib gating, sizing, and `risk_state.py` unless new evidence proves they must be reopened
- if explicit activation is needed, it should use one documented default-off research leaf under `multi_timeframe`, with matching support in `schema.py` and `authority.py`
- if the slice cannot remain local to candidate formation plus explicit config-authority support, it must stop and re-packet rather than broaden in place

This remains a **preferred hypothesis only**.
It is not verified sufficient and it is not approved implementation.

## What this packet does not assume

This packet does **not** assume that:

- `decision_gates.py` alone is already sufficient
- the exact research leaf name or parameter shape is already decided
- a new research leaf can be added without touching config authority/schema
- the fixed bridge config should be edited in the same slice as runtime support
- the later code slice may proceed without fresh proof and fresh approval

## Required proof before any later implementation slice may proceed

No implementation may proceed from this packet unless a later governed code slice includes proof that the chosen widened carrier remains local, bounded, and behavior-safe relative to the intended default path.

That proof must be produced in that later code slice; this packet contains no such proof.

At minimum, the required proof set must include:

### 1. Candidate-formation locality proof

A later code slice must prove that the candidate is expressed at candidate-formation time and does not rely on downstream sizing/post-fib reinterpretation.

### 2. Explicit default-off config-authority proof

If a new research leaf is introduced, a later code slice must prove:

- absent leaf == explicit disabled leaf in canonical dump semantics
- whitelist/schema acceptance is explicit, bounded, and default-off
- no unrelated config-authority surface drifts

### 3. Baseline-default parity proof

A later code slice must prove that default behavior remains unchanged when the candidate carrier is absent or disabled.

### 4. Downstream preserve-not-repurpose proof

A later code slice must prove that `decision_sizing.py` and `risk_state.py` remain downstream consumers unless separate authority explicitly reopens them.

### 5. Backtest-surface separation proof

A later code slice must prove that enabling runtime support does not by itself imply launch authorization, bridge-config activation, or runnable candidate execution.

## Non-goals

This packet does **not** define or authorize any of the following:

- a code implementation
- the exact config-leaf name
- a bridge-config file update
- a launch packet
- a backtest execution
- a candidate execution summary
- runtime integration, paper coupling, readiness, cutover, or promotion scope
- family-rule or runtime-default changes

## Bottom line

The prior single-file sizing seam was a useful falsification step, not a failure to reason. The next honest carrier question is now upstream: `defensive_transition_state mandate/confidence 2` looks closer to candidate formation than to sizing propagation. If a later bounded runtime attempt is opened, it should be rooted first in `src/core/strategy/decision_gates.py::select_candidate(...)`, with explicit `schema.py` / `authority.py` support only if a documented default-off research leaf is truly required. This packet records that widened hypothesis only; it does not authorize code by itself.
