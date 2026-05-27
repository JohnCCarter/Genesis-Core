# Genesis-Core — V2 seed boundary map

Date: 2026-05-27
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base containment anchor: `docs/analysis/system/genesis_runtime_legacy_containment_2026-05-27.md`
Base SHA anchor: `f82fc37c`
Status: `completed / docs+artifact V2 seed boundary map / non-authorizing`

## Purpose

This bounded slice defines one practical boundary question only:

> if a future `Genesis-Core-V2` seed is opened, which current Genesis-Core surfaces should be treated as seed-now, promote-later, exclude-by-default, or verify-before-seed?

This slice does **not** create a V2 repository.
It does **not** authorize copying files, cutting over defaults, or promoting branch-current runtime state into a new repo.

Its role is simply to convert the already completed runtime truth / classification / containment slices into a seed boundary map that is easier to act on later.

## Mode proof

This work remains `RESEARCH` because it is a docs+artifact boundary map built from current evidence notes and repo-local lifecycle/routing guidance.
That allows a small non-authorizing planning artifact.
It does **not** allow runtime behavior changes, champion edits, config-authority changes, or actual repo extraction work.
If this slice were to start editing runtime/default/champion surfaces or create a new repository scaffold, it would need stricter handling or a differently scoped task.

## Scope

### Scope IN

- convert existing runtime truth findings into V2 seed buckets
- distinguish structure/logic from branch-current state/artifacts
- identify the smallest safe default inclusion boundary for a future V2 seed
- emit one machine-readable boundary artifact

### Scope OUT

- creating `Genesis-Core-V2`
- moving/copying/deleting files
- changing runtime or config behavior
- changing current branch authority surfaces
- promoting current branch runtime snapshot as an approved future default

## Evidence inputs

Primary completed slices:

- `docs/analysis/system/genesis_runtime_truth_inventory_2026-05-27.md`
- `docs/analysis/system/genesis_runtime_surface_classification_2026-05-27.md`
- `docs/analysis/system/genesis_runtime_legacy_containment_2026-05-27.md`
- `results/research/runtime_truth_inventory/genesis_runtime_legacy_containment_2026-05-27.json` (read-only input only)

Boundary/routing support:

- `docs/system/GENESIS_TOPOLOGY_WORK_QUEUE.md`
- `docs/knowledge/GENESIS_TOPOLOGY_LIFECYCLE_AUTHORITY_MAP.md`
- `docs/knowledge/KNOWLEDGE_AUTHORITY_RULES.md`
- `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`
- `config/README.md`

## Emitted artifact

- `results/research/runtime_truth_inventory/genesis_v2_seed_boundary_map_2026-05-27.json`

## Observed

### 1. The strongest current V2 boundary anchors are runtime truth, classification, and containment — not a pre-existing V2 packet

This slice did **not** find an existing direct `Genesis-Core-V2` packet or seed artifact.

Instead, the strongest current anchors are:

- runtime truth inventory
- runtime surface classification
- legacy containment verification
- zone-level lifecycle/routing maps that explain how to keep the slice non-authorizing

So the correct shape here is a derivative boundary map, not a faux-authoritative migration plan.

### 2. Active runtime logic is a stronger seed candidate than current branch runtime state

The existing slices already support a stable active-runtime logic spine:

- `pipeline.py`
- `BacktestEngine`
- `evaluate.py`
- `features_asof.py`
- `decision.py`
- runtime-support pieces such as precompute, regime authority, and merge-policy-adjacent support

But they do **not** support blindly treating the current branch runtime snapshot as the future target.

Important distinction:

- runtime/control **structure** is seedable
- current branch **state** is not automatically seedable

This matters especially for:

- `config/runtime.json`
- champion JSON files
- model registry contents
- sample champion freshness

The current branch snapshot is still legacy-shaped, and earlier slices explicitly left open whether that snapshot is the intended long-term product target or simply the current branch state.

### 3. Legacy compatibility surfaces should stay out of the default V2 seed

The earlier classification and containment slices already support a clean default exclusion for:

- `src/core/strategy/features.py`
- `src/core/config/validator.py`

These are retained legacy surfaces with verified containment.
That means they are useful compatibility boundaries in the current repo, but they should not be part of the default V2 seed unless a concrete compatibility requirement is later proven.

### 4. Optional-off surfaces should not be silently promoted into the seed

The runtime truth inventory identified current null/disabled surfaces such as:

- `features`
- `htf_fib`
- `ltf_fib`
- disabled research override surfaces

These should not be silently seeded as “active V2 scope.”
If they are ever carried forward, they should be marked as promote-later-only and activated by explicit intent.

### 5. Helper territory and mixed-freshness artifacts belong in verification, not in the default seed

The earlier slices already left several boundaries unresolved or mixed:

- MACD/helper territory not strongly observed on the active spine
- champion/model freshness not uniformly current
- external usage of retained legacy surfaces unknown
- current runtime snapshot intent unresolved

Those are classic `verify_before_seed` items.
They are too uncertain for default inclusion and too live to classify as default exclusion without more evidence.

## Inferred

### 1. The best V2 default is “active runtime logic + support + guardrails”, not “copy the whole branch shape”

The cleanest future V2 seed is not a historical cherry-pick and not a whole-repo carry-over.
It is a narrower shape centered on:

- active runtime logic
- runtime support logic
- verification/guardrail surfaces that preserve the intended boundary
- minimal boundary/reference notes needed to explain what was and was not seeded

### 2. Current stateful artifacts should default to verify-before-seed

For a future V2, the following should default to verification rather than blind carry-over:

- `config/runtime.json` current payload
- champion files
- model registry payloads
- paper/live surface assumptions
- optional-off config surfaces

This is the key protection against cloning today’s branch state as if it were tomorrow’s intended product state.

### 3. The default exclusion line is already clear enough to use

The safest default exclusion line is now straightforward:

- retained legacy compatibility surfaces
- broad research/output corpora not needed for runtime bootstrapping
- helper territory still sitting in `needs_verification`
- branch-local historical or evidence surfaces that explain Genesis-Core but do not belong inside a minimal executable seed

## Unverified

- whether a future V2 should preserve the current `legacy` family as a temporary bootstrap or deliberately switch family posture during extraction
- whether any model/champion artifacts are fresh enough to carry unchanged
- whether paper/live API edges match the desired future seed boundary
- whether external consumers exist for the retained legacy surfaces

## V2 seed buckets

### Seed now — runtime logic

These are the strongest default candidates for a future executable seed:

- `src/core/pipeline.py`
- `src/core/backtest/engine.py`
- `src/core/backtest/engine_precompute.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/features_asof.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/model_registry.py`
- `src/core/strategy/champion_loader.py`
- `src/core/intelligence/regime/authority.py`
- `src/core/strategy/regime.py` as support/mode-gated surface, not as proven primary authority default

### Seed now — guardrails and verification support

These should travel with the seed boundary or be recreated immediately:

- `tests/governance/test_no_legacy_feature_imports.py`
- `tests/governance/test_dead_code_tripwires.py`
- `tests/integration/test_config_endpoints.py`
- boundary notes that explain active runtime vs legacy vs optional-off distinctions

### Promote later only if explicitly chosen

These are not default seed-now material, but may be promoted later with explicit intent:

- optional-off runtime surfaces such as `features`, `htf_fib`, `ltf_fib`
- disabled research override surfaces
- any deliberate family/authority-mode change relative to the current branch snapshot

### Verify before seed

These require additional decisions or freshness checks before inclusion:

- current `config/runtime.json` payload
- `config/models/registry.json`
- champion JSON payloads
- sample model/champion freshness
- paper/live API entrypoints and operational assumptions
- MACD/helper territory and other currently unresolved helper surfaces

### Exclude by default

These should stay outside the default V2 seed unless a later bounded slice proves otherwise:

- `src/core/strategy/features.py`
- `src/core/config/validator.py`
- broad `results/research/**` corpora not needed for executable bootstrapping
- Edge Topology evidence corpus as default seed material
- branch-local/historical planning surfaces whose role is explanation rather than execution

## Decision

`FREEZE_V2_SEED_BOUNDARY_AS_LOGIC_PLUS_SUPPORT_NOT_BRANCH_STATE`

Meaning:

- future V2 seeding should start from active runtime logic and support boundaries
- branch-current state/artifacts should default to verification before inclusion
- retained legacy surfaces should default to exclusion
- this map is a non-authorizing boundary aid, not a migration approval packet

## What changed and what did not

What changed:

- the repo now has one bounded V2 seed boundary map
- current runtime findings are now converted into seed-now / promote-later / verify / exclude buckets
- the distinction between executable logic and branch-current state is now explicit

What did **not** change:

- no V2 repository was created
- no files were moved or copied
- no runtime/config/champion behavior changed
- the locally modified runtime surface classification artifact remained untouched
- the locally modified runtime legacy containment artifact remained untouched
