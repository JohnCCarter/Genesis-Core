# Genesis-Core — runtime surface classification

Date: 2026-05-27
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base runtime inventory: `docs/analysis/system/genesis_runtime_truth_inventory_2026-05-27.md`
Base SHA anchor: `f0f1d4b4`
Status: `completed / docs+artifact classification / observational-dispositional only`

## Purpose

This bounded slice classifies the branch-current runtime-adjacent surfaces identified in the runtime truth inventory.

The question here is narrower than the inventory question:

> for the currently observed runtime-adjacent surfaces, what should be treated as keep-now runtime, keep-as-support, keep-but-off, retained legacy compatibility, maybe-later archive territory, or still-needs-verification?

This is a disposition slice only.
It does **not** authorize cleanup, archive moves, deletion, V2 extraction, or runtime changes.

## Mode proof

This work remains `RESEARCH` because the branch is `feature/*` and this slice is docs+artifact classification only.
That allows a small observational/dispositional note built from current repo evidence.
It does **not** allow changing runtime authority, champion surfaces, defaults, or strict-only behavior.
If this slice were to enter runtime-default authority changes, champion file edits, or config semantics changes, it would need to stop and re-evaluate under stricter governance.

## Scope

### Scope IN

- classify the already-observed runtime surfaces from the runtime truth inventory
- separate keep-now runtime, support, optional-off, compatibility, and unverified buckets
- recommend one smallest admissible cleanup pilot
- emit one machine-readable classification artifact

### Scope OUT

- code changes
- archive execution
- file relocation
- V2 repo creation
- deletion proposals framed as already approved
- changes to `config/runtime.json`, champions, or runtime authority logic

## Evidence inputs

Primary basis:

- `docs/analysis/system/genesis_runtime_truth_inventory_2026-05-27.md`
- `results/research/runtime_truth_inventory/genesis_runtime_truth_inventory_2026-05-27.json`

Focused classification evidence:

- `src/core/strategy/features.py`
- `src/core/config/validator.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/regime.py`
- `src/core/indicators/vectorized.py`
- `docs/audits/DEAD_GHOST_ZOMBIE.md`
- `docs/system/GENESIS_TOPOLOGY_WORK_QUEUE.md`

## Emitted artifact

- `results/research/runtime_truth_inventory/genesis_runtime_surface_classification_2026-05-27.json`

## Observed

### 1. The core runtime spine remains a clear keep-now bucket

The prior inventory already established one dominant active runtime spine.
Nothing in the current classification pass weakens that read.

`keep_now_runtime` remains the correct disposition for:

- `config/runtime.json` via `ConfigAuthority`
- `scripts/run/run_backtest.py`
- `src/core/pipeline.py`
- `src/core/backtest/engine.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/features_asof.py`
- `src/core/strategy/model_registry.py`
- `src/core/strategy/champion_loader.py`
- `src/core/strategy/decision.py`

These are not archive or cleanup candidates in this slice.
They are the branch-current runtime truth core.

### 2. Some surfaces are active support or mode-gated support, not dead weight

`src/core/strategy/regime.py` should **not** be treated as immediate dead-code or archive material in this slice.

Observed reasons:

- `evaluate.py` keeps a local compatibility wrapper that imports `detect_regime_from_candles` from `core.strategy.regime`
- the shadow-observer path is still present for observability/test parity
- the authoritative regime path is config-gated and can still reference this surface when authority mode selects the regime-module path

So the right disposition here is:

- `keep_runtime_support_mode_gated`

That means “not current primary authority on the observed runtime snapshot” is **not** the same thing as “safe archive/delete candidate.”

### 3. Some surfaces are explicitly retained legacy compatibility, and the repo already says so out loud

Two surfaces are unusually clear:

- `src/core/strategy/features.py`
- `src/core/config/validator.py`

Observed text support:

- `features.py` says it is a `Legacy compatibility shim` and that internal runtime code should import `core.strategy.features_asof` instead
- `validator.py` says it is `intentionally legacy/test-only` and must not be treated as runtime-config authority
- `evaluate.py` imports `extract_features_backtest` / `extract_features_live` directly and explicitly says deprecated wrappers should be avoided in core runtime code
- `docs/audits/DEAD_GHOST_ZOMBIE.md` already classifies these surfaces conservatively as compatibility / likely dead / test-only, not as active runtime SSOT

So the correct disposition is:

- `keep_legacy_compatibility`

Not:

- `keep_active_runtime`
- `archive_now`
- `delete_now`

These files still serve compatibility/test/documented residue roles, even though they are not branch-current runtime SSOT.

### 4. Optional-but-off surfaces should be retained as optional-off, not mislabeled as active

The runtime inventory showed that several schema-declared or config-declared surfaces are currently null or disabled, including:

- `features`
- `htf_fib`
- `ltf_fib`
- research overrides currently disabled in the active runtime snapshot

The right disposition for these is:

- `keep_optional_off`

This matters because the current confusion in the repo often comes from collapsing three different states into one:

- exists in schema
- exists in code
- active on current runtime snapshot

This slice keeps those states separate.

### 5. MACD/SMA helper territory is still a verification bucket, not an archive bucket

This slice again observed helper-level presence for:

- `MACD`
- generic SMA helpers
- volume-SMA-adjacent helper logic

But this evidence remains weaker than the evidence for the core runtime and compatibility surfaces.

The right disposition remains:

- `needs_verification`

That is stronger than calling them active runtime, but more conservative than calling them archive-ready.

### 6. Current archive guidance does not support moving runtime-adjacent surfaces yet

`docs/system/GENESIS_TOPOLOGY_WORK_QUEUE.md` explicitly separates:

- docs analysis/routing work
- archive-candidate work
- red-bucket config/runtime-adjacent classification work

It also says archive moves require reference and provenance checks.

So this slice cannot honestly mark any runtime-adjacent code surface as:

- `move_now`
- `archive_now`

The repo already has an archive workflow, but this classification slice is **not** that workflow.

## Inferred

### 1. The safest actionable bucket map is keep-heavy, not move-heavy

The current branch truth does **not** support a large “move/archive/delete” posture.
It supports a clearer separation posture:

- keep the runtime spine
- keep support surfaces that remain mode-gated or observability-relevant
- keep optional-off surfaces clearly labeled as off
- keep compatibility surfaces demoted from SSOT status
- leave weakly evidenced helper territory in verification

So the first win is **containment and labeling**, not aggressive cleanup.

### 2. The best cleanup pilot is legacy containment, not archive execution

The smallest admissible cleanup pilot after this slice is:

- `legacy containment pilot`

Meaning:

- treat `src/core/strategy/features.py` and `src/core/config/validator.py` as retained legacy surfaces
- do **not** move them yet
- do **not** delete them yet
- keep the runtime path pointed at `features_asof` and `ConfigAuthority`
- if a later slice is opened, prefer strengthening labels/tripwires/routing over filesystem moves

This is a much safer first pilot than trying to archive code immediately.

### 3. A future V2 seed should default to active runtime + support, and exclude legacy by default

If a future `Genesis-Core-V2` seed is opened, the default import set should be:

- keep-now runtime
- runtime support
- optional-off only when intentionally promoted

And the default non-seed set should be:

- legacy compatibility shims
- test-only legacy validators
- helper surfaces still sitting in `needs_verification`

That gives V2 a cleaner starting boundary than cherry-picking from historical intuition.

## Unverified

- whether `core.strategy.regime` is exercised materially in paper/live paths outside the currently inspected spine
- whether MACD/helper surfaces become active in symbol/timeframe-specific paths not sampled here
- whether any external consumer still relies on the compatibility shim or legacy config validator beyond the repo-local evidence surfaces
- whether a later archive workflow would clear any of these surfaces after provenance checks

## Keep / move / archive / legacy map

### Keep now

- `config/runtime.json` authority path
- `scripts/run/run_backtest.py`
- `src/core/pipeline.py`
- `src/core/backtest/engine.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/features_asof.py`
- `src/core/strategy/model_registry.py`
- `src/core/strategy/champion_loader.py`
- `src/core/strategy/decision.py`

### Keep as support

- `src/core/backtest/engine_precompute.py`
- `src/core/intelligence/regime/authority.py`
- `src/core/strategy/regime.py`
- HTF Fibonacci support / exit Fibonacci support
- champion/runtime merge policy surfaces

### Keep but currently off

- `features`
- `htf_fib`
- `ltf_fib`
- disabled research override surfaces in the active runtime snapshot

### Keep as legacy compatibility

- `src/core/strategy/features.py`
- `src/core/config/validator.py`

### Needs verification before any lifecycle call

- `MACD` helper surfaces
- generic SMA helper surfaces outside the already-observed active indicator path
- volume-SMA-adjacent helper surfaces as dominant decision inputs

### Archive or move now

- none established in this slice

## Recommended cleanup pilot

### Pilot 01 — legacy containment

Recommended next bounded slice after this classification:

- objective: keep compatibility surfaces visible but clearly demoted from SSOT/runtime status
- target surfaces:
  - `src/core/strategy/features.py`
  - `src/core/config/validator.py`
- admissible shape:
  - docs / routing / tripwire-strengthening proposal or narrow follow-up audit
- inadmissible shape:
  - delete/move/archive execution
  - runtime import rewiring that changes behavior
  - config authority changes

This pilot is intentionally boring.
That is a feature, not a bug.

## What changed and what did not

What changed:

- the repo now has one bounded runtime surface classification note
- the inventory is now converted into explicit disposition buckets
- one smallest admissible cleanup pilot is now named

What did **not** change:

- no runtime behavior changed
- no files were moved, archived, or deleted
- no champion/config/runtime-authority surface was edited
- no aggressive cleanup was authorized by this slice
- unrelated local modifications remained out of scope
