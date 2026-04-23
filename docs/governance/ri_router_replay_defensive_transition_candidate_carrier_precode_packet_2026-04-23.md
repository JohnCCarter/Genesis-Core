# RI router replay defensive-transition candidate-carrier pre-code packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code-defined / hypothesis-only / no implementation authorization`

This packet records a **föreslagen** bounded carrier hypothesis for expressing the `defensive_transition_state mandate/confidence 2` candidate on runtime/backtest-adjacent surfaces.

It does **not** authorize implementation, does **not** authorize execution, and does **not** widen runtime-default, config, family, readiness, or promotion authority.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: this packet is docs-only and defines one bounded pre-code carrier hypothesis without opening implementation or execution.
- **Required Path:** `Quick`
- **Objective:** define one bounded pre-code hypothesis for the smallest repo-visible carrier surface, if any, that could later express `defensive_transition_state mandate/confidence 2` on the fixed RI backtest subject without changing runtime defaults, bridge-config semantics, family rules, or unrelated transition sizing behavior.
- **Candidate:** `defensive-transition mandate-2 carrier`
- **Base SHA:** `2dc6df79`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Hypothesis-only / non-authorizing`
- `No runtime-default / family-rule / promotion reopening`
- `No env/config semantics changes`
- `Future code slice requires separate approval`

### Skill Usage

- **Applied repo-local skill:** none in this packet
- **Reason:** this artifact is docs-only and does not execute an implementation workflow.
- **Reserved for any later code slice:** `python_engineering`
- **Deferred to any later runnable backtest step:** `backtest_run`, `genesis_backtest_verify`
- **Not claimed:** no skill coverage is claimed as completed by this packet.

### Scope

- **Scope IN:**
  - one docs-only pre-code packet for one minimal candidate-carrier hypothesis
  - explicit problem statement tied to the missing repo-visible carrier for `defensive_transition_state mandate/confidence 2`
  - explicit preferred carrier hypothesis
  - explicit proof requirements before any later code slice may proceed
  - re-anchor `GENESIS_WORKING_CONTRACT.md` to this carrier-precode state
- **Scope OUT:**
  - no code changes
  - no `src/**` edits
  - no `tests/**` edits
  - no `config/**` edits
  - no launch authorization
  - no actual baseline or candidate execution
  - no CLI flag additions
  - no bridge-config schema expansion
  - no runtime integration / paper / readiness / cutover / promotion widening
- **Expected changed files:**
  - `docs/governance/ri_router_replay_defensive_transition_candidate_carrier_precode_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- no sentence may authorize code changes
- no sentence may claim the preferred carrier is already proven sufficient
- no sentence may treat a CLI/config expansion as co-equal default path without separate authority
- no sentence may treat transition-state sizing logic as already equivalent to mandate-ranking logic
- no sentence may let this packet's `LOW / Quick` classification bleed into any later code slice

### Stop Conditions

- any wording that treats the carrier as already safe or already approved
- any wording that treats a new config field or CLI flag as implicitly acceptable default remediation
- any wording that claims `src/core/intelligence/regime/risk_state.py` already provides the required mandate carrier by itself
- any wording that silently broadens the target beyond the smallest repo-visible transition-adjacent seam
- any need to modify files outside the two scoped docs files

### Output required

- reviewable carrier pre-code packet
- explicit preferred carrier hypothesis
- explicit proof requirements before implementation
- explicit statement that future code remains separately governed

## Purpose

This packet records a **föreslagen** bounded carrier hypothesis for a later separately governed code slice.

The problem it isolates is no longer “what should be backtested?”
That subject is already fixed.

The problem it isolates is now:

- what is the smallest repo-visible surface, if any, that could carry the `defensive_transition_state mandate/confidence 2` candidate without widening into generic gate rewrites or runtime-default drift?

Fail-closed interpretation:

> Preferred hypothesis: if a bounded carrier exists, it should be sought first in the transition-state propagation seam already visible in `src/core/strategy/decision_sizing.py`, while preserving `src/core/intelligence/regime/risk_state.py` as a downstream sizing consumer rather than repurposing it into a mandate-ranking carrier. If that proof is incomplete or fails, no implementation is authorized under this packet.

## Upstream governed basis

This packet is downstream of the following tracked documents:

- `docs/governance/ri_router_replay_defensive_transition_semantics_packet_2026-04-23.md`
- `docs/governance/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`
- `docs/governance/ri_router_replay_defensive_transition_backtest_setup_only_packet_2026-04-23.md`

Carried-forward meaning from those packets:

1. the replay-local finding remains semantically local to `defensive_transition_state`
2. the first bounded backtest subject is already fixed
3. the baseline run is repo-visible on current surfaces
4. the candidate run still lacks a bounded repo-visible carrier

This packet does **not** change any of those already-recorded conclusions.

## Exact target surfaces under discussion

### Preferred primary carrier hypothesis

The preferred later code target hypothesized by this packet is:

- `src/core/strategy/decision_sizing.py`

Specifically, the currently visible transition-state propagation seam:

- `_build_regime_transition_state(...)`
- `_build_sizing_state_updates(...)`

### Adjacent downstream surface to preserve, not repurpose

The key adjacent downstream surface is:

- `src/core/intelligence/regime/risk_state.py`

Current visible role:

- consumes `bars_since_regime_change`
- computes `transition_mult`
- affects position sizing only

### Explicit non-carrier surfaces for this packet

The following are explicitly treated as non-preferred/non-carrier surfaces unless separately reopened later:

- `scripts/run/run_backtest.py`
- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- bridge-config schema or runtime-config schema expansion
- generic threshold / hysteresis / min-dwell rewrites

## Problem statement

The setup-only packet established that:

- the baseline run is expressible today
- the candidate run is not expressible as a bounded config/CLI-only command

Current repo-visible evidence narrows the carrier question further:

1. `scripts/run/run_backtest.py` can pass config and execution-mode controls, but exposes no mandate-semantics override for `defensive_transition_state`
2. the fixed bridge config exposes gate values like `hysteresis_steps` and `cooldown_bars`, but no field for `defensive_transition_state mandate/confidence`
3. `src/core/strategy/decision_sizing.py` is the currently visible seam that builds and propagates `bars_since_regime_change`
4. `src/core/intelligence/regime/risk_state.py` consumes that propagated state only for sizing via `transition_mult`

Therefore the bounded question becomes:

- is the smallest honest carrier a research-only code slice rooted at the transition-state propagation seam, or does the candidate require a deeper decision-ranking seam that would need a fresh re-packet before any implementation is considered?

## Preferred carrier hypothesis

The preferred carrier hypothesis is:

- a later separately governed code slice may be proposed first against the transition-state propagation seam in `src/core/strategy/decision_sizing.py`
- that slice must attempt to express the candidate as locally as possible without adding a new CLI flag, without adding a new bridge-config field, and without reinterpreting `risk_state.py` sizing output as if it were already a mandate-ranking surface

This remains a **preferred hypothesis only**.
It is not a verified sufficient carrier and it is not approved implementation.

### Why this is the preferred hypothesis

Based on current repo-visible state:

- the candidate question is explicitly transition-local
- `decision_sizing.py` already owns the propagation of `last_regime` / `bars_since_regime_change`
- `risk_state.py` is already downstream of that seam and exposes only multiplier semantics, not mandate-ranking semantics
- using `run_backtest.py` or the fixed bridge config as the first carrier would immediately widen CLI/config semantics rather than isolating the minimal transition-adjacent seam

## What this packet does not assume

This packet does **not** assume that:

- `decision_sizing.py` alone is sufficient to express the candidate
- a change in `risk_state.py` multiplier behavior would be semantically equivalent to mandate/confidence `1 -> 2`
- bridge config should gain a new candidate field
- a CLI flag should be the preferred carrier
- the later code slice may proceed without separate proof and separate approval

## Required proof before any later implementation slice may proceed

No implementation may proceed from this packet unless a later governed code slice includes proof that the chosen carrier remains local, bounded, and behavior-safe relative to the intended default path.

That proof must be produced in that later code slice; this packet contains no such proof.

At minimum, the required proof set must include:

### 1. Carrier sufficiency proof

A later code slice must prove that the chosen carrier can actually express a bounded candidate distinct from baseline on the fixed backtest subject.

### 2. Non-carrier proof

A later code slice must prove that it did **not** need to widen into:

- new CLI semantics
- new bridge-config semantics
- family-rule changes
- runtime-default changes
- generic gate-stack rewrites

If any of those become necessary, the slice must stop and re-packet rather than broaden in place.

### 3. Baseline-default parity proof

A later code slice must prove that default behavior remains unchanged when the candidate carrier is absent or disabled.

### 4. Downstream sizing preservation proof

A later code slice must prove that `src/core/intelligence/regime/risk_state.py` remains a downstream sizing consumer unless separate authority explicitly reopens that surface.

### 5. Canonical backtest comparability proof

A later code slice must preserve, and then verify, comparability on the fixed backtest subject for:

- symbol/timeframe/start/end
- warmup `120`
- `GENESIS_RANDOM_SEED=42`
- canonical `1/1` mode
- result attribution discipline on timestamped artifacts

## Non-goals

This packet does **not** define or authorize any of the following:

- a code implementation
- a bridge-config schema addition
- a new backtest CLI flag
- a launch packet
- a backtest execution
- a candidate execution summary
- changes to `risk_state.py` semantics by default
- changes to family rules, thresholds, hysteresis, or cooldown semantics
- runtime integration, paper coupling, readiness, cutover, or promotion scope

## Preferred vs non-preferred future path

### Preferred future path

- a separately governed minimal code-carrier slice rooted first at the transition-state propagation seam in `src/core/strategy/decision_sizing.py`, if proof later supports it

### Non-preferred future paths

- adding a CLI override to `scripts/run/run_backtest.py`
- adding a new field to the fixed bridge config as the first carrier move
- editing `src/core/intelligence/regime/risk_state.py` as if sizing multipliers already encoded mandate semantics
- reopening generic threshold/hysteresis/min-dwell tuning as the first carrier move

These non-preferred paths are recorded only as rejected defaults unless separately reopened by a new governed packet.

## Bottom line

This packet opens one narrow next hypothesis only:

- if a bounded carrier exists for the mandate-2 candidate, the first place to test is the transition-state propagation seam already visible in `src/core/strategy/decision_sizing.py`
- `src/core/intelligence/regime/risk_state.py` should currently be treated as a downstream sizing-preservation surface, not as the candidate carrier itself
- any broader carrier move remains **föreslagen only** until separate proof and separate approval exist

Nothing in this packet authorizes implementation, execution, CLI/config widening, runtime-default drift, or broader lane widening.
