# Precompute-cache config-subset identity pre-code packet

Date: 2026-05-21
Branch: `feature/risk-hardening-wave3`
Status: `pre-code-defined / docs-only / non-authorizing`

This packet defines the exact bounded `#2` candidate left open by the 2026-05-21 follow-up selection packet. It grants no runtime, backtest, test, script, workflow, env/config, determinism, readiness, paper/live, launch, or promotion authority. It must not be read as approval to begin `src/**`, `tests/**`, or CI/workflow changes.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/*`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only, but it narrows a live cache-contract question close to `src/core/backtest/**`, where wording drift could be mistaken for approval to hash broad runtime config or change cache/env semantics immediately
- **Required Path:** `Quick`
- **Lane:** `Concept` — why: this slice defines the next bounded implementation candidate only; it does not change runtime or test behavior
- **Objective:** define the exact `#2` config-subset identity candidate, exact minimal code locus, and focused proof expectations for a later implementation-bearing slice
- **Candidate line:** `#2 producer-adjacent precompute-spec identity`
- **Base SHA:** `49a8070f`
- **Skill Usage:** `none required`

### Scope

- **Scope IN:** this packet; one small live-note refinement in `handoff.md`; explicit observed/inferred/unverified framing; exact current producer-vs-consumer reading of the on-disk precompute cache surface; explicit exclusions for over-broad config hashing
- **Scope OUT:** all edits under `src/**`, `tests/**`, `scripts/**`, `.github/**`, `config/**`, `results/**`, and `artifacts/**`; all changes to `GENESIS_PRECOMPUTE_CONFIG_HASH` semantics; all cache-key changes; all `PRECOMPUTE_SCHEMA_VERSION` changes; all `#12` writer/schema-owner work; all claims that the chosen candidate is already implemented
- **Expected changed files:** `docs/decisions/governance/precompute_cache_config_subset_identity_precode_packet_2026-05-21.md`, `handoff.md`
- **Max files touched:** `2`

### Gates required

For this docs-only slice:

- targeted docs validation for the changed markdown files
- manual path audit for every named code/test path
- manual wording audit that the candidate is a next-step only, not an approved runtime change
- manual wording audit that broad effective-config fingerprinting is explicitly out of scope here
- manual wording audit that `#12` remains out of scope
- self-review for hidden behavior impact

### Stop Conditions

- any wording that claims the persisted `.npz` producer currently depends on the full effective strategy config
- any wording that treats `GENESIS_PRECOMPUTE_CONFIG_HASH` as already mandatory or already superseded
- any wording that claims HTF mapping columns are persisted in the on-disk precompute cache
- any wording that routes the first implementation candidate through `_config_fingerprint(...)` or broad config hashing without proof
- any wording that bundles `#12` back into the same packet

## Purpose

This packet answers one narrow question only:

- what exact config-subset candidate should the next implementation-bearing `#2` slice evaluate, truthfully and minimally?

## What changed in this slice

- one new packet grounds the exact `#2` candidate after the follow-up selection packet
- `handoff.md` gets a small live-note refinement so the next agent does not reopen “whole strategy config hash” as the default reading

## What did not change

- no runtime/backtest/cache behavior changed
- no tests, scripts, workflows, or env/config semantics changed
- no cache-key logic changed
- no selector-policy validator logic changed
- no `PRECOMPUTE_SCHEMA_VERSION` behavior changed
- no `#12` writer/schema-owner grounding changed

## Governing basis

### Observed

1. `src/core/backtest/engine.py::_precompute_cache_key_material()` already hashes a hardcoded producer-side spec containing:
   - indicator periods for ATR, EMA, RSI, Bollinger, and ADX
   - a partial Fibonacci swing policy (`atr_depth`, `max_swings`, `min_swings`, `precompute_swing_history`, `precompute_max_lookback`)
2. `src/core/backtest/engine_precompute.py::prepare_precomputed_features(...)` persists only these on-disk payload families in the `.npz` cache:
   - `atr_14`, `atr_50`
   - `ema_20`, `ema_50`
   - `rsi_14`
   - `bb_position_20_2`
   - `adx_14`
   - `fib_high_idx`, `fib_low_idx`, `fib_high_px`, `fib_low_px`
3. `prepare_precomputed_features(...)` does **not** persist HTF mapping columns. It computes HTF Fibonacci mapping after cache load/build and appends those columns to the in-memory `pre` dict for the current run only.
4. The same producer path currently instantiates `FibonacciConfig(atr_depth=3.0, max_swings=8, min_swings=1)` and then expands that into a full-history swing-detection config by copying:
   - `swing_threshold_multiple`
   - `swing_threshold_min`
   - `swing_threshold_step`
   - `max_lookback` (expanded to full-history policy via `max(fib_cfg.max_lookback, len(closes_all))`)
5. In the current repo state, `src/core/indicators/fibonacci.py::FibonacciConfig` defaults those copied swing-threshold fields to:
   - `swing_threshold_multiple = 1.1`
   - `swing_threshold_min = 0.45`
   - `swing_threshold_step = 0.2`
6. `_precompute_cache_key_material()` currently records the indicator spec and the high-level full-history swing policy, but it does **not** explicitly encode the swing-threshold trio copied from `FibonacciConfig`.
7. `src/core/strategy/features_asof_parts/extraction_context_utils.py` reads consumer config such as `thresholds.signal_adaptation.atr_period`, but that consumer-side knob changes fast-path usage/fallback behavior rather than the persisted `.npz` producer contract itself.
8. `src/core/backtest/engine.py::_precompute_cache_key(...)` still treats `GENESIS_PRECOMPUTE_CONFIG_HASH` as an optional `_cfg...` namespace segment only; unset/empty preserves the legacy key shape.
9. `tests/backtest/test_precompute_cache_key.py` currently proves the optional-env behavior above, including no raw env leakage into the cache path.

### Inferred

- The remaining truthful `#2` identity question is **not** “hash the whole effective strategy config.” The persisted on-disk precompute producer does not currently consume most runtime strategy-config surfaces.
- Hashing the whole effective config would therefore over-scope cache identity, over-isolate caches, and misstate the actual producer seam.
- The honest first candidate is a **producer-adjacent persisted precompute spec subset** only.
- That candidate should be defined once and reused by both the cache-key material path and the producer path, so future drift in producer-owned swing settings does not depend entirely on manual schema-bump discipline.
- Consumer-only config surfaces should stay out of the first candidate unless a later bounded slice proves they alter the persisted `.npz` artifact rather than only runtime consumption/fallback.

### Unverified in this packet

- whether a later implementation should express the producer subset via explicit literals, a shared helper, or a tiny canonical spec object
- whether `GENESIS_PRECOMPUTE_CONFIG_HASH` should remain purely optional override-only after the producer-subset work lands
- whether any later repo state will introduce true runtime-config-driven precompute producer knobs that deserve inclusion
- whether `PRECOMPUTE_SCHEMA_VERSION` should continue as the manual lever for producer changes not captured by the subset digest

## Boundary decision

### Exact `#2` candidate

If Wave 3 continues with an implementation-bearing `#2` slice, the exact config-subset identity candidate should be:

- the **producer-owned persisted precompute spec**, not the whole effective strategy config

That subset currently means:

1. **Persisted indicator spec**
   - `atr_periods = [14, 50]`
   - `ema_periods = [20, 50]`
   - `rsi_period = 14`
   - `bb.period = 20`
   - `bb.std_dev = 2.0`
   - `adx_period = 14`
2. **Persisted LTF swing-detection spec**
   - `atr_depth = 3.0`
   - `min_swings = 1`
   - `max_swings_policy = full_history`
   - `max_lookback_policy = full_history`
   - `swing_threshold_multiple = 1.1` (current observed default)
   - `swing_threshold_min = 0.45` (current observed default)
   - `swing_threshold_step = 0.2` (current observed default)

### Explicit exclusions from the first candidate

The first candidate should **not** include:

- the whole effective `configs` dict
- `_config_fingerprint(...)`
- consumer-only knobs such as `thresholds.signal_adaptation.atr_period`
- `htf_exit_config`, `htf_fib`, `ltf_fib`, or broader strategy gating config
- `features.percentiles`, `features.versions`, or unrelated runtime metadata
- HTF mapping levels/weights, because those are recomputed per run and not persisted in the `.npz`
- the raw value of `GENESIS_PRECOMPUTE_CONFIG_HASH`

## Exact minimal code locus

If a later implementation slice is opened, the preferred minimal locus should be:

1. **Primary locus:** `src/core/backtest/engine.py::_precompute_cache_key_material()`
2. **Paired producer locus:** `src/core/backtest/engine_precompute.py::prepare_precomputed_features(...)`

Preferred shape:

- introduce one small producer-owned helper or canonical spec owner for the persisted precompute subset
- have `_precompute_cache_key_material()` canonicalize/hash that subset
- have `prepare_precomputed_features(...)` consume the same subset owner for the producer-side swing/indicator settings it already uses

The first implementation slice should **not** start by threading full runtime config into `_precompute_cache_key(...)` and should **not** route through `_config_fingerprint(...)`.

## Focused proof expectations for the later slice

If the later implementation slice is opened, the focused proof bundle should center on:

1. `tests/backtest/test_precompute_cache_key.py`
   - preserve the current unset/empty `GENESIS_PRECOMPUTE_CONFIG_HASH` legacy-shape proof
   - preserve the current non-empty `_cfg...` namespace proof
   - add a focused proof that changing the producer-owned swing-threshold subset changes the cache-key material deterministically
2. `tests/backtest/test_precompute_cache_key_versioning.py`
   - preserve current schema-version key-change coverage
3. `tests/utils/test_validate_precompute_cache_selector_policy.py`
   - update the selector-policy watcher proof if a new producer-spec helper becomes a tracked symbol
4. only if helper extraction changes producer control flow materially: add one focused `tests/backtest/test_backtest_engine.py` regression covering cache-hit/cache-miss parity for the affected path

### Default-behavior constraints for the later slice

Unless explicitly reopened in a future governance pass, the later implementation should preserve:

- optional `GENESIS_PRECOMPUTE_CONFIG_HASH` behavior
- no raw env/config leakage in cache paths
- no broad effective-config fingerprinting
- no `#12` coupling
- no change to cache read/write enablement semantics

## Bottom line

The next truthful `#2` candidate is **not** “hash all strategy config.” It is the narrower producer-adjacent persisted precompute spec: the actual indicator periods and LTF swing-detection knobs that shape the `.npz` payload. If Wave 3 continues into code, the next admissible move should be a fresh governance pass limited to that small producer-owned locus and its focused tests.
