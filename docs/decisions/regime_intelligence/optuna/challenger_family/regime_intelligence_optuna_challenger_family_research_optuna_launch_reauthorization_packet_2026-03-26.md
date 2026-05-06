# Regime Intelligence challenger family — research / Optuna launch re-authorization packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `historical state-bound re-authorization snapshot / branch-specific / no active execution authority`

> Current status note:
>
> - [HISTORICAL 2026-05-05] This file records a point-in-time re-authorization decision on `feature/ri-role-map-implementation-2026-03-24`, not an active launch authority on `feature/next-slice-2026-05-05`.
> - Later slice8 follow-up and cross-regime packets use the reproduced slice8 launch surface as historical input rather than current authority.
> - Preserve this file as historical launch-governance provenance only.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet re-evaluates the earlier fail-closed launch decision for one bounded RI-family-internal Optuna research run, but remains docs-only and must not reopen comparison, readiness, promotion, or runtime/default change
- **Required Path:** `Quick`
- **Objective:** Re-assess the earlier `NOT AUTHORIZED NOW` decision using updated launch-readiness evidence, while keeping the setup packet as prerequisite input only and preserving strict RI research-lane boundaries.
- **Candidate:** `slice8 RI research launch re-authorization`
- **Base SHA:** `1b6a34a6`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Setup packet remains prerequisite input only`
- `No comparison/readiness/promotion reopening`
- `No bridge-claim expansion beyond RI is runnable`
- `Authorization is state-bound and self-revoking`

### Skill Usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Supporting repo reference:** `docs/optuna/OPTUNA_BEST_PRACTICES.md`
- **Consulted for exclusion only:** `backtest_run` — not the active skill because this packet authorizes an Optuna research launch surface, not a manual backtest

### Scope

- **Scope IN:**
  - one docs-only re-authorization packet for the already-open RI research / Optuna lane
  - explicit updated yes/no launch decision for the exact original launch subject
  - explicit evidence basis, self-revoking clause, run boundary, and output discipline
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, or `results/**` changes
  - no actual Optuna launch by this packet
  - no reinterpretation of the setup packet as launch approval
  - no comparison reopening
  - no readiness reopening
  - no promotion reopening
  - no writeback
  - no new evidence class
  - no runtime/default/config-authority change
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_launch_reauthorization_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must remain a separate re-authorization artifact
- no sentence may collapse setup and authorization into the same decision
- no sentence may extend authorization beyond the current clean launch surface
- no sentence may reopen comparison, readiness, or promotion
- no sentence may expand bridge claims beyond `RI is runnable`

### Stop Conditions

- any wording that turns this into a durable or general authorization independent of current repo state
- any wording that upgrades research launchability into comparison, readiness, or promotion evidence
- any wording that turns the smoke config into the primary launch subject
- any wording that implies execution was performed by this packet
- any need to modify files outside the one scoped packet

### Output required

- reviewable launch re-authorization packet
- explicit re-authorization verdict
- explicit exact launch subject
- explicit current-green evidence basis
- explicit self-revoking clause
- explicit research-only output discipline

## Purpose

This packet records a **separate launch re-authorization decision** for the already-open
RI research / Optuna lane.

It does **not** reinterpret the setup packet as launch approval.

The setup packet remains prerequisite input only. This packet re-evaluates the launch decision
using updated launch-readiness evidence gathered after the earlier fail-closed authorization packet.

## Upstream governed basis

This packet is downstream of the following already tracked decisions:

- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_execution_setup_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_launch_authorization_packet_2026-03-26.md`

Carried-forward meaning from those packets:

1. the lane remains RI-family-internal research only
2. the setup packet remains setup-only and not launch approval
3. the earlier launch decision was correctly fail-closed at the time it was written
4. the bridge artifact remains bounded to the claim `RI is runnable`
5. no comparison, readiness, or promotion reopening is allowed here

## Exact launch subject

The exact launch subject re-authorized by this packet is:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`

This remains the only primary launch subject.

This packet does not authorize by implication:

- any alternate YAML
- any edited copy of the YAML
- the bridge artifact as launch substitute
- the temporary smoke config as launch subject
- any derived candidate file

## Supporting evidence only: temporary smoke config

The temporary smoke config used in this session is supporting evidence only:

- `tmp/ri_slice8_smoke_20260326.yaml`

It is an operational verification aid, not the primary launch subject.

Its role is limited to demonstrating that the RI slice8 research search surface produces runnable
research artifacts under a bounded small-budget smoke run.

## Re-authorization verdict

### Decision

- **AUTHORIZED NOW**

### Scope of that authorization

This decision authorizes launch **only** for the exact launch subject above, and **only** on the
current clean launch surface verified in this packet.

This is not a durable general authorization. It is a point-in-time, state-bound launch decision.

### Self-revoking clause

This authorization automatically ceases to apply if any of the following occurs before launch:

1. the working tree is no longer clean
2. unrelated changes are reintroduced, including restoration of the currently stashed docs changes
3. the launch subject changes in content or path
4. the primary storage path is no longer free while `resume=false`
5. validator or preflight no longer remain green for the exact launch subject

If any of the above occurs, this authorization is void and a new fail-closed review is required.

## Current-green evidence basis observed in this session

### 1. Working tree clean on current launch surface

Observed state:

- clean working tree at the time of re-authorization review

Operational note:

- unrelated local docs changes were preserved outside the working tree as named stash
  `stash@{0}` with message `prelaunch-clean-20260326-docs`

Governance meaning:

- the clean launch predicate is satisfied now, but only so long as that clean state is preserved

### 2. Primary storage path free under `resume=false`

Observed state:

- the original launch storage path is free again

Primary path:

- `results/hparam_search/storage/ri_challenger_family_slice8_3h_2024_v1.db`

Preserved previous DB artifact:

- `results/hparam_search/storage/ri_challenger_family_slice8_3h_2024_v1_prelaunch_backup_20260326.db`

Governance meaning:

- the launch subject no longer points at an already-existing DB while `resume=false`

### 3. Config validation explicit green by exit code

Observed state:

- validator completed with explicit exit code `0`

Launch subject validated:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`

Interpretation boundary:

- warnings were observed, but the validator returned explicit success and therefore the validation
  predicate is treated as green for launch authorization purposes

### 4. Preflight explicit green

Observed state:

- preflight completed green for the exact launch subject

Observed basis:

- `scripts/preflight/preflight_optuna_check.py`
- result included `[OK] Alla preflight-checkar passerade - Optuna bör kunna köras`

Governance meaning:

- the earlier fail-closed blocker tied to storage/restart conflict is resolved on the current
  launch surface

### 5. Baseline / smoke completed and documented

Observed state:

- bounded smoke run completed successfully with exit code `0`

Run identity:

- run id: `ri_slice8_smoke_20260326`

Supporting artifact paths:

- `results/hparam_search/ri_slice8_smoke_20260326/run_meta.json`
- `results/hparam_search/ri_slice8_smoke_20260326/validation/trial_001.json`

Observed smoke support:

- `run_meta.json` records `validated=5`
- `validation/trial_001.json` records `constraints.ok=true` and `num_trades=63`

Interpretation boundary:

- this smoke run supports launchability of the RI research surface only
- it does not support comparison, readiness, or promotion claims

## Run boundary remains unchanged

Any launch authorized by this packet remains strictly bounded as follows.

### Allowed boundary

- research only
- RI-family-internal only
- bounded to the already-open RI research / Optuna lane

### Disallowed boundary

- no comparison claims
- no readiness claims
- no promotion claims
- no champion replacement claims
- no writeback claims

The bridge artifact remains bounded to the claim:

- `RI is runnable`

This packet does not extend that claim beyond runnable RI research execution.

## Output handling and artifact discipline after launch

If launch is executed under this authorization, output handling must remain disciplined as follows.

### Raw run artifacts

Raw run artifacts may remain under the expected local research output area, including:

- `results/hparam_search/...`
- `results/hparam_search/storage/...`
- `results/hparam_search/.../validation/...`

These remain RI-family-internal research artifacts only.

They are not by themselves tracked proof of comparison, readiness, or promotion.

### Required provenance capture

Any launch report must record at minimum:

- exact config path launched
- git commit used for the run
- study name and storage path
- sample and validation windows
- actual launch-session env/flag surface
- outcome of validator, preflight, and baseline/smoke prerequisites

### Tracked summary discipline

If any tracked summary is created after launch, it must:

- remain explicitly research-only
- identify the run as RI-family-internal
- avoid comparison, readiness, and promotion framing
- avoid upgrading the bridge claim beyond `RI is runnable`

## Bottom line

This packet records a separate governed re-authorization decision for the RI research / Optuna
lane.

That decision is:

- **AUTHORIZED NOW**

But only for:

- the exact launch subject `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`
- the current clean launch surface verified in this packet

If that state changes before launch, this authorization no longer applies and a new fail-closed
review is required.
