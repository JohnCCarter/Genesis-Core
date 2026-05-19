# Cache schema-bump touch-triggered selector policy packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `selector-policy-proposed / docs-only / non-authorizing`

This document is a planning / decision artifact in `RESEARCH` and grants no implementation, runtime, test-policy activation, CI/workflow, cache, determinism, readiness, paper/live, launch, or promotion authority. It must not be used as approval to begin source, test, script, workflow, or env/config behavior changes.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only, but wording drift could be mistaken for adopting a new backtest/cache enforcement policy before any governed implementation exists
- **Required Path:** `Quick`
- **Lane:** `Concept` — why: this slice selects a single proposed first enforcement locus only; it does not implement a gate, workflow, or runtime behavior
- **Objective:** choose one exact first enforcement locus for `#2` on the tracked precompute-cache surface without reopening `#12` or implying runtime/CI adoption
- **Candidate line:** `#2 precompute-cache schema-bump enforcement`
- **Proposed first locus:** `precompute-cache schema-bump enforcement via touch-triggered pytest selector policy`
- **Base SHA:** `7e8c0182`
- **Skill Usage:** `ingen matchande skill identifierad`

### Scope

- **Scope IN:** one docs-only pre-code packet; explicit observed/inferred/unverified framing; exact current code/test anchors for the tracked precompute-cache contract surface; explicit proposed selector bundle for the first `#2` locus; explicit statement that `GENESIS_PRECOMPUTE_CONFIG_HASH` remains current-state context only and that `#12` remains out of scope and under-traced; explicit comparison of why broader CI-gate and runtime-assertion alternatives are not chosen first here
- **Scope OUT:** all edits under `src/**`, `tests/**`, `.github/workflows/**`, `scripts/**`, `config/**`, `results/**`, and `artifacts/**`; all `PRECOMPUTE_SCHEMA_VERSION` bumps; all new CI/workflow gates; all runtime assertions; all env/default changes; all changes to `GENESIS_PRECOMPUTE_CONFIG_HASH` semantics; all claims that the proposed selector policy already exists or is active; all claims that `#12` is current, fixed, or implementation-ready
- **Expected changed files:** `docs/decisions/governance/cache_schema_bump_touch_triggered_selector_policy_packet_2026-05-19.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- targeted docs validation for this file
- manual path/selector audit for every named file path, symbol, test selector, and workflow anchor
- manual wording audit that the selector-policy locus remains explicitly `föreslagen` rather than adopted
- manual wording audit that CI gate and runtime assertion remain later alternatives rather than globally rejected options
- manual wording audit that `GENESIS_PRECOMPUTE_CONFIG_HASH` and `#12` remain explicitly out of scope for the first reopen path
- manual wording audit that no source-change, test-change, workflow-change, or behavior-change authority is implied

### Stop Conditions

- any wording that treats the selector policy as already implemented or already required by CI
- any wording that upgrades current global `pytest -q` into a `#2`-specific enforcement gate without a separate implementation slice
- any wording that treats CI gate or runtime assertion as permanently rejected rather than simply not chosen first here
- any wording that widens the trigger from the current precompute-cache contract surface into a repo-wide feature-change detector
- any wording that turns `GENESIS_PRECOMPUTE_CONFIG_HASH` into a first-slice requirement
- any wording that reopens `#12` or claims its carrier is current, fixed, or implementation-ready

## Purpose

This packet answers one narrow question only:

- after the `#2 / #12` boundary split, what is the smallest honest first enforcement locus for the tracked precompute-cache schema-bump seam?

## Governing basis

This packet is downstream of the following current-state surfaces:

- `docs/decisions/governance/cache_schema_bump_enforcement_boundary_packet_2026-05-18.md`
- `docs/audit/BACKTEST_ENGINE_AUDIT.md`
- `.github/workflows/ci.yml`
- `src/core/backtest/engine.py`
- `tests/backtest/test_precompute_cache_key_versioning.py`
- `tests/backtest/test_backtest_engine.py`

### Observed

1. `src/core/backtest/engine.py` currently defines a tracked precompute-cache contract surface through `PRECOMPUTE_SCHEMA_VERSION`, `_precompute_cache_key_material()`, `_build_precompute_cache_metadata(...)`, `_validate_metadata_bearing_precompute_cache(...)`, `_precompute_cache_key(...)`, and the `prepare_precomputed_features(...)` call-site wiring inside `load_data()`.
2. `tests/backtest/test_precompute_cache_key_versioning.py::test_precompute_cache_key_changes_when_schema_version_changes` already proves that changing `PRECOMPUTE_SCHEMA_VERSION` changes the on-disk precompute cache key.
3. `tests/backtest/test_backtest_engine.py` already carries metadata-bearing cache tests that prove valid payloads load and that invalid cache material is recomputed rather than silently reused, including:
   - `test_engine_precompute_cache_metadata_payload_loads_when_valid`
   - `test_engine_precompute_cache_metadata_payload_recomputes_on_dense_length_mismatch`
   - `test_engine_precompute_cache_metadata_payload_recomputes_on_material_mismatch`
   - `test_engine_precompute_cache_metadata_payload_recomputes_on_swing_pair_misalignment`
4. `.github/workflows/ci.yml` currently runs a global `pytest -q` step.
5. The current docs / `.github` scan in this slice did not locate a repo-visible `#2`-specific touch-triggered selector policy for the tracked precompute-cache contract surface.
6. `docs/audit/BACKTEST_ENGINE_AUDIT.md` Fynd C frames the remaining concern as enforcement discipline and config-context isolation, not as absence of basic precompute-cache versioning.
7. `docs/decisions/governance/cache_schema_bump_enforcement_boundary_packet_2026-05-18.md` requires the next `#2` move to choose one exact enforcement locus only and keep `#12` separate.

### Inferred

- Because tracked versioning and recompute anchors already exist, the smallest honest first `#2` enforcement candidate is not new runtime logic but a narrow policy that says when the existing cache-contract selector bundle must be run.
- A touch-triggered pytest selector policy is smaller than a new CI/workflow gate for the first slice because it reuses existing tests and avoids choosing workflow trigger semantics before the narrow trigger boundary is settled.
- A touch-triggered pytest selector policy is smaller than a runtime assertion for the first slice because it stays out of `src/core/backtest/engine.py` runtime behavior and avoids changing fallback/cache behavior on a high-sensitivity backtest surface.
- The first trigger boundary should remain narrow: it should only cover edits to the current tracked precompute-cache contract surface in `src/core/backtest/engine.py`, not generalized feature/config changes across the repository.
- `GENESIS_PRECOMPUTE_CONFIG_HASH` is relevant current-state context, but making it mandatory, default-on, or selector-bearing would widen this first packet from schema-bump enforcement into config-context-isolation policy.

### Unverified

- the exact later carrier that would operationalize the proposed selector policy if a follow-up slice implements it
- whether a later governed follow-up should prefer CI/workflow enforcement or another non-runtime carrier after this first locus selection is recorded
- whether `GENESIS_PRECOMPUTE_CONFIG_HASH` should later be paired with the same selector bundle once its separate policy question is reopened
- any broader mechanism that would detect all feature-semantics changes beyond the currently anchored precompute-cache contract tests

## Proposed first-locus selection

### Current standing conclusion

This packet proposes only one first `#2` enforcement locus:

- `precompute-cache schema-bump enforcement via touch-triggered pytest selector policy`

More specifically, the proposed first trigger boundary is:

- edits to the tracked precompute-cache contract surface in `src/core/backtest/engine.py`, limited to:
  - `PRECOMPUTE_SCHEMA_VERSION`
  - `_precompute_cache_key_material()`
  - `_build_precompute_cache_metadata(...)`
  - `_validate_metadata_bearing_precompute_cache(...)`
  - `_precompute_cache_key(...)`
  - the `prepare_precomputed_features(...)` cache-contract wiring inside `load_data()`

The proposed first selector bundle is the existing cache-contract test set anchored to:

- `tests/backtest/test_precompute_cache_key_versioning.py::test_precompute_cache_key_changes_when_schema_version_changes`
- `tests/backtest/test_backtest_engine.py::test_engine_precompute_cache_metadata_payload_loads_when_valid`
- `tests/backtest/test_backtest_engine.py::test_engine_precompute_cache_metadata_payload_recomputes_on_dense_length_mismatch`
- `tests/backtest/test_backtest_engine.py::test_engine_precompute_cache_metadata_payload_recomputes_on_material_mismatch`
- `tests/backtest/test_backtest_engine.py::test_engine_precompute_cache_metadata_payload_recomputes_on_swing_pair_misalignment`

This packet does **not** conclude that the selector policy is already implemented. It records the first proposed locus only.

### Why the other loci are not chosen first here

- **Broad CI/workflow gate:** not chosen first because it would force workflow-carrier semantics before the narrow trigger boundary is settled and would create premature “already enforced” optics on a still-docs-only line.
- **Runtime assertion:** not chosen first because it would enter `src/core/backtest/engine.py` runtime behavior on a high-sensitivity backtest surface before the smaller policy/gate question is narrowed.
- **Config-hash enforcement:** not chosen first because it widens the slice from schema-bump enforcement into config-context isolation and default/env semantics.

These alternatives remain possible later governed follow-up paths. They are not rejected globally by this packet.

### What changed

This packet adds one clarification only:

- the repository now has an explicit docs-only record that the first proposed `#2` enforcement locus is a touch-triggered pytest selector policy anchored to the existing precompute-cache contract tests

### What did not change

This packet does **not** change any of the following:

- runtime behavior in `src/core/backtest/engine.py`
- current tests or their outcomes
- `.github/workflows/ci.yml`
- the current global `pytest -q` CI step
- `PRECOMPUTE_SCHEMA_VERSION`
- `GENESIS_PRECOMPUTE_CONFIG_HASH` semantics
- the `#12` carrier-trace status
- approval for any implementation slice

## Reopen rule

If this line is reopened later, the next admissible move under this packet must still be a **separate bounded follow-up** that keeps the chosen locus narrow.

That later follow-up must not silently widen into:

- a CI/workflow implementation without saying so
- a runtime assertion on the backtest surface without saying so
- a `GENESIS_PRECOMPUTE_CONFIG_HASH` policy change
- a bundled `#2 + #12` packet
- a repo-wide feature-diff detector claim

This packet does not authorize any of those moves by itself.

## Bottom line

The current repo already has real tracked precompute-cache versioning and metadata/recompute anchors for `#2`. The smallest honest first enforcement candidate is therefore a **proposed touch-triggered pytest selector policy** on the existing cache-contract tests, not a new runtime assertion or a broader CI gate. `GENESIS_PRECOMPUTE_CONFIG_HASH` and `#12` remain separate lines for later governed work.
