# RI policy router bars-7 continuation-persistence runtime packet

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `implemented / gates green / exact helper-hit proof passed / post-diff audit APPROVED_WITH_NOTES`

This packet is the bounded runtime-integration follow-up to the separate bars-7 continuation-persistence candidate.
The bounded implementation is now complete, retained in `src/core/strategy/ri_policy_router.py`, and verified as one exact row-specific enabled-path reconsideration.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice proposes an enabled-only behavior change inside `src/core/strategy/ri_policy_router.py`, a high-sensitivity strategy-runtime surface, while keeping the default path unchanged and leaving later low-zone rows, seam-A, aged-weak continuation, cooldown, sizing, config, and authority surfaces out of scope.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is the cheapest admissible lane now: the negative bars-8 candidate is closed, and the next smallest remaining row-specific unknown is whether the exact first low-zone collapse after continuation at `2023-12-20T03:00:00+00:00` can be tested via one state-sensitive continuation-persistence reconsideration without reopening broader floor semantics.
- **Objective:** implement one enabled-only router-local reconsideration that, on the exact bars-7 continuation-persistence signature only, bypasses the initial raw `insufficient_evidence` no-trade return and hands control unchanged to the existing downstream classifier plus stability controls, leaving all other router behavior unchanged.
- **Candidate:** `bars-7 continuation-persistence reconsideration`
- **Base SHA:** `75246d369ef7611870d740ec0d88cd7ff9d63363`

## Review status

- pre-code review: `Opus 4.6 Governance Reviewer` → `APPROVED_WITH_NOTES`
- pre-code review lock: keep the helper tied to the existing early raw `RI_no_trade_policy` / `insufficient_evidence` return rather than recomputing classifier logic, and keep exact exclusion proof on the later low-zone rows
- post-diff audit: `Opus 4.6 Governance Reviewer` → `APPROVED_WITH_NOTES`
- post-diff audit lock: the active behavior remains acceptably bounded so long as `allow_insufficient_evidence_fallthrough=True` is scoped only to helper-fired rows, the bars-8 runtime family remains negative evidence only, and the exact helper-hit artifact remains `{2023-12-20T03:00:00+00:00}`

## Focused verification outcome

- exact helper-hit artifact: `results/backtests/ri_policy_router_bars7_continuation_20260427/fail_b_helper_hit_timestamps.json`
- emitted helper-hit set: `[
  "2023-12-20T03:00:00+00:00"
]`
- explicit non-hits preserved on the pinned fail-B carrier:
  - `2023-12-21T18:00:00+00:00`
  - `2023-12-22T09:00:00+00:00`
- focused router/scenario tests passed
- source gates passed: `pre-commit run --all-files`, `ruff check .`
- required high-sensitivity selectors passed: import smoke, determinism smoke, feature-cache invariance selectors, pipeline fast-hash guard
- security scan passed: `bandit -r src/core/strategy -c bandit.yaml`
- the earlier low-zone bars-8 runtime family remains reverted / negative only and is not present in active runtime code

## Skill Usage

Skills invoked: `decision_gate_debug` (selector-hit and exclusion replay proof), `python_engineering` (minimal-diff router helper + focused tests).

## Evidence anchors

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_bars7_continuation_persistence_candidate_packet_2026-04-27.md`
- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_low_zone_bars8_evidence_floor_runtime_closeout_2026-04-27.md`
- `results/backtests/ri_policy_router_low_zone_bars8_runtime_20260427/fail_b_helper_hit_diagnostics.json`
- `src/core/strategy/ri_policy_router.py`

## Authoritative row lock

This packet applies only to the following exact router-executed row on the pinned fail-B carrier:

| Timestamp (UTC)             | Zone  | Bars since regime change | Clarity score | Confidence gate |    Action edge | Previous policy          | Raw target           | Selected policy      | Switch reason           | Dwell duration |
| --------------------------- | ----- | -----------------------: | ------------: | --------------: | -------------: | ------------------------ | -------------------- | -------------------- | ----------------------- | -------------: |
| `2023-12-20T03:00:00+00:00` | `low` |                      `7` |          `35` |  `0.5060251200` | `0.0120502401` | `RI_continuation_policy` | `RI_no_trade_policy` | `RI_no_trade_policy` | `insufficient_evidence` |            `1` |

## Constraints

- `DEFAULT PATH UNCHANGED`
- `Behavior may change only when multi_timeframe.research_policy_router.enabled=true`
- single explicit behavior-change exception under consideration: only the exact bars-7 helper-activation row may bypass the initial raw `insufficient_evidence` return and fall through to the unchanged downstream classifier plus existing stability controls
- do not force `POLICY_CONTINUATION`
- do not force `POLICY_DEFENSIVE`
- if the unchanged downstream classifier plus stability controls still resolve `POLICY_NO_TRADE`, that is a valid falsifier rather than a reason to widen the mechanism
- no new config leaf, schema change, config-authority change, env change, or runtime-default authority change
- do not edit router point weights, floors, policy labels, seam-A single-veto semantics, aged-weak continuation semantics, cooldown, sizing, exits, or downstream decision gates

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_bars7_continuation_persistence_runtime_packet_2026-04-27.md`
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
  - later low-zone rows on `2023-12-21T18:00:00+00:00` and `2023-12-22T09:00:00+00:00`
  - seam-A single-veto semantics
  - aged-weak continuation semantics
  - cooldown behavior
  - sizing
  - exits
  - config/env/schema/authority surfaces
  - promotion/default/champion/readiness surfaces
- **Expected changed files:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_bars7_continuation_persistence_runtime_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Max files touched:** `5`

## Proposed implementation shape

- keep the direct runtime diff inside `src/core/strategy/ri_policy_router.py`
- add one private router-local helper for this exact row signature only
- the helper must remain state-sensitive and require:
  - `previous_policy == RI_continuation_policy`
  - the row would otherwise short-circuit to raw `RI_no_trade_policy` with `insufficient_evidence`
  - `bars_since_regime_change == 7`
  - `zone == low`
  - `clarity_score == 35`
  - `0 < (0.515 - confidence_gate) <= 0.01`
  - `0.010 <= action_edge <= 0.014`
- when the helper is false, preserve the current early raw no-trade short-circuit unchanged
- when the helper is true, do not immediately return raw no-trade; continue into the existing downstream classifier and existing stability controls unchanged

## Proof obligations

- default path unchanged when `research_policy_router` is absent or disabled
- direct code delta confined to the router-local no-trade short-circuit seam
- the helper does not modify router floors, point weights, policy labels, or downstream sizing semantics
- the helper must be wired to the existing early raw `RI_no_trade_policy` / `insufficient_evidence` return and must not recalculate floor/classifier logic independently
- the exact helper-hit set on router-executed bars must equal `{2023-12-20T03:00:00+00:00}`
- fail on any extra hit, any missing hit, or any hit on `2023-12-21T18:00:00+00:00` or `2023-12-22T09:00:00+00:00`

## Tests required

- `tests/utils/test_ri_policy_router.py`
  - exact bars-7 signature row with previous continuation falls through and the unchanged stability controls preserve continuation via the existing threshold/hysteresis path
  - later low-zone rows with previous no-trade do not hit the helper
  - same previous continuation state keeps the current early return when `0.515 - confidence_gate <= 0` or `> 0.01`
  - same previous continuation state keeps the current early return when `action_edge < 0.010` or `> 0.014`
  - seam-A single-veto path remains unchanged
  - aged-weak continuation guard remains unchanged
- `tests/utils/test_decision_scenario_behavior.py`
  - enabled-path exact bars-7 signature row no longer collapses immediately to router no-trade when previous continuation state is present
  - later low-zone rows do not hit the helper
  - preserved seam-A single-veto scenario remains unchanged
  - preserved aged-weak continuation scenario remains unchanged

## Gates required

- `pre-commit run --all-files`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check .`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_ri_policy_router.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_decision_scenario_behavior.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/utils/test_feature_cache.py tests/utils/diffing/test_feature_cache.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m bandit -r src/core/strategy -c bandit.yaml`

## Focused bounded verification

- one exact fail-B helper-hit probe must assert helper-hit set equality `{2023-12-20T03:00:00+00:00}` on router-executed bars
- if the helper needs to include either later low-zone row to work, stop and close negative rather than widen

## Stop Conditions

- any need to include `2023-12-21T18:00:00+00:00` or `2023-12-22T09:00:00+00:00` in the same mechanism
- any need to alter seam-A or aged-weak semantics as the primary mechanism
- any need to alter router floors, point weights, or policy labels
- any need to touch `decision.py`, `decision_gates.py`, `decision_sizing.py`, family surfaces, config authority, or env semantics

## Output required

- bounded implementation diff in the router-local no-trade seam plus focused tests
- exact commands run and pass/fail outcomes
- focused one-row verification note stating whether exact helper-hit set equality holds and whether the unchanged downstream classifier plus stability controls resolve the row without wider drift
