# SCPE RI V1 shadow-backtest bridge slice1 setup-only packet

Date: 2026-04-21
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `setup-only / planning-only / no launch authorization`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: this packet is a docs-only setup specialization for one possible later RI-only shadow-backtest bridge slice, with no code/config/test/runtime changes and no execution authority.
- **Required Path:** `Quick`
- **Objective:** define one bounded setup-only surface for a possible later RI-only prove-or-stop shadow-backtest bridge slice1 run, including exact anchor identity, descriptive paired command targets, writable-surface discipline, and launch-time re-verification items.
- **Candidate:** `shadow-backtest bridge slice1 setup only`
- **Base SHA:** `a70d2d41`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Setup-only / non-authorizing`
- `No runtime/paper/readiness/promotion reopening`
- `No env/config semantics changes`

### Skill Usage

- **Applied repo-local skill:** none
- **Reason:** this packet is docs-only setup framing and does not yet authorize or execute a run-domain workflow.
- **Deferred:** any run-domain skill invocation belongs to a later launch-authorization packet, if such a packet is ever proposed.

### Scope

- **Scope IN:**
  - create one docs-only setup-only packet for the already-defined RI-only shadow-backtest bridge slice1
  - lock the exact bridge anchor, observational context, and descriptive future command shape
  - record launch-time re-verification items for CLI support, bounded output surfaces, and ledger-root expectation
  - preserve that the slice remains RI-only, observational-only, non-authoritative, and fail-closed
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, or `artifacts/**` changes
  - no launch authorization
  - no actual control run
  - no actual shadow run
  - no comparison/readiness/promotion reopening
  - no runtime instrumentation approval
  - no paper-shadow coupling
  - no new env/config/default authority
- **Expected changed files:** `docs/decisions/scpe_ri_v1/scpe_ri_v1_shadow_backtest_bridge_slice1_setup_only_packet_2026-04-21.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- no sentence may authorize or imply execution
- no sentence may treat the descriptive command targets as already approved runs
- no sentence may treat the generic shadow seam as already sufficient proof for RI-specific execution
- no sentence may treat `--no-save` as sufficient by itself to prove full write containment
- no sentence may reopen runtime, paper, readiness, cutover, or promotion

### Stop Conditions

- any wording that sounds like launch authorization instead of setup-only framing
- any wording that presents current CLI support or ledger derivation as already-proven launch authority
- any wording that expands writable surfaces beyond the bounded paths fixed in the pre-code packet
- any wording that changes env/config semantics instead of citing current repo surfaces
- any need to modify files outside this one scoped packet

### Output required

- reviewable setup-only packet
- explicit exact anchor identity
- explicit descriptive future command targets
- explicit writable-surface discipline
- explicit launch-time re-verification items
- explicit exclusions and disallowed claims

## Purpose

This document is a **setup-only packet** for the already-defined RI-only shadow-backtest bridge slice1.

It defines a bounded setup surface for a possible later prove-or-stop RI shadow evidence-capture run.
It does **not** authorize execution, artifact generation, readiness, promotion, runtime instrumentation, paper coupling, or any broader runtime/integration step.

Fail-closed interpretation:

> This packet defines only a proposed future setup surface for a later, separately reviewed launch-authorization packet. It does not authorize execution, does not prove seam sufficiency, and does not change the writable-surface boundaries already fixed by the pre-code packet.

## Upstream governed basis

This packet is downstream of the following tracked documents:

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_research_closeout_report_2026-04-20.md`
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_integration_roadmap_2026-04-20.md`
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_integration_seam_inventory_2026-04-20.md`
- `docs/decisions/scpe_ri_v1/scpe_ri_v1_shadow_backtest_packet_boundary_2026-04-20.md`
- `docs/decisions/scpe_ri_v1/scpe_ri_v1_shadow_backtest_bridge_slice1_precode_packet_2026-04-21.md`

This sequencing choice is also consistent with prior RI governance packets that separated setup-only framing from launch authorization, including:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_followup_setup_only_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_slice8_followup_launch_authorization_packet_2026-03-26.md`

Those earlier packets are precedent only. They do not by themselves create authority for this slice.

Carried-forward meaning from the upstream SCPE RI V1 chain:

1. the bounded SCPE RI research lane is closed and grants no inherited runtime/integration approval
2. the generic shadow seam is the smallest currently visible implementation-adjacent seam
3. the current slice remains RI-only, observational-only, and non-authoritative
4. any runnable slice still requires later separate launch authorization and launch-time re-verification

## Setup subject and exact anchor

The only active setup subject in this packet is the RI shadow-backtest bridge slice1 anchored to:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

### Exact anchor identity

- SHA256: `824e409d39b7e09a7b04fd2aee9a34e4d0c3f010440fb6d68069764eb17a0bad`

Any later launch packet must recompute the anchor fingerprint and confirm it still matches this exact identity before treating the setup surface as unchanged.

### Exact observational context

- symbol: `tBTCUSD`
- timeframe: `3h`
- date window: `2024-01-02 -> 2024-12-31`

## Admissible input surface

Only the following inputs are admissible inside this setup-only packet.

### 1. Governance anchors

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_shadow_backtest_bridge_slice1_precode_packet_2026-04-21.md`
- `docs/decisions/scpe_ri_v1/scpe_ri_v1_shadow_backtest_packet_boundary_2026-04-20.md`
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_integration_seam_inventory_2026-04-20.md`

Allowed use:

- preserve the already-defined RI-only slice boundary
- preserve bounded writable surfaces
- preserve the prove-or-stop framing

### 2. Exact RI bridge anchor

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

Allowed use:

- preserve the exact RI bridge surface for a possible later control/shadow pair
- preserve RI-only family identity and `authority_mode = regime_module`
- preserve that the subject remains backtest-only and not promotion evidence

### 3. Existing repo-authoritative backtest entrypoints

- `scripts/run/run_backtest.py`
- `src/core/backtest/intelligence_shadow.py`
- `src/core/backtest/engine.py`

Allowed use:

- cite the current repo-visible CLI and passive hook surfaces that a later launch packet would need to re-verify
- define descriptive future command targets only

This packet does not prove those surfaces are sufficient for execution.
It only records them as the current implementation surfaces that a later launch packet must re-check.

## Descriptive future command targets only

The command targets below are **descriptive setup targets only**.
They are not approved for execution in this packet.
They may only be used if a later launch-authorization packet re-verifies that the entrypoint, flags, anchor file, and bounded output paths still match current repo state.

### Canonical local interpreter note

If a later launch packet is proposed, the local interpreter surface to re-verify is expected to be:

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe`

This is a reproducibility note only, not launch authority.

### Future control-run target

A later launch packet may consider the following descriptive control-run target:

`C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/control_decision_rows.ndjson --decision-rows-format ndjson --no-save`

### Future shadow-run target

A later launch packet may consider the following descriptive shadow-run target:

`C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe scripts/run/run_backtest.py --symbol tBTCUSD --timeframe 3h --start 2024-01-02 --end 2024-12-31 --config-file config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json --decision-rows-out results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_decision_rows.ndjson --decision-rows-format ndjson --intelligence-shadow-out results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_summary.json --no-save`

### Why the paired shape matters

The paired control/shadow shape is descriptive only, but it captures the intended prove-or-stop question for a later launch packet:

- the control run would capture baseline decision rows on the exact bridge subject
- the shadow run would capture decision rows plus passive intelligence-shadow output on the same exact bridge subject
- later comparison would test whether the shadow path preserves decision parity while emitting bounded non-authoritative shadow artifacts

## Writable-surface discipline

The pre-code packet already fixed the only future writable surfaces that may be considered later:

1. `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/control_decision_rows.ndjson`
2. `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_decision_rows.ndjson`
3. `results/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/shadow_summary.json`
4. `artifacts/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/research_ledger/`
5. `docs/analysis/scpe_ri_v1/scpe_ri_v1_shadow_backtest_bridge_slice1_execution_summary_2026-04-21.md`

### `--no-save` guardrail

`--no-save` is required in the descriptive command targets because it suppresses default emission of backtest result artifacts from `scripts/run/run_backtest.py`.

That flag is a necessary guard, but it is **not sufficient by itself** to prove full write containment.
A later launch-authorization packet must still re-verify that every actual write remains confined to the already pre-approved bounded surfaces only.

If any later slice would write anywhere outside those surfaces, that slice must stop as `BLOCKED` rather than widen in place.

## Current implementation expectation for ledger-root derivation

Under current implementation, a shadow output path whose filename stem is `shadow_summary` is expected to derive the shadow `run_id` from the parent directory name, and then derive the research-ledger root under:

- `artifacts/intelligence_shadow/<run_id>/research_ledger/`

For the currently proposed descriptive shadow-run target, that expectation points to:

- `artifacts/intelligence_shadow/tBTCUSD_3h_ri_shadow_bridge_slice1_20260421/research_ledger/`

This is a **current implementation expectation only** based on the current repo-visible code path in `src/core/backtest/intelligence_shadow.py`.
It is not proof in this setup-only packet.
A later launch packet must re-verify the exact derivation path against current repo state before using it as authorization evidence.

## Preconditions for any later launch-authorization packet

Any later launch packet that wishes to use this setup surface remains blocked unless all of the following are true:

1. the working tree is clean for tracked files touching the anchor, backtest entrypoint, passive shadow seam, or bounded output-surface decision
2. the exact bridge anchor still exists at the same path and still matches SHA256 `824e409d39b7e09a7b04fd2aee9a34e4d0c3f010440fb6d68069764eb17a0bad`
3. `scripts/run/run_backtest.py` still supports the required flags:
   - `--config-file`
   - `--decision-rows-out`
   - `--decision-rows-format`
   - `--intelligence-shadow-out`
   - `--no-save`
4. the control/shadow command targets can still be expressed without Python, config, test, runtime, or paper-path changes
5. the later slice can keep all writes confined to the bounded writable surfaces fixed above
6. the later slice remains RI-only, observational-only, non-authoritative, and below runtime integration
7. the later slice re-verifies the current ledger-root derivation expectation against current repo state instead of assuming this packet is proof

These are preconditions for a later separate launch packet only.
They are not launch approval in this packet.

## Reproducibility notes (non-authority)

Any environment variables, interpreter paths, CLI flags, or output locations mentioned here are recorded only as **reproducibility notes** and **descriptive setup targets**.

They do **not**:

- authorize execution
- create new env/config/default authority
- prove seam sufficiency
- prove write containment
- prove launch readiness

If a later launch packet is ever proposed, only the then-current, actually verified values should be treated as run evidence.

## Explicit exclusions / not in scope

The following remain explicitly outside this packet:

- actual control execution
- actual shadow execution
- launch authorization
- comparison verdicts
- readiness, cutover, or promotion framing
- code/config/test/runtime changes
- runtime instrumentation approval
- paper-shadow coupling
- any new evidence class

## Disallowed claims

This packet must not be read as permitting any of the following claims:

- `launch is approved`
- `the command targets may now be run`
- `the generic shadow seam is already sufficient`
- `--no-save alone proves write containment`
- `the ledger-root derivation is already proven`
- `this packet changes env/config/default semantics`
- `this packet creates readiness, cutover, or promotion evidence`

## Bottom line

This packet creates only a **setup-only surface** for a possible later RI-only shadow-backtest bridge slice1 run.

It locks:

- the exact RI bridge anchor and fingerprint
- the exact observational context
- the descriptive paired control/shadow command targets
- the bounded writable-surface discipline
- the launch-time re-verification items

It does **not** authorize launch, execution, seam sufficiency, runtime integration, or any broader authority claim.
