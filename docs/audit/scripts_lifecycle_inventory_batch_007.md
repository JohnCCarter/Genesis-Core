# Batch 007 scripts lifecycle inventory audit

Date: 2026-05-22
Mode: `RESEARCH`
Observed branch/worktree: `feature/genesis-topology-lifecycle-authority-map`
Status: `read-only lifecycle inventory / non-authorizing / docs-only / no behavior change`

> This file is a bounded audit/inventory artifact for the `scripts/` zone.
> It does **not** move scripts, archive scripts, delete scripts, or rewrite script behavior by
> itself.
>
> Batch controller for this slice: `docs/system/GENESIS_TOPOLOGY_WORK_QUEUE.md`
> (`Batch 007 — scripts lifecycle`).

## Scope boundary

This audit starts with the current scripts-lifecycle documentation surface rather than the full
script tree.

Primary candidate in scope:

- `scripts/docs/README.md`

Supporting evidence surfaces in scope:

- `docs/repository-layout-policy.md`
- `docs/knowledge/GENESIS_TOPOLOGY_LIFECYCLE_AUTHORITY_MAP.md`
- current `scripts/` folder shape

Out of scope in this batch:

- moving any script
- deleting any script
- reclassifying actual script code paths one by one
- changing runtime/test/build behavior
- archive-prep execution work

## Method

Checked in this slice:

- full read of `scripts/docs/README.md`
- supporting policy read for `docs/repository-layout-policy.md` (`scripts/` rules)
- current `scripts/` folder listing
- existence checks for lifecycle tools named in `scripts/docs/README.md`
- exact string hits for wrapper/deprecation guidance named in `scripts/docs/README.md`

Machine-readable evidence artifact:

- `artifacts/diagnostics/batch007_scripts_lifecycle_evidence.json`

## Observed

### Current `scripts/` tree shape

Observed purpose-based subfolders in the current checked-in tree:

- `analyze/`
- `audit/`
- `build/`
- `deploy/`
- `docs/`
- `extract/`
- `fetch/`
- `mcp/`
- `ops/`
- `optimize/`
- `preflight/`
- `promote/`
- `run/`
- `train/`
- `validate/`

Observed retained root-level script files:

- `mcp_session_preflight.py`
- `paper_trading_runner.py`
- `run_skill.py`
- shell / PowerShell helpers such as `capture_paper_rc.sh`, `set_bitfinex_env.ps1`,
  `wait_for_paper.sh`, `weekend_bot_gate.sh`

Observed reading:

- the current tree is primarily purpose-based, not wrapper-first and not organized around a
  committed deprecate-wrapper workflow

### Current policy support

Observed policy support in `docs/repository-layout-policy.md`:

- scripts belong in canonical purpose-based locations under `scripts/`
- direct placement is preferred over wrappers
- compatibility wrappers, mapping layers, or duplicate launchers should not be kept unless
  explicitly required and justified

Observed support in `docs/knowledge/GENESIS_TOPOLOGY_LIFECYCLE_AUTHORITY_MAP.md`:

- `scripts/` is a mixed active + controlled deprecation zone
- safest bias is canonical purpose-based placement, not casual wrapper proliferation

### Drift inside `scripts/docs/README.md`

Observed stale or unsupported guidance in the current README:

- it defines a `deprecated` category as scripts moved to archive while wrappers remain on the old
  path
- it instructs a wrapper-based deprecation flow and a 14-day wrapper window
- it names a repo-wide audit command via `scripts/audit_scripts.py`
- it names a deprecate helper via `scripts/deprecate_move.py`
- it names a usage log via `scripts/deprecated-usage.log`

Observed evidence result:

- `scripts/audit_scripts.py` was **not** found in the current tree
- `scripts/deprecate_move.py` was **not** found in the current tree
- `scripts/deprecated-usage.log` was **not** found in the current tree
- the wrapper/deprecate guidance therefore reads as stale documentation rather than a truthful
  description of current committed tooling

## Inferred

- `scripts/docs/README.md` is still intended to be an active scripts-lifecycle guide, but it needs
  a docs-only policy-alignment pass
- the safe current fix is documentation alignment, not script movement
- the patch-safe change in this batch is to rewrite `scripts/docs/README.md` so it:
  - describes the current purpose-based scripts taxonomy truthfully
  - aligns with the canonical no-wrapper-by-default repo policy
  - stops pointing readers to non-existent lifecycle tooling
  - keeps archive/deprecation work framed as a separate bounded slice rather than an assumed default
    wrapper flow

## Unverified

- `UNRESOLVED:` whether a later `scripts/` lifecycle slice should normalize the retained root-level
  helper scripts into canonical subfolders or keep them as explicit entrypoint exceptions
- `UNRESOLVED:` whether a future committed repo-wide scripts inventory tool should exist again, or
  whether bounded audit slices plus targeted search remain the intended operating model
- `UNRESOLVED:` whether a future archive-prep workflow for scripts should use an explicit
  `scripts/archive/**` taxonomy in the checked-in tree or remain a later design choice

## Batch result summary

- Candidates reviewed in this bounded slice: `1`
- `READY_POLICY_ALIGNMENT`: `1`
- `KEEP_AS_IS`: `0`
- `UNKNOWN_KEEP`: `0`

## Candidate table

| Candidate                | Observed role                  | Evidence of drift                                                                                                    | Classification           | Safe change in this batch                                                                       |
| ------------------------ | ------------------------------ | -------------------------------------------------------------------------------------------------------------------- | ------------------------ | ----------------------------------------------------------------------------------------------- |
| `scripts/docs/README.md` | active scripts-lifecycle guide | wrapper-first deprecate flow conflicts with current layout policy; named lifecycle tools/log are not present in tree | `READY_POLICY_ALIGNMENT` | rewrite current guidance to match purpose-based placement and no-wrapper-by-default repo policy |

## What changed vs. what did not change

This audit supports changing:

- current docs wording in `scripts/docs/README.md`
- current routing/policy wording so it matches the checked-in tree and the higher-order layout
  guidance

This audit does **not** support changing:

- actual script paths
- archive placement of any script
- deletion of any script
- creation of wrapper shims
- runtime, config, test, or build behavior

## Bottom line

Batch 007 has a small docs-only follow-up available immediately.

The truthful next move is **not** to touch script code.
It is to align `scripts/docs/README.md` with:

1. the current purpose-based `scripts/` tree
2. the repository layout rule that direct placement is preferred over wrappers
3. the fact that the README currently names lifecycle tools/log files that are not present in the
   committed tree
