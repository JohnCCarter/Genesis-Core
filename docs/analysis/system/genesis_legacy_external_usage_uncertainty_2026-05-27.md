# Genesis-Core — legacy external usage uncertainty

Date: 2026-05-27
Branch: `feature/research-attribution-layer-foundation-2026-05-26`
Mode: `RESEARCH`
Base V2 boundary anchor: `docs/analysis/system/genesis_v2_seed_boundary_map_2026-05-27.md`
Base SHA anchor: `24d7c7c2`
Status: `completed / docs+artifact uncertainty audit / non-authorizing`

## Purpose

This bounded slice answers one narrow follow-up question from the runtime truth / containment / V2 boundary work:

> does the current repository provide positive evidence that the retained legacy surfaces have external/public consumers, or does the uncertainty remain unresolved?

Target legacy surfaces:

- `src/core/strategy/features.py`
- `src/core/config/validator.py`

This slice is **not** an external telemetry audit.
It is a repo-local uncertainty audit only.

## Mode proof

This work remains `RESEARCH` because it is a docs+artifact audit built from current repo-local evidence only.
It does not change runtime behavior, packaging behavior, config authority, or filesystem placement.
If this slice were to change packaging/public API commitments, delete legacy surfaces, or create a new V2 repo, it would need a different and likely stricter scope.

## Scope

### Scope IN

- inspect repo-local evidence for public or external-consumer expectations around the two retained legacy surfaces
- separate positive evidence from absence-of-evidence
- record the narrow lifecycle consequence for current V2/default-exclusion reasoning
- emit one machine-readable uncertainty artifact

### Scope OUT

- package metadata changes
- code changes
- delete/archive/move execution
- external telemetry, PyPI statistics, or consumer repos
- proving absence of all external consumers

## Evidence inputs

Legacy-surface anchors:

- `src/core/strategy/features.py`
- `src/core/config/validator.py`
- `tests/governance/test_no_legacy_feature_imports.py`
- `tests/governance/test_dead_code_tripwires.py`
- `tests/integration/test_config_endpoints.py`

Public/package-facing evidence:

- `pyproject.toml`
- `README.md`
- `src/core/server.py`
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/ARCHITECTURE_VISUAL.md`
- `docs/governance/runtime_config_live_update_matrix_2026-05-15.md`

Upstream slice context:

- `docs/analysis/system/genesis_runtime_legacy_containment_2026-05-27.md`
- `docs/analysis/system/genesis_v2_seed_boundary_map_2026-05-27.md`
- `results/research/runtime_truth_inventory/genesis_v2_seed_boundary_map_2026-05-27.json` (read-only input only)

## Emitted artifact

- `results/research/runtime_truth_inventory/genesis_legacy_external_usage_uncertainty_2026-05-27.json`

## Observed

### 1. The legacy surfaces are described as compatibility/test-only, not as recommended public APIs

Observed support:

- `src/core/strategy/features.py` declares itself a legacy compatibility shim and says internal runtime code should import `core.strategy.features_asof`
- `src/core/config/validator.py` declares itself intentionally legacy/test-only and says runtime validation must go through `ConfigAuthority.validate`
- `docs/architecture/ARCHITECTURE.md` explicitly says `core.config.validator` exposes only legacy/test-only helpers and that runtime authority does not depend on it
- `docs/governance/runtime_config_live_update_matrix_2026-05-15.md` lists `core.config.validator.*` under `Legacy helper surface`
- `docs/architecture/ARCHITECTURE_VISUAL.md` classifies `core.strategy.features` as `DEPRECATED_PATH` and `core.config.validator` as `TEST_ONLY`

So the repo does **not** present these surfaces as preferred current interfaces.

### 2. Repo-local public guidance is app/service oriented, not library-import oriented

Observed support:

- `README.md` describes Genesis-Core as deterministic backtest/optimization plus a FastAPI service
- the README quickstart shows `pip install -e` followed by `uvicorn core.server:app --reload --app-dir src`
- `README.md` documents config authority through `config/runtime.json`, `ConfigAuthority`, and `/config/runtime*` API routes
- `src/core/server.py` acts as the canonical application assembler/entrypoint for the FastAPI service

This is important because it means the repo’s main user-facing guidance points to:

- running the service
- using the config API
- using managed runtime authority surfaces

It does **not** point readers toward importing `core.strategy.features` or `core.config.validator` as stable public APIs.

### 3. The package surface keeps external importability technically possible

Observed support:

- `pyproject.toml` defines a Python package named `genesis-core`
- `tool.setuptools.packages.find` includes `core*` from `src`
- repo install guidance uses editable installation (`pip install -e "[dev]"` / optional extras)

So while the repo does not positively advertise the legacy surfaces as current public APIs, those modules are still technically installable/importable by external consumers.

That means repo-local evidence can support:

- no positive public-API endorsement

But it cannot support:

- proof that no external consumer imports them

### 4. Repo-local usage evidence stays internal and containment-oriented

Observed support:

- `tests/governance/test_no_legacy_feature_imports.py` blocks internal repo imports of `core.strategy.features`
- `tests/governance/test_dead_code_tripwires.py` uses the legacy surfaces only to enforce delegation/containment contracts
- `tests/integration/test_config_endpoints.py` imports `validate_legacy_config` and `diff_legacy_config` as explicit test-only compatibility helpers

So the positive usage evidence found in-repo is:

- governance enforcement
- compatibility verification
- integration testing

Not:

- public client guidance
- recommended consumer API
- documented extension surface

## Inferred

### 1. There is no positive repo-local evidence of external/public consumer expectation for the legacy surfaces

The strongest repo-local read is:

- these modules remain installed and importable
- they are retained for compatibility/test purposes
- they are actively demoted from SSOT/runtime-authority status
- they are not documented as preferred external APIs

So there is **no positive repo-local evidence** that external consumers are expected to rely on them.

### 2. External-consumer absence still cannot be proven from this repo alone

Because the package publishes `core*` packages and because repo-local evidence cannot inspect external repos or private automation, this slice cannot honestly claim:

- zero external consumers
- delete-safe by external-usage proof
- archive-safe by external-usage proof

The uncertainty remains real, but it is specifically an **absence-of-proof** problem rather than a **positive external-usage** finding.

### 3. Current V2 default exclusion remains supported

This uncertainty audit does not weaken the current V2 boundary.
In fact it supports it:

- default V2 exclusion for retained legacy surfaces still stands
- stronger lifecycle action in the current repo should wait for a different package/public-API or external-consumer slice

So the practical rule remains:

- exclude by default in V2
- keep contained in current repo
- do not mistake package importability for positive product commitment

## Unverified

- whether any private/local automation outside this repo imports `core.strategy.features`
- whether any private/local automation outside this repo imports `core.config.validator`
- whether any published wheel/editable install consumers actually rely on these modules today
- whether a future explicit package/public-API contract slice would narrow the uncertainty enough for stronger lifecycle action

## Uncertainty verdict

### Supported by repo-local evidence

- no positive public-API endorsement for the two legacy surfaces
- repo guidance is app/service oriented
- legacy surfaces are retained compatibility/test-only boundaries
- package metadata keeps external importability technically possible

### Not supported by repo-local evidence

- proof of zero external consumers
- delete readiness based on external-consumer absence
- archive readiness based on external-consumer absence

## Decision

`NO_POSITIVE_REPO_LOCAL_EXTERNAL_USAGE_EVIDENCE_KEEP_UNCERTAINTY_OPEN`

Meaning:

- keep current legacy containment boundary
- keep V2 default exclusion for the legacy surfaces
- do not escalate to delete/archive based on this slice alone
- if stronger lifecycle action is desired later, open a separate package/public-API or external-consumer audit

## What changed and what did not

What changed:

- the repo now has one bounded external-usage uncertainty audit for the retained legacy surfaces
- the distinction between `no positive repo-local evidence` and `no possible external consumers` is now explicit
- the current V2 exclusion rationale is now better grounded

What did **not** change:

- no runtime behavior changed
- no packaging behavior changed
- no file was moved, archived, or deleted
- the locally modified V2 boundary artifact remained untouched
- the locally modified runtime surface classification artifact remained untouched
