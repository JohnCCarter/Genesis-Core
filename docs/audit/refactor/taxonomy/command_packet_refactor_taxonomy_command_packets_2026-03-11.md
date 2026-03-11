# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/* -> RESEARCH`)
- **Risk:** `LOW` — why: documentation-only taxonomy move
- **Required Path:** `Full`
- **Objective:** Move loose refactor command/context docs from `docs/audit/refactor/` root into deterministic subfolders.
- **Candidate:** `docs-refactor-taxonomy-batch-1`
- **Base SHA:** `34848989`
- **Category:** `docs`
- **Constraints:** `NO BEHAVIOR CHANGE` (docs relocation only, no runtime/config/test code changes)
- **Done criteria:** all mapped files moved to target subfolders; no loose `command_packet*`/`context_map_*` left in refactor root; references updated if needed; full gate stack green.

## Skill Usage

- `context-map` (map files/dependencies before move)
- `refactor-plan` (safe multi-file sequence and rollback thinking)

## Scope

- **Scope IN:**
  - `docs/audit/refactor/command_packet*.md`
  - `docs/audit/refactor/context_map_*.md`
  - `docs/audit/refactor/candidate*_*.md`
  - `docs/audit/refactor/taxonomy/*.md`
  - New folders under `docs/audit/refactor/` for taxonomy buckets
- **Scope OUT:**
  - all non-doc files
  - `src/**`, `tests/**`, `config/**`, `.github/workflows/**`, `scripts/**`, `mcp_server/**`
  - `.claude/worktrees/**` (explicitly excluded; no mirrored-tree moves)
- **Expected changed files:** 120-150 (moves + taxonomy docs)
- **Max files touched:** 170

## Gates required

- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_feature_cache.py tests/utils/diffing/test_feature_cache.py tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py`

## Stop Conditions

- Scope drift outside `docs/audit/refactor/**`
- Any touched path under `.claude/worktrees/**`
- Any runtime/test/config file touched
- Ambiguous destination for any filename family
- Any source->target collision in move manifest

## Output required

- **Implementation Report**
- **Move manifest (source -> target)**
- **Collision check report (no overwrite / no duplicate destination)**
