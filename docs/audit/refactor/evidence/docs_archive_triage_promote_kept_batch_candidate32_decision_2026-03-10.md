# Triage Decision — Candidate32 promote kept docs from archive (2026-03-10)

## Decision

Promote 5 previously retained archive docs into active `docs/**` subfolders.

## Selection rationale

- User requested that retained files be moved out of deprecated archive into corresponding subfolders.
- All 5 source files exist and all 5 destination files are currently absent (no overwrite risk).
- Move-only action preserves content while reducing dependency on deprecated archive location.

## Candidate32 in-scope moves

1. `docs/archive/deprecated_2026-02-24/docs/config/CHAMPION_REPRODUCIBILITY.md` -> `docs/config/CHAMPION_REPRODUCIBILITY.md`
2. `docs/archive/deprecated_2026-02-24/docs/mcp/privacy-policy.md` -> `docs/mcp/privacy-policy.md`
3. `docs/archive/deprecated_2026-02-24/docs/optimization/optimizer.md` -> `docs/optimization/optimizer.md`
4. `docs/archive/deprecated_2026-02-24/docs/performance/OPTUNA_OPTIMIZATIONS.md` -> `docs/performance/OPTUNA_OPTIMIZATIONS.md`
5. `docs/archive/deprecated_2026-02-24/docs/performance/PERFORMANCE_GUIDE.md` -> `docs/performance/PERFORMANCE_GUIDE.md`
