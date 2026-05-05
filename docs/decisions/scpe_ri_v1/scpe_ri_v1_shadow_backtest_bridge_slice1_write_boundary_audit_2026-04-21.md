# SCPE RI V1 shadow-backtest bridge slice1 write-boundary audit

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `docs-only audit / static repo-visible only / no authorization`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: this packet is a docs-only static audit of the future control/shadow run write surface, with no code/config/test/runtime changes and no execution authority.
- **Required Path:** `Quick`
- **Objective:** audit the repo-visible write surface of the future RI-only shadow-backtest bridge slice1 control/shadow run targets, record the bounded output paths visible in current code, and determine whether bounded write containment can be marked green.
- **Candidate:** `shadow-backtest bridge slice1 write-boundary audit`
- **Base SHA:** `515983b8`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Static repo-visible audit only`
- `No execution claimed`
- `No writable-surface expansion`
- `No implementation authorization`

### Skill Usage

- **Applied repo-local skill:** none
- **Reason:** this packet is a docs-only governance audit and does not authorize or execute a run-domain workflow.
- **Not claimed:** no process-coverage or run-skill coverage is claimed by this audit.

### Scope

- **Scope IN:**
  - one docs-only audit packet for the future RI-only shadow-backtest bridge slice1 write surface
  - explicit review of repo-visible write sites in `scripts/run/run_backtest.py`
  - explicit review of repo-visible shadow-summary / ledger-root derivation sites in `src/core/backtest/intelligence_shadow.py`
  - explicit conclusion on whether bounded write containment can be marked green
  - explicit preferred future remediation framing
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, or `artifacts/**` changes
  - no actual control run
  - no actual shadow run
  - no launch authorization change
  - no implementation authorization
  - no writable-surface exception approval
  - no runtime/paper/readiness/promotion reopening
- **Expected changed files:** `docs/decisions/scpe_ri_v1/scpe_ri_v1_shadow_backtest_bridge_slice1_write_boundary_audit_2026-04-21.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- no sentence may claim execution was performed in this audit
- no sentence may treat repo-visible code review as runtime-backed proof of full write exhaustiveness
- no sentence may treat `--no-save` as sufficient by itself to make containment green
- no sentence may authorize implementation or writable-surface expansion
- no sentence may reinterpret the prior `NOT AUTHORIZED NOW` verdict as changed

### Stop Conditions

- any wording that upgrades static repo-visible audit into execution proof
- any wording that treats current CLI or shadow code as already sufficient launch authority
- any wording that expands writable surfaces beyond the previously bounded paths
- any wording that authorizes a code fix or a writable-surface exception from this audit
- any need to modify files outside the one scoped packet

### Output required

- reviewable static write-boundary audit
- explicit repo-visible write-site inventory
- explicit containment verdict
- explicit preferred future remediation framing
- explicit statement that prior launch verdict is unchanged

## Purpose

This document is a **static repo-visible write-boundary audit** for the future RI-only shadow-backtest bridge slice1 control/shadow run surface.

This audit does **not** claim that the command was executed in this session.
It records only what the current repo-visible code path shows about write-intent, bounded output derivation, and containment risk.

Fail-closed interpretation:

> This audit is static and repo-visible only. It does not claim that the future control/shadow command pair was executed in this session. It records that the current run surface contains an unconditional filesystem-touch call against `config/__init__.py`, which prevents bounded write containment from being marked green.

## Upstream governed basis

This packet is downstream of the following tracked documents:

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_shadow_backtest_bridge_slice1_precode_packet_2026-04-21.md`
- `docs/decisions/scpe_ri_v1/scpe_ri_v1_shadow_backtest_bridge_slice1_setup_only_packet_2026-04-21.md`
- `docs/decisions/scpe_ri_v1/scpe_ri_v1_shadow_backtest_bridge_slice1_launch_authorization_packet_2026-04-21.md`

Carried-forward meaning from those packets:

1. the slice remains RI-only, observational-only, and non-authoritative
2. writable surfaces were already bounded upstream
3. `--no-save` was already treated as necessary but not sufficient
4. ledger-root derivation was already treated as current implementation expectation only
5. the prior launch verdict remains `NOT AUTHORIZED NOW` unless separately changed later

This audit does **not** change that prior launch verdict.

## Exact future subject under audit

The audited future subject remains the same exact RI bridge anchor:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

Bounded context carried forward unchanged:

- symbol: `tBTCUSD`
- timeframe: `3h`
- date window: `2024-01-02 -> 2024-12-31`
- SHA256: `824e409d39b7e09a7b04fd2aee9a34e4d0c3f010440fb6d68069764eb17a0bad`

## Repo-visible write-site review

The following review is limited to repo-visible code sites inspected in this session.
It should not be read as execution-backed proof that no additional runtime-conditioned writes exist elsewhere.

### A. `scripts/run/run_backtest.py` — repo-visible write-intent

Current repo-visible write sites include:

- `CONFIG_DIR = ROOT_DIR / "config"`
- `CONFIG_DIR.mkdir(exist_ok=True)`
- `(CONFIG_DIR / "__init__.py").touch(exist_ok=True)`
- `_write_decision_rows(...)`
  - `path.parent.mkdir(parents=True, exist_ok=True)`
  - `path.write_text(...)` for JSON mode
  - NDJSON streaming writes to the explicitly provided path for NDJSON mode
- `logger.save_all(results)` only when `not args.no_save`

Observed repo-visible implications:

1. the current run surface contains an unconditional filesystem-touch call against `config/__init__.py`
2. decision-row output writes are explicitly path-bound to the provided `--decision-rows-out` target
3. default result persistence is suppressed when `--no-save` is present because `logger.save_all(results)` is skipped on the repo-visible path reviewed here

### B. `src/core/backtest/intelligence_shadow.py` — repo-visible shadow output derivation

Current repo-visible shadow write sites include:

- `summary_path.parent.mkdir(parents=True, exist_ok=True)`
- `run_id = derive_shadow_run_id(summary_path)`
- `ledger_root = derive_shadow_ledger_root(repo_root=self.repo_root, run_id=run_id)`
- `ledger_root.mkdir(parents=True, exist_ok=True)`
- `summary_path.write_text(...)`

Observed repo-visible implications:

1. the shadow summary file is written to the explicitly provided summary path
2. the shadow ledger root is derived from the `run_id`
3. when the summary filename stem is `shadow_summary`, `derive_shadow_run_id(summary_path)` uses the parent directory name as `run_id`
4. `derive_shadow_ledger_root(...)` then maps that `run_id` under `artifacts/intelligence_shadow/<run_id>/research_ledger/`

For the already-defined descriptive shadow-run target from the setup-only packet, current repo-visible derivation therefore points to:

- summary path: `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_summary.json`
- derived `run_id`: `tBTCUSD_3h_ri_shadow_bridge_slice1_20260421`
- derived ledger root: `artifacts/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/research_ledger/`

This remains a **current implementation expectation only**.
It is not execution-backed proof in this audit.

## Containment analysis against the previously bounded writable surfaces

The previously bounded future writable surfaces were:

1. `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/control_decision_rows.ndjson`
2. `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_decision_rows.ndjson`
3. `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_summary.json`
4. `artifacts/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/research_ledger/`
5. `docs/analysis/scpe_ri_v1/scpe_ri_v1_shadow_backtest_bridge_slice1_execution_summary_2026-04-21.md`

### What currently fits inside the bounded surface

On static repo-visible review, the following surfaces are aligned with the bounded envelope:

- explicit control decision-row output path
- explicit shadow decision-row output path
- explicit shadow summary output path
- current ledger-root derivation path from the shadow summary target

### What does not fit inside the bounded surface

The current run surface also includes the unconditional filesystem-touch call against:

- `config/__init__.py`

That path is **outside** the previously bounded writable surfaces.

### Why `--no-save` is not enough

`--no-save` suppresses default result persistence on the repo-visible path reviewed here, but it does **not** by itself make write containment green because the run surface still includes the unconditional `config/__init__.py` touch side effect.

## Containment verdict

### Decision

- **BOUNDED WRITE CONTAINMENT: NOT GREEN**

### Why this is the correct fail-closed decision

Bounded write containment cannot be marked green on static audit evidence alone because the current repo-visible run logic still contains an out-of-bound write-intent / side effect relative to the already approved writable surfaces:

- `(CONFIG_DIR / "__init__.py").touch(exist_ok=True)` against `config/__init__.py`

This is enough to block a green containment conclusion.

This audit does **not** claim that the future run was executed and observed writing that path.
It does claim that the current repo-visible run surface includes that unconditional filesystem-touch call, which is sufficient to prevent containment from being treated as green.

## Implication for the prior launch decision

The prior launch packet recorded:

- **NOT AUTHORIZED NOW**

This audit leaves that verdict unchanged.

If anything, the audit narrows the open blocker more precisely:

- containment is not merely “not yet re-verified”; the current repo-visible run surface contains a concrete out-of-bound side effect that prevents green containment under the existing boundary definition

## Preferred future remediation path

The preferred future remediation is:

- a **separately governed code-fix packet** that removes the out-of-bound side effect from the run surface

A writable-surface exception or expansion remains:

- a separate
- non-preferred
- not-authorized-by-this-audit

future governance path.

This audit does **not** authorize either remediation path.
It only records the preferred direction if future work continues.

## What would need to be true before containment could later turn green

A later separately tracked step would need to show, at minimum, that:

1. the unconditional `config/__init__.py` touch side effect has been removed from the relevant run surface under separate governance
2. explicit decision-row writes remain confined to the pre-approved output paths
3. shadow summary and ledger-root derivation still map to the pre-approved bounded paths
4. no other out-of-bound write-intent remains on the relevant repo-visible run surface

## Explicit exclusions / not in scope

The following remain explicitly outside this audit:

- actual control execution
- actual shadow execution
- launch authorization changes
- code changes
- writable-surface exception approval
- runtime instrumentation approval
- paper coupling
- readiness, cutover, or promotion framing

## Bottom line

This audit records a static repo-visible finding for the future RI-only shadow-backtest bridge slice1 run surface:

- the bounded decision-row and shadow-summary / ledger-root outputs are visible and align with the pre-approved envelope in current code
- `--no-save` suppresses default result persistence on the reviewed path, but does not make containment green by itself
- the current run surface still includes an unconditional filesystem-touch call against `config/__init__.py`

Therefore:

- **bounded write containment is not green**
- the prior `NOT AUTHORIZED NOW` launch verdict remains unchanged
- any future continuation should prefer a separately governed code-fix packet rather than a writable-surface expansion
