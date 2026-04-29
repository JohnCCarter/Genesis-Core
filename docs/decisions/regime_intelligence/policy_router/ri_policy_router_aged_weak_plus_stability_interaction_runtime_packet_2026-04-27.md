# RI policy router aged-weak plus stability interaction runtime packet

Date: 2026-04-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `negative closeout / exact fail-B verification falsified implementation / reverted`

This packet is the bounded runtime-integration follow-up to `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_plus_stability_interaction_precode_packet_2026-04-27.md`.

It is now a **historical closeout record** for that bounded runtime attempt.
The implementation was attempted inside the exact approved scope, but the packet's locked fail-B verification falsified it on the active router-enabled carrier, so the runtime code and focused tests were reverted.

Within the aged-weak continuation seam only, the first qualifying aged-weak guard hit in a bounded late-continuation pocket must still block unchanged; only the repeated second-hit residual row in that same pocket may be reconsidered, and only through one explicit interaction contract between the aged-weak guard and same-origin stability/min-dwell retention. Low-zone families, bars-7 continuation persistence, seam-A single-veto, already-strong continuation / seam-B, generic threshold retuning, cooldown, sizing, exits, and config/env/schema/authority surfaces remain OUT.

## Closeout result

- bounded implementation was attempted in:
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- focused/source gates passed during the attempt, but the exact helper-hit proof on the active router-enabled fail-B carrier failed the packet lock
- expected direct helper-hit set:
  - `2023-12-28T09:00:00+00:00`
  - `2023-12-30T21:00:00+00:00`
- actual direct helper-hit set on the active carrier:
  - `2023-12-28T09:00:00+00:00`
  - `2023-12-31T00:00:00+00:00`
- decisive falsifier:
  - `2023-12-30T21:00:00+00:00` remained `RESEARCH_POLICY_ROUTER_NO_TRADE`
  - `2023-12-31T00:00:00+00:00` was incorrectly released instead
- interpretation on the active carrier:
  - `2023-12-30T12:00:00+00:00` is already a continuation entry
  - `2023-12-30T15:00:00+00:00` and `2023-12-30T18:00:00+00:00` are cooldown rows
  - therefore `2023-12-30T21:00:00+00:00` no longer arrives as the same-origin `RI_no_trade_policy` row assumed by this packet's residual-lock story
- outcome:
  - the slice is closed negative on the active carrier
  - no aged-weak-plus-stability interaction code remains in active runtime after revert
  - any reopen requires a fresh packet re-anchored to the active carrier truth rather than a reuse of this packet's residual-row assumption

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `api`
- **Risk:** `HIGH` — why: this slice proposes an enabled-only behavior change inside `src/core/strategy/ri_policy_router.py`, a high-sensitivity strategy-runtime surface, and it explicitly reopens the aged-weak residual seam only by touching the interaction with `switch_blocked_by_min_dwell` while keeping default-path, config-authority, low-zone, seam-A, and strong-continuation surfaces out of scope.
- **Required Path:** `Full`
- **Lane:** `Runtime-integration` — why this is the cheapest admissible lane now: the older router-local second-hit release packet is already closed negative because unchanged stability controls retained `RI_no_trade_policy`, so the next honest unknown is a narrow enabled-only interaction test on the exact two residual rows rather than another raw-guard retry or a generic stability retune.
- **Objective:** implement one enabled-only aged-weak plus same-origin stability/min-dwell interaction in `src/core/strategy/ri_policy_router.py` that keeps the first aged-weak guard hit blocked, but allows the exact repeated residual row in the same pocket to fall through the raw aged-weak guard and one same-origin min-dwell retention barrier only, while preserving thresholds, hysteresis, default path, and all unrelated seams unchanged.
- **Candidate:** `aged-weak plus stability interaction`
- **Base SHA:** `16870ee6e97d19709d21e506c741094d87c78acc`

## Review status

- `Opus 4.6 Governance Reviewer`: `APPROVED_WITH_NOTES`
- reviewed scope: one bounded enabled-only aged-weak runtime slice in `src/core/strategy/ri_policy_router.py` plus focused router/scenario tests and exact fail-B replay proof on the locked December 2023 carrier
- review lock to enforce:
  - the slice must remain an interaction contract between the aged-weak seam and same-origin `min_dwell` retention only
  - the implementation must not hardcode symbol, timeframe, date window, bridge path, or literal timestamps as runtime eligibility logic
  - the slice must not introduce any new config/env/schema path if the existing `multi_timeframe.research_policy_router.enabled` gate proves insufficient
  - any one-shot provenance/release state must clear fail-closed on pocket change, origin change, or after one consumed release
  - no new runtime/public/result debug contract may be created merely to prove the interaction

## Skill Usage

- **Applied repo-local spec:** `decision_gate_debug`
  - reason: the residual surface is already row-locked, and the packet must stay anchored to verified switch/state mechanics rather than a threshold-story rewrite.
- **Applied repo-local spec:** `python_engineering`
  - reason: any follow-up implementation must stay as a small typed Python diff with focused tests, `ruff`, and `bandit`.
- **Applied repo-local spec:** `backtest_run`
  - reason: any focused fail-B replay/backtest verification must keep canonical mode, explicit seed, warmup, and exact window discipline.
- **Applied repo-local spec:** `genesis_backtest_verify`
  - reason: any replay/output comparison on this surface must remain deterministic and artifact-bounded, with no unapproved trading artifact widening.

### Runtime-integration lane

- **Durable surface som föreslås:**
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Varför billigare icke-runtime-form inte längre räcker:**
  - the docs-only pre-code packet already fixed the exact residual row-set,
  - the older router-local second-hit release packet is falsified precisely because `_apply_stability_controls(...)` still resolves `switch_blocked_by_min_dwell`,
  - the next unknown is therefore runtime behavior on one explicit interaction seam, not docs-only framing.
- **Default-path stance:** `unchanged`
- **Required packet / review:**
  - Opus pre-code review required before implementation
  - Opus post-diff audit required after implementation

## Evidence anchors

- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_plus_stability_interaction_precode_packet_2026-04-27.md`
- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_second_hit_release_runtime_packet_2026-04-27.md`
- `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_second_hit_release_runtime_closeout_2026-04-27.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_single_veto_release_residual_blocked_longs_diagnosis_2026-04-27.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_aged_weak_continuation_guard_failset_evidence_2026-04-24.md`
- `results/backtests/ri_policy_router_aged_weak_residual_probe_20260427/aged_weak_residual_rows.json`
- `src/core/strategy/ri_policy_router.py`

## Exact fail-B subject lock

Any focused replay/backtest verification under this packet must stay on the same pinned fail-B carrier subject:

- symbol: `tBTCUSD`
- timeframe: `3h`
- date window: `2023-12-01 -> 2023-12-31`
- warmup: `120`
- data-source policy: `curated_only`
- canonical env discipline:
  - `GENESIS_RANDOM_SEED=42`
  - `GENESIS_FAST_WINDOW=1`
  - `GENESIS_PRECOMPUTE_FEATURES=1`
  - `GENESIS_PRECOMPUTE_CACHE_WRITE=0`
- baseline bridge path: `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

No new candidate bridge artifact is authorized by this packet.
The intended runtime delta is source-local to `ri_policy_router.py` on the current branch only.

## Authoritative residual row-set lock

This packet applies only to the following exact residual blocked baseline longs on the pinned fail-B carrier:

| Timestamp (UTC)             | Baseline fail-B | Current fail-B candidate | Zone  | Bars since regime change | Clarity score | Confidence gate |    Action edge | Previous policy      | Raw target           | Selected policy      | Switch reason                  | Dwell duration |
| --------------------------- | --------------- | ------------------------ | ----- | -----------------------: | ------------: | --------------: | -------------: | -------------------- | -------------------- | -------------------- | ------------------------------ | -------------: |
| `2023-12-28T09:00:00+00:00` | `LONG`          | `NONE`                   | `low` |                     `20` |          `38` |  `0.5289101921` | `0.0578203842` | `RI_no_trade_policy` | `RI_no_trade_policy` | `RI_no_trade_policy` | `AGED_WEAK_CONTINUATION_GUARD` |            `2` |
| `2023-12-30T21:00:00+00:00` | `LONG`          | `NONE`                   | `low` |                     `23` |          `37` |  `0.5234482255` | `0.0468964510` | `RI_no_trade_policy` | `RI_no_trade_policy` | `RI_no_trade_policy` | `AGED_WEAK_CONTINUATION_GUARD` |            `2` |

Context anchors that must remain out of the direct helper-hit set:

- `2023-12-28T06:00:00+00:00` — first aged-weak guard hit in the first pocket
- `2023-12-30T18:00:00+00:00` — first aged-weak guard hit in the second pocket
- `2023-12-31T00:00:00+00:00` — later aged-weak guard row on the same carrier, but not a residual blocked baseline long

If a later replay changes this exact residual row-set materially, stop and re-anchor before implementation.

## Constraints

- `DEFAULT PATH UNCHANGED`
- `Behavior may change only when multi_timeframe.research_policy_router.enabled=true`
- the implementation must derive eligibility solely from router-local runtime state/provenance already present on the live surface; do **not** branch on symbol, timeframe, date window, bridge path, or literal timestamp constants
- this packet relies on the already-existing `multi_timeframe.research_policy_router.enabled` gate only; if that gate/path is not sufficient on the governed runtime surface, stop and reopen with explicit config-authority scope rather than introducing any new config/env/schema shape
- single explicit behavior-change exception under consideration:
  - first aged-weak guard hit in a bounded pocket must still block unchanged
  - only the exact repeated residual row in that same pocket may bypass the raw `AGED_WEAK_CONTINUATION_GUARD` return
  - only one same-origin `switch_blocked_by_min_dwell` retention may be bypassed for that same-pocket aged-weak residual row
  - `switch_threshold`, `hysteresis`, and the configured numeric `min_dwell` value remain unchanged
- do **not** weaken generic stability behavior for any other `RI_no_trade_policy` origin
- do **not** retune aged thresholds, confidence floors, edge floors, point weights, or policy labels
- do **not** force `POLICY_CONTINUATION`
- do **not** force `POLICY_DEFENSIVE`
- if the unchanged downstream classifier and the still-active non-min-dwell stability checks continue to resolve `POLICY_NO_TRADE`, that is a valid falsifier rather than a reason to widen
- no new config leaf, schema change, config-authority change, env change, or runtime-default authority change
- do not edit low-zone bars-8 semantics, bars-7 continuation-persistence semantics, seam-A single-veto semantics, already-strong continuation / seam-B semantics, cooldown behavior, sizing, exits, or downstream decision-gate surfaces

## Scope

- **Scope IN:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_plus_stability_interaction_runtime_packet_2026-04-27.md`
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
  - `scripts/**`
  - `results/**`
  - `artifacts/**`
  - any new candidate bridge artifact
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
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_aged_weak_plus_stability_interaction_runtime_packet_2026-04-27.md`
  - `GENESIS_WORKING_CONTRACT.md`
  - `src/core/strategy/ri_policy_router.py`
  - `tests/utils/test_ri_policy_router.py`
  - `tests/utils/test_decision_scenario_behavior.py`
- **Max files touched:** `5`

## Proposed implementation shape

- keep the direct runtime diff inside `src/core/strategy/ri_policy_router.py`
- add at most one private aged-weak-specific provenance / interaction helper and, only if necessary, one enabled-only aged-weak-specific state bit that distinguishes:
  - prior `RI_no_trade_policy` originated from the same-pocket aged-weak guard,
  - and one same-pocket aged-weak release has not already been consumed
- any aged-weak-specific provenance or one-shot release state must be strictly fail-closed: it must clear on pocket change, policy-origin change, or after one consumed release, and it must never survive into a later unrelated pocket
- define the exact interaction question as:
  - first aged-weak hit in a bounded late-continuation pocket still blocks,
  - repeated second-hit residual row in that same pocket may fall through the raw aged-weak guard,
  - and if `_apply_stability_controls(...)` would block only because `previous_state.selected_policy == RI_no_trade_policy` from that same aged-weak pocket and `previous_state.dwell_duration < min_dwell`, allow one same-pocket release through unchanged threshold/hysteresis checks
- when the exact interaction helper is false, preserve the current raw aged-weak return and current `_apply_stability_controls(...)` behavior unchanged
- when the exact interaction helper is true, do not rewrite classifier scoring, thresholds, or policy labels; continue into the existing continuation classifier and unchanged non-min-dwell stability checks

### Predicate lock

The helper must remain bound to the exact aged-weak residual interaction surface, not a generic late-age or generic stability region.

Allowed selector shape for this packet:

- `candidate == LONG`
- the row would otherwise short-circuit to raw `RI_no_trade_policy`
- `raw_switch_reason == AGED_WEAK_CONTINUATION_GUARD`
- prior selected policy came from the same aged-weak guard pocket, not from a generic no-trade origin
- direct helper-hit set must remain exactly the two residual rows above
- the min-dwell interaction exception may apply only when the current row is the repeated same-pocket aged-weak residual row and the only block under review is `switch_blocked_by_min_dwell`

The helper must also emit one explicit router-debug proof field when it fires:

- `aged_weak_stability_interaction_applied = true`

That field is evidence-only and may use only an already-existing internal router debug/trace surface on this path. If no such internal surface exists without changing a runtime/public/result contract, prove the interaction via tests/assertions/replay evidence instead of adding a new externally meaningful debug schema.

## Proof obligations

- default path unchanged when `research_policy_router` is absent or disabled
- direct code delta confined to the router-local aged-weak seam plus its same-origin min-dwell interaction only
- first aged-weak guard hit in each bounded pocket still blocks unchanged
- direct helper-hit set on router-executed bars must equal `{2023-12-28T09:00:00+00:00, 2023-12-30T21:00:00+00:00}`
- fail on any extra hit, any missing hit, or any direct hit on:
  - `2023-12-28T06:00:00+00:00`
  - `2023-12-30T18:00:00+00:00`
  - `2023-12-31T00:00:00+00:00`
- generic `switch_blocked_by_min_dwell` behavior for non-aged-weak origins must remain unchanged
- bars-7 continuation-persistence, low-zone bars-8, seam-A single-veto, and strong-continuation semantics must remain unchanged

## Tests required

- `tests/utils/test_ri_policy_router.py`
  - first aged-weak guard hit in a pocket still blocks
  - repeated exact aged-weak residual row in the same pocket can bypass the raw aged-weak return only when the same-origin stability interaction predicate is satisfied
  - generic min-dwell blocking from non-aged-weak `RI_no_trade_policy` origins remains unchanged
  - direct helper-hit exclusions for the first-hit rows and the downstream `2023-12-31T00:00:00+00:00` analogue remain fail-closed
  - low-zone bars-8 helper remains unchanged
  - bars-7 continuation-persistence helper remains unchanged
  - seam-A single-veto path remains unchanged
- `tests/utils/test_decision_scenario_behavior.py`
  - enabled-path exact aged-weak residual rows no longer collapse immediately to router no-trade when the interaction predicate is satisfied
  - the first-hit context rows remain blocked
  - a generic non-aged-weak no-trade origin still blocks on `min_dwell`
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
- one exact fail-B replay/backtest verification must stay on the locked subject above and must remain canonical (`GENESIS_RANDOM_SEED=42`, `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`, `GENESIS_PRECOMPUTE_CACHE_WRITE=0`, warmup `120`, `curated_only`)
- if the interaction needs to include `2023-12-28T06:00:00+00:00`, `2023-12-30T18:00:00+00:00`, or `2023-12-31T00:00:00+00:00` directly to work, stop and close negative rather than widen
- if release still requires changing configured `min_dwell`, `switch_threshold`, `hysteresis`, or any floor, stop and close negative rather than widen

## Stop Conditions

- any need to retune the aged threshold itself
- any need to alter confidence/edge floors, point weights, or policy labels
- any need to weaken generic `min_dwell` behavior rather than one same-origin aged-weak interaction
- any need to touch low-zone bars-8, bars-7 continuation-persistence, seam-A single-veto, or strong-continuation semantics as the primary mechanism
- any need to touch `decision.py`, `decision_gates.py`, `decision_sizing.py`, family surfaces, config authority, or env semantics
- inability to express the contract using only router-local aged-weak provenance plus one same-origin stability interaction

## Output required

- bounded implementation diff in the router-local aged-weak seam plus focused tests
- exact commands run and pass/fail outcomes
- focused fail-B verification note stating whether exact helper-hit set equality holds and whether the same-origin `min_dwell` interaction is enough to release the residual rows without wider drift
