# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` (`feature/* -> RESEARCH`)
- **Risk:** `LOW` — why: documentation-only taxonomy move (batch 2)
- **Required Path:** `Full`
- **Objective:** Move remaining loose markdown docs from `docs/audit/refactor/` root into deterministic subfolders while keeping canonical root anchors.
- **Candidate:** `docs-refactor-taxonomy-batch-2-loose-docs`
- **Base SHA:** `34848989`
- **Category:** `docs`
- **Constraints:** `NO BEHAVIOR CHANGE` (docs relocation only)
- **Done criteria:** mapped files moved; only canonical root anchors remain (`readme.md`, `hard_rules_refactor.md`); collision check PASS; references updated for moved overlay paths.

## Scope

- **Scope IN:**
  - `docs/audit/refactor/*_signoff_*.md`
  - `docs/audit/refactor/test_prototypes_review_2026-03-06.md`
  - `docs/audit/refactor/shard_a_breadth_audit_report_2026-03-06.md`
  - `docs/audit/refactor/genesis_refactor_agent_overlay_shard_*.md`
  - `docs/audit/refactor/tests_subfolder_classification_plan_2026-03-09.md`
  - `docs/audit/refactor/taxonomy/*.md`
  - direct docs references to moved overlay files (`docs/**/*.md`)
- **Scope OUT:**
  - all non-doc files
  - `.claude/worktrees/**`
  - `src/**`, `tests/**`, `config/**`, `.github/workflows/**`, `scripts/**`, `mcp_server/**`
- **Expected changed files:** 20-60
- **Max files touched:** 90

## Gates required

- pre-move: 1:1 move manifest generated + collision preflight PASS
- `python -m pre_commit run --all-files`
- `python -m pytest -q tests/governance/test_import_smoke_backtest_optuna.py`
- `python -m pytest -q tests/backtest/test_backtest_determinism_smoke.py`
- `python -m pytest -q tests/utils/test_feature_cache.py tests/utils/diffing/test_feature_cache.py tests/utils/test_features_asof_cache.py tests/utils/test_features_asof_cache_key_deterministic.py`
- `python -m pytest -q tests/governance/test_pipeline_fast_hash_guard.py`
- docs-link check: verify moved overlay/root-anchor references no longer point to old root overlay paths

## Stop Conditions

- Scope drift outside approved paths
- Any touched path under `.claude/worktrees/**`
- Any source->target collision in manifest
- Any runtime/test/config file touched

## Output required

- **Implementation Report**
- **Move manifest (source -> target)**
- **Collision check report**
