# Genesis-Core — V2 seed manifest candidate

Date: 2026-05-27
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base uncertainty anchor: `docs/analysis/system/genesis_legacy_external_usage_uncertainty_2026-05-27.md`
Base SHA anchor: `5f081e63`
Status: `completed / docs+artifact manifest candidate / non-authorizing`

## Purpose

This bounded slice converts the existing V2 boundary work into one more concrete artifact:

> a top-level path manifest candidate for a future `Genesis-Core-V2` seed

This is still **not** a repo creation step.
It is a candidate path map only.

The key question is:

> which top-level current paths should be treated as include-now roots, verify-before-include roots, exclude-by-default roots, or reference-only inputs for a future V2 seed?

## Mode proof

This work remains `RESEARCH` because it is a docs+artifact classification/selection slice built from the existing runtime truth, boundary, containment, and uncertainty notes.
It does not copy files, create a repository, or change runtime/config/champion behavior.
If this slice were to start building a new repo, editing runtime/default surfaces, or entering champion/config authority paths, it would require stricter handling or a differently scoped task.

## Scope

### Scope IN

- produce one candidate manifest of top-level current path roots for a future V2 seed
- keep the candidate honest about what is and is not yet dependency-complete
- distinguish executable logic roots from branch-current state roots and legacy roots
- emit one machine-readable manifest candidate artifact

### Scope OUT

- repo creation
- copying or moving files
- transitive dependency closure across all imports
- runtime or packaging changes
- approval of a final V2 structure

## Evidence inputs

Primary basis:

- `docs/analysis/system/genesis_v2_seed_boundary_map_2026-05-27.md`
- `docs/analysis/system/genesis_legacy_external_usage_uncertainty_2026-05-27.md`
- `results/research/runtime_truth_inventory/genesis_legacy_external_usage_uncertainty_2026-05-27.json` (read-only input only)

Placement / taxonomy support:

- `docs/repository-layout-policy.md`
- `README.md`
- `pyproject.toml`

## Emitted artifact

- `results/research/runtime_truth_inventory/genesis_v2_seed_manifest_candidate_2026-05-27.json`

## Interpretation boundary

This manifest candidate is:

- **top-level and selected-path only**
- **not dependency-complete**
- **not an approved copy list**
- **not a final V2 tree**

Its purpose is to make the next repo-seeding conversation concrete without pretending that all transitive imports, bootstrap files, and service assumptions are already settled.

## Observed

### 1. The current V2 boundary work is strong enough for a selected-path manifest, but not for a full closure manifest

The earlier slices already support stable bucket decisions for several direct surfaces:

- active runtime logic roots
- guardrail/test roots
- retained legacy exclusions
- verify-before-seed state/config/artifact roots

But the same slices also leave open:

- full transitive dependency expansion
- final service/API inclusion boundary
- final package metadata shape
- final stateful artifact carry-over decisions

So the honest next artifact is a **candidate manifest**, not a fake-complete file list.

### 2. Domain-grouped roots are more useful than root-level scatter

`docs/repository-layout-policy.md` explicitly prefers domain placement over vague or root-level drift.
That supports grouping the manifest candidate by path role and zone, rather than producing a flat, pseudo-final extraction dump.

So the candidate is structured around a few path-root buckets:

- `include_now_roots`
- `verify_before_include_roots`
- `exclude_by_default_roots`
- `reference_only_inputs`

### 3. The strongest include-now roots remain runtime logic and guardrails, not current state

The V2 boundary map already showed that the cleanest seed is:

- active runtime logic
- runtime support logic
- guardrail/test surfaces

The external-usage uncertainty audit did not change that.
It only reinforced that default exclusion of the retained legacy surfaces is still the safe call.

### 4. Root/bootstrap files remain a verification boundary, not a blind include bucket

Even obviously important files such as:

- `pyproject.toml`
- `README.md`
- service entrypoints
- `config/runtime.json`

should not be blindly included unchanged.

Why:

- package metadata may need narrowing or renaming in a future V2
- the README currently describes Genesis-Core as it exists today, not a future extracted repo
- service/API boundaries are still only partially classified for V2 purposes
- runtime/config/champion payloads are current-state artifacts, not automatically future defaults

So these belong in `verify_before_include_roots`, not `include_now_roots`.

## Inferred

### 1. A good V2 seed manifest starts with primary carriers, not exhaustive closure

The right first manifest is a primary-carrier manifest:

- what the future seed should definitely start from
- what must be explicitly checked before inclusion
- what should stay out by default
- what is reference-only and helps seed the work without being seed material itself

### 2. The selected-path manifest sharpens the next human decision

After this slice, the next real decision is no longer abstract “should we make a V2?”
It becomes more concrete:

- do we want to expand this candidate into a transitive dependency manifest?
- do we want a minimal runtime-only V2 or a runtime+API V2?
- which verify bucket should be resolved first: packaging, service edge, or stateful config/model artifacts?

### 3. Exclusion remains a feature, not a loss

The manifest becomes more useful precisely because it excludes things on purpose.
The point is not to carry everything forward.
The point is to make the seed boundary narrower and cleaner than the current repo.

## Unverified

- full transitive import closure for the selected runtime roots
- whether `src/core/server.py` and `src/core/api/**` belong in the first V2 seed or a later expansion
- whether `pyproject.toml` should stay close to current shape or be narrowed/renamed
- whether any current config/model/champion payload should carry unchanged into a future seed

## V2 seed manifest candidate

### Include now roots

These are the strongest selected roots for a future V2 seed start:

- `src/core/pipeline.py`
- `src/core/backtest/engine.py`
- `src/core/backtest/engine_precompute.py`
- `src/core/strategy/evaluate.py`
- `src/core/strategy/features_asof.py`
- `src/core/strategy/decision.py`
- `src/core/strategy/model_registry.py`
- `src/core/strategy/champion_loader.py`
- `src/core/intelligence/regime/authority.py`
- `src/core/strategy/regime.py`
- `tests/governance/test_no_legacy_feature_imports.py`
- `tests/governance/test_dead_code_tripwires.py`
- `tests/integration/test_config_endpoints.py`

These are the current primary carriers.
They are still not guaranteed to be dependency-complete by themselves.

### Verify before include roots

These should be resolved explicitly before any future seed uses them:

- `pyproject.toml`
- `README.md`
- `src/core/server.py`
- `src/core/api/**`
- `config/runtime.json`
- `config/runtime.seed.json`
- `config/models/**`
- `config/strategy/champions/**`
- paper/live API entrypoints and operational assumptions
- unresolved helper territory such as MACD/helper-class paths

### Exclude by default roots

These should stay outside the default future V2 seed unless a later bounded slice proves otherwise:

- `src/core/strategy/features.py`
- `src/core/config/validator.py`
- `results/research/**`
- `docs/analysis/edge_topology/**`
- branch-local historical planning / explanation surfaces

### Reference-only inputs

These help explain the seed decision but are not default seed material:

- `docs/analysis/system/genesis_runtime_truth_inventory_2026-05-27.md`
- `docs/analysis/system/genesis_runtime_surface_classification_2026-05-27.md`
- `docs/analysis/system/genesis_runtime_legacy_containment_2026-05-27.md`
- `docs/analysis/system/genesis_v2_seed_boundary_map_2026-05-27.md`
- `docs/analysis/system/genesis_legacy_external_usage_uncertainty_2026-05-27.md`

## Decision

`FREEZE_TOP_LEVEL_V2_SEED_MANIFEST_CANDIDATE_NOT_DEPENDENCY_COMPLETE`

Meaning:

- the future V2 seed now has a concrete top-level path candidate
- the candidate is intentionally narrower than the current repo
- verify buckets remain explicit instead of being silently inherited
- this artifact still does not authorize repo creation or final extraction

## What changed and what did not

What changed:

- the repo now has one bounded V2 seed manifest candidate
- the V2 boundary map is now translated into a more concrete path-root artifact
- the next decision about V2 can now focus on specific verify buckets instead of vague repo-wide intuition

What did **not** change:

- no V2 repository was created
- no files were copied, moved, or deleted
- no runtime/config/champion behavior changed
- the locally modified legacy uncertainty artifact remained untouched
- the locally modified runtime surface classification artifact remained untouched
