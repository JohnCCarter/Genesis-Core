# Research findings bank — repo-native structure

This memo is docs-only and fail-closed.
It decides how the repository can track research findings correctly without losing context between packets, evidence runs, and later follow-up slices.

Governance packet: `docs/decisions/research_findings/research_findings_bank_repo_native_packet_2026-04-24.md`

## Source surface used

- `src/core/research_ledger/models.py`
- `src/core/research_ledger/service.py`
- `src/core/research_ledger/storage.py`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_non_runtime_evidence_namespace_2026-04-17.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_release_failset_evidence_2026-04-24.md`
- `docs/analysis/regime_intelligence/policy_router/ri_policy_router_weak_pre_aged_release_cooldown_displacement_diagnosis_2026-04-24.md`
- existing top-level `artifacts/` layout

## Decision question

How should the repository keep track of findings correctly so that research conclusions remain searchable, attributable, and recoverable without introducing a separate traditional database or widening runtime authority?

## Short answer

**Use a repo-native findings bank built on the existing `research_ledger` + `artifacts` substrate.**

The minimal durable shape should be:

1. **ledger-primary identity** via existing `ArtifactRecord` registration,
2. **bundle-secondary payloads** that hold the concrete finding bundles under `artifacts/bundles/findings/...`, and
3. **one deterministic derived index** (for browsing/query) under `artifacts/research_ledger/indexes/findings_index.json`.

This is the cheapest admissible structure because it preserves provenance, stays file-backed, and does not require a new DB or a new runtime authority surface.

## Why a findings bank is worth doing

The repository already preserves:

- candidate lifecycle metadata,
- governance packets,
- fail-set evidence notes,
- row-level artifacts,
- result bundles.

What is still easy to lose is the _meaning_ of those materials across time, for example:

- which seam was actually hit,
- whether the result was positive, negative, mixed, or blocked,
- which mechanism explained the outcome,
- which timestamps were the anchor rows,
- which evidence artifacts proved the claim,
- which next bounded step became admissible afterward.

Those items are findings.
They should be preserved as first-class research evidence, not left only as prose scattered across packets and diagnosis notes.

## Why the existing ledger substrate is the right base

### 1. The repository already has stable file-backed identity

`src/core/research_ledger/storage.py` resolves a stable ledger root under:

- `artifacts/research_ledger/`

with deterministic JSON persistence and stable entity IDs.

That means the repository already has a durable, auditable place to anchor evidence identity.
There is no need to introduce SQLite, Postgres, or another external store just to solve findings traceability.

### 2. `ArtifactRecord` already fits evidence registration

`src/core/research_ledger/models.py` defines `ArtifactRecord` with fields such as:

- `artifact_kind`
- `path`
- `role`
- `checksum_sha256`
- `metadata`

That shape is already appropriate for registering a concrete findings bundle as evidence.
The finding payload can live in a bundle file while the ledger record gives it stable identity and provenance.

### 3. Existing service behavior already supports metadata tagging

`ResearchLedgerService.append_record_with_strategy_family(...)` shows the ledger can already carry descriptive metadata without changing runtime identity.

The same principle should apply here:

- findings metadata is descriptive evidence metadata,
- not runtime selection authority,
- not promotion/champion authority,
- not config identity.

### 4. The repository already has artifact namespace patterns that fit findings bundles

The top-level `artifacts/` tree already contains bundle- and evidence-oriented roots.
So a findings bank can fit repo conventions instead of inventing a new top-level surface.

## Recommended identity split

The important separation is:

- **candidate identity** = what was tried
- **finding identity** = what was learned
- **artifact identity** = what concrete files prove it

These are related, but they are not interchangeable.

That distinction matters because:

- one candidate can generate several findings,
- one finding can cite several artifacts,
- one finding can veto a candidate without deleting candidate history,
- one finding can supersede an earlier finding while preserving lineage.

So the findings bank should not be collapsed into the candidate registry alone.

## Recommended namespace shape

### Primary identity

Each finding should be registered as a ledger-backed evidence object through an `ArtifactRecord` under the existing ledger root.

That keeps the identity layer inside the already-governed substrate:

- `artifacts/research_ledger/artifacts/ART-<year>-<nnnn>.json`

### Concrete payload

Each finding should have one concrete bundle payload under a dedicated findings bundle root, for example:

- `artifacts/bundles/findings/<domain>/<finding_slug>.json`

Examples of `<domain>` for current work could include:

- `ri_policy_router`
- `ri_router_replay`
- `strategy_candidate_lifecycle`

### Derived browse/query index

The repository should eventually materialize one deterministic projection for browsing and quick filtering, for example:

- `artifacts/research_ledger/indexes/findings_index.json`

That index should be treated as a derived view, not as the authoritative source.
Authoritative truth remains the combination of ledger record + finding bundle payload.

## Recommended minimum finding bundle shape

Each finding bundle should carry enough structure to make the conclusion searchable and auditable without rereading every supporting doc.

Recommended fields:

- `finding_id`
- `created_at`
- `subject`
- `domain`
- `symbol`
- `timeframe`
- `window`
- `candidate_refs`
- `seam_class`
- `verdict` (`positive | negative | mixed | blocked`)
- `mechanism`
- `key_timestamps`
- `metrics_summary`
- `evidence_refs`
- `related_findings`
- `supersedes`
- `next_admissible_step`
- `governance_lane`
- `runtime_authority` (must be explicit and non-runtime, e.g. `none`)

The exact initial schema can stay small, but the bundle must always answer:

1. what was tested or observed,
2. what was learned,
3. what evidence proves it,
4. what should happen next.

## Why not start with a separate traditional database

For the repository’s current needs, a separate DB would be heavier than necessary.

It would add:

- another authority surface,
- operational complexity,
- migration and backup questions,
- extra drift risk between DB rows and repo artifacts.

The repo already prefers deterministic, file-backed, reviewable surfaces.
The findings bank should follow that pattern first.

If later query pressure proves the file-backed shape insufficient, a stronger store can still be evaluated from evidence.
That is not the honest first move now.

## Why not start by adding a new dedicated ledger entity type

That may become useful later, but it is not the smallest admissible first step.

A new entity type would require code, validation, storage, index, and test expansion.
The repository can prove value earlier by using:

- existing `ArtifactRecord` identity,
- finding bundle payloads,
- one derived findings index.

That keeps the first implementation low-risk and evidence-led.

## First bounded population for current work

The current RI router work already supplies a good seed set for a first findings bank population.

Good initial entries would include at least:

1. the `aged weak continuation guard` fail-set-negative result,
2. the split-seam direction lock,
3. the seam-A weak pre-aged release fail-set-negative result,
4. the cooldown displacement diagnosis explaining the chained no-trade pocket and two-bar release shift.

That seed set is small, recent, and already well-supported by existing docs and artifacts.

## Smallest admissible implementation after this memo

The next honest implementation slice should remain non-runtime and low-risk.

It should do only this:

1. define one minimal finding-bundle schema,
2. write a small set of finding bundle JSON payloads for the current RI router case,
3. register those bundles as ledger `ArtifactRecord` evidence,
4. materialize one deterministic `findings_index.json` projection.

It should **not** do any of the following:

- create a separate DB,
- create runtime consumers,
- change candidate/champion authority,
- blur finding identity into runtime config identity,
- claim promotion or readiness.

## Bottom line

The repository should keep track of findings through a **repo-native findings bank**.

The clean first shape is:

- **ledger-primary identity**,
- **bundle-secondary finding payloads**,
- **derived deterministic findings index**.

That is enough to preserve what was learned, why it mattered, and what should happen next — without inventing a second system or widening runtime authority.
