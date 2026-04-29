# RI advisory environment-fit — Phase 3 non-runtime evidence namespace

This memo is docs-only and fail-closed.
It decides where the corrected Phase C RI donor should live if Phase 3 is to continue without smuggling runtime-valid carrier authoring into the lane.

Governance packet: `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_non_runtime_evidence_namespace_packet_2026-04-17.md`

## Source surface used

- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_strategy_family_bridge_admissibility_2026-04-17.md`
- `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json`
- `src/core/research_ledger/models.py`
- `src/core/research_ledger/service.py`
- `src/core/research_ledger/storage.py`
- existing top-level `artifacts/` layout

## Decision question

What namespace can hold the Phase C donor as fixed RI research evidence without making it runtime-config or reintroducing the blocked `strategy_family` bridge problem?

## Short answer

**Use a ledger-primary / bundle-secondary non-runtime evidence namespace.**

That means:

1. the authoritative identity for the frozen donor should be a `research_ledger` `ArtifactRecord`, and
2. the concrete frozen payload should live under a non-runtime artifact path such as `artifacts/bundles/...`, referenced by the ledger record.

This is the smallest admissible Phase 3 opening because it preserves provenance and RI classification while staying outside runtime config surfaces.

## Why this namespace is admissible

### 1. `artifacts/research_ledger` is already a real repository surface

`src/core/research_ledger/storage.py` resolves a stable ledger root at:

- `artifacts/research_ledger/`

with dedicated entity folders and deterministic JSON persistence.
This is already a repo-native evidence namespace.
It is not a proposed abstraction.

### 2. Ledger artifact records are not runtime config

`src/core/research_ledger/models.py` defines `ArtifactRecord` with fields such as:

- `artifact_kind`
- `path`
- `role`
- `checksum_sha256`
- `metadata`

That shape is evidence-oriented, not runtime-authoritative.
Nothing in the ledger model makes an artifact path executable strategy config by itself.

### 3. Strategy family can live as ledger metadata without mutating donor `cfg`

`ResearchLedgerService.append_record_with_strategy_family(...)` can tag a record with `strategy_family` metadata.
For a non-runtime artifact record, the family can be carried as metadata on the record rather than injected into donor `cfg`.

That metadata is descriptive only.
It must not be treated as runtime config identity for the donor payload.

That keeps the key distinction intact:

- `strategy_family` as runtime config identity remains blocked inside donor `cfg`
- `strategy_family` as evidence classification remains admissible at the ledger layer

This is exactly the separation Phase 3 now needs.

### 4. Bundle paths under `artifacts/` already fit the payload side of the problem

The repository already has non-runtime artifact roots such as:

- `artifacts/bundles/`
- `artifacts/diagnostics/`
- `artifacts/intelligence_shadow/`

So a frozen Phase C donor snapshot does not need to invent a new top-level surface.
It can be placed under a bundle-style path and referenced from the ledger.

## Recommended namespace shape

The preferred pattern is:

- **Primary identity:** `research_ledger` artifact record
- **Concrete payload:** bundle file under `artifacts/bundles/ri_advisory_environment_fit/...`

The bundle should contain only non-runtime evidence material, for example:

- raw donor artifact copy or canonical snapshot
- extracted donor `merged_config` as evidence payload
- provenance metadata
- checksum / version notes
- explicit statement that the payload is not runtime-authoritative

## What should not be used

### Not `config/strategy/candidates/**`

That surface is too close to runtime carrier semantics and is now explicitly tied to the blocked bridge problem.
Even if inertness was proven for champion loading, the surface still invites semantic confusion about carrier status.

### Not `tmp/**`

`tmp/` is too weak for a fixed Phase 3 evidence surface.
It does not provide the provenance or permanence expected for a bounded RI research lane.

### Not ledger-only without payload snapshot

A ledger record without a frozen payload path is too thin.
Phase 3 needs a fixed object that later capture-v2 work can reference deterministically.
So the ledger should identify the object, but a bundle path should hold the actual frozen snapshot.

Every ledger entry in the future implementation slice should therefore reference one concrete frozen payload under `artifacts/**`.

## Admissibility verdict

A future implementation slice is admissible if it does only this:

1. create one non-runtime frozen donor snapshot under `artifacts/bundles/...`
2. register it as an `ArtifactRecord` in `artifacts/research_ledger/...`
3. attach RI family classification at the ledger metadata level
4. avoid any runtime-valid carrier authoring

That future slice should keep its practical scope IN only under `artifacts/**`.
The following should remain explicitly scoped OUT:

- `config/strategy/candidates/**`
- `tmp/**`
- ConfigAuthority write/validate paths used for runtime carrier work
- any runtime consumer path that would interpret the frozen donor as executable config

That future slice would still be bounded and honest:

- not a runtime carrier
- not a champion
- not a promotion step
- not a baseline implementation
- just a fixed Phase 3 evidence object

## What that unlocks next

If the namespace decision is accepted, the next admissible implementation sequence becomes:

1. **freeze the Phase C donor as non-runtime evidence**
2. **run capture v2 against that evidence object in a research-only slice**
3. **only then define the minimal deterministic baseline**

That reopens Phase 3 without cheating the config-authority boundary.

## Bottom line

Phase 3 should proceed through a **ledger-primary / bundle-secondary non-runtime evidence namespace**.

That is the clean bridge between:

- the blocked runtime-carrier path, and
- the still-valid goal of capturing richer RI context from the corrected Phase C donor.

It is the smallest next step that preserves provenance, preserves family labeling, and keeps runtime authority untouched.
