# Repository Layout Policy

Last update: 2026-03-12
Status: draft

## Purpose

This document defines practical layout and file-placement guidance for Genesis-Core.
It exists to reduce sprawl, improve discoverability, and make future refactors easier
for both humans and agents.

This is a repository-structure policy, not a constitutional or governance source of truth.
It must not override higher-order governance or mode-resolution documents.

## Relationship to higher-order documents

This document is subordinate to the repository's higher-order governance sources.
In case of conflict, follow the higher-order documents first, especially:

- `.github/copilot-instructions.md`
- `docs/OPUS_46_GOVERNANCE.md`
- `docs/governance_mode.md`
- `AGENTS.md`

Role-specific interpretation may also require:

- `.github/agents/Codex53.agent.md`
- `.github/agents/Opus46.agent.md`

This policy focuses on where repository content should live, how modules should be split,
and when to prefer folders, sibling modules, or local helper files.

## Scope

This policy applies to the whole repository, with different levels of strictness by zone.

Primary layout zones:

- `src/`
- `tests/`
- `scripts/`
- `tools/`
- `config/`

Secondary support zones:

- `docs/`
- `.github/`
- `registry/`
- `data/`

Output and hygiene zones:

- `artifacts/`
- `results/`
- `logs/`
- `cache/`
- `tmp/`
- `archive/`

This policy also applies to repository-root placement decisions.

This policy does not define:

- runtime behavior
- governance gates
- CI authority
- freeze rules
- merge approval criteria

## Goals

The repository layout should make it easy to answer four questions quickly:

1. Where does this behavior belong?
2. What is the public entrypoint for this area?
3. Which files are internal support versus stable domain modules?
4. Where should related tests, scripts, configs, docs, or generated outputs live?

## Zone model

### Primary layout zones

These zones should follow the strongest and most explicit placement rules:

- `src/`
- `tests/`
- `scripts/`
- `tools/`
- `config/`

These are active working areas where layout directly affects maintainability,
testability, refactor cost, and agent accuracy.

### Secondary support zones

These zones should follow clear placement rules, but usually at a coarser grain:

- `docs/`
- `.github/`
- `registry/`
- `data/`

The goal here is clarity of taxonomy and ownership, not over-designed subfolder lawyering.

### Output and hygiene zones

These zones should emphasize containment, naming hygiene, and lifecycle rules more than
fine-grained internal structure:

- `artifacts/`
- `results/`
- `logs/`
- `cache/`
- `tmp/`
- `archive/`

These areas should stay predictable and should not leak active work back into the repo root.

## Core principles

### Place files by domain before by implementation style

Prefer grouping by business/domain responsibility first, not by vague technical labels.
A file should live near the domain it serves.

Good:

- `src/core/strategy/decision_fib_gating.py`
- `src/core/strategy/features_asof_parts/`
- `src/core/ml/evaluation_metrics.py`

Less good:

- broad cross-domain dumping into generic `helpers`, `common`, `misc`, or `temp` modules

### Keep one clear public entrypoint per local area when possible

If one file acts as the orchestrator or public entrypoint for a local domain flow,
keep that file thin and readable. Push private detail into adjacent files only when it
improves clarity.

### Split only when the new boundary is meaningful

Do not split files just because they are long.
Split when the extracted code has a stable and understandable role such as:

- a distinct sub-flow
- a coherent calculation family
- reusable internal utilities for one domain
- a separate reporting, metrics, or trading concern

### Avoid wrapper inflation

Do not create files whose main purpose is to:

- re-export one local function without a real boundary
- rename a concept without clarifying responsibility
- add mapping/wrapping layers with no domain value
- create one-function-per-file fragmentation without a navigation benefit

A smaller file is not automatically a better file. Tiny indirection factories are still clutter,
just wearing a neat shirt.

### Keep the repository root intentional

The repo root should contain only genuinely root-level files and folders.
If something belongs to a domain, workflow, output area, or documentation bucket,
it should normally live there instead of in the root.

## Terminology

### Orchestrator module

A module that coordinates a local flow and remains the most obvious entrypoint for that area.
It may import internal parts/helpers/components.

Examples:

- `src/core/strategy/decision_fib_gating.py`
- `src/core/ml/evaluation.py`

### Parts package

Use a `_parts/` package when one domain grows beyond a clean single-file shape and has several
closely related internal sub-areas.

Use `_parts/` when all of the following are true:

- the parent module remains the natural entrypoint
- the extracted files are still part of one local domain
- multiple internal sub-areas exist
- sibling modules would become noisy or ambiguous

Example:

- `src/core/strategy/features_asof_parts/`

A `_parts/` package is preferred over a long tail of weakly named sibling files when the pieces
are internal to one larger module.

### Component module

Use a component when the extracted unit represents a clearer subsystem or role with a more stable
identity than a helper.

Typical signs:

- the module has a named responsibility
- the boundary is understandable on its own
- the module may earn dedicated tests or future extension
- the name describes what it is, not merely that it helps

Examples of role-based siblings:

- `src/core/ml/evaluation_metrics.py`
- `src/core/ml/evaluation_trading.py`
- `src/core/ml/evaluation_report.py`

### Helper or utility module

Use a local helper file only for tightly related support logic that is:

- internal to one nearby domain
- not a stable subsystem
- small enough that a `_parts/` package would be overkill

Example:

- `src/core/strategy/decision_fib_gating_helpers.py`

Helpers must stay narrow. If a helper file becomes a cross-domain junk drawer, it should be split,
renamed, or folded back into better domain modules.

## Layout rules for `src/`

### Rule 1: Keep modules near their owning domain

Code should live in the nearest domain folder that owns the behavior.
Do not place strategy-specific logic in a generic shared location just because another area might
someday reuse it.

### Rule 2: Prefer descriptive sibling modules for distinct roles

If one module grows distinct responsibilities, prefer descriptive sibling names over generic names.

Prefer:

- `evaluation_metrics.py`
- `evaluation_trading.py`
- `evaluation_report.py`

Over:

- `evaluation_helpers.py`
- `evaluation_utils.py`
- `evaluation_more.py`

### Rule 3: Use `_parts/` for one larger internal domain, not for everything

A `_parts/` package is appropriate when a single parent module has several internal clusters.
It is not the default for every split.

Use `_parts/` when:

- the parent file remains the public face
- the sub-files are mainly internal implementation detail
- the package improves browsing

Do not use `_parts/` when one or two nearby sibling modules are enough.

### Rule 4: Keep private support local before making it shared

If extracted logic is used by only one local domain, keep it adjacent to that domain first.
Promote it to a shared area only after real, repeated reuse appears.

### Rule 5: Avoid anonymous generic names

Avoid creating new modules or folders named only:

- `helpers`
- `utils`
- `common`
- `misc`
- `temp`
- `new`
- `old`

unless the name is locally scoped and the contents are narrow, intentional, and temporary by design.

## Layout rules for `tools/` and `config/`

### Rule 1: Separate operational tooling from runtime code

Use `tools/` for auxiliary tooling, local automation helpers, analysis utilities, and developer-facing
support code that is not part of the main runtime domain model.

Do not place runtime domain logic in `tools/` just because it is inconvenient to classify.

### Rule 2: Keep configuration near configuration authority

Use `config/` for configuration files, schemas, defaults, validation definitions, and related support
material whose primary role is configuration authority or configuration interpretation.

Do not scatter active config across unrelated folders unless there is a strong ownership reason.

### Rule 3: Prefer descriptive substructure inside `config/`

Subfolders and filenames under `config/` should reflect what is being configured, such as strategy,
optimizer, models, validation, runtime, or temporary staging.

Avoid vague names that hide whether a file is a default, schema, override, runtime authority,
or example.

## Layout rules for `tests/`

### Rule 1: Tests should follow domain ownership

Place tests near the domain they validate, using the existing test taxonomy where possible.
Avoid root-level sprawl for new tests.

### Rule 2: Mirror responsibility, not every implementation seam

A new helper file does not automatically require a new top-level test file.
Add tests based on behavior, contract, or regression risk.

Good outcomes:

- keep tests in an existing domain test file when behavior is unchanged and the seam is internal
- add a focused test file when a new internal unit has a meaningful contract or repeated edge cases

### Rule 3: Prefer descriptive grouping over historical leftovers

As the suite evolves, tests should move toward stable subfolders by purpose, such as:

- domain/unit tests
- integration tests
- governance or invariant tests
- utility-focused tests

Do not keep adding to root-level `tests/test_*.py` when a clearer subfolder already exists.

## Layout rules for `scripts/`

### Rule 1: Scripts belong in canonical purpose-based locations under `scripts/`

Do not leave operational scripts floating in the repo root or hide them in archive-like side paths
when they are still active.

### Rule 2: Prefer direct placement over wrappers

If a script belongs under a canonical subfolder in `scripts/`, move it there directly.
Do not keep compatibility wrappers, mapping layers, or duplicate launcher files unless explicitly
required and justified.

### Rule 3: Group by operational purpose

Scripts should be grouped by what they do, for example build, audit, migration, diagnostics,
or backtest tooling, instead of by who happened to write them.

### Rule 4: Keep script names task-oriented

A script name should reveal its job clearly enough to be found via search or folder scanning.
Avoid vague names such as `run_once`, `tmp_fix`, or `misc_tools`.

## Layout rules for `docs/`, `.github/`, `registry/`, and `data/`

### Rule 1: Organize support zones by document or asset type

Use coarse, understandable taxonomy in support zones.
For example, documentation should be grouped by operational purpose, audit class, architecture,
feature area, or workflow stage rather than by author preference.

### Rule 2: Keep governance, policy, audit, and operational docs distinct

Do not mix constitutional or governance material with routine layout guidance, implementation notes,
or one-off audit artifacts.

For example, repository layout guidance belongs in a practical docs location such as
`docs/repository-layout-policy.md`, not in `AGENTS.md`.

### Rule 3: Use `.github/` for repository automation and Copilot/GitHub behavior only

Files under `.github/` should exist because they configure repository automation, contribution flows,
or agent behavior in GitHub/VS Code contexts.

Do not use `.github/` as a general storage area for arbitrary documentation or scratch material.

### Rule 4: Keep `registry/` and `data/` taxonomy explicit

Folders under `registry/` and `data/` should signal whether material is curated, raw, archived,
fixture-like, schema-driven, or generated.

Avoid names that blur whether a dataset or registry artifact is authoritative, intermediate,
or disposable.

## Layout rules for output and hygiene zones

### Rule 1: Keep generated outputs out of active source areas

Generated artifacts, cached material, results, logs, and temporary outputs should live in their
designated zones rather than creeping into `src/`, `tests/`, `scripts/`, or the repo root.

### Rule 2: Distinguish active, curated, and archival material

If a file or folder is retained for history, quarantine, or deferred cleanup, place it in an archival
or explicitly non-active zone rather than leaving it beside active implementation files.

### Rule 3: Contain temporary work explicitly

Temporary material should live in locations such as `tmp/` or another clearly temporary bucket.
If it becomes durable, move it into a proper long-lived home.

### Rule 4: Do not treat output zones as long-term junk drawers

These zones may be broader and less strictly structured than source areas, but they still require
intentional naming and visible lifecycle boundaries.

## Layout rules for the repository root

### Rule 1: Root is for true root-level control files and top-level entry folders

Files in the root should justify their presence by repo-wide control, discovery, or onboarding value.
Typical root-level candidates include top-level manifests, repo-wide readmes, and primary policy files.

### Rule 2: Avoid root-level drift

Do not add new root files when the content clearly belongs in `docs/`, `scripts/`, `config/`,
`tools/`, `tests/`, or an output zone.

### Rule 3: Prefer one good home over “temporary for now” root placement

Root-level temporary placement has a habit of becoming permanent. Choose the proper folder early.

## When to choose each structure

### Choose a single file when

- the module is still readable end to end
- one reader can understand the full flow without scrolling into orbit
- extracted files would mostly be pass-through noise

### Choose sibling modules when

- responsibilities are distinct and nameable
- each file has a stable role
- the resulting names improve discoverability

### Choose a `_parts/` package when

- one parent module owns a larger internal implementation surface
- several internal clusters exist
- those clusters are not independent enough to deserve first-class peer status

### Choose a helper file when

- the extracted logic is local support code
- the role is real but small
- a package would be over-structured for the amount of code

### Choose a new top-level zone or subfolder only when the category is durable

- the content type is likely to persist
- the category improves navigation for future work
- the folder represents something more stable than one temporary campaign or cleanup wave

## When to split a module

Split when:

- a clear sub-domain or internal cluster exists
- multiple responsibilities appear in the same file
- readability is declining, especially in larger modules
- extracted parts can be named more clearly than the current whole

Consider splitting when:

- the file grows beyond roughly 500-800 lines
- one reader can no longer follow the full flow comfortably

Line count is a warning signal, not a rule by itself.

Do not split when:

- only one small function would be extracted
- the new file would be only a wrapper or pass-through layer
- the new names become weaker, vaguer, or more generic
- the split reduces line count but not actual complexity

## Anti-patterns

Avoid introducing any of the following unless there is a documented reason:

- one-function-per-file fragmentation
- generic helper dumping grounds
- duplicate mapping layers
- wrapper modules with no domain value
- `*_v2`, `*_new`, `*_final`, or similar naming drift
- root-level script clutter
- new root-level tests when an appropriate subfolder already exists
- root-level output drift
- config scattered across unrelated folders without clear authority
- dumping operational notes into constitutional or governance documents

## Review checklist for future changes

Before adding a new module or folder, ask:

1. Which domain owns this behavior?
2. Is this a real role, a local helper, or just extracted line count?
3. Would a descriptive sibling be clearer than a generic helper?
4. Is a `_parts/` package justified by multiple internal clusters?
5. Should the tests stay in an existing file or move into a clearer domain bucket?
6. Does this script belong in a canonical `scripts/` subfolder?
7. Does this belong in `tools/`, `config/`, `docs/`, `.github/`, `registry/`, or a data/output zone instead?
8. Should this be in the repo root at all?
9. Am I reducing complexity, or just moving it sideways?

## Status of this document

This file is a first repo-specific draft.
It should be refined incrementally against real refactor decisions across the repository,
especially in `src/`, `tests/`, `scripts/`, `tools/`, `config/`, and `docs/`.

It is intended to guide placement and naming decisions, not to replace engineering judgment.
