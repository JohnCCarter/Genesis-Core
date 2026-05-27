# Genesis-Core — V2 runtime-first execution plan

Date: 2026-05-27
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base manifest anchor: `docs/analysis/system/genesis_v2_seed_manifest_candidate_2026-05-27.md`
Base SHA anchor: `0320cc3c`
Status: `completed / docs+artifact V2 execution plan / non-authorizing`

## Purpose

This bounded slice resolves the next concrete V2 planning question left open by the boundary map and manifest candidate:

> should the first `Genesis-Core-V2` seed be `runtime-only` or `runtime+API`, and what dependency/bootstrap work is minimally required to open that seed honestly?

This slice does **not** create a new repository.
It does **not** copy files.
It does **not** approve current branch state as a future V2 default.

It converts the existing V2 planning stack into one execution order that is concrete enough to follow later without pretending that extraction work has already happened.

## Mode proof

This work remains `RESEARCH` because it is a docs+artifact planning slice built from current repo-local import evidence, test boundaries, and already completed V2 planning notes.
That allows a non-authorizing execution plan.
It does **not** allow runtime behavior changes, champion edits, API cutover work, or actual repo extraction.
If this slice were to start creating a new repository, changing runtime/default authority, or editing champion/config authority surfaces, it would require stricter handling or a differently scoped task.

## Scope

### Scope IN

- decide whether the first V2 seed should be runtime-only or runtime+API
- map the main transitive dependency families behind the runtime seed candidate
- distinguish hard-bootstrap surfaces from soft/verify-later stateful surfaces
- define one phased execution order for a future V2 seed opening
- emit one machine-readable execution-plan artifact

### Scope OUT

- creating `Genesis-Core-V2`
- copying, moving, or deleting code
- changing runtime/config/champion behavior
- resolving every transitive import to file-level closure
- approving any current config/model/champion payload as future V2 default state

## Evidence inputs

Existing V2 planning anchors:

- `docs/analysis/system/genesis_v2_seed_boundary_map_2026-05-27.md`
- `docs/analysis/system/genesis_v2_seed_manifest_candidate_2026-05-27.md`
- `results/research/runtime_truth_inventory/genesis_v2_seed_manifest_candidate_2026-05-27.json` (current read-only input only)

Import / runtime evidence:

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
- `src/core/server.py`
- `config/__init__.py`
- `config/timeframe_configs.py`

Guardrail / phase-boundary evidence:

- `tests/governance/test_no_legacy_feature_imports.py`
- `tests/governance/test_dead_code_tripwires.py`
- `tests/integration/test_config_endpoints.py`

## Emitted artifact

- `results/research/runtime_truth_inventory/genesis_v2_runtime_first_execution_plan_2026-05-27.json`

## Observed

### 1. The runtime seed candidate does not need `server.py` or `src/core/api/**` to define the kernel

The selected runtime roots import into:

- backtest helpers
- strategy orchestration and gating
- indicator families
- regime/intelligence helpers
- config-support helpers
- utility/observability helpers

But the inspected runtime roots do **not** import `src/core/server.py` or `src/core/api/**` as part of the kernel path.

The import direction visible in `src/core/server.py` runs the other way:

- `server.py` assembles the FastAPI app
- `server.py` imports `core.api.*` routers
- API modules can import `core.server` back as part of the service shell

That makes the API layer an additive shell around the runtime core rather than a prerequisite for the kernel itself.

### 2. The runtime seed expands into support families, not just the headline files

The current top-level runtime roots are only the front edge of the real seed.
Import evidence shows that a runtime-first V2 still needs a broader but coherent support closure including at least:

- `src/core/backtest/{engine_results.py,htf_exit_engine.py,position_tracker.py}`
- `src/core/strategy/{confidence.py,prob_model.py,fib_logging.py,decision_fib_gating.py,decision_gates.py,decision_sizing.py,ri_policy_router.py,htf_selector.py}`
- `src/core/strategy/features_asof_parts/**`
- `src/core/intelligence/regime/{authority.py,htf.py}`
- `src/core/indicators/**` for ATR/EMA/RSI/Bollinger/Fibonacci/ADX/exit paths
- `src/core/config/{authority_mode_resolver.py,merge_policy.py}`
- `src/core/utils/**` support used by pipeline, registry, logging, diffing, and environment handling
- `src/core/observability/metrics.py`

So the first V2 seed can be runtime-only, but it cannot be only ten files and a smile.

### 3. Bootstrap requirements already split into hard-bootstrap and soft-bootstrap surfaces

The inspected runtime path shows a useful split:

#### Hard-bootstrap for importable runtime behavior

These are directly required or effectively hard-wired into the current runtime path:

- `config/__init__.py`
- `config/timeframe_configs.py`
- package/import structure for `core.*`
- runtime code families listed above

Why this matters:

- `ChampionLoader` imports `config.timeframe_configs` at module import time
- `config/__init__.py` currently exposes that package surface
- the runtime kernel is therefore not bootstrap-free even before any API shell exists

#### Soft-bootstrap / verify-later surfaces

These are currently important, but the code path shows they should not be blindly carried as default state:

- `config/backtest_defaults.yaml` — optional defaults in `pipeline.py`
- `config/models/registry.json` — optional registry in `model_registry.py`
- `config/strategy/champions/**` — optional champion payloads because `ChampionLoader` falls back to timeframe configs
- `cache/precomputed/**` — performance/cache surface, not required for semantic seed correctness
- current branch payloads under config/model/champion state

#### Operational bootstrap still needed for real backtests

Even without the API shell, `BacktestEngine` still reads under repo `data/**` and uses an explicit data-source policy.
So a future V2 runtime seed still needs a narrow decision about what minimal data fixture or curated/frozen input shape travels with it.

### 4. The test boundary already supports a runtime-first and API-later split

The governance guardrails align well with a runtime-only first seed:

- `tests/governance/test_no_legacy_feature_imports.py`
- `tests/governance/test_dead_code_tripwires.py`

These protect runtime/legacy boundaries without requiring the FastAPI shell.

By contrast, `tests/integration/test_config_endpoints.py` imports:

- `core.server`
- FastAPI `TestClient`
- runtime config endpoints

That makes it a better fit for the later API/service phase rather than for the first runtime-only seed.

## Inferred

### 1. The first V2 seed should be `runtime-only`

The import direction and test boundary both support the same conclusion:

- runtime kernel first
- API/service shell later

This is the narrowest seed that still matches the actual active logic spine.
It avoids dragging `server.py`, `src/core/api/**`, and service-adjacent dependencies into the first extraction step.

### 2. The first V2 seed should carry runtime guardrails, but only runtime-shaped ones

The first seed should carry the guardrails that preserve the cleaned boundary:

- no internal imports of `core.strategy.features`
- legacy compatibility stays contained
- runtime source does not grow new dependencies on `core.config.validator`

But it should not force API endpoint tests into phase 1 just because they were useful in current-repo containment work.

### 3. Bootstrap state should be recreated minimally, not cloned wholesale

The runtime-first plan should prefer:

- minimal package/bootstrap shell
- explicit, narrow config bootstrap
- controlled admission of current stateful artifacts only after review

It should avoid:

- copying current `config/runtime.json` as if it were future truth
- blindly carrying current champion payloads
- blindly carrying current model registry payloads
- treating current README/app shell as already correct for V2

### 4. The first honest dependency question after top-level manifesting is family closure, not API inclusion

Now that the first seed is decided as runtime-only, the next real dependency work is:

- finalize the runtime-support family closure
- define the minimal bootstrap shell
- choose the smallest reproducible data/input fixture

Only after that does the API/service question become worth resolving operationally.

## Unverified

- the exact minimum package metadata shape for a future V2 repo
- the smallest reproducible data fixture that should travel with a runtime-only seed
- whether any current `config/models/**` payload is fresh enough to carry unchanged
- whether any current `config/strategy/champions/**` payload is fresh enough to carry unchanged
- whether paper/live surfaces should ever be part of the first V2 remit after the API shell arrives

## Recommended V2 execution order

### Phase 1 — open a runtime-only seed

Include first:

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

Carry or recreate immediately as required support families:

- supporting backtest modules
- supporting strategy modules and `features_asof_parts`
- indicator modules
- config-support modules used by runtime
- utility/observability modules used by runtime
- `config/__init__.py`
- `config/timeframe_configs.py`

Carry as runtime-only guardrails:

- `tests/governance/test_no_legacy_feature_imports.py`
- `tests/governance/test_dead_code_tripwires.py`

Hold out of phase 1:

- `src/core/server.py`
- `src/core/api/**`
- `tests/integration/test_config_endpoints.py`
- paper/live service edges

### Phase 2 — add minimal bootstrap shell

Resolve explicitly, but minimally:

- narrowed package metadata (`pyproject.toml` or equivalent future shape)
- minimal README/bootstrap note suited to V2 rather than current Genesis-Core
- whether `config/backtest_defaults.yaml` is copied, narrowed, or regenerated
- minimal data fixture / curated-frozen input needed for first runtime smoke path
- whether precompute cache support exists only as optional performance layer

### Phase 3 — admit stateful artifacts one bucket at a time

Resolve next, without blind carry-over:

- `config/models/**`
- `config/strategy/champions/**`
- any future runtime-state payloads
- any model/champion freshness claims

Admission rule:

- if a payload is needed, prove it
- if it is only current branch state, treat it as verify-before-include

### Phase 4 — add the API/service shell

Only after phases 1-3 are stable:

- `src/core/server.py`
- `src/core/api/**`
- service-edge dependencies such as API router coupling and Bitfinex-facing service paths
- `tests/integration/test_config_endpoints.py`

This is where config endpoint behavior, auth shells, UI, and public/account/paper routers belong.
Not in the first kernel seed.

### Phase 5 — paper/live-adjacent expansion only if still desired

Leave for the end:

- paper/live operational assumptions
- exchange/service edges not needed for the runtime kernel
- any readiness-shaped or production-near claims

## Default exclusions and late buckets

### Exclude by default from the first V2 seed

- `src/core/strategy/features.py`
- `src/core/config/validator.py`
- broad `results/research/**`
- `docs/analysis/edge_topology/**`
- branch-local historical/explanatory planning surfaces

### Keep as verify-before-include

- `pyproject.toml`
- `README.md`
- `config/backtest_defaults.yaml`
- `config/models/**`
- `config/strategy/champions/**`
- `data/**` selection for first reproducible runtime execution
- any optional-off/helper territory not yet proven essential

## Decision

`FREEZE_V2_RUNTIME_ONLY_FIRST_WITH_BOOTSTRAP_AND_API_LATER`

Meaning:

- the first future V2 seed should be runtime-only
- runtime-support family closure and minimal bootstrap come before API addition
- current stateful artifacts remain verify-before-include by default
- API/service shell is phase-4 work, not phase-1 seed material
- this remains a non-authorizing execution plan, not a repo-creation approval

## What changed and what did not

What changed:

- V2 planning now has one concrete execution order instead of only boundary buckets
- the first seed decision is now explicit: `runtime-only`, not `runtime+API`
- runtime guardrails are now separated from API-phase integration coverage
- bootstrap work is now split into hard-bootstrap, soft-bootstrap, and state-admission phases

What did **not** change:

- no V2 repository was created
- no files were copied or moved
- no runtime/config/champion behavior changed
- no current branch state was promoted as future V2 default truth
- locally modified unrelated files remained untouched
