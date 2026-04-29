# SCPE RI V1 shadow-backtest bridge slice1 containment-fix pre-code packet

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code-defined / hypothesis-only / no implementation authorization`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: this packet is a docs-only pre-code definition for one possible no-behavior-change containment-fix slice; it does not authorize code changes and it does not change writable surfaces.
- **Required Path:** `Quick`
- **Objective:** define one bounded pre-code hypothesis for removing the out-of-bound filesystem-touch side effect from the future RI-only shadow-backtest bridge slice1 run surface without changing canonical CLI behavior, bounded output paths, runtime merge behavior, backtest metrics logic, or intelligence-shadow derivation logic.
- **Candidate:** `shadow-backtest bridge slice1 containment fix`
- **Base SHA:** `f2284ebf`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Hypothesis-only / non-authorizing`
- `No writable-surface expansion`
- `No runtime/paper/readiness/promotion reopening`
- `Future code slice requires separate approval`

### Skill Usage

- **Applied repo-local skill:** none in this packet
- **Reason:** this artifact is docs-only and does not yet execute an implementation workflow.
- **Reserved for any later code slice:** `repo_clean_refactor`
- **Possible supporting analysis for any later code slice:** `python_engineering`
- **Not claimed:** no skill coverage is claimed as completed by this packet.

### Scope

- **Scope IN:**
  - one docs-only pre-code packet for one minimal containment-fix hypothesis targeting `scripts/run/run_backtest.py`
  - explicit problem statement tied to the unconditional `config/__init__.py` touch side effect
  - explicit preferred fix hypothesis
  - explicit proof requirements before any later code slice may proceed
  - explicit non-goals and stop conditions
- **Scope OUT:**
  - no code changes
  - no `src/**` changes
  - no `tests/**` changes
  - no writable-surface exception approval
  - no runtime integration, paper coupling, readiness, cutover, or promotion widening
  - no launch reauthorization
- **Expected changed files:** `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_precode_packet_2026-04-21.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- no sentence may authorize code changes
- no sentence may claim proof of safety already exists
- no sentence may treat the preferred fix hypothesis as already approved
- no sentence may widen writable surfaces
- no sentence may let this packet's `LOW / Quick` classification bleed into any later code slice

### Stop Conditions

- any wording that treats the fix as already safe or already approved
- any wording that treats writable-surface expansion as co-equal preferred remediation
- any wording that claims config-package resolution is already proven unchanged after removal
- any wording that authorizes implementation from this packet
- any need to modify files outside this one scoped packet

### Output required

- reviewable containment-fix pre-code packet
- explicit preferred fix hypothesis
- explicit proof requirements before implementation
- explicit statement that future code remains separately governed

## Purpose

This packet records a **föreslagen** no-behavior-change containment-fix hypothesis for a later separately governed code slice targeting `scripts/run/run_backtest.py`.

It does **not** authorize implementation, does **not** claim proof of safety, and does **not** widen writable surfaces.

Fail-closed interpretation:

> Preferred hypothesis: remove the unconditional `config` mkdir/touch side effect from the canonical run surface only if a focused proof later demonstrates unchanged config-package resolution and unchanged canonical run behavior. If that proof is incomplete or fails, no implementation is authorized under this packet.

## Upstream governed basis

This packet is downstream of the following tracked documents:

- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_launch_authorization_packet_2026-04-21.md`
- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_write_boundary_audit_2026-04-21.md`

Carried-forward meaning from those packets:

1. the future launch verdict remains `NOT AUTHORIZED NOW`
2. bounded write containment is not green
3. the current run surface includes an unconditional filesystem-touch call against `config/__init__.py`
4. preferred future remediation is a separate governed code fix rather than writable-surface expansion

This packet does **not** change any of those already-recorded conclusions.

## Exact target surface

The exact later code target hypothesized by this packet is:

- `scripts/run/run_backtest.py`

The exact current repo-visible side-effect surface under discussion is:

- `CONFIG_DIR = ROOT_DIR / "config"`
- `CONFIG_DIR.mkdir(exist_ok=True)`
- `(CONFIG_DIR / "__init__.py").touch(exist_ok=True)`

## Problem statement

The write-boundary audit established that the current repo-visible run surface contains an out-of-bound filesystem-touch side effect relative to the already-approved writable surfaces for the RI-only shadow bridge slice1.

That side effect prevents bounded write containment from being marked green.

The problem this packet isolates is therefore:

- can that out-of-bound side effect be removed from the canonical run surface without changing package resolution or any other audited behavior that the RI shadow bridge slice depends on?

## Preferred fix hypothesis

The preferred fix hypothesis is:

- remove the `CONFIG_DIR.mkdir(exist_ok=True)` and `(CONFIG_DIR / "__init__.py").touch(exist_ok=True)` block from `scripts/run/run_backtest.py`

This remains a **preferred hypothesis only**.
It is not a verified safe fix and it is not approved implementation.

### Why this is the preferred hypothesis

Based on current repo state visible in this session:

- the repository already contains `config/__init__.py`
- the script already inserts both repo root and `src` into `sys.path`
- the containment blocker is localized to a small, explicit block at module scope in `scripts/run/run_backtest.py`

That makes full removal the narrowest currently visible candidate remediation.

### What this packet does not assume

This packet does **not** assume that:

- full removal is already safe
- config-package resolution is already proven unchanged after removal
- no fallback condition exists elsewhere in the canonical run surface
- the later code slice may proceed without proof and separate approval

## Required proof before any later implementation slice may proceed

No implementation may proceed from this packet unless a later governed code slice includes proof that removing the mkdir/touch block preserves canonical config-package resolution and leaves the audited run surface behavior unchanged.

That proof must be produced in that later code slice; this packet contains no such proof.

At minimum, the required proof set must include:

### 1. Focused canonical-run smoke

A later code slice must prove that the canonical run surface still starts and resolves required packages without the mkdir/touch block.

### 2. Targeted config-package resolution proof

A later code slice must prove that `config` package resolution remains intact from tracked repo state without runtime creation or touching of `config/__init__.py`.

### 3. No-behavior-change boundary proof

A later code slice must explicitly preserve, and then verify unchanged behavior for:

- canonical CLI flags
- bounded decision-row output paths
- `--no-save` suppression of default result persistence
- runtime merge behavior
- backtest metrics logic
- intelligence-shadow summary and ledger-root derivation logic

### 4. Containment proof

A later code slice must prove that removal of the side effect actually makes bounded write containment green on the audited run surface without introducing another out-of-bound write-intent elsewhere.

## Non-goals

This packet does **not** define or authorize any of the following:

- writable-surface expansion
- launch reauthorization
- control or shadow execution
- test additions by default
- changes in `src/**`
- changes to intelligence-shadow derivation semantics
- changes to CLI flag semantics
- runtime integration, paper coupling, readiness, cutover, or promotion scope

## Future implementation classification boundary

This packet's `LOW / Quick` classification applies **only** to this present docs-only artifact.

Any code change to `scripts/run/run_backtest.py` remains a separate implementation slice requiring independent review, approval, and verification.
That later slice must be reclassified independently under then-current change class, risk, path, and gates, and it must not inherit this packet's docs-only classification.

## Preferred vs non-preferred future path

### Preferred future path

- a separately governed minimal code-fix slice removing the out-of-bound side effect if proof later supports it

### Non-preferred future path

- a separately governed writable-surface exception or expansion

The non-preferred path is recorded only as a rejected fallback unless separately reopened by a new governed packet.
It is **not** authorized or recommended by this packet.

## Bottom line

This packet opens one narrow next hypothesis only:

- a separately governed, no-behavior-change containment-fix slice may later be proposed against `scripts/run/run_backtest.py`
- the preferred hypothesis is full removal of the current mkdir/touch side-effect block
- that hypothesis remains **föreslagen only** until separate proof and separate approval exist

Nothing in this packet authorizes implementation, writable-surface expansion, launch reauthorization, or any broader lane widening.
