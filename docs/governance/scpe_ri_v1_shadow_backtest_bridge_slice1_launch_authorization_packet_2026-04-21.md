# SCPE RI V1 shadow-backtest bridge slice1 launch authorization packet

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `launch authorization decision recorded / fail-closed / not authorized now`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet records an explicit launch-authorization decision for a bounded RI-only shadow-backtest bridge slice, but must remain docs-only and must not reopen runtime integration, paper coupling, readiness, cutover, or promotion.
- **Required Path:** `Quick`
- **Objective:** convert the existing setup-only packet into a separate governed launch decision for the exact RI shadow bridge slice1 subject while keeping setup and launch authorization as distinct artifacts.
- **Candidate:** `shadow-backtest bridge slice1 launch authorization`
- **Base SHA:** `5df1c6d5`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Setup packet is prerequisite input only`
- `No runtime/paper/readiness/promotion reopening`
- `No bridge-claim expansion beyond RI-only observational evidence capture`

### Skill Usage

- **Applied repo-local skill:** none
- **Reason:** this packet records a docs-only launch decision and does not itself execute a run-domain workflow.
- **Deferred:** any run-domain skill invocation belongs to a later operational step only if authorization is later granted.

### Scope

- **Scope IN:**
  - one docs-only launch-authorization packet for the exact RI-only shadow bridge slice1 subject
  - explicit `AUTHORIZED NOW` or `NOT AUTHORIZED NOW` verdict
  - explicit evidence matrix against the setup-only packet preconditions
  - explicit research-only run boundary and output discipline
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, or `artifacts/**` changes
  - no actual control run
  - no actual shadow run
  - no reinterpretation of setup-only as launch approval
  - no runtime instrumentation approval
  - no paper-shadow coupling
  - no readiness/cutover/promotion reopening
  - no new evidence class
- **Expected changed files:** `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_launch_authorization_packet_2026-04-21.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must remain a separate launch-authorization artifact
- no sentence may treat the setup-only packet as launch approval
- no sentence may authorize launch unless all cited preconditions are green
- no sentence may upgrade the future slice into runtime, paper, readiness, cutover, or promotion evidence
- no sentence may imply execution was performed by this packet

### Stop Conditions

- any wording that collapses setup and launch authorization into the same decision
- any wording that upgrades descriptive command targets into execution approval
- any wording that turns current repo-visible support into seam sufficiency proof
- any wording that widens writable surfaces beyond the bounded paths fixed upstream
- any need to modify files outside the one scoped packet

### Output required

- reviewable launch-authorization packet
- explicit authorization verdict
- explicit evidence matrix
- explicit research-only run boundary
- explicit output handling and artifact discipline rules

## Purpose

This packet records a **separate launch-authorization decision** for the already-defined RI-only shadow-backtest bridge slice1.

This packet does **not** reinterpret the setup-only packet as launch approval.
The setup-only packet is used only as prerequisite input to a distinct launch-authorization assessment.

Fail-closed interpretation:

> This packet uses the setup-only packet only as prerequisite input to a separate launch-authorization decision for the exact RI-only shadow bridge slice1 subject. It does not itself authorize execution unless all required preconditions are explicitly green.

## Upstream governed basis

This packet is downstream of the following tracked documents:

- `docs/governance/scpe_ri_v1_shadow_backtest_packet_boundary_2026-04-20.md`
- `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_precode_packet_2026-04-21.md`
- `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_setup_only_packet_2026-04-21.md`

Carried-forward meaning from those packets:

1. the generic shadow seam remains implementation-adjacent only and not self-authorizing
2. the exact slice remains RI-only, observational-only, and non-authoritative
3. setup-only framing does not by itself authorize launch
4. only the bounded writable surfaces fixed upstream may ever be considered later

## Exact launch subject

The exact launch subject evaluated by this packet is the RI bridge anchor:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

Bounded context:

- symbol: `tBTCUSD`
- timeframe: `3h`
- date window: `2024-01-02 -> 2024-12-31`
- SHA256: `824e409d39b7e09a7b04fd2aee9a34e4d0c3f010440fb6d68069764eb17a0bad`

This packet authorizes or declines launch only for that exact bridge subject and bounded context.
No alternate config, edited copy, bridge variant, or widened execution surface is authorized by implication.

## Authorization verdict

### Decision

- **NOT AUTHORIZED NOW**

### Why this is the correct fail-closed decision

The setup-only packet established that any later launch packet remains blocked unless all required preconditions are green.
That threshold is not met in the evidence observed in this session.

At minimum, the following launch preconditions are not green now:

1. the working tree is not clean for tracked files touching governed surfaces
2. bounded write containment has not been launch-time re-verified in a separate operational check
3. ledger-root derivation remains a current implementation expectation only and has not been launch-time re-verified for authorization purposes

Because those conditions remain open, launch authorization cannot be granted now without violating fail-closed governance.

## Evidence observed in this session

### 1. Working tree status

Observed state:

- dirty working tree

Observed evidence:

- `git status --short` reported tracked changes outside this packet scope:
  - `M docs/governance/scpe_ri_v1_no_trade_axis_ceiling_audit_report_2026-04-20.md`
  - `M docs/governance/scpe_ri_v1_no_trade_min_dwell_audit_report_2026-04-20.md`
  - `?? docs/scpe_ri_v1_architecture.md`

Implication:

- the clean-working-tree precondition from the setup-only packet is not satisfied now

### 2. Exact anchor identity

Observed state:

- green

Observed evidence:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json` exists
- SHA256 captured in this session: `824e409d39b7e09a7b04fd2aee9a34e4d0c3f010440fb6d68069764eb17a0bad`

Implication:

- the exact subject identity is currently stable enough to remain the only launch subject under consideration

### 3. Repo-visible CLI support

Observed state:

- green as current repo-visible surface only

Observed evidence:

- `scripts/run/run_backtest.py` currently exposes:
  - `--config-file`
  - `--decision-rows-out`
  - `--decision-rows-format`
  - `--intelligence-shadow-out`
  - `--no-save`

Implication:

- the descriptive control/shadow command targets from the setup-only packet still map to current repo-visible flags
- this is not by itself launch approval or seam sufficiency proof

### 4. Bounded write-containment status

Observed state:

- not yet explicitly green for launch authorization

Observed evidence:

- the setup-only packet defined bounded writable surfaces and the descriptive command targets include `--no-save`
- no later separate launch-time verification has yet been recorded proving that all writes would remain confined to only those bounded surfaces
- the presence of `--no-save` is not sufficient on its own to prove full bounded write containment

Implication:

- write-containment remains open as a launch precondition

### 5. Ledger-root derivation status

Observed state:

- not yet explicitly green for launch authorization

Observed evidence:

- `src/core/backtest/intelligence_shadow.py` currently indicates that a `shadow_summary.json` output is expected to derive `run_id` from the parent directory name and then derive the research ledger root under `artifacts/intelligence_shadow/<run_id>/research_ledger/`
- the setup-only packet explicitly framed this as current implementation expectation only

Implication:

- ledger-root derivation remains open as a launch-time re-verification item and cannot yet be counted as green authorization evidence

## Exact preconditions and current status

| Check                                        | Required state | Current status in this session     | Why it matters                                                        |
| -------------------------------------------- | -------------- | ---------------------------------- | --------------------------------------------------------------------- |
| Working tree clean                           | Green          | Red                                | provenance and exact-state launch discipline must remain reviewable   |
| Exact bridge anchor identity                 | Green          | Green                              | launch subject must remain exact and fingerprint-stable               |
| Current repo-visible CLI flag support        | Green          | Green                              | descriptive command targets must still match current repo entrypoints |
| Descriptive control/shadow command-target shape | Green          | Green at repo-visible CLI surface only | later launch must remain no-code in shape                          |
| Full bounded write containment               | Green          | Red / not yet explicitly verified  | launch may not leak writes outside bounded surfaces                   |
| Ledger-root derivation re-verification       | Green          | Red / not yet explicitly verified  | launch evidence may not rely on assumption alone                      |
| RI-only observational boundary retained      | Green          | Green                              | slice must stay below runtime integration and paper coupling          |

## Research-only run boundary

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

These listed paths remain conditional on a later separately tracked authorization and launch-time re-verification; listing them here is not approval proof.

### Allowed raw outputs

Only the already-bounded surfaces fixed upstream may be used:

- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/control_decision_rows.ndjson`
- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_decision_rows.ndjson`
- `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_summary.json`
- `artifacts/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/research_ledger/`
- `docs/governance/scpe_ri_v1_shadow_backtest_bridge_slice1_execution_summary_2026-04-21.md`

### Forbidden post-run handling

- no automatic backtest result save outside the bounded surfaces
- no automatic comparison packet
- no automatic runtime/paper/readiness/promotion packet
- no code/config/test/runtime widening in place

## What must happen before a later authorization packet could say yes

Before a later packet may change the verdict to `AUTHORIZED NOW`, all of the following must be explicitly documented green:

1. the working tree is clean for tracked files touching the anchor, backtest entrypoint, passive shadow seam, or bounded output-surface decision
2. the exact bridge anchor still matches SHA256 `824e409d39b7e09a7b04fd2aee9a34e4d0c3f010440fb6d68069764eb17a0bad`
3. the current repo-visible CLI flags still support the descriptive control/shadow command targets
4. full bounded write containment is explicitly verified for launch-time use, not only inferred from `--no-save`
5. ledger-root derivation is explicitly re-verified against current repo state for launch-time use
6. the run remains strictly inside the RI-only observational research lane with no widening

## Bottom line

This packet records the separate governed launch decision for the exact RI-only shadow-backtest bridge slice1.

That decision is:

- **NOT AUTHORIZED NOW**

Reason:

- current launch prerequisites are not fully green, including a dirty working tree and missing explicit launch-time verification for bounded write containment and ledger-root derivation.

The setup-only packet remains prerequisite input only.
No execution, runtime integration, paper coupling, readiness, cutover, or promotion scope is opened here.
