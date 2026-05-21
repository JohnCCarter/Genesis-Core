# Cache schema-bump enforcement boundary packet

Date: 2026-05-18
Branch: `feature/risk-hardening-wave2`
Status: `packet-boundary-defined / docs-only / non-authorizing`

This document is a planning/decision artifact in `RESEARCH` and grants no implementation, runtime, backtest, determinism, cache, CI, readiness, paper/live, launch, or promotion authority. It must not be used as approval to begin source, test, script, workflow, or env/config behavior changes.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only, but it sits adjacent to backtest/determinism surfaces where wording drift could be mistaken for approval to add CI/runtime enforcement or to claim that an under-traced cache carrier already has a verified code fix
- **Required Path:** `Quick`
- **Lane:** `Concept` — why: this slice defines the next admissible packet types only; it does not introduce runtime or CI behavior
- **Objective:** separate the real tracked `#2` precompute-cache enforcement gap from the currently under-traced `#12` feature-cache claim, and define what must be proven before either line can reopen as implementation-bearing work
- **Candidate:** `cache schema-bump enforcement boundary / carrier-trace split`
- **Base SHA:** `3a0bca4c`
- **Skill Usage:** `ingen matchande skill identifierad`

### Scope

- **Scope IN:** one docs-only boundary packet; explicit current-state read of tracked precompute-cache versioning in `src/core/backtest/engine.py`; exact evidence selectors for the already-visible `#2` tests; explicit statement that the `#12` PyArrow feature-cache carrier is not yet concretely traced in current `src/**`; explicit stop/reopen rules for any future enforcement or carrier-trace slice
- **Scope OUT:** all edits under `src/**`, `tests/**`, `scripts/**`, `.github/workflows/**`, `config/**`, `results/**`, and `artifacts/**`; all `PRECOMPUTE_SCHEMA_VERSION` bumps; all new CI gates; all runtime assertions; all env/default changes; all claims that `#12` is already fixed in code; all claims that repo-visible schema-bump enforcement already exists beyond the current versioning/tests
- **Expected changed files:** `docs/decisions/governance/cache_schema_bump_enforcement_boundary_packet_2026-05-18.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- targeted docs validation for this file
- manual link/path audit for every file path and test selector named here
- manual wording audit that `#2` existing versioning is not overstated as full enforcement
- manual wording audit that `#12` remains explicitly under-traced rather than silently upgraded into a verified code defect
- manual wording audit that no source-change, CI-change, or behavior-change authority is implied

### Stop Conditions

- any wording that treats this packet as approval to add CI/runtime schema-bump enforcement
- any wording that claims `PRECOMPUTE_SCHEMA_VERSION` discipline is absent from the current repo
- any wording that claims the `#12` PyArrow feature-cache carrier has already been located in current `src/**`
- any wording that claims `#12` is fixed, stale, or implementation-ready without an exact tracked reader/writer and evidence path
- any wording that combines `#2` enforcement work and `#12` carrier-trace work into one implicitly approved future slice

## Purpose

This packet answers one narrow question only:

- after mapping `#2 / #12`, what is the next honest boundary for follow-up work without pretending that both items already share the same verified tracked carrier?

## Governing basis

### Observed current tracked state for `#2`

The current repo already contains a non-trivial precompute-cache versioning discipline in tracked code:

1. `src/core/backtest/engine.py` defines `PRECOMPUTE_SCHEMA_VERSION = 3` with an explicit bump-policy docstring stating when the on-disk precompute artifact meaning or shape has changed and when a bump is **not** required
2. `src/core/backtest/engine.py::_precompute_cache_key_material()` includes the schema version plus a deterministic spec digest in the cache key material
3. `src/core/backtest/engine.py::_build_precompute_cache_metadata(...)` and `src/core/backtest/engine.py::_validate_metadata_bearing_precompute_cache(...)` validate metadata-bearing cache payloads against current expected schema/material/candle-count state before reuse
4. the current repo also carries targeted tests that anchor this behavior:
   - `tests/backtest/test_precompute_cache_key_versioning.py::test_precompute_cache_key_changes_when_schema_version_changes`
   - `tests/backtest/test_backtest_engine.py::test_engine_precompute_cache_metadata_payload_loads_when_valid`
   - `tests/backtest/test_backtest_engine.py::test_engine_precompute_cache_metadata_payload_recomputes_on_dense_length_mismatch`
   - `tests/backtest/test_backtest_engine.py::test_engine_precompute_cache_metadata_payload_recomputes_on_material_mismatch`
   - `tests/backtest/test_backtest_engine.py::test_engine_precompute_cache_metadata_payload_recomputes_on_swing_pair_misalignment`
5. `docs/audit/BACKTEST_ENGINE_AUDIT.md` Fynd C already frames the remaining concern as a contract/policy seam: versioning exists, but repo-visible bump-enforcement and config-context isolation are not fully closed

### Inferred current gap for `#2`

The still-open `#2` gap is therefore **not** "the repo forgot to version precompute cache artifacts".

The remaining gap is narrower:

- the repo does not currently expose a CI/runtime enforcement point that proves `PRECOMPUTE_SCHEMA_VERSION` will be bumped whenever feature semantics change in a way that keeps the cache key otherwise plausible
- `GENESIS_PRECOMPUTE_CONFIG_HASH` remains optional, which means context isolation across different feature-config runs is available but not universally enforced by default

That is a **policy/gate question**, not proof that current precompute versioning is absent.

### Observed vs unverified state for `#12`

Observed in current repo-facing documentation/evidence surfaces:

- `CLAUDE.md` describes a file-backed feature-cache in PyArrow/columnar terms
- `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` names `#12` as a separate "PyArrow feature-cache `schema_version=1`" seam and explicitly frames it as an open bounded follow-up question rather than an already-opened implementation slice

Unverified in this slice:

- this review did **not** locate a concrete current `src/**` reader/writer or enforcement point for that exact `#12` carrier on the current tracked repo surface
- this slice therefore cannot honestly claim that `#12` has a ready code fix, or even that the described carrier is definitely current rather than partially historical, generated, or described at a higher architectural level than the currently traced code path

`#12` is therefore classified here as **under-traced**, not as fixed and not as implementation-approved.

## What this packet does and does not conclude

### Current standing conclusion

This packet concludes only the following:

- `#2` has a real, tracked code carrier today, but the remaining seam is repo-visible enforcement discipline rather than missing basic schema versioning
- `#12` has not yet been grounded to a concrete current tracked reader/writer in `src/**`, so it must not be handled as if it were already a ready code-fix target
- future work must split these two lines instead of treating them as one convenience bundle

### What this packet does not conclude

This packet does **not** conclude that:

- a new CI gate should be added now
- runtime should assert harder now
- `PRECOMPUTE_SCHEMA_VERSION` should be bumped now
- `GENESIS_PRECOMPUTE_CONFIG_HASH` should become mandatory now
- the `#12` carrier is definitely stale
- the `#12` carrier is definitely current
- either `#2` or `#12` has been implementation-approved by this packet

## Boundary decision

### Future `#2` reopen shape

If work continues on `#2`, the next admissible step may only be:

- a **separate bounded pre-code packet** for one exact schema-bump enforcement candidate on the precompute-cache surface

That future packet must define at minimum:

- the exact enforcement locus (`CI`, targeted selector policy, runtime assertion, or another single named mechanism)
- the exact feature-schema or cache-contract changes that are intended to trigger enforcement
- what must remain unchanged on the current default path
- whether `GENESIS_PRECOMPUTE_CONFIG_HASH` remains optional, becomes required, or stays out of scope for the first slice
- the smallest focused gates required for that candidate

### Future `#12` reopen shape

If work continues on `#12`, the next admissible step may only be:

- a **separate carrier-trace / evidence packet** that first identifies the exact current tracked reader/writer, artifact path, and enforcement point for the named PyArrow feature-cache seam

That future packet must define at minimum:

- the exact current file path(s) in tracked code that read/write the carrier
- where the claimed `schema_version=1` currently lives
- whether the carrier is current, historical, generated elsewhere, or stale on present master/feature state
- what blast-radius the carrier actually has across backtest / optimizer / paper paths
- whether a later implementation slice is even justified once the carrier is grounded

## Hard stop and reopen rule

From this boundary onward, any future work must stop and reopen as a separate packet if it needs to:

- edit `src/core/backtest/engine.py`
- edit any test that defines current precompute-cache behavior
- add or modify CI/workflow enforcement
- add runtime assertions around cache schema/version discipline
- change defaults or env/config interpretation for cache behavior
- claim that the `#12` PyArrow feature-cache seam is implementation-ready without first grounding its exact current tracked carrier

No future slice may smuggle code, tests, or CI enforcement under the cover of this docs-only classification packet.

## Bottom line

The current repo already shows real tracked precompute-cache versioning for `#2`; the unresolved part is whether that discipline should later gain a repo-visible enforcement mechanism. `#12`, by contrast, is not yet grounded to a concrete current tracked code carrier in this slice. The next honest move is therefore **split follow-up**: one future packet for a narrowly defined `#2` enforcement candidate, and a separate carrier-trace packet before anyone claims a `#12` code fix.
