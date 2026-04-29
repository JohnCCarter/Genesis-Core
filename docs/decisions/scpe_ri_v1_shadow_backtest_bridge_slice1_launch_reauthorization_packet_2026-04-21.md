# SCPE RI V1 shadow-backtest bridge slice1 launch re-authorization packet

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `re-reviewed on updated bridge surface / fail-closed / not authorized now`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet re-evaluates the earlier fail-closed launch decision for one bounded RI-only shadow-backtest bridge slice using updated containment-fix evidence, but must remain docs-only and must not reopen runtime integration, paper coupling, readiness, cutover, or promotion.
- **Required Path:** `Quick`
- **Objective:** re-assess the earlier `NOT AUTHORIZED NOW` decision for the exact RI-only shadow bridge slice1 using updated current-session evidence after the containment-fix implementation lane, while keeping setup-only framing and launch authority as separate artifacts.
- **Candidate:** `shadow-backtest bridge slice1 launch re-authorization`
- **Base SHA:** `749315ea`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Setup packet remains prerequisite input only`
- `No runtime/paper/readiness/promotion reopening`
- `No bridge-claim expansion beyond RI-only observational evidence capture`
- `Authorization remains state-bound and fail-closed`

### Skill Usage

- **Applied repo-local skill:** none
- **Reason:** this packet is a docs-only re-authorization decision and does not itself execute a run-domain workflow.
- **Deferred:** any run-domain skill invocation belongs to a later operational step only if authorization is later granted on a clean launch surface.

### Scope

- **Scope IN:**
  - one docs-only re-authorization packet for the exact RI-only shadow bridge slice1 subject
  - explicit updated yes/no launch decision for the exact original launch subject
  - explicit evidence basis after the containment-fix implementation lane
  - explicit state-bound blocker accounting and research-only run boundary
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, or `artifacts/**` changes
  - no actual control run
  - no actual shadow run
  - no reinterpretation of the setup-only packet as launch approval
  - no runtime instrumentation approval
  - no paper-shadow coupling
  - no readiness/cutover/promotion reopening
  - no new evidence class
- **Expected changed files:** `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_launch_reauthorization_packet_2026-04-21.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must remain a separate re-authorization artifact
- no sentence may collapse setup and launch authority into the same decision
- no sentence may authorize launch unless all cited preconditions are green in the current repo state
- no sentence may upgrade the future slice into runtime, paper, readiness, cutover, or promotion evidence
- no sentence may imply execution was performed by this packet

### Stop Conditions

- any wording that turns historical green evidence into durable authorization independent of current repo state
- any wording that treats the earlier setup-only packet as launch approval
- any wording that upgrades launchability into runtime, paper, readiness, or promotion evidence
- any wording that widens writable surfaces beyond the bounded paths already fixed upstream
- any need to modify files outside this one scoped packet

### Output required

- reviewable launch re-authorization packet
- explicit updated authorization verdict
- explicit current evidence matrix
- explicit remaining blocker accounting
- explicit research-only run boundary and artifact discipline rules

## Purpose

This packet records a **separate launch re-authorization decision** for the already-defined RI-only shadow-backtest bridge slice1.

It does **not** reinterpret the setup-only packet as launch approval.
The setup-only packet remains prerequisite input only.
This packet re-evaluates the earlier fail-closed launch decision using updated evidence gathered after the separately governed containment-fix implementation lane.

Fail-closed interpretation:

> This packet uses the earlier setup-only and launch-authorization packets only as prerequisite inputs to a separate re-authorization decision for the exact RI-only shadow bridge slice1 subject. It does not authorize execution unless all required preconditions are explicitly green in the current repo state.

## Upstream governed basis

This packet is downstream of the following tracked documents:

- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_setup_only_packet_2026-04-21.md`
- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_launch_authorization_packet_2026-04-21.md`
- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_write_boundary_audit_2026-04-21.md`
- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_precode_packet_2026-04-21.md`
- `docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_packet_2026-04-21.md`
- `docs/analysis/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_report_2026-04-21.md`

Carried-forward meaning from those packets:

1. the exact slice remains RI-only, observational-only, and non-authoritative
2. setup-only framing never by itself authorizes launch
3. the earlier launch decision was correctly fail-closed under the evidence available at that time
4. the containment-fix lane is now closed with approved gates and approved post-diff audit
5. any future runnable slice still requires current-state launch authorization on a clean launch surface

## Exact launch subject

The exact launch subject re-reviewed by this packet remains the RI bridge anchor:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

Bounded context remains unchanged:

- symbol: `tBTCUSD`
- timeframe: `3h`
- date window: `2024-01-02 -> 2024-12-31`
- SHA256: `824e409d39b7e09a7b04fd2aee9a34e4d0c3f010440fb6d68069764eb17a0bad`

This packet re-authorizes or declines launch only for that exact bridge subject and bounded context.
No alternate config, edited copy, bridge variant, or widened execution surface is authorized by implication.

## Re-authorization verdict

### Decision

- **NOT AUTHORIZED NOW**

### Why this remains the correct fail-closed decision

The earlier launch packet listed three non-green predicates:

1. working tree cleanliness
2. bounded write containment
3. ledger-root derivation re-verification

Updated evidence in this session resolves items 2 and 3, but item 1 remains red.
Because the launch surface is still not clean, launch authorization cannot yet be granted without violating exact-state and provenance discipline.

## Current evidence observed in this session

### 1. Working tree status

Observed state:

- red / dirty working tree

Observed evidence:

- `git status --short` currently reports tracked and untracked changes including:
  - `M docs/analysis/scpe_ri_v1_no_trade_axis_ceiling_audit_report_2026-04-20.md`
  - `M docs/analysis/scpe_ri_v1_no_trade_min_dwell_audit_report_2026-04-20.md`
  - `M docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_precode_packet_2026-04-21.md`
  - `M docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_launch_authorization_packet_2026-04-21.md`
  - `M docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_write_boundary_audit_2026-04-21.md`
  - `M scripts/run/run_backtest.py`
  - `?? docs/decisions/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_packet_2026-04-21.md`
  - `?? docs/analysis/scpe_ri_v1_shadow_backtest_bridge_slice1_containment_fix_implementation_report_2026-04-21.md`
  - `?? docs/scpe_ri_v1_architecture.md`

Implication:

- the clean-working-tree predicate from the setup-only packet is still not satisfied now
- this single remaining red predicate is sufficient to keep launch fail-closed

### 2. Exact anchor identity

Observed state:

- green

Observed evidence:

- current SHA256 recorded in this session:
  - `824E409D39B7E09A7B04FD2AEE9A34E4D0C3F010440FB6D68069764EB17A0BAD`

Implication:

- the exact launch subject remains stable and unchanged

### 3. Repo-visible CLI support

Observed state:

- green at current repo-visible CLI surface

Observed evidence basis carried forward and preserved after the containment-fix implementation lane:

- `scripts/run/run_backtest.py --help` passed in the containment-fix gate run
- the gate-covered CLI surface still includes:
  - `--config-file`
  - `--decision-rows-out`
  - `--decision-rows-format`
  - `--intelligence-shadow-out`
  - `--no-save`

Implication:

- the descriptive control/shadow command targets remain expressible on the current repo-visible surface
- this remains a support predicate only, not execution proof

### 4. Bounded write-containment status

Observed state:

- green on the currently reviewed run surface

Observed evidence:

- the out-of-bound side effect against `config/__init__.py` was removed from `scripts/run/run_backtest.py`
- the containment-fix implementation lane passed:
  - config-package resolution proof
  - canonical CLI help smoke
  - targeted `run_backtest` selectors
  - determinism replay
  - feature-cache invariance
  - pipeline hash guard
- Opus post-diff audit approved the no-behavior-change containment fix

Implication:

- the earlier concrete containment blocker recorded in the write-boundary audit is now resolved on the reviewed run surface
- bounded write containment is no longer red for the reasons cited in the earlier launch packet

### 5. Ledger-root derivation status

Observed state:

- green on currently reviewed evidence

Observed evidence:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe -m pytest -q tests/backtest/test_run_backtest_intelligence_shadow.py::test_run_backtest_main_writes_shadow_summary_without_changing_dummy_results`
  - Result: `PASS` (`1 passed`)
- that targeted selector verifies, on the current repo-visible code path, that shadow-summary output is written and the derived research ledger root exists under the expected run-id-based path.

Implication:

- ledger-root derivation is no longer merely an implementation expectation for launch-review purposes
- the earlier ledger-root blocker is now resolved on the reviewed evidence surface

## Updated exact preconditions and current status

| Check                                           | Required state | Current status in this session | Why it matters                                                        |
| ----------------------------------------------- | -------------- | ------------------------------ | --------------------------------------------------------------------- |
| Working tree clean                              | Green          | Red                            | provenance and exact-state launch discipline must remain reviewable   |
| Exact bridge anchor identity                    | Green          | Green                          | launch subject must remain exact and fingerprint-stable               |
| Current repo-visible CLI flag support           | Green          | Green                          | descriptive command targets must still match current repo entrypoints |
| Descriptive control/shadow command-target shape | Green          | Green                          | later launch must remain no-code in shape                             |
| Full bounded write containment                  | Green          | Green                          | launch may not leak writes outside bounded surfaces                   |
| Ledger-root derivation re-verification          | Green          | Green                          | launch evidence may not rely on assumption alone                      |
| RI-only observational boundary retained         | Green          | Green                          | slice must stay below runtime integration and paper coupling          |

## Research-only run boundary remains unchanged

If launch is ever authorized later in a separate tracked step, the run boundary remains strictly limited as follows.

### Allowed boundary

- research only
- RI-only only
- observational-only only
- exact bridge anchor only
- bounded to `tBTCUSD`, `3h`, `2024-01-02 -> 2024-12-31`

### Disallowed boundary

- no runtime integration claims
- no paper-shadow claims
- no readiness or cutover claims
- no promotion claims
- no champion/default/config-authority claims
- no widened execution surface beyond the exact paired control/shadow setup

## Output handling and artifact discipline after any later launch

If a later separately tracked step eventually authorizes and executes the run, output handling must remain bounded as follows.

### Allowed raw outputs

Only the already-bounded surfaces fixed upstream may be used:

- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/control_decision_rows.ndjson`
- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_decision_rows.ndjson`
- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_summary.json`
- `artifacts/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/research_ledger/`
- `docs/analysis/scpe_ri_v1_shadow_backtest_bridge_slice1_execution_summary_2026-04-21.md`

### Forbidden post-run handling

- no automatic backtest result save outside the bounded surfaces
- no automatic comparison packet
- no automatic runtime/paper/readiness/promotion packet
- no code/config/test/runtime widening in place

## What must be true before a later packet could say yes

Before a later packet may change the verdict to `AUTHORIZED NOW`, all of the following must be explicitly documented green in the then-current repo state:

1. the working tree is clean for tracked files touching the anchor, backtest entrypoint, passive shadow seam, or bounded output-surface decision
2. the exact bridge anchor still matches SHA256 `824e409d39b7e09a7b04fd2aee9a34e4d0c3f010440fb6d68069764eb17a0bad`
3. the current repo-visible CLI flags still support the descriptive control/shadow command targets
4. bounded write containment remains green on the relevant run surface
5. ledger-root derivation remains green against the current repo-visible code path
6. the run remains strictly inside the RI-only observational research lane with no widening

## Bottom line

This packet records the separate governed launch re-authorization decision for the exact RI-only shadow-backtest bridge slice1.

That updated decision is:

- **NOT AUTHORIZED NOW**

Reason:

- the earlier containment and ledger-root blockers are now resolved, but the current launch surface is still not clean.

This narrows the remaining blocker to exact-state cleanliness only.
No execution, runtime integration, paper coupling, readiness, cutover, or promotion scope is opened here.
