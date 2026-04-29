# RI policy router low-zone bars-8 evidence-floor runtime packet

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `blocked after exact helper-hit verification / implementation reverted / candidate closed negative`

This packet is the bounded runtime-integration follow-up to the re-anchored low-zone bars-8 candidate.
It does not revive the blocked three-row packet and grants no implementation authority until pre-code review is complete.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice proposes an enabled-only behavior change inside `src/core/strategy/ri_policy_router.py`, a high-sensitivity strategy-runtime surface, while keeping the default path unchanged and leaving seam-A, the `2023-12-20 03:00` continuation-persistence seam, aged-weak continuation, cooldown, sizing, config, and authority surfaces out of scope.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is the cheapest admissible lane now: the low-zone surface is already re-anchored and preserved as one exact two-row candidate, so the next honest unknown is whether one router-local reconsideration of the early raw no-trade short-circuit can test that surface without widening into broader continuation, floor retuning, or classifier edits.
- **Objective:** implement one enabled-only router-local reconsideration in `src/core/strategy/ri_policy_router.py` that, on the exact bars-8 low-zone evidence-floor surface only, bypasses the initial raw no-trade return and hands control unchanged to the existing downstream point classifier, leaving all other router behavior unchanged.
- **Candidate:** `low-zone bars-8 evidence-floor downstream reconsideration`
- **Base SHA:** `75246d369ef7611870d740ec0d88cd7ff9d63363`

## Review status

- `Opus 4.6 Governance Reviewer`: `APPROVED`
- review lock: this remains an enabled-only downstream reconsideration experiment on the exact two-row surface below, not a generic near-floor carve-out and not a forced-defensive outcome

## Focused verification outcome

- implementation attempt was **reverted** after the packet's own exact helper-hit verification failed on the pinned December fail-B surface
- expected helper-hit set on router-executed bars:
  - `2023-12-21T18:00:00+00:00`
  - `2023-12-22T09:00:00+00:00`
- actual helper-hit artifact:
  - `results/backtests/ri_policy_router_low_zone_bars8_runtime_20260427/fail_b_helper_hit_timestamps.json`
  - contents: `[]`
- diagnostic artifact:
  - `results/backtests/ri_policy_router_low_zone_bars8_runtime_20260427/fail_b_helper_hit_diagnostics.json`
- the diagnostic replay on router-executed bars showed that the expected timestamps still appeared as raw low-zone `insufficient_evidence` rows with `bars_since_regime_change = 7`, and the explicitly excluded `2023-12-20T03:00:00+00:00` row also remained in the same router-executed low-zone surface on the pinned carrier
- because the packet required exact helper-hit set equality and explicit exclusion of `2023-12-20T03:00:00+00:00`, the candidate is closed negative rather than widened toward the older three-row surface
- no runtime authority remains active under this packet

## Skill Usage

- **Applied repo-local spec:** `decision_gate_debug`
  - reason: the slice changes one diagnosed decision-routing seam and must stay anchored to verified router-state evidence rather than threshold storytelling.
- **Applied repo-local spec:** `python_engineering`
  - reason: the intended implementation is a small typed Python diff with focused tests plus the full required gate stack.

### Runtime-integration lane

- **Durable surface som föreslås:**
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Varför billigare icke-runtime-form inte längre räcker:**
  - the candidate is already preserved in repo-visible form,
  - the remaining unknown is enabled-path runtime behavior inside the router-local no-trade short-circuit,
  - that unknown cannot be resolved honestly without one bounded runtime experiment on the exact two-row surface.
- **Default-path stance:** `unchanged`
- **Required packet / review:**
  - Opus pre-code review required before implementation
  - Opus post-diff audit required after implementation

## Evidence anchors

- `docs/decisions/ri_policy_router_low_zone_bars8_evidence_floor_candidate_packet_2026-04-27.md`
- `docs/decisions/ri_policy_router_low_zone_near_floor_insufficient_evidence_residual_hypothesis_packet_2026-04-27.md`
- `docs/analysis/ri_policy_router_weak_pre_aged_single_veto_release_low_zone_insufficient_evidence_diagnosis_2026-04-27.md`
- `docs/analysis/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `docs/decisions/ri_policy_router_low_zone_near_floor_insufficient_evidence_downstream_handoff_implementation_packet_2026-04-27.md`
- `src/core/strategy/ri_policy_router.py`

## Authoritative live row-set lock

This packet applies only to the following **post-router-filter live surface**:

| Timestamp (UTC)             | Zone  | Bars since regime change | Clarity score | Confidence gate |    Action edge | Raw target           | Switch reason           |
| --------------------------- | ----- | -----------------------: | ------------: | --------------: | -------------: | -------------------- | ----------------------- |
| `2023-12-21T18:00:00+00:00` | `low` |                      `8` |          `35` |  `0.5068924643` | `0.0137849287` | `RI_no_trade_policy` | `insufficient_evidence` |
| `2023-12-22T09:00:00+00:00` | `low` |                      `8` |          `35` |  `0.5052986704` | `0.0105973409` | `RI_no_trade_policy` | `insufficient_evidence` |

The earlier three-row runtime packet remains blocked and non-authoritative.
This packet does **not** reintroduce `2023-12-20T03:00:00+00:00`.

## Constraints

- `DEFAULT PATH UNCHANGED`
- `Behavior may change only when multi_timeframe.research_policy_router.enabled=true`
- single explicit behavior-change exception under consideration: only rows in the exact helper-activation set may bypass the initial raw `insufficient_evidence` no-trade return and hand control unchanged to the existing downstream point classifier; all other rows must remain unchanged even if they share nearby metrics
- do not guarantee or force `POLICY_DEFENSIVE`
- do not guarantee or force `POLICY_CONTINUATION`
- downstream `POLICY_NO_TRADE` remains admissible if that is what the unchanged downstream classifier resolves
- if the unchanged downstream classifier does not yield a bounded result on the locked surface, stop rather than widen the helper or force a policy result
- no new config leaf, schema change, config-authority change, env change, or runtime-default authority change
- do not edit router point weights
- do not edit router floors
- do not edit policy labels
- do not edit defensive size multiplier semantics
- do not edit seam-A single-veto semantics
- do not edit the `2023-12-20 03:00` bars-7 continuation-persistence seam
- do not edit aged-weak continuation guard semantics
- do not edit cooldown, sizing, exits, or downstream decision gates

## Scope

- **Scope IN:**
  - `docs/decisions/ri_policy_router_low_zone_bars8_evidence_floor_runtime_packet_2026-04-27.md`
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
  - `2023-12-20 03:00` continuation-persistence semantics
  - aged-weak continuation semantics
  - cooldown behavior
  - sizing
  - exits
  - config/env/schema/authority surfaces
  - promotion/default/champion/readiness surfaces
- **Expected changed files:**
  - `docs/decisions/ri_policy_router_low_zone_bars8_evidence_floor_runtime_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Max files touched:** `5`

## Proposed implementation shape

- keep the direct runtime diff inside `src/core/strategy/ri_policy_router.py`
- add one private router-local helper or predicate for this exact bars-8 surface only
- compute the helper only when the row would otherwise short-circuit to raw `RI_no_trade_policy` with reason `insufficient_evidence`
- when the helper is false, preserve the current early raw no-trade short-circuit unchanged
- when the helper is true, do not immediately return raw no-trade; continue into the existing continuation/transition point classifier unchanged and accept whatever it returns

### Predicate lock

The helper must remain bound to the observed bars-8 evidence-floor signature, not a generic near-floor region.

Allowed selector shape for this packet:

- `zone == "low"`
- the row would otherwise short-circuit to raw `RI_no_trade_policy`
- the raw short-circuit reason would otherwise be `insufficient_evidence`
- `bars_since_regime_change == 8`
- `clarity_score == 35`
- `0 < (0.515 - confidence_gate) <= 0.01`
- `0.010 <= action_edge <= 0.014`

The helper must also emit one explicit router-debug proof field when it fires:

- `low_zone_bars8_evidence_floor_reconsideration_applied = true`

That field is evidence-only and exists to support exact helper-hit containment checks on router-executed bars.

If exact `clarity_score == 35` or `bars_since_regime_change == 8` turns out not to be stable enough at implementation time, stop and reopen the packet rather than silently widening.

## Expected downstream behavior

- the only required behavioral proof on the locked surface is that the unchanged downstream classifier is reached; the resulting policy label is observational until verified and must not be forced
- this packet does **not** authorize hard-setting `RI_defensive_transition_policy` or `RI_continuation_policy`
- if the downstream classifier remains `RI_no_trade_policy`, that is a valid falsifier rather than a reason to widen the mechanism

## Proof obligations

- default path unchanged when `research_policy_router` is absent or disabled
- direct code delta confined to the router-local no-trade short-circuit seam
- the helper does not modify router floors, point weights, policy labels, or downstream sizing semantics
- on the exact locked surface, the handoff must route through the unchanged downstream classifier rather than hard-setting a policy
- on focused verification, helper-hit containment must satisfy exact set equality on router-executed bars:
  - required set = `{2023-12-21T18:00:00+00:00, 2023-12-22T09:00:00+00:00}`
  - fail on any extra hit
  - fail on any missing hit
  - fail if `2023-12-20T03:00:00+00:00` ever registers a helper hit, even if final output remains `POLICY_NO_TRADE`

## Tests required

- `tests/utils/test_ri_policy_router.py`
  - exact bars-8 signature row bypasses the early short-circuit, emits `low_zone_bars8_evidence_floor_reconsideration_applied = true`, and resolves to the current unchanged downstream result: `RI_defensive_transition_policy` with `defensive_transition_state`
  - exact excluded row equivalent to `2023-12-20T03:00:00+00:00` keeps helper false and preserves raw `POLICY_NO_TRADE` with `insufficient_evidence`
  - boundary pinning keeps containment fail-closed:
    - `confidence_gate == 0.515` does not bypass
    - immediate off-window confidence just below the allowed lower edge does not bypass
    - `action_edge` just outside `0.010 <= edge <= 0.014` does not bypass
  - aged-weak continuation guard remains unchanged
  - seam-A single-veto path remains unchanged
- `tests/utils/test_decision_scenario_behavior.py`
  - enabled-path exact bars-8 signature row no longer ends at router-local no-trade, emits the helper-applied debug flag, and preserves the current defensive-size path when downstream scoring resolves defensive
  - enabled-path excluded `2023-12-20 03:00` analogue remains router no-trade with no helper-applied flag
  - preserved seam-A single-veto scenario remains unchanged
  - preserved aged-weak continuation scenario remains unchanged

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

- one exact fail-B helper-hit verification command must be recorded in the closeout note and must confirm exact helper-activation set equality on router-executed bars
- the proof must fail on any extra hit, any missing hit, or any hit at `2023-12-20T03:00:00+00:00`, even if final action labels outside the two-row set do not change

### Pinned focused verification surface

- replay style: use a read-only `BacktestEngine(... evaluation_hook=...)` probe that records helper hits only when `meta["decision"]["versions"].get("ri_policy_router") == "ri_policy_router_v1"`, thereby filtering to router-executed bars rather than stale carried debug
- exact verification command path: `scripts/run/run_backtest.py` remains the baseline decision-row command path, and a repo-venv inline Python probe over `BacktestEngine` must emit the exact helper-hit set artifact described below
- config carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- subject: `tBTCUSD` / `3h` / `2023-12-01 -> 2023-12-31`
- warmup: `120`
- data source policy: `curated_only`
- canonical env: `GENESIS_RANDOM_SEED=42`, `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`, `GENESIS_PRECOMPUTE_CACHE_WRITE=0`, `GENESIS_MODE_EXPLICIT=1`
- required helper-hit artifact: `results/backtests/ri_policy_router_low_zone_bars8_runtime_20260427/fail_b_helper_hit_timestamps.json`
- required helper-hit artifact contents: sorted JSON array equal to `[
  "2023-12-21T18:00:00+00:00",
  "2023-12-22T09:00:00+00:00"
]`
- packet fails if the emitted helper-hit artifact differs by any extra or missing timestamp

## Stop Conditions

- any need to widen from the exact two-row signature into a generic near-floor region
- any need to alter router floors, point weights, or policy labels
- any need to force defensive or continuation instead of accepting the unchanged downstream classifier result
- any need to touch seam-A single-veto semantics, `2023-12-20 03:00` continuation-persistence semantics, or aged-weak continuation behavior as the primary mechanism
- any need to touch `decision.py`, `decision_gates.py`, `decision_sizing.py`, family surfaces, config authority, or env semantics
- any reclassified row outside the two preserved timestamps on focused verification

## Output required

- bounded implementation diff in the router-local no-trade short-circuit seam plus focused tests
- exact commands run and pass/fail outcomes
- focused two-row verification note stating whether exact helper-hit set equality holds and whether the unchanged downstream classifier resolves the two preserved rows without drifting onto additional rows
