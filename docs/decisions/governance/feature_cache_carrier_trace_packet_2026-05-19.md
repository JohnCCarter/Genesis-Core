# Feature-cache carrier-trace packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `decision-recorded / docs-only / non-authorizing`

This document records the smallest honest current-branch grounding pass for parked item `#12`. It grants no implementation approval, no cache-policy change, no runtime/backtest/optimizer/paper authority, and no claim that the named feature-cache seam already has a ready code fix.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only, but it sits adjacent to determinism/cache wording that could easily be over-read as approval for code, CI, or schema-enforcement work
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice grounds a previously under-traced cache claim against current tracked surfaces only; it does not reopen implementation work
- **Skill usage:** `none required` — bounded carrier-trace slice; no repo-local skill matched this change
- **Objective:** identify what current tracked carrier, if any, supports the named `#12` “file-backed feature-cache / PyArrow / schema_version=1” seam, and record whether that seam is current, partially current, historical, generated elsewhere, or stale on the present branch state
- **Base SHA:** `d2ee262fcb0ecd978b29257b0903de51da7cbba9`
- **Related artifacts:** `CLAUDE.md`, `src/core/utils/data_loader.py`, `scripts/train/train_model.py`, `src/core/strategy/features_asof.py`, `src/core/backtest/engine.py`, `src/core/backtest/engine_precompute.py`, `src/core/ml/label_cache.py`, `docs/decisions/governance/cache_schema_bump_enforcement_boundary_packet_2026-05-18.md`

### Scope

- **Scope IN:** this packet only; explicit current-state classification of the named `#12` seam; exact tracked reader/writer findings; explicit separation between current in-memory feature cache, current backtest precompute cache, and training-side on-disk feature artifacts
- **Scope OUT:** all edits under `src/**`, `tests/**`, `scripts/**`, `config/**`, `results/**`, and `artifacts/**`; all `schema_version` or cache-format changes; all CI/runtime enforcement; all attempts to treat `#12` as implementation-approved; all edits to `CLAUDE.md` or other broader architectural docs in the same slice
- **Expected changed files:** `docs/decisions/governance/feature_cache_carrier_trace_packet_2026-05-19.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- targeted docs validation for this packet
- manual path audit for every tracked file named here
- manual wording audit that the slice does not silently upgrade `#12` into a ready code fix
- manual wording audit that current precompute-cache and current in-memory feature-cache surfaces are not conflated with the named on-disk feature-artifact seam

## Purpose

This packet answers one narrow question only:

- what current tracked carrier, if any, actually supports parked item `#12` on `feature/risk-hardening-wave2`?

## What changed in this slice

- one new carrier-trace packet records the current tracked reader/writer evidence for `#12`
- the packet separates three similarly named but distinct surfaces: in-memory feature cache, on-disk precompute cache, and on-disk feature artifacts used in the training path

## What did not change

- no cache behavior changed
- no schema/enforcement logic changed
- no existing architecture/governance docs were rewritten in this slice
- no runtime/backtest/optimizer/paper behavior changed

## Governing basis

### Observed

1. `CLAUDE.md` still describes a file-backed **feature-cache** in PyArrow/columnar terms with `schema_version=1`.
2. `src/core/strategy/features_asof.py` currently implements a **runtime in-memory** feature-result cache via `_feature_cache: OrderedDict[...]`, `_compute_feature_cache_key(...)`, `_feature_cache_lookup(...)`, and `_feature_cache_store(...)`.
3. `src/core/backtest/engine.py` plus `src/core/backtest/engine_precompute.py` currently implement a distinct **on-disk precompute cache** stored as compressed `.npz`, keyed by `PRECOMPUTE_SCHEMA_VERSION = 3` and metadata-bearing cache material.
4. `src/core/utils/data_loader.py::load_features(...)` currently reads on-disk feature artifacts from:
   - `data/curated/v1/features`
   - `data/archive/features`
   - `data/features`
   using `.feather` first and `.parquet` second.
5. `scripts/train/train_model.py::load_features_and_prices(...)` is the current tracked consumer found that calls `load_features(...)`.
6. The current tracked scan did **not** locate a corresponding writer or schema-owner for those feature artifacts in present `src/**` or `scripts/**`.
7. `src/core/ml/label_cache.py` is a separate parquet-backed cache under `cache/labels` and therefore is **not** the same carrier as the feature-artifact seam named by `#12`.
8. The current tracked scan did **not** locate a present reader for `data/**/features` under current backtest, optimizer execution, or paper/live surfaces.

### Inferred

- The current repo contains at least **three different cache/artifact concepts** that can be confused if read too quickly:
  - runtime in-memory feature cache
  - backtest precompute cache on disk (`.npz`)
  - training-side on-disk feature artifacts (`.feather` / `.parquet`)
- The named `#12` seam is therefore **not** honestly grounded as “the same thing” as the runtime in-memory cache or the backtest precompute cache.
- The `#12` claim is also **not fully stale**, because there is a current tracked reader for on-disk feature artifacts in the training path.
- But the stronger wording `file-backed feature-cache / PyArrow / schema_version=1` is still **under-grounded** on the current tracked repo surface because no current tracked writer or schema-owner for that exact contract was found.

### Unverified in this packet

- where the current producer for `data/**/features` artifacts lives, if it is still active
- whether the producer exists outside the current tracked repo surface
- whether `schema_version=1` is still a live contract anywhere other than the architecture claim in `CLAUDE.md`
- whether the training-side feature artifacts should still be described as a “cache” rather than as generated feature inputs or snapshots

## Current classification

### What is current and grounded

The following surfaces are grounded on the current tracked branch state:

- **runtime in-memory feature cache** in `src/core/strategy/features_asof.py`
- **on-disk precompute cache** in `src/core/backtest/engine.py` / `engine_precompute.py`
- **training-side on-disk feature-artifact reader** in `src/core/utils/data_loader.py`, currently consumed by `scripts/train/train_model.py`

### What is not yet grounded

The following specific `#12` contract elements are **not** grounded on the current tracked repo surface:

- a current tracked writer for the on-disk feature artifacts
- a current tracked schema-owner for those feature artifacts
- a current tracked proof that the artifacts are governed by `schema_version=1`
- a current tracked proof that the seam is active across backtest / optimizer / paper paths

## Blast-radius read

On the current tracked branch state, the honest blast-radius reading is:

- **Backtest:** no current proof that `data/**/features` artifacts are consumed; current cache-bearing backtest surface is the separate `.npz` precompute cache
- **Optimizer execution path:** no current proof that optimizer trial execution reads `data/**/features` artifacts as an active runtime cache carrier
- **Paper/live:** no current proof of a consumer seam
- **Training/ML:** one current tracked reader exists through `load_features(...)` → `scripts/train/train_model.py`

## Boundary decision

### Current standing conclusion

For `feature/risk-hardening-wave2`, the smallest honest `#12` reading is:

- `#12` is **not stale enough to delete outright**
- `#12` is **not grounded enough to treat as a ready code fix**
- the only currently grounded part is a **training-side on-disk feature-artifact reader**
- the stronger `schema_version=1` / file-backed feature-cache contract remains under-traced on the present tracked repo surface

This packet therefore keeps `#12` in the **under-grounded / evidence-first** bucket.

### Non-goals

This slice does **not**:

- approve any implementation-bearing `#12` follow-up
- approve edits to `CLAUDE.md`
- claim that the feature-artifact seam is fully current across runtime paths
- claim that the seam is definitely historical or definitely external

## Next admissible move

If work continues on `#12`, the next honest move may only be one of these:

1. a **separate writer-trace / schema-owner packet** that identifies the current tracked producer and any live schema-version owner for `data/**/features`, or
2. a **separate docs-truthfulness packet** that narrows or corrects higher-level architecture wording if no such current tracked producer/schema-owner can be grounded

No implementation-bearing cache-enforcement or schema-bump slice is justified from this packet alone.

## Bottom line

`#12` now has a more honest shape: the present repo does show a current tracked reader for on-disk feature artifacts, but it does **not** yet ground the stronger claim that there is a current tracked file-backed feature-cache contract with `schema_version=1`. So `#12` is no longer just vague — it is now **partially grounded, but still under-traced and not implementation-ready**.
