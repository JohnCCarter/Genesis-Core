# RI policy router aged-weak second-hit release runtime packet

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `closed negative / focused feasibility falsified / implementation reverted / no retained runtime authority`

This packet is the bounded runtime-integration follow-up to the residual aged-weak second-hit release candidate.
It grants no implementation authority until pre-code review is complete.

Within the aged-weak continuation seam only, the first qualifying aged-weak guard hit in a bounded pocket remains blocked; a repeated second-hit row in that same pocket may fall through to the existing continuation classifier and stability controls unchanged. All low-zone families, bars-7 continuation persistence, seam-A single-veto, already-strong continuation/seam-B, cooldown, sizing, exits, and config/env/schema/authority surfaces remain OUT.

## Post-attempt verdict

Pre-code review was completed, but the retained implementation outcome for this packet is **negative**.

A bounded router-local prototype plus focused tests showed that even when the second-hit row is allowed to bypass the raw `AGED_WEAK_CONTINUATION_GUARD` return, the unchanged stability path still preserves `RI_no_trade_policy` on the exact residual rows because the prior same-pocket aged-weak block leaves the router in `previous_policy = RI_no_trade_policy` with `dwell_duration = 1`, so `_apply_stability_controls(...)` resolves `switch_blocked_by_min_dwell` on the attempted second-hit release.

That means this packet's own locked objective — exact direct release on only `2023-12-28T09:00:00+00:00` and `2023-12-30T21:00:00+00:00` while keeping downstream stability controls unchanged — is not achievable on the current governed surface. The experimental code was therefore reverted, and this packet now remains historical evidence only.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice proposes an enabled-only behavior change inside `src/core/strategy/ri_policy_router.py`, a high-sensitivity strategy-runtime surface, while keeping low-zone families, seam-A, strong continuation, cooldown, sizing, config, and authority surfaces out of scope.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is the cheapest admissible lane now: the remaining unresolved residual surface is no longer low-zone or seam-A; it is the older aged-weak continuation seam, and the smallest plausible runtime question is whether only the repeated second-hit rows in two bounded late-continuation pockets deserve router-local reconsideration.
- **Objective:** implement one enabled-only router-local aged-weak second-hit release that preserves the first aged-weak guard block in a late-continuation pocket but lets the repeated second-hit row fall back to the existing continuation classifier plus stability controls unchanged, leaving all other router behavior unchanged.
- **Candidate:** `aged-weak second-hit release`
- **Base SHA:** `75246d369ef7611870d740ec0d88cd7ff9d63363`

## Skill Usage

Skills invoked: `decision_gate_debug` (row-set lock and helper-hit proof), `python_engineering` (minimal-diff router helper + focused tests), `backtest_run` (canonical fail-B replay verification).

## Evidence anchors

- `docs/governance/ri_policy_router_aged_weak_second_hit_release_candidate_packet_2026-04-27.md`
- `docs/governance/ri_policy_router_aged_weak_continuation_guard_failset_evidence_2026-04-24.md`
- `docs/governance/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `results/backtests/ri_policy_router_aged_weak_residual_probe_20260427/aged_weak_residual_rows.json`
- `src/core/strategy/ri_policy_router.py`

## Authoritative residual row-set lock

This packet applies only to the following exact residual blocked baseline longs on the pinned fail-B carrier:

| Timestamp (UTC)             | Baseline fail-B | Current fail-B candidate | Previous policy      | Switch reason                  | Dwell duration |
| --------------------------- | --------------- | ------------------------ | -------------------- | ------------------------------ | -------------: |
| `2023-12-28T09:00:00+00:00` | `LONG`          | `NONE`                   | `RI_no_trade_policy` | `AGED_WEAK_CONTINUATION_GUARD` |            `2` |
| `2023-12-30T21:00:00+00:00` | `LONG`          | `NONE`                   | `RI_no_trade_policy` | `AGED_WEAK_CONTINUATION_GUARD` |            `2` |

Context anchors that must stay out of the direct helper-hit set:

- `2023-12-28T06:00:00+00:00` — first aged-weak guard hit in the first pocket
- `2023-12-30T18:00:00+00:00` — first aged-weak guard hit in the second pocket
- `2023-12-31T00:00:00+00:00` — later aged-weak guard row on the carrier, but not a residual blocked baseline long

## Constraints

- `DEFAULT PATH UNCHANGED`
- `Behavior may change only when multi_timeframe.research_policy_router.enabled=true`
- single explicit behavior-change exception under consideration: only the exact residual aged-weak second-hit rows may bypass the raw `AGED_WEAK_CONTINUATION_GUARD` return and fall through to the existing continuation classifier plus stability controls unchanged
- first aged-weak guard hit in each bounded pocket must remain allowed to block
- pocket identity / reset must remain derived from existing row continuity plus one guard-specific latch only; no generic runtime-global counter or cross-pocket carry is allowed
- do not force `POLICY_CONTINUATION`
- do not force `POLICY_DEFENSIVE`
- if the unchanged downstream classifier plus stability controls still resolve `POLICY_NO_TRADE`, that is a valid falsifier rather than a reason to widen the mechanism
- no new config leaf, schema change, config-authority change, env change, or runtime-default authority change
- do not edit router point weights, floors, policy labels, low-zone families, seam-A single-veto semantics, strong continuation semantics, cooldown, sizing, exits, or downstream decision gates

## Scope

- **Scope IN:**
  - `docs/governance/ri_policy_router_aged_weak_second_hit_release_runtime_packet_2026-04-27.md`
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
  - low-zone bars-8 family
  - bars-7 continuation-persistence family
  - seam-A single-veto semantics
  - already-strong continuation / seam-B semantics
  - cooldown behavior
  - sizing
  - exits
  - config/env/schema/authority surfaces
  - promotion/default/champion/readiness surfaces
- **Expected changed files:**
  - `docs/governance/ri_policy_router_aged_weak_second_hit_release_runtime_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Max files touched:** `5`

## Proposed implementation shape

- keep the direct runtime diff inside `src/core/strategy/ri_policy_router.py`
- add one private router-local helper and, only if needed for provenance, one enabled-only guard-specific pocket latch for the aged-weak seam
- define the aged-weak second-hit question as:
  - first aged-weak hit in a bounded late-continuation pocket may still block,
  - repeated second-hit row in that same pocket may fall through to the existing continuation classifier plus existing stability controls unchanged
- when the helper is false, preserve the current raw `AGED_WEAK_CONTINUATION_GUARD` return unchanged
- when the helper is true, do not immediately return raw no-trade; continue into the existing downstream continuation classifier and existing stability controls unchanged

### Predicate lock

The helper must remain bound to the exact aged-weak second-hit residual surface, not a generic late-age region.

Allowed selector shape for this packet:

- `candidate == LONG`
- the row would otherwise short-circuit to raw `RI_no_trade_policy`
- `raw_switch_reason == AGED_WEAK_CONTINUATION_GUARD`
- the prior selected policy came from the same aged-weak guard pocket, not from a generic no-trade origin
- the direct helper-hit set must remain exactly the residual rows above

The helper must also emit one explicit router-debug proof field when it fires:

- `aged_weak_second_hit_release_applied = true`

That field is evidence-only and exists to support exact helper-hit containment checks on router-executed bars.

## Proof obligations

- default path unchanged when `research_policy_router` is absent or disabled
- direct code delta confined to the router-local aged-weak seam
- first aged-weak guard hit in each bounded pocket still blocks unchanged
- direct helper-hit set on router-executed bars must equal `{2023-12-28T09:00:00+00:00, 2023-12-30T21:00:00+00:00}`
- fail on any extra hit, any missing hit, or any direct hit on:
  - `2023-12-28T06:00:00+00:00`
  - `2023-12-30T18:00:00+00:00`
  - `2023-12-31T00:00:00+00:00`
- the helper must not modify low-zone bars-8, bars-7, seam-A single-veto, or strong-continuation semantics

## Tests required

- `tests/utils/test_ri_policy_router.py`
  - first aged-weak guard hit in a pocket still blocks
  - second exact aged-weak hit in the same pocket may fall through to the unchanged continuation path
  - direct helper-hit exclusions for the first-hit rows and the downstream `2023-12-31T00:00:00+00:00` analogue remain fail-closed
  - low-zone bars-8 helper remains unchanged
  - bars-7 continuation-persistence helper remains unchanged
  - seam-A single-veto path remains unchanged
- `tests/utils/test_decision_scenario_behavior.py`
  - enabled-path exact aged-weak second-hit rows no longer collapse immediately to router no-trade when the helper predicate is satisfied
  - first-hit rows remain blocked
  - bars-7 continuation-persistence scenario remains unchanged
  - preserved seam-A single-veto scenario remains unchanged
  - preserved strong-continuation scenario remains unchanged

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

- one exact fail-B helper-hit probe must assert helper-hit set equality `{2023-12-28T09:00:00+00:00, 2023-12-30T21:00:00+00:00}` on router-executed bars
- if the helper needs to include `2023-12-28T06:00:00+00:00`, `2023-12-30T18:00:00+00:00`, or `2023-12-31T00:00:00+00:00` directly to work, stop and close negative rather than widen

## Stop Conditions

- any need to retune the aged threshold itself
- any need to alter confidence/edge floors or policy labels
- any need to touch low-zone bars-8, bars-7, seam-A single-veto, or strong-continuation semantics as the primary mechanism
- any need to touch `decision.py`, `decision_gates.py`, `decision_sizing.py`, family surfaces, config authority, or env semantics

## Output required

- bounded implementation diff in the router-local aged-weak seam plus focused tests
- exact commands run and pass/fail outcomes
- focused two-row verification note stating whether exact helper-hit set equality holds and whether the unchanged downstream classifier plus stability controls resolve the residual rows without wider drift
