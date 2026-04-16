# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `HIGH` — runtime decision/sizing-path touch in strategy evaluation, but intended as a default-off research-only carveout narrower than the existing sizing floor seam
- **Required Path:** `Full`
- **Objective:** Add the smallest default-off research sizing seam needed to test whether the verified bull/high persistence size-floor effect can be narrowed to the higher-value November-like context by applying only when the current override-admitted bar is not already volatility-penalized.
- **Candidate:** `bull/high persistence volatility-aware sizing floor`
- **Base SHA:** `8e23ddb45d08784e8a8a340f83334f5842505e0e`

## Scope

- **Scope IN:**
  - `src/core/strategy/decision_sizing.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py` (only the whitelist/additive authority surface for the new research leaf)
  - focused tests covering sizing/runtime semantics/schema backcompat
  - `docs/governance/bull_high_persistence_volatility_aware_floor_precode_packet_2026-04-15.md`
- **Scope OUT:**
  - champion configs
  - runtime defaults
  - optimizer/backtest engine semantics
  - fib gating logic
  - admission/reasons logic for the existing override
  - broader risk-map redesign
  - non-research volatility sizing redesign
  - docs outside this packet unless strictly required for evidence
- **Expected changed files:**
  - `src/core/strategy/decision_sizing.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `tests/utils/test_decision_scenario_behavior.py`
  - `tests/governance/test_config_schema_backcompat.py`
  - `docs/governance/bull_high_persistence_volatility_aware_floor_precode_packet_2026-04-15.md`
- **Max files touched:** `6`

## Skill Usage

- **Repo-local skill specs to apply:**
  - `.github/skills/config_authority_lifecycle_check.json` — authority/additive-leaf discipline for config-surface changes
  - `.github/skills/repo_clean_refactor.json` — strict scope/minimal-diff/no-drift discipline for the narrow implementation slice
- **Why these skills apply:**
  - the slice adds a new research-only config/authority leaf and therefore needs explicit authority-surface discipline
  - the slice must remain tightly scoped and default-safe while touching runtime-adjacent code
- **Not primary for this slice:**
  - `.github/skills/feature_parity_check.json` is not the main skill because this seam does not change feature computation logic

## Planned behavior

- Extend the existing research-only config surface `multi_timeframe.research_bull_high_persistence_override` with a new default-off boolean leaf `require_neutral_volatility_for_min_size_base`.
- The new leaf is research-only and gives no behavior change when absent or `false`.
- When `require_neutral_volatility_for_min_size_base = true`, the already-existing research `min_size_base` substitution may apply only when all existing conditions are satisfied **and** the current-bar volatility sizing multiplier is neutral (`size_vol_mult >= 1.0`).
- This is intended to exclude the March override bar (`size_vol_mult = 0.7`) while preserving the November override bar (`size_vol_mult = 1.0`) on the canonical replay window.
- The new condition must read the already-derived canonical current-bar `size_vol_mult` as a read-only signal inside `src/core/strategy/decision_sizing.py`; it must not duplicate, recompute, or reorder the existing volatility-sizing derivation.
- The new condition must not read from debug-only state or any stale carry-over field; it must bind to the same current-bar sizing calculation that produces the final `size_vol_mult` used for `combined_mult`.
- Do not alter confidence gates, regime thresholds, hysteresis logic, cooldown logic, or non-override sizing paths.
- Do not change behavior for any path where `min_size_base <= 0.0`.

## Evidence basis for this slice

- The current bracket (`0.005`, `0.010`, `0.020`) changes exactly the same two override-admitted LONG bars and no others.
- The `0.010` bracket captures about 92.4% of the `0.020` score gain while using half the floor.
- Trade-sequence decomposition shows that the net `0.010` improvement is dominated by the November 2024 override entry, while the March sequence is mixed/slightly net negative after accounting for the trades it displaces.
- The two affected bars differ materially in volatility sizing context:
  - March 2024 bar: `size_vol_mult = 0.7`, `size_combined_mult = 0.56`
  - November 2024 bar: `size_vol_mult = 1.0`, `size_combined_mult = 0.8`
- This supports a narrower hypothesis: the valuable edge may live in the non-volatility-penalized subset of override bars.

## Gates required

- `pre-commit run --files src/core/strategy/decision_sizing.py src/core/config/schema.py src/core/config/authority.py tests/utils/test_decision_scenario_behavior.py tests/governance/test_config_schema_backcompat.py`
- focused pytest selectors for touched sizing/schema/runtime-semantic surfaces
- focused canonical smoke replay on `scripts/run/run_backtest.py` with locked `tBTCUSD 3h 2024-01-02..2024-12-31`
- determinism replay selector
- feature cache invariance selector
- pipeline hash guard selector
- canonical parity proof that default behavior remains identical when the new leaf is absent **and** when it is explicitly `false`
- canonical config/authority proof that the resolved authority surface is identical for leaf absent vs explicit `false`
- canonical replay proof that `min_size_base > 0.0` + `require_neutral_volatility_for_min_size_base = true` changes fewer or equal bars than the unconstrained `min_size_base` seam
- targeted proof that the volatility-aware enabled path affects only the known candidate subset and, on the current locked window, no bars beyond the existing two-bar research seam
- locked-window enabled-path comparison against the `0.010` unconstrained seam to determine whether the volatility-aware carveout preserves or improves risk-adjusted value

## Stop Conditions

- Scope drift outside listed files
- Any behavior change when the new leaf is absent or `false`
- Need to alter volatility-sizing logic outside the research-only floor gate
- Determinism/hash regression
- Evidence shows the November-only style narrowing does not preserve enough of the edge to justify the extra condition

## Output required

- **Implementation Report**
- **PR evidence template**

## Evidence wording discipline

- Any enabled-path result delta is research efficacy evidence only.
- No enabled-path outcome may be cited as default parity or contract-preservation proof.
- The slice is only valid if default/no-leaf behavior remains identical.
- Any volatility-aware enabled-path claim must distinguish “same two bars but smaller subset activated” from broader runtime improvement; if a third bar changes, the seam is out of contract until re-reviewed.
