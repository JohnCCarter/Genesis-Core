# REGIME INTELLIGENCE T9 CONTRACT (P2 Clarity Score v1 — Contract Freeze)

Date: 2026-03-04
Category: `docs`
Status: **historical contract reference / not active on current branch**

> [HISTORICAL 2026-05-05] This T9 clarity contract is not an active RI lane on `feature/next-slice-2026-05-05`.
> Preserve it as historical contract context only; current live RI anchors are tracked via `GENESIS_WORKING_CONTRACT.md` and the later RI policy-router chain.

DoD reference: `docs/ideas/REGIME_INTELLIGENCE_DOD_P1_P2_2026-02-27.md`
Design reference: `docs/ideas/REGIME_INTELLIGENCE_DESIGN_2026-02-23.md`

## 1) Commit contract

### Scope IN (strict)

- `docs/ideas/REGIME_INTELLIGENCE_T9_CONTRACT_2026-03-04.md`

### Scope OUT (strict)

- All runtime source files under `src/**`
- All scripts except docs/evidence tooling
- Any change to runtime defaults, API contracts, or execution behavior
- Any change under `config/strategy/champions/*`
- Any change to `.github/workflows/champion-freeze-guard.yml`

### Constraints

- Default mode: **NO BEHAVIOR CHANGE**
- T9 is a contract-only tranche (docs/governance lock)
- No implementation in this contract PR

## 2) T9 objective

Freeze the P2/v2 implementation contract for a deterministic and auditable clarity-score rollout behind explicit flag/version.

## 3) P2 clarity v1 behavior locks (normative)

### 3.1 Normalization lock

All clarity input components must be normalized to bounded range before aggregation:

- `normalized_component ∈ [0,1]`
- deterministic transform only
- no stochastic transform
- no hidden state mutation

For v1 decision path, normalization constants must be **static and versioned**.

### 3.2 Aggregation lock

Clarity raw score is weighted sum of normalized components:

- `clarity_raw = Σ(w_i * c_i)`
- `w_i >= 0`
- `Σ w_i = 1.0`

For v1, weights are fixed constants (`weights_v1`) and version-locked.

### 3.3 Score conversion lock

Clarity score conversion is fixed:

- `clarity_score = round_policy(clamp(clarity_raw * 100, 0, 100))`
- `round_policy` must be explicit and versioned (no environment-dependent ambiguity)
- `round_policy` must specify deterministic tie handling (for example `half_up` or `half_even`) and produce integer output in `[0,100]`

## 4) Authority / SSOT lock for clarity input

Clarity must consume authoritative regime output from existing authority resolver path (with source attribution), not direct ad hoc calls.

- authoritative value source remains runtime authority resolver path
- authority source attribution must be logged
- no implicit authority source override in T9
- implementation tranche reports (T9A+) must explicitly name the resolver symbol/path used in code

## 5) OFF/ON behavior lock

- `OFF` (default): must preserve P1 behavior and parity expectations
- `ON` (explicit): allows P2 behavior only behind version/flag

No P2 behavior may activate without explicit `ON`.

## 6) Logging lock (minimum required fields)

Per decision/bar, minimum fields for attribution:

- context: `run_id`, `git_sha`, `symbol`, `timeframe`, `timestamp_utc`, `bar_index`
- governance: `ri_flag_enabled`, `ri_version`, `authority_mode`, `authority_mode_source`
- clarity: raw components, normalized components, weights/version, `clarity_raw`, `clarity_score`, clamp/round metadata
- mapping/sizing: `risk_curve_version`, multiplier pre/post caps, sizing decomposition and final size
- decision outcome: action, reasons, blocker label if any

## 7) Determinism lock

Equivalent input must yield equivalent output under fixed config/version.

- no lookahead
- fixed as-of semantics
- stable rounding policy
- stable pipeline order hash/invariance gates

## 8) P2 evidence matrix (implementation tranche prerequisite)

Before claiming P2 implementation done:

1. OFF/ON parity matrix exists and is reproducible
2. OFF mode proves no behavior drift vs approved P1 baseline
3. ON mode evidence includes sizing decomposition attribution
4. governance review explicitly approves behavior-change scope

## 9) Required gates for implementation tranche (T9A+)

When implementation starts (not this PR), required PRE/POST gates include:

Skill runs are supplemental evidence and must not replace determinism/invariance gates.

1. `pre-commit run --files <touched files>`
2. `pytest -q tests/test_import_smoke_backtest_optuna.py`
3. `pytest -q tests/backtest/test_backtest_determinism_smoke.py`
4. `pytest -q tests/test_features_asof_cache_key_deterministic.py`
5. `pytest -q tests/test_pipeline_fast_hash_guard.py::test_pipeline_component_order_hash_contract_is_stable`
6. `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_shadow_error_rate_contract`
7. `pytest -q tests/test_evaluate_pipeline.py::test_evaluate_pipeline_authority_mode_source_invariant_contract`
8. `python scripts/run_skill.py --skill feature_parity_check --manifest dev --dry-run`
9. `python scripts/run_skill.py --skill config_authority_lifecycle_check --manifest dev --dry-run`

## 10) Done criteria for this T9 contract PR

- T9 contract file exists and is reviewable
- P2 clarity locks are explicit (normalization, weights, rounding, OFF/ON behavior)
- SSOT/authority usage rule is explicit
- minimum logging attribution fields are explicit
- implementation gates are enumerated for later tranche

## 11) Non-goals in T9

- no runtime implementation
- no config/champion changes
- no API changes
- no gate weakening

## 12) References

- `docs/ideas/REGIME_INTELLIGENCE_DOD_P1_P2_2026-02-27.md`
- `docs/ideas/REGIME_INTELLIGENCE_DESIGN_2026-02-23.md`
- `docs/ideas/REGIME_INTELLIGENCE_T8_CONTRACT_2026-02-26.md`
