# RI policy router continuation-release hysteresis carrier validation

Date: 2026-05-04
Branch: `feature/next-slice-2026-04-29`
Mode: `RESEARCH`
Status: `completed / read-only seam validation / null on exact fail-B carrier`

This slice validates the already-implemented enabled-only `continuation_release_hysteresis` seam on the exact December fail-B RI carrier that was previously used for bounded policy-router evidence.
It does **not** modify runtime/config/schema/authority surfaces and does **not** constitute promotion, readiness, or new runtime authority.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/next-slice-2026-04-29`
- **Risk:** `MED` — why: this slice runs deterministic read-only backtests on a high-sensitivity router carrier, but does not alter runtime/default/authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the continuation-release seam is already implemented and validated at unit/integration scope, and the next honest question is whether that seam actually exercises or changes behavior on one fixed historical carrier before any broader interpretation is attempted.
- **Objective:** compare the same fixed RI carrier with the router leaf enabled as-is versus the same enabled carrier with `continuation_release_hysteresis=0`, and determine whether the exact fail-B carrier actually enters the defensive-to-continuation release seam.
- **Candidate:** `continuation_release_hysteresis exact carrier validation`
- **Base SHA:** `52b43e82b1c1e1aaceab3a078c62c736b6eea371`

## Skill Usage

- **Applied repo-local spec:** `backtest_run`
  - reason: the slice must stay on canonical deterministic backtest settings with explicit env and a fixed evidence carrier.
- **Applied repo-local spec:** `genesis_backtest_verify`
  - reason: the slice compares deterministic backtest outputs and must separate real behavior drift from artifact-only differences.
- **Applied repo-local spec:** `decision_gate_debug`
  - reason: the conclusion depends on whether the router actually enters the `continuation_release` switch-control seam, not on top-line metrics alone.
- **Applied repo-local spec:** `python_engineering`
  - reason: the new analysis probe script is typed, small, and was validated with `ruff` plus a successful execution run.

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/decisions/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_runtime_packet_2026-04-30.md`
  - `docs/analysis/regime_intelligence/policy_router/ri_policy_router_enabled_vs_absent_bounded_contribution_evidence_2026-04-28.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Candidate / comparison surface:**
  - fixed carrier config `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
  - same carrier with router leaf unchanged versus same carrier with `continuation_release_hysteresis=0`
  - exact subject `tBTCUSD`, `3h`, `2023-12-01 -> 2023-12-31`, `warmup=120`, `data_source_policy=curated_only`
- **Vad ska förbättras:**
  - determine whether the implemented seam is actually exercised on the exact fail-B carrier
  - distinguish behavioral drift from parameter-only debug/fingerprint drift
- **Vad får inte brytas / drifta:**
  - no runtime edits
  - no config/schema/authority edits
  - no legacy reopening
  - no promotion/default/champion/readiness claims from this slice alone
- **Reproducerbar evidens som måste finnas:**
  - same fixed carrier in both runs
  - canonical env with explicit seed and 1/1 mode
  - one summary artifact and one row-diff artifact
  - explicit proof of whether `switch_control_mode == continuation_release` occurs on this subject

## Scope

### Scope IN

- one new read-only probe script under `scripts/analyze/`
- one new analysis note
- local JSON artifacts under `results/backtests/ri_policy_router_continuation_release_hysteresis_20260504/`
- `GENESIS_WORKING_CONTRACT.md`

### Scope OUT

- `src/**`
- `config/**`
- `tests/**`
- new runtime packets
- legacy surfaces
- promotion/readiness/champion/default authority changes

## Canonical env for all runs

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_PRECOMPUTE_CACHE_WRITE=0`
- `GENESIS_MODE_EXPLICIT=1`
- `GENESIS_FAST_HASH=0`
- `GENESIS_SCORE_VERSION=v2`

## Fixed read-only evidence inputs

- `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- `scripts/analyze/ri_policy_router_continuation_release_hysteresis_carrier_validation_20260504.py`

These inputs are fixed evidence surfaces for this slice and are out of edit scope once recorded.

## Exact commands run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/analyze/ri_policy_router_continuation_release_hysteresis_carrier_validation_20260504.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_carrier_validation_20260504.py`

## Actual emitted artifacts

- `results/backtests/ri_policy_router_continuation_release_hysteresis_20260504/continuation_release_hysteresis_summary.json`
- `results/backtests/ri_policy_router_continuation_release_hysteresis_20260504/continuation_release_hysteresis_row_diffs.json`

## Outcomes

### Top-line metrics are identical

Baseline (`enabled` carrier as-is, implicit shared hysteresis):

- final capital: `9998.750142827499`
- total return: `-0.012498571725009242%`
- trades: `13`
- profit factor: `1.8925643673350818`
- max drawdown: `0.2532619664095436%`
- net position PnL: `-1.2498571724996923`

Release-zero (`enabled` carrier with `continuation_release_hysteresis=0`):

- final capital: `9998.750142827499`
- total return: `-0.012498571725009242%`
- trades: `13`
- profit factor: `1.8925643673350818`
- max drawdown: `0.2532619664095436%`
- net position PnL: `-1.2498571724996923`

### Row-level interpretation

Observed diff counts from the probe:

- raw row diff count: `121`
- action diff count: `0`
- reason-only diff count: `121`
- behavioral row diff count: `0`
- parameter-only diff count: `121`
- `continuation_release` rows in baseline: `0`
- `continuation_release` rows in release-zero run: `0`
- diffs involving `continuation_release`: `0`

The apparent `121` row diffs are not behavioral. They come from the debug-carried
`router_params.continuation_release_hysteresis` value (`1` vs `0`) and the resulting config
fingerprint drift, while action, selected policy, size, reasons, and summary metrics remain identical.

### Exact read of this carrier

On this exact fail-B subject, the router never entered the bounded release seam:

- no row emitted `switch_control_mode == continuation_release`
- therefore the enabled-only override had no opportunity to alter stability control behavior
- the carrier remains a valid null check for the seam, but not an exercising surface for it

## Consequence

The honest current read is:

- the exact fail-B carrier is **non-exercising** for `continuation_release_hysteresis`
- this slice does **not** show the seam is harmful, helpful, or broadly irrelevant
- it only shows that this particular fixed subject never enters the defensive-to-continuation release path

What this slice justifies:

- keep the seam implemented and bounded as previously validated
- treat this exact carrier as a null validation surface for the seam
- require an exercising subject before making any broader payoff claim about the seam

What this slice does **not** justify:

- runtime widening
- tuning claims from this null carrier
- a broad statement that `continuation_release_hysteresis` has no effect in practice
- promotion/default/champion/readiness claims

## Next admissible move

If this line is continued, the next honest step is one additional bounded RI-only validation on a fixed subject that actually exercises:

- `previous_policy == RI_defensive_transition_policy`, and
- `raw_target_policy == RI_continuation_policy`

In practice that means choosing one exact window/carrier where `switch_control_mode == continuation_release` is observed, then rerunning the same default-vs-release-zero comparison there.
