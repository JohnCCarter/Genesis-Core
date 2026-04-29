# RI policy router low-zone near-floor insufficient-evidence downstream handoff implementation packet

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `blocked after focused verification / implementation reverted / re-anchor required`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice proposes an enabled-only behavior change inside `src/core/strategy/ri_policy_router.py`, a high-sensitivity strategy-runtime surface, while keeping the default path unchanged and leaving seam-A, aged-weak continuation, seam-B / strong continuation, cooldown, sizing, config, and authority surfaces out of scope.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is the cheapest admissible lane now: the low-zone residual surface is already diagnosed and preserved as one bounded hypothesis, so the next honest unknown is whether one exact enabled-only downstream handoff can test that surface without widening into global floor retuning or forced policy semantics.
- **Objective:** implement one enabled-only router-local downstream handoff in `src/core/strategy/ri_policy_router.py` that, on the verified low-zone near-floor insufficient-evidence residual envelope only, bypasses the initial raw no-trade return and hands control unchanged to the existing downstream point classifier, leaving all other router behavior unchanged.
- **Candidate:** `low-zone near-floor insufficient-evidence downstream handoff`
- **Base SHA:** `75246d369ef7611870d740ec0d88cd7ff9d63363`

## Review status

- `Opus 4.6 Governance Reviewer`: `APPROVED_WITH_NOTES`
- concept mirror: `APPROVED_WITH_NOTES` on the runtime shape, with lock that this remains a downstream handoff experiment rather than a guaranteed defensive result
- review lock: implementation remains admissible only if it stays on the exact residual envelope below and accepts whatever the unchanged downstream classifier returns

## Focused verification outcome

- first implementation attempt was **reverted** after the packet's own pinned fail-B verification failed
- the first naive replay scan over-counted handoff hits because `research_policy_router_debug` can remain stale on bars where the router does not run, for example when an earlier gate exits before router evaluation
- after filtering to bars where the router actually ran, the attempted helper no longer matched the packet's locked three-row envelope as written
- current replay evidence therefore invalidates this packet's exact residual-envelope lock and triggers the packet stop condition: stop and reopen rather than widen toward a generic near-floor region
- no runtime authority remains active under this packet until the low-zone surface is re-anchored with fresh docs-level evidence

## Skill Usage

- **Applied repo-local spec:** `decision_gate_debug`
  - reason: the slice changes one diagnosed decision-routing seam and must stay anchored to verified router-state evidence rather than blind threshold retuning.
- **Applied repo-local spec:** `python_engineering`
  - reason: the intended implementation is a small typed Python diff with focused tests plus full required gates.

### Runtime-integration lane

- **Durable surface som föreslås:**
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Varför billigare icke-runtime-form inte längre räcker:**
  - the low-zone residual surface is already preserved in repo-visible form,
  - the blocker is no longer conceptual identification but enabled-path runtime behavior inside the router-local no-trade short-circuit,
  - that unknown cannot be resolved honestly without one bounded runtime experiment on the exact verified residual envelope.
- **Default-path stance:** `unchanged`
- **Required packet / review:**
  - Opus pre-code review required before implementation
  - Opus post-diff audit required after implementation

## Evidence anchors

- `docs/decisions/ri_policy_router_low_zone_near_floor_insufficient_evidence_residual_hypothesis_packet_2026-04-27.md`
- `docs/analysis/ri_policy_router_weak_pre_aged_single_veto_release_low_zone_insufficient_evidence_diagnosis_2026-04-27.md`
- `docs/analysis/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `src/core/strategy/ri_policy_router.py`

Verified residual envelope for this packet only:

| Timestamp (UTC)             | Zone  | Bars since regime change | Clarity score | Confidence gate |    Action edge | Raw target           | Switch reason           |
| --------------------------- | ----- | -----------------------: | ------------: | --------------: | -------------: | -------------------- | ----------------------- |
| `2023-12-20T03:00:00+00:00` | `low` |                      `7` |          `35` |  `0.5060251200` | `0.0120502401` | `RI_no_trade_policy` | `insufficient_evidence` |
| `2023-12-21T18:00:00+00:00` | `low` |                      `7` |          `35` |  `0.5068924643` | `0.0137849287` | `RI_no_trade_policy` | `insufficient_evidence` |
| `2023-12-22T09:00:00+00:00` | `low` |                      `7` |          `35` |  `0.5052986704` | `0.0105973409` | `RI_no_trade_policy` | `insufficient_evidence` |

## Constraints

- `DEFAULT PATH UNCHANGED`
- `Behavior may change only when multi_timeframe.research_policy_router.enabled=true`
- single explicit behavior-change exception under consideration: when the enabled router encounters only the verified residual envelope below, it may bypass the initial raw no-trade return and hand control unchanged to the existing downstream point classifier
- do not guarantee or force `POLICY_DEFENSIVE`
- do not force `POLICY_CONTINUATION`
- if the unchanged downstream classifier does not yield the expected bounded outcome on the verified residual envelope, stop rather than widening the helper or forcing a policy result
- no new config leaf, schema change, config-authority change, env change, or runtime-default authority change
- do not edit router point weights
- do not edit router floors
- do not edit policy labels
- do not edit defensive size multiplier semantics
- do not edit seam-A single-veto semantics
- do not edit aged weak continuation guard semantics
- do not edit seam-B / strong continuation target behavior
- do not edit cooldown, sizing, exits, or downstream decision gates

## Scope

- **Scope IN:**
  - `docs/decisions/ri_policy_router_low_zone_near_floor_insufficient_evidence_downstream_handoff_implementation_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Scope OUT:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/decision_gates.py`
  - `src/core/strategy/decision_sizing.py`
  - `src/core/strategy/family_registry.py`
  - `src/core/strategy/family_admission.py`
  - `src/core/config/**`
  - `src/core/backtest/**`
  - `src/core/optimizer/**`
  - `config/**`
  - `results/**`
  - `artifacts/**`
  - router point weights
  - router floors
  - policy labels
  - seam-A single-veto semantics
  - aged weak continuation guard semantics
  - seam-B / strong continuation target rows
  - cooldown behavior
  - sizing
  - exits
  - config/env/schema/authority surfaces
  - promotion/default/champion/readiness surfaces
- **Expected changed files:**
  - `docs/decisions/ri_policy_router_low_zone_near_floor_insufficient_evidence_downstream_handoff_implementation_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Max files touched:** `5`

## Proposed implementation shape

- keep the direct runtime diff inside `src/core/strategy/ri_policy_router.py`
- add one private router-local helper or predicate for this residual surface only
- compute the helper only against the locked residual hypothesis region below; if focused verification on the preserved December subject finds any hit outside the three preserved timestamps, stop and reopen rather than widening toward a generic failed-floor region
- when the helper is false, preserve the current early raw no-trade short-circuit unchanged
- when the helper is true, do not immediately return raw no-trade; continue into the existing continuation/transition point classifier unchanged and accept whatever it returns

### Residual-envelope predicate lock

The helper must remain bound to the observed residual envelope, not a generic near-floor region.

Allowed selector shape for this packet:

- `zone == "low"`
- the row would otherwise short-circuit to raw `RI_no_trade_policy`
- the raw short-circuit reason would otherwise be `insufficient_evidence`
- `bars_since_regime_change == 7`
- `clarity_score == 35`
- `0 < (0.515 - confidence_gate) <= 0.01`
- `0.010 <= action_edge <= 0.014`

If exact `clarity_score == 35` turns out not to be stable enough at implementation time, stop and reopen the packet rather than silently widening to `>= 35`.

### Expected downstream behavior

- the only required behavioral proof on the verified residual envelope is that the unchanged downstream classifier is reached; the resulting policy label is observational until verified and must not be forced
- this packet does **not** authorize forcing that result
- if the downstream classifier instead remains `RI_no_trade_policy` or unexpectedly yields continuation on the verified envelope, stop and re-review before widening the experiment

## Proof obligations

- default path unchanged when `research_policy_router` is absent or disabled
- direct code delta confined to the router-local no-trade short-circuit seam
- the residual-envelope helper does not modify router floors, point weights, policy labels, or downstream sizing semantics
- on the exact verified residual envelope, the handoff must route through the unchanged downstream classifier rather than hard-setting a policy
- on the exact verified residual envelope, the downstream classifier is expected to resolve away from the early raw no-trade short-circuit without reopening seam-A, aged weak continuation, or seam-B logic
- if any bar outside the three preserved timestamps is reclassified on the focused verification surface, the packet fails and must not widen silently

## Tests required

- `tests/utils/test_ri_policy_router.py`
  - helper false preserves current raw no-trade short-circuit outside the exact residual envelope
  - exact residual-envelope row bypasses the early short-circuit and falls through to unchanged downstream scoring
  - aged weak continuation guard remains unchanged
  - seam-A single-veto path remains unchanged
- `tests/utils/test_decision_scenario_behavior.py`
  - enabled-path scenario proves the exact residual-envelope row no longer ends at router-local no-trade when the downstream classifier is reached
  - preserved seam-A single-veto scenario remains unchanged
  - preserved strong continuation / seam-B-like scenario remains unchanged

## Gates required

### Pre-change and post-change source checks

- `pre-commit run --all-files`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check .`

### Focused router/runtime tests

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_ri_policy_router.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_decision_scenario_behavior.py`

### Required high-sensitivity gates

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_feature_cache.py tests/utils/diffing/test_feature_cache.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m bandit -r src/core/strategy -c bandit.yaml`

### Focused bounded verification before any readiness claim

- one exact fail-B verification command or replay artifact on the preserved December subject must be recorded in the packet and must confirm whether only the three preserved timestamps leave the early raw no-trade short-circuit
- if the focused verification shows any additional reclassified rows outside the preserved timestamps, stop and reopen the packet before any keep-set, stress-set, or wider fail-set work

### Pinned focused verification surface

- replay style: reuse the existing read-only `evaluation_hook` probe shape on the preserved fail-B subject rather than relying on thin decision-row output alone
- config carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- subject: `tBTCUSD` / `3h` / `2023-12-01 -> 2023-12-31`
- warmup: `120`
- data source policy: `curated_only`
- canonical env: `GENESIS_RANDOM_SEED=42`, `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`, `GENESIS_PRECOMPUTE_CACHE_WRITE=0`, `GENESIS_MODE_EXPLICIT=1`
- required replay output: exact list of timestamps where the early raw no-trade short-circuit is no longer taken; packet fails if any timestamp outside the three preserved low-zone rows appears in that list

## Stop Conditions

- any need to widen from the exact residual envelope into a generic near-floor region
- any need to alter router floors, point weights, or policy labels
- any need to force defensive or continuation instead of accepting the unchanged downstream classifier result
- any need to touch seam-A single-veto semantics, aged weak continuation guard semantics, or seam-B / strong continuation behavior as the primary mechanism
- any need to touch `decision.py`, `decision_gates.py`, `decision_sizing.py`, family surfaces, config authority, or env semantics
- any reclassified row outside the three preserved timestamps on focused verification

## Output required

- bounded implementation diff in the router-local no-trade short-circuit seam plus focused tests
- exact commands run and pass/fail outcomes
- focused residual-envelope verification note stating whether the unchanged downstream classifier resolves the three preserved rows without drifting onto additional rows
