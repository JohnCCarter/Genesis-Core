# Candidate16 Proposed Mapping Plan (2026-03-09)

> Status: **föreslagen** (review/prep only, no filesystem moves applied)

## Batch A — Static historical assets (low risk)

### Source roots

- `archive/2025-11-03/config_models/**`
- `archive/2025-11-03/models_trimmed/**`
- `archive/2025-11-03/optimizer_configs/**`
- `archive/2025-11-03/docs/**`
- `archive/model_optimization/1d_optimized_configs.json`

### Proposed target roots

- `archive/curated/2025-11-03/config_models/**`
- `archive/curated/2025-11-03/models_trimmed/**`
- `archive/curated/2025-11-03/optimizer_configs/**`
- `archive/curated/2025-11-03/docs/**`
- `archive/curated/model_optimization/1d_optimized_configs.json`

### Rationale

- Immutable evidence-like payloads.
- No executable code move in this batch.

## Batch B — Executable legacy scripts (quarantine)

### Source roots

- `archive/2025-11-03/debug_scripts/*.py`
- `archive/2025-11-03/scripts/*.py`
- `archive/model_optimization/*.py` (except `1d_optimized_configs.json`)

### Proposed target roots

- `archive/quarantine/executable/2025-11-03/debug_scripts/*.py`
- `archive/quarantine/executable/2025-11-03/scripts/*.py`
- `archive/quarantine/executable/model_optimization/*.py`

### Rationale

- Prevent accidental execution assumptions.
- Preserve provenance while making risk explicit.

## Batch C — Temporary config snapshots (decision batch)

### Source roots

- `archive/2025-11-03/tmp_configs/*.json`

### Proposed target options

1. Keep: `archive/quarantine/tmp_configs/2025-11-03/*.json`
2. Prune after signoff: remove files with manifest+signoff artifact

### Rationale

- Appears ephemeral/experimental.
- Should be explicitly retained or removed (no implicit behavior).

## Preconditions before execution

1. Exact per-file old->new mapping file generated from inventory.
2. Fresh external refscan captured for all moved paths.
3. Candidate16 command packet approved for execution path.
4. Gates executed pre/post move batch.

Exact mapping artifact generated:

- `docs/audit/refactor/evidence/candidate16_exact_old_new_manifest_2026-03-09.tsv`
