# RI router replay defensive-transition semantics packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / semantics-focused research packet / docs-only / no execution authority by itself`

This packet opens the next smallest admissible question after the bounded RI router replay counterfactual closeout.
It does **not** authorize runtime integration, default changes, family authority, promotion claims, or any execution surface by itself.

Its purpose is narrower:

- lock the next semantics question,
- keep the follow-up below runtime/default/family authority,
- and prevent another round of broad gate-toggling without a more explicit semantic hypothesis.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `LOW` — docs-only packet work that scopes a bounded research question without opening runtime or default-authority surfaces.
- **Required Path:** `Lite`
- **Lane:** `Research-evidence` — the question is no longer conceptual container choice; it is now a bounded semantics question on an already frozen and reproducible evidence surface.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** scope one fresh semantics-focused research question: whether `defensive_transition_state` should be treated as a mandate-2 candidate on research surfaces only.
- **Candidate:** `defensive_transition_state mandate semantics`
- **Base SHA:** `0d736cba`

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/governance/ri_router_replay_implementation_packet_2026-04-23.md`
  - `docs/governance/ri_router_replay_counterfactual_closeout_report_2026-04-23.md`
  - `results/research/ri_router_replay_v1/`
  - `results/research/ri_router_replay_v1_counterfactual_switch_threshold_1/`
  - `results/research/ri_router_replay_v1_counterfactual_defensive_transition_mandate_2/`
- **Candidate / comparison surface:**
  - the semantics of the raw `defensive_transition_state` branch only, treated as a bounded research interpretation problem rather than as a broad stability-stack problem.
- **Vad ska förbättras:**
  - semantic precision,
  - honest localization of the blocker,
  - reduced dependence on global gate toggles as the explanatory container.
- **Vad får inte brytas / drifta:**
  - runtime behavior,
  - default path semantics,
  - family/runtime authority boundaries,
  - replay recommendation semantics,
  - frozen evidence roots already written in the closed counterfactual lane.
- **Reproducerbar evidens som måste finnas om nästa steg öppnas:**
  - explicit comparison against baseline fresh replay root,
  - explicit comparison against `switch_threshold: 2 -> 1`,
  - explicit comparison against `defensive_transition_state mandate/confidence: 1 -> 2`,
  - deterministic rerun proof for any new executable slice,
  - explicit proof that the semantics question stays local to the defensive branch and does not silently widen into a broader router rewrite.

## Why this packet exists now

The closed counterfactual lane established three facts that change the admissible next step:

1. `switch_threshold: 2 -> 1` materially improves defensive selection.
2. `defensive_transition_state mandate/confidence: 1 -> 2` produces the same routed outcome as `switch_threshold: 2 -> 1` on the frozen surface.
3. `hysteresis` and `min_dwell` are no longer the most useful explanatory frontier for this lane.

Interpretation:

- The next useful question is no longer “which stability gate should move?”
- It is now “is the raw `defensive_transition_state` branch semantically under-ranked?”

## Scope

- **Scope IN:**
  - `docs/governance/ri_router_replay_defensive_transition_semantics_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - `tmp/**`
  - `results/**`
  - runtime integration
  - backtest execution integration
  - family-rule surfaces
  - readiness / promotion semantics
  - champion / default authority
- **Expected changed files:**
  - `docs/governance/ri_router_replay_defensive_transition_semantics_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Mode proof

- **Why this mode applies:** branch mapping from `feature/*` resolves to `RESEARCH` per `docs/governance_mode.md`.
- **What RESEARCH allows here:** one small reproducible packet that narrows the next admissible semantics question without opening runtime/default authority.
- **What remains forbidden here:** runtime integration, family-rule surfaces, readiness/promotion semantics, champion surfaces, and any default-path change.
- **What would force STRICT escalation:** touching `config/strategy/champions/`, `.github/workflows/champion-freeze-guard.yml`, runtime-default authority surfaces, family-rule surfaces, or promotion/readiness surfaces.

## The exact semantics question to preserve

This packet freezes the following question only:

> On the current frozen RI router replay evidence surface, should `defensive_transition_state` be treated as a mandate-2 candidate rather than a mandate-1 candidate?

This packet does **not** assume the answer is yes.
It only records that this is now the next bounded question worth testing.

## What would count as a useful answer

A useful answer must distinguish between at least these possibilities:

1. `defensive_transition_state` is globally under-ranked and mandate-2 semantics are broadly justified on the frozen surface.
2. Only a narrower sub-pocket of `defensive_transition_state` rows is under-ranked.
3. The apparent improvement is only a threshold alias and does not survive a more semantics-specific reading.

If the lane cannot distinguish among those, it should stop rather than broaden into runtime or family language.

## Gates required for this packet

Choose the minimum docs-only gates appropriate to the current scope:

1. `pre-commit run --files GENESIS_WORKING_CONTRACT.md docs/governance/ri_router_replay_defensive_transition_semantics_packet_2026-04-23.md`
2. basic file diagnostics for both markdown files

No runtime-classified gates are required for this packet itself because it is docs-only and opens no executable surface by itself.

## Stop Conditions

- the semantics question starts implicitly authorizing runtime/default changes
- the packet starts assuming mandate-2 is already validated rather than merely scoped as the next question
- the next follow-up would require `src/**`, `config/**`, or family-rule changes without a fresh packet
- the question cannot remain local to `defensive_transition_state` and begins widening back into a generic gate-stack rewrite

## Output required

- one semantics-focused research packet
- one updated working anchor

## Bottom line

The current counterfactual lane has already done enough generic gate isolation work. The next admissible step is to treat `defensive_transition_state` as a bounded semantics question, not as another broad stability-stack tuning problem. This packet opens that narrower question only; it does not authorize any runtime or default-authority follow-up by itself.
