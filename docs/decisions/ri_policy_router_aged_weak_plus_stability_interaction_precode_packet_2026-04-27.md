# RI policy router aged-weak plus stability interaction pre-code packet

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code-defined / docs-only / no implementation authorization`

This packet defines the next smallest admissible RI-router follow-up after the retained bars-7 closeout and the negative aged-weak second-hit runtime closeout.

It does **not** authorize implementation, execution, runtime integration, default changes, threshold retuning, family authority, readiness claims, or promotion claims.

Any future runtime slice on this surface still requires a separate follow-up packet with fresh scope approval and explicit review of the aged-weak plus stability/min-dwell interaction question.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: this packet is docs-only and narrows one future RI-router follow-up question without opening runtime/default/champion surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — the aged-weak router-local runtime slice is already closed negative, so the next honest move is to define whether any reopen must explicitly address aged-weak plus stability/min-dwell interaction instead of attempting another router-local second-hit release.
- **Objective:** define one bounded pre-code question for the exact aged-weak residual row-set and decide whether any future reopen must be framed as an aged-weak plus stability/min-dwell interaction slice.
- **Candidate:** `aged-weak plus stability interaction`
- **Base SHA:** `06faa3eb`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `No runtime authorization`
- `No seam-A or seam-B reopening by implication`
- `No low-zone family reopening`
- `No generic threshold or stability weakening`

### Skill Usage

- **Applied repo-local skill:** none
- **Reason:** this packet is docs-only and frames one future question without implementation or execution.
- **Reserved for any later code slice:** `python_engineering`, `decision_gate_debug`
- **Not claimed:** no runtime/backtest skill coverage is claimed as completed by this packet.

### Research-evidence lane

- **Baseline / frozen references:**
  - `GENESIS_WORKING_CONTRACT.md`
  - `docs/analysis/ri_policy_router_weak_pre_aged_single_veto_release_failset_evidence_2026-04-27.md`
  - `docs/analysis/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
  - `docs/decisions/ri_policy_router_bars7_continuation_persistence_runtime_closeout_2026-04-27.md`
  - `docs/decisions/ri_policy_router_low_zone_bars8_evidence_floor_runtime_packet_2026-04-27.md`
  - `docs/decisions/ri_policy_router_aged_weak_second_hit_release_candidate_packet_2026-04-27.md`
  - `docs/decisions/ri_policy_router_aged_weak_second_hit_release_runtime_closeout_2026-04-27.md`
  - `results/backtests/ri_policy_router_aged_weak_residual_probe_20260427/aged_weak_residual_rows.json`
- **Candidate / comparison surface:**
  - the exact aged-weak residual rows `2023-12-28T09:00:00+00:00` and `2023-12-30T21:00:00+00:00`, with `2023-12-28T06:00:00+00:00`, `2023-12-30T18:00:00+00:00`, and `2023-12-31T00:00:00+00:00` preserved only as context anchors.
- **Vad ska förbättras:**
  - decide whether the aged-weak residual seam can be reopened honestly only via an explicit aged-weak plus stability/min-dwell interaction contract,
  - preserve the exact residual row-set,
  - keep already-closed seam-A, low-zone, and seam-B families out of scope.
- **Vad får inte brytas / drifta:**
  - seam-A target reachability must remain closed positive,
  - seam-A single-veto remains informative but not the live blocker,
  - low-zone bars-8 remains closed negative,
  - bars-7 remains closed positive and retained,
  - seam-B / strong continuation remains direction-locked unless explicitly reopened later,
  - no generic aged-threshold, confidence-floor, edge-floor, or stability weakening may be implied.
- **Reproducerbar evidens som måste finnas:**
  - the exact residual row-set and context anchors,
  - the negative aged-weak runtime closeout that local second-hit release still retained `RI_no_trade_policy` through stability/min-dwell,
  - explicit do-not-repeat constraints,
  - one fresh follow-up packet if any runtime slice is later proposed.

## Purpose

This packet answers one narrow question only:

- after the negative aged-weak second-hit closeout, is any future reopen still admissible only if it explicitly addresses the interaction between aged-weak reconsideration and stability/min-dwell retention?

This packet is **planning-only governance**.

It does **not**:

- authorize runtime code changes
- authorize a new aged-weak router-local retry
- authorize low-zone or seam-A reopening
- authorize strong-continuation or seam-B work
- authorize keep-set or stress-set verification
- authorize readiness, cutover, or promotion claims

## Why this packet exists now

The current RI-router chain already established the following bounded conclusions:

1. seam-A target reachability is proven and must not be reopened as an active blocker.
2. seam-A single-veto removed the repeated same-pocket displacement loop but remained fail-set negative overall.
3. the low-zone family is resolved honestly for this chain: bars-7 is retained positive, while bars-8 runtime is closed negative.
4. the aged-weak router-local second-hit runtime attempt is closed negative because unchanged stability controls still retained `RI_no_trade_policy` via `switch_blocked_by_min_dwell`.

Interpretation:

- the next useful step is no longer another router-local aged-weak runtime attempt.
- the next useful step is one explicit pre-code packet that frames the reopen question as an aged-weak plus stability/min-dwell interaction problem, if it is reopened at all.

## Exact residual subject boundary

### Direct target rows

- `2023-12-28T09:00:00+00:00`
- `2023-12-30T21:00:00+00:00`

These are the direct residual blocked baseline-long rows pinned in:

- `results/backtests/ri_policy_router_aged_weak_residual_probe_20260427/aged_weak_residual_rows.json`

### Context-only anchors

- `2023-12-28T06:00:00+00:00`
- `2023-12-30T18:00:00+00:00`
- `2023-12-31T00:00:00+00:00`

These rows remain context anchors only. They are not direct helper targets for the next slice.

## Upstream governed basis

This packet is downstream of the following tracked documents and result artifacts:

- `docs/analysis/ri_policy_router_weak_pre_aged_single_veto_release_failset_evidence_2026-04-27.md`
- `docs/analysis/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `docs/decisions/ri_policy_router_bars7_continuation_persistence_runtime_closeout_2026-04-27.md`
- `docs/decisions/ri_policy_router_low_zone_bars8_evidence_floor_runtime_packet_2026-04-27.md`
- `docs/decisions/ri_policy_router_aged_weak_second_hit_release_candidate_packet_2026-04-27.md`
- `docs/decisions/ri_policy_router_aged_weak_second_hit_release_runtime_closeout_2026-04-27.md`
- `results/backtests/ri_policy_router_bars7_continuation_20260427/fail_b_helper_hit_timestamps.json`
- `results/backtests/ri_policy_router_aged_weak_residual_probe_20260427/aged_weak_residual_rows.json`

Reusable durable anchors from the findings bank remain:

- `artifacts/bundles/findings/ri_policy_router/FIND-2026-0002_continuation_split_seam_direction_lock.json`
- `artifacts/bundles/findings/ri_policy_router/FIND-2026-0003_weak_pre_aged_release_target_reachability_positive.json`
- `artifacts/bundles/findings/ri_policy_router/FIND-2026-0005_cooldown_displacement_loop_negative.json`

## Do not repeat

The following are explicit carry-forward constraints for any later slice:

- do **not** bundle seam-A and seam-B
- do **not** treat target-row hit as improvement by itself
- do **not** reopen seam-A reachability or seam-A discovery
- do **not** reopen low-zone bars-8 implicitly
- do **not** fold `2023-12-20T03:00:00+00:00` back into the aged-weak packet; it belongs to the retained bars-7 slice
- do **not** treat `2023-12-28T06:00:00+00:00`, `2023-12-30T18:00:00+00:00`, or `2023-12-31T00:00:00+00:00` as direct helper targets
- do **not** generic-retune aged thresholds, confidence floors, edge floors, or strong-continuation semantics
- do **not** advance aged-weak work to keep-set or stress-set verification in its current form

## Prove-or-stop question

The exact bounded prove-or-stop question for any later slice is:

- can the exact aged-weak residual seam be reopened only through an explicit interaction contract between aged-weak reconsideration and stability/min-dwell retention, or should it remain closed absent such widening?

This packet does **not** answer that question with code.
It only fixes the question boundary so that a later slice cannot pretend the negative aged-weak runtime closeout never happened.

## Scope

- **Scope IN:**
  - `docs/decisions/ri_policy_router_aged_weak_plus_stability_interaction_precode_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `scripts/**`
  - `results/**`
  - `artifacts/**`
  - any runtime packet
  - any keep-set or stress-set verification
  - any seam-A, seam-B, or low-zone reopening
  - readiness / promotion / champion semantics
- **Expected changed files:**
  - `docs/decisions/ri_policy_router_aged_weak_plus_stability_interaction_precode_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Mode proof

- **Why this mode applies:** branch mapping from `feature/*` resolves to `RESEARCH` per `docs/governance_mode.md`.
- **What RESEARCH allows here:** one small docs-only packet that narrows a future RI-router reopen question below runtime/default authority.
- **What remains forbidden here:** runtime edits, low-zone reopening, seam-A widening, strong-continuation/seam-B reopening, default changes, readiness/promotion framing, and keep/stress verification.
- **What would force STRICT escalation:** touching `config/strategy/champions/`, `.github/workflows/champion-freeze-guard.yml`, runtime-default authority surfaces, family-rule surfaces, or promotion/readiness surfaces.

## Gates required for this packet

Choose the minimum docs-only gates appropriate to the current scope:

1. `pre-commit run --files GENESIS_WORKING_CONTRACT.md docs/decisions/ri_policy_router_aged_weak_plus_stability_interaction_precode_packet_2026-04-27.md`
2. basic file diagnostics for both markdown files

No runtime-classified gates are required for this packet itself because it is docs-only and opens no runnable surface by itself.

## Stop Conditions

- the packet starts implicitly authorizing runtime work instead of narrowing the future question
- the packet reopens seam-A, seam-B, or low-zone families by wording drift
- the packet stops being local to the exact aged-weak residual row-set
- the packet starts assuming that stability weakening is already accepted rather than merely packet-worthy
- any need to modify files outside the two scoped docs files

## Output required

- one aged-weak plus stability interaction pre-code packet
- one updated working anchor

## Bottom line

The next admissible RI-router move is not another runtime retry. It is one docs-only `Research-evidence` packet that fixes the aged-weak residual seam to the exact two residual rows and explicitly frames any future reopen as an aged-weak plus stability/min-dwell interaction question. This packet defines that future slice boundary only; it does not authorize implementation by itself.
