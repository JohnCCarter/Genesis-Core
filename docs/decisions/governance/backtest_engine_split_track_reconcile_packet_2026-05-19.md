# Backtest engine split-track reconcile packet

Date: 2026-05-19
Branch: `feature/risk-hardening-wave2`
Status: `truthfulness-only / reconcile / non-authorizing`

This document records branch-current tracked evidence for parked item `#15` as of 2026-05-19. It does not authorize implementation, approve an engine split, approve a strict pre-code packet, or replace a later strict packet if one is opened.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/risk-hardening-wave2`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice is docs-only truthfulness/reconciliation work; the main risk is overstating absence-of-evidence as if it were implementation guidance
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why: this slice reconciles a historical carry-forward claim against current tracked branch evidence only
- **Skill usage:** `none required` — bounded docs-only reconcile slice; no repo-local skill matched this work
- **Objective:** establish the smallest honest current-branch reading of parked item `#15` before any strict pre-code packet is considered
- **Candidate line:** `future #15 backtest-engine modularization follow-up, if later reopened from current tracked evidence`
- **Base SHA:** `8a7b88c65bfcc45034f35cd7a7a61266fda7dbe7`
- **Related artifacts:** `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`, `docs/audit/BACKTEST_ENGINE_AUDIT.md`, `docs/audit/refactor/htf_exit/command_packet_htf_exit_engine_split_slice1_2026-03-12.md`, `docs/audit/refactor/htf_exit/command_packet_htf_exit_engine_split_remaining_2026-03-12.md`, `src/core/backtest/engine.py`, `src/core/backtest/htf_exit_engine.py`, `src/core/backtest/htf_exit_partials.py`, `src/core/backtest/htf_exit_structure.py`, `src/core/backtest/htf_exit_swing_updates.py`, `src/core/backtest/htf_exit_trailing.py`
- **Pre-code review:** `Opus 4.6 Governance Reviewer -> APPROVED_WITH_NOTES` for a truthfulness-only reconcile slice limited to docs

### Scope

- **Scope IN:** one new truthfulness-only reconcile packet; one dated later-branch note in the historical premortem baseline; explicit separation between historical 2026-05-18 observation and current tracked branch evidence for `#15`
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; all implementation guidance for a future split; all claims that the historical worktree claim was false; all claims that no such split exists anywhere outside the current tracked branch review
- **Expected changed files:** `docs/decisions/governance/backtest_engine_split_track_reconcile_packet_2026-05-19.md`, `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md`
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation for both touched markdown files
- manual wording audit that the slice remains truthfulness-only and non-authorizing
- manual wording audit that “not identified in current review” is not silently upgraded to “does not exist”
- manual consistency review against the historical premortem baseline and current tracked repo state

### Stop Conditions

- any wording that treats this packet as approval to implement a split
- any wording that rewrites the 2026-05-18 baseline as if it had always described current branch truth
- any wording that upgrades absence-of-evidence in this checkout into proof that the separate worktree never existed
- any wording that treats `htf_exit*` split artifacts as if they resolved `src/core/backtest/engine.py`

## Purpose

This packet answers one narrow question only:

- what is the smallest honest current-branch reading of the `#15` “worktree-engine-modul-split” carry-forward on `feature/risk-hardening-wave2`?

## What changed in this slice

- one new reconcile packet records the branch-current tracked evidence for `#15`
- one dated later-branch note is added to the historical premortem baseline so readers do not over-read the 2026-05-18 `MEMORY.md` / `worktree-engine-modul-split` line as current tracked branch evidence

## What did not change

- no source files changed
- no engine split was implemented
- no strict pre-code packet was opened
- no runtime/backtest behavior changed
- no queue or readiness authority changed

## Governing basis

### Observed

1. `docs/analysis/diagnostics/genesis_core_deep_premortem_project_baseline_2026-05-18.md` is the only tracked artifact identified in the current review that directly ties `#15` to `MEMORY.md` and `worktree-engine-modul-split`.
2. A repo-wide tracked file search in the current review did **not** identify a `MEMORY.md` file in this checkout.
3. A repo-wide tracked search in the current review found `worktree-engine-modul-split`, `engine-modul-split`, and `MEMORY.md` references only in the historical premortem baseline noted above.
4. Current branch state still carries `src/core/backtest/engine.py` as a large hot file; current measured line count in this review is `1557`.
5. Current tracked `src/core/backtest/` also carries `htf_exit_engine.py` plus helper modules `htf_exit_partials.py`, `htf_exit_structure.py`, `htf_exit_swing_updates.py`, and `htf_exit_trailing.py`.
6. The tracked `htf_exit` split command packets explicitly scope `src/core/backtest/engine.py` **OUT**, so those artifacts do not by themselves carry `#15`'s engine-file modularization claim.

### Inferred

- the 2026-05-18 premortem baseline contains a **historical carry-forward observation** about a separate worktree, not a current tracked branch proof artifact for this checkout
- current tracked branch evidence is therefore **not yet sufficient** to support a strict pre-code packet for `#15` that relies on the claimed `worktree-engine-modul-split` line
- `htf_exit*` split artifacts are current tracked repo history, but they are a different split track and cannot honestly be cited as proof that `src/core/backtest/engine.py` has already been modularized on this branch
- the current `#15` truth is simpler: `src/core/backtest/engine.py` remains the hot file on this branch, while the claimed separate-worktree engine split is not identified as a tracked in-repo carrier in the present review

### Unverified in this packet

- whether the separate worktree split existed outside the current tracked branch review
- whether that worktree should later be surfaced as a tracked carrier
- whether a future strict pre-code packet should be opened from current `engine.py` reality instead of from the historical worktree claim

## Current standing conclusion

For `feature/risk-hardening-wave2`, the smallest honest `#15` reading is:

- `#15` remains open as a current hot-file / change-blast-radius concern around `src/core/backtest/engine.py`
- the historical `MEMORY.md` / `worktree-engine-modul-split` carry-forward must **not** be read as current tracked branch evidence in this checkout
- current tracked branch evidence is **not yet sufficient** to support a strict pre-code packet that depends on that carry-forward claim

This is a truthfulness conclusion only. It does **not** decide whether a future engine split should or should not happen.

## Next admissible move

If work continues on `#15`, the next honest move may only be one of these:

1. surface a tracked current-branch carrier for the claimed separate worktree split, or
2. open a later separately governed strict pre-code packet that is grounded directly in the current `src/core/backtest/engine.py` hot-file reality rather than in the historical carry-forward claim

This packet authorizes neither path by itself.

## Bottom line

On the current branch review, `#15` should be read as a still-open `engine.py` hot-file risk, not as an already-grounded split-in-progress on this checkout. The historical premortem line remains useful as historical context, but current tracked branch evidence is not yet sufficient to treat `worktree-engine-modul-split` as a live carrier for a strict pre-code packet.
