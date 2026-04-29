# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `HIGH` — runtime decision/sizing-path touch in strategy evaluation, but intended as a default-off research-only carveout
- **Required Path:** `Full`
- **Objective:** Add the smallest default-off research sizing seam needed to test whether the existing bull/high persistence admission carveout has executable edge once the champion risk-map floor no longer forces `size_base = 0.0` on admitted override bars.
- **Candidate:** `bull/high persistence sizing floor override`
- **Base SHA:** `feature/ri-role-map-implementation-2026-03-24 (working tree)`

## Scope

- **Scope IN:**
  - `src/core/strategy/decision.py` (only if needed for exact current-bar override plumbing)
  - `src/core/strategy/decision_sizing.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - focused tests covering sizing/runtime semantics/schema backcompat
  - this packet
- **Scope OUT:**
  - champion configs
  - runtime defaults
  - optimizer/backtest engine semantics
  - fib gating logic
  - non-research sizing redesign
  - docs outside this packet unless strictly required for evidence
- **Expected changed files:**
  - `src/core/strategy/decision.py`
  - `src/core/strategy/decision_sizing.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
  - `tests/utils/test_decision_scenario_behavior.py`
  - `tests/integration/test_golden_trace_runtime_semantics.py`
  - `tests/governance/test_config_schema_backcompat.py`
  - `docs/governance/bull_high_persistence_sizing_override_precode_packet_2026-04-15.md`
- **Max files touched:** `7`

## Planned behavior

- Extend the existing research-only config surface `multi_timeframe.research_bull_high_persistence_override` with a new default-off numeric leaf `min_size_base`.
- `min_size_base` is research-only and gives no behavior change when the leaf is absent or set to `0.0`.
- When `min_size_base > 0.0`, this is an explicit behavior-change candidate, strictly limited to bars admitted via `RESEARCH_BULL_HIGH_PERSISTENCE_OVERRIDE` where normal sizing produced `size_base == 0.0`; existing multipliers are then applied unchanged.
- Apply this leaf only when all are true:
  - the existing bull/high persistence override is enabled
  - the current bar was admitted via `RESEARCH_BULL_HIGH_PERSISTENCE_OVERRIDE`
  - the candidate was admitted via `RESEARCH_BULL_HIGH_PERSISTENCE_OVERRIDE` on the current bar
  - normal sizing computed `size_base = 0.0`
  - `min_size_base > 0.0`
- When active, replace only the current-bar sizing base with `min_size_base` before existing multipliers are applied.
- Preserve current behavior exactly when `min_size_base` is absent or `0.0`.
- Do not alter confidence gates, regime thresholds, hysteresis logic, cooldown logic, or non-override sizing paths.

## Evidence basis for this slice

- On the canonical CLI backtest path, the override-reason bars are split into:
  - bars blocked before sizing (`EDGE_TOO_SMALL` / `HYST_WAIT`)
  - bars that reach sizing but remain `size = 0.0`
- For the sizing-reached bars, `size_base = 0.0` while observed multipliers remain positive, so the current blocker is the champion risk-map floor rather than execution-layer rejection.
- The first champion risk-map bucket size is `0.02`, which would yield hypothetical sizes around `0.0112` or `0.016` on the affected executable bars under current multipliers.

## Gates required

- `pre-commit run --all-files`
- focused pytest selectors for touched sizing/schema/runtime-semantic surfaces
- determinism replay selector
- feature cache invariance selector
- pipeline hash guard selector
- canonical parity proof comparing leaf absent vs explicit `min_size_base = 0.0`
- locked-window disabled-path replay/smoke confirming zero behavior drift when `min_size_base = 0.0`
- locked-window baseline-vs-flag comparison for the enabled sizing seam (research efficacy evidence only; not a no-drift proof)

## Stop Conditions

- Scope drift outside listed files
- Any behavior change when `min_size_base = 0.0`
- Need for broader risk-map redesign or champion mutation
- Determinism/hash regression
- Evidence shows the executable seam still fails before reaching realized-trade comparison

## Output required

- **Implementation Report**
- **PR evidence template**

## Evidence wording discipline

- Any enabled-path trade/result delta is research efficacy evidence only.
- No enabled-path outcome may be cited as default parity, determinism proof, or contract-preservation proof.
- The slice is valid only if disabled-path behavior remains identical to the current canonical path.
