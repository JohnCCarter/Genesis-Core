# Candidate16 — First Review (2026-03-09)

## Scope reviewed

- `archive/2025-11-03/**`
- `archive/model_optimization/**`

## Inventory summary

- Total files in review scope: **72**
- Extension mix:
  - `.json`: 50
  - `.py`: 12
  - `.yaml`: 8
  - `.backup`: 1
  - `.md`: 1

Detailed inventory is recorded in:

- `docs/audit/refactor/evidence/candidate16_archive_inventory_2026-03-09.txt`

## External reference scan

- Repository-wide scan found **no explicit references** to:
  - `archive/2025-11-03`
  - `archive/model_optimization`

Recorded in:

- `docs/audit/refactor/evidence/candidate16_archive_refscan_2026-03-09.txt`

## Risk findings

1. `archive/model_optimization/update_1d_config.py` contains write logic to active config path (`config/timeframe_configs.py`) if executed.
2. Multiple archive python files include debug/test behavior and local `sys.path` manipulation patterns.
3. `tmp_configs/*.json` appear to be temporary experiment snapshots with low long-term value unless explicitly retained for provenance.

## Proposed classification (review stage)

### KEEP (historical evidence)

- `archive/2025-11-03/config_models/**`
- `archive/2025-11-03/models_trimmed/**`
- `archive/2025-11-03/optimizer_configs/**`
- `archive/2025-11-03/docs/**`
- `archive/model_optimization/1d_optimized_configs.json`

### QUARANTINE / Caution (executable legacy)

- `archive/2025-11-03/debug_scripts/*.py`
- `archive/2025-11-03/scripts/*.py`
- `archive/model_optimization/*.py`

### LOW-Priority candidates (requires explicit signoff)

- `archive/2025-11-03/tmp_configs/*.json`

## Proposed curation order (no behavior change)

1. **Data-first pass:** normalize static json/yaml/md storage layout only.
2. **Script quarantine pass:** isolate `.py` artifacts under clearly marked legacy/executable area.
3. **Temporary configs pass:** move or prune `tmp_configs` with explicit manifest and signoff.

## Next mandatory artifact before any move/delete

- Exact **old->new path mapping manifest** per batch.
