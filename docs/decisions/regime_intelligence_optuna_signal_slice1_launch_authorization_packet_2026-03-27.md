# Regime Intelligence challenger family — SIGNAL slice1 launch authorization packet

Date: 2026-03-27
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `AUTHORIZED NOW / research-only / full grid execution only`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet authorizes one specific research-only full-grid execution after smoke proof and full launch-subject validation, but does not authorize runtime validity, comparison, readiness, promotion, or writeback
- **Required Path:** `Quick`
- **Objective:** Decide whether the exact first admissible SIGNAL slice is authorized now for research-only full-grid execution under the pinned canonical envelope.
- **Candidate:** `tBTCUSD 3h RI SIGNAL slice1 full grid launch`
- **Base SHA:** `d227be7e`

### Skill Usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Usage mode in this packet:** evidence interpretation / launch-decision discipline only; this packet itself does not modify runtime code, family rules, comparison authority, readiness authority, promotion authority, or writeback authority

### Scope

- **Scope IN:** one docs-only launch-authorization packet that evaluates whether the exact canonical SIGNAL slice is launchable now at research authority based on completed smoke evidence and current validator/preflight evidence.
- **Scope OUT:** no source-code changes, no config changes, no changes under `src/core/**`, no changes under `scripts/**`, no changes under `config/runtime/**`, no changes under `config/strategy/champions/**`, no changes to `family_registry.py`, no changes to `family_admission.py`, no comparison opening, no readiness opening, no promotion opening, no writeback.
- **Expected changed files:** `docs/decisions/regime_intelligence_optuna_signal_slice1_launch_authorization_packet_2026-03-27.md`
- **Max files touched:** `1`

### Gates required

Before authorization may be granted:

- bounded smoke evidence must prove the exact research envelope runs successfully
- canonical launch-subject validator run must return no hard failure
- canonical launch-subject preflight must return overall `[OK]`
- family admission must be green for `run_intent=research_slice`
- exactly 3 searchable parameters must be present
- outputs must remain explicitly research-only

### Stop Conditions

- smoke ambiguity that cannot be resolved to exact artifacts
- validator hard failure on the canonical launch subject
- preflight failure on the canonical launch subject
- family admission failure
- parameter-surface widening beyond the three approved SIGNAL dimensions
- any attempt to reinterpret authorization as runtime validity, comparison authority, readiness authority, promotion authority, or writeback authority

### Output required

- one reviewable launch-authorization packet
- one explicit verdict: `AUTHORIZED NOW` or `NOT AUTHORIZED NOW`
- exact evidence basis for the verdict
- exact execution boundary if authorization is granted

## Purpose

This packet answers one narrow question only:

- is the exact canonical first SIGNAL slice authorized now for research-only full-grid execution?

This packet is a **launch decision artifact**, not a runtime-validity artifact.

It does **not**:

- change RI family rules
- change `research_slice` admission semantics
- authorize comparison, readiness, promotion, or writeback
- grant runtime-valid RI conformity

## Governing basis

This packet is downstream of the current tracked RI SIGNAL chain:

- `docs/decisions/regime_intelligence_optuna_signal_lane_launch_admissibility_packet_2026-03-27.md`
- `docs/decisions/regime_intelligence_optuna_signal_first_admissible_slice_precode_command_packet_2026-03-27.md`
- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_slice1_2024_v1.yaml`
- `tmp/tBTCUSD_3h_ri_signal_slice1_smoke_20260327.yaml`
- `results/hparam_search/ri_signal_slice1_smoke/run_meta.json`
- `results/hparam_search/ri_signal_slice1_smoke/trial_001.json`
- `results/hparam_search/ri_signal_slice1_smoke/tBTCUSD_3h_trial_001.json`

Nothing in this packet changes, softens, or reinterprets those upstream boundaries.

## 1) Launch subject under review

The exact launch subject reviewed here is:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_slice1_2024_v1.yaml`

The canonical launch subject remains bounded to exactly three searchable SIGNAL dimensions:

- `thresholds.signal_adaptation.zones.low.entry_conf_overall`
- `thresholds.signal_adaptation.zones.mid.entry_conf_overall`
- `thresholds.signal_adaptation.zones.high.entry_conf_overall`

The canonical launch subject remains an exact `3 × 3 × 3 = 27` grid under `run_intent=research_slice` with promotion disabled.

## 2) Phase 1 — Smoke evidence

### Smoke subject

- `tmp/tBTCUSD_3h_ri_signal_slice1_smoke_20260327.yaml`

Allowed semantic diff versus canonical launch subject:

- shorter bounded sample window
- `validation.enabled: false`

All three approved searchable SIGNAL dimensions and all non-SIGNAL fixed surfaces remained unchanged.

### Smoke validation evidence

Smoke YAML checks completed under canonical flags:

1. optimizer validator: passed with warnings only, no hard failure
2. preflight: overall `[OK]`
3. family admission: green for `run_intent=research_slice`
4. searchable dimensions: exactly `3`

### Smoke execution evidence

Fresh isolated smoke artifact directory:

- `results/hparam_search/ri_signal_slice1_smoke/`

Verified evidence from the smoke artifacts:

1. `run_meta.json` binds the run to `tmp\tBTCUSD_3h_ri_signal_slice1_smoke_20260327.yaml`
2. the smoke run produced exactly `27` per-trial JSON artifacts (`trial_001.json` … `trial_027.json`)
3. the smoke run also produced exact result payload files (`tBTCUSD_3h_trial_001.json` … `tBTCUSD_3h_trial_027.json`)
4. repository search over the smoke artifact set found no `Traceback`, `ERROR`, `FAILED`, or `SKIPPED` markers
5. file-based evidence confirms non-zero trades (`num_trades: 13`) in the produced trial/result artifacts

### Smoke interpretation

Smoke passed as **execution proof only**.

Smoke is sufficient to prove:

- launch-envelope executability
- artifact production
- no zero-trade collapse in the bounded window

Smoke is **not** sufficient to prove:

- uplift versus plateau
- runtime-valid RI conformity
- comparison readiness
- promotion readiness

## 3) Phase 2 — Canonical launch-subject revalidation

The canonical launch subject was revalidated under canonical flags on 2026-03-27.

### Validator result

- `scripts/validate/validate_optimizer_config.py` returned warnings only, with no hard failure
- warnings remained consistent with the already accepted research-only framing of the slice
- no new parameter leakage or widening was observed

### Preflight result

- `scripts/preflight/preflight_optuna_check.py` returned overall `[OK]`
- family admission passed for `run_intent=research_slice`
- exactly `3` searchable parameters were found
- data/snapshot/sample-range checks were green for the canonical launch subject
- champion drift smoke remained non-blocking and produced non-zero trades in the bounded quick check

### Non-blocking warnings acknowledged

The following warnings remain non-blocking for this research-only grid slice:

- storage/study resume warnings
- sampler timeout/default warnings
- champion comparison warnings for fixed surfaces intentionally left outside this slice
- absence of `risk.risk_map_deltas`

These do not widen scope, do not create runtime authority, and do not invalidate research-only full-grid launch.

## 4) Authorization decision

### Verdict

`AUTHORIZED NOW`

### Why authorization is granted

Authorization is granted because all research-launch prerequisites defined by the upstream admissibility chain are satisfied:

1. one exact canonical launch subject exists
2. the slice remains confined to the approved three-dimensional SIGNAL surface
3. bounded smoke proof is green and artifact-complete
4. the canonical launch subject passes validator/preflight at research authority
5. family admission is green for `run_intent=research_slice`
6. outputs remain explicitly research-only

### Boundary of authorization

This authorization grants only:

- one research-only full execution of the exact canonical YAML under canonical flags

This authorization does **not** grant:

- runtime-valid RI conformity
- comparison authority
- readiness authority
- promotion authority
- champion/default writeback

## 5) Exact authorized execution envelope

If executed under this authorization, the full run must use:

- config: `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_signal_slice1_2024_v1.yaml`
- canonical flags:
  - `GENESIS_FAST_WINDOW=1`
  - `GENESIS_PRECOMPUTE_FEATURES=1`
  - `GENESIS_RANDOM_SEED=42`
  - `GENESIS_FAST_HASH=0`
  - `GENESIS_PREFLIGHT_FAST_HASH_STRICT=1`
  - `PYTHONPATH=src`
  - `PYTHONIOENCODING=utf-8`
  - `TQDM_DISABLE=1`
  - `OPTUNA_MAX_DUPLICATE_STREAK=2000`
- exact run id: `ri_signal_slice1_launch_20260327`
- output interpretation: research-only

If any of the following occurs during execution, authorization is considered exhausted and the workflow must stop for review:

- runtime error or failed trial
- artifact incompleteness
- zero-trade collapse across the run
- scope drift from the exact canonical YAML

## Bottom line

The first admissible RI SIGNAL slice is **authorized now** for one research-only full-grid execution because:

- the smoke subject proved executable and artifact-complete,
- the canonical launch subject re-passed validator/preflight under canonical flags,
- family admission and parameter-surface bounds remain green, and
- no runtime, comparison, readiness, promotion, or writeback authority is implied.

This packet authorizes only the next research execution step.
