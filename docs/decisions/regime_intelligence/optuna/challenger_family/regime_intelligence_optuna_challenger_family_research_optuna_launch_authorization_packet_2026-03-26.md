# Regime Intelligence challenger family — research / Optuna launch authorization packet

Date: 2026-03-26
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `launch authorization decision recorded / fail-closed / not authorized now`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet makes an explicit launch-authorization decision for a bounded RI-family-internal Optuna research run, but must remain docs-only and must not reopen comparison, readiness, promotion, or runtime/default change
- **Required Path:** `Quick`
- **Objective:** Convert the existing setup-only packet into a separate governed launch decision for the already-open RI research / Optuna lane, while keeping setup and launch authorization as distinct artifacts.
- **Candidate:** `slice8 RI research launch authorization`
- **Base SHA:** `f9a140f2`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Setup packet is prerequisite input only`
- `No comparison/readiness/promotion reopening`
- `No bridge-claim expansion beyond RI is runnable`

### Skill Usage

- **Applied repo-local skill:** `optuna_run_guardrails`
- **Supporting repo reference:** `docs/optuna/OPTUNA_BEST_PRACTICES.md`
- **Consulted for exclusion only:** `backtest_run` — not the active skill because this packet does not authorize or execute a manual backtest

### Scope

- **Scope IN:**
  - one docs-only launch-authorization packet for the already-open RI research / Optuna lane
  - explicit yes/no decision on whether launch is authorized now
  - explicit launch subject, pre-launch checks, run boundary, and output discipline
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, or `results/**` changes
  - no actual Optuna launch
  - no reinterpretation of setup as launch approval
  - no comparison reopening
  - no readiness reopening
  - no promotion reopening
  - no writeback
  - no new evidence class
  - no runtime/default/config-authority change
- **Expected changed files:** `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_launch_authorization_packet_2026-03-26.md`
- **Max files touched:** `1`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- the packet must remain a separate launch-authorization artifact
- no sentence may treat the setup packet as launch approval
- no sentence may authorize launch unless all listed pre-launch checks are green
- no sentence may reopen comparison, readiness, or promotion
- no sentence may expand bridge claims beyond `RI is runnable`

### Stop Conditions

- any wording that collapses setup and launch authorization into the same decision
- any wording that upgrades a research launch into comparison, readiness, or promotion evidence
- any wording that turns the bridge artifact into merit, parity, readiness, or promotion proof
- any wording that implies execution was performed by this packet
- any need to modify files outside the one scoped packet

### Output required

- reviewable launch-authorization packet
- explicit authorization verdict
- explicit launch subject and pre-launch check matrix
- explicit research-only run boundary
- explicit output handling and artifact discipline rules

## Purpose

This packet records a **separate launch-authorization decision** for the already-open
RI research / Optuna lane.

This packet does **not** reinterpret the setup packet as launch approval.

The setup packet is used only as prerequisite input to a distinct launch-authorization assessment.

Fail-closed interpretation:

> This packet does not treat the setup packet as launch approval. It uses the setup packet only as
> prerequisite input to a separate launch-authorization decision for the already-open RI research /
> Optuna lane.

## Upstream governed basis

This packet is downstream of the following already tracked decisions:

- `docs/analysis/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_runtime_bridge_classification_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_next_admissible_lane_decision_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_lane_packet_2026-03-26.md`
- `docs/decisions/regime_intelligence/optuna/challenger_family/regime_intelligence_optuna_challenger_family_research_optuna_execution_setup_packet_2026-03-26.md`

Carried-forward meaning from those packets:

1. the current lane is RI-family-internal research only
2. the setup packet is setup-only and not launch approval
3. the bridge artifact remains bounded to the claim `RI is runnable`
4. no comparison, readiness, or promotion reopening is allowed here

## Launch subject

The exact launch subject evaluated by this packet is:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`

This packet authorizes or declines launch only for that exact RI research / Optuna input artifact.

No other config, bridge artifact, candidate JSON, or derived comparison surface is authorized by
implication.

## Authorization verdict

### Decision

- **NOT AUTHORIZED NOW**

### Why this is the correct fail-closed decision

At least three launch preconditions are not green on the evidence observed in this session:

1. the working tree is not clean
2. preflight is not green because `resume=false` while the configured storage DB already exists
3. the required baseline/smoke step for a long Optuna run has not been run and recorded in this
   session

Config validation also has **not** in this session been explicitly documented as green; observed
warnings without a documented success signal are not enough to satisfy a launch precondition.

Because these blockers remain open, launch authorization cannot be granted now without violating
fail-closed governance.

## Evidence observed in this session

The following evidence was observed directly before writing this packet.

### 1. Working tree status

Observed state:

- dirty working tree

Observed evidence:

- `git status --short` reported unstaged Markdown changes outside this packet scope

Implication:

- the clean-working-tree precondition from the setup packet is not currently satisfied

### 2. Preflight result

Observed state:

- preflight failed

Observed evidence:

- `scripts/preflight/preflight_optuna_check.py` reported:
  - `Resume=false men storage-fil finns redan: results/hparam_search/storage/ri_challenger_family_slice8_3h_2024_v1.db`

Implication:

- launch is blocked until the storage/restart conflict is resolved outside this packet

### 3. Storage existence

Observed state:

- storage exists

Observed evidence:

- explicit check returned `STORAGE_EXISTS=1`

Implication:

- the current storage target may not be silently reused while `resume=false`

### 4. Config validation status

Observed state:

- warnings observed; explicit green success not documented in this session

Observed evidence:

- `scripts/validate/validate_optimizer_config.py` produced warnings but no separately captured
  explicit success signal in the recorded session evidence

Implication:

- config validation is not yet eligible to be counted as a documented green pre-launch check in
  this packet

### 5. Baseline / smoke status

Observed state:

- not yet run or recorded in this session

Observed basis:

- `optuna_run_guardrails`
- `docs/optuna/OPTUNA_BEST_PRACTICES.md`

Implication:

- the required baseline/smoke prerequisite for a long run remains open

## Exact pre-launch checks that must be green before later authorization can flip to yes

The following checks must all be green before a later separately tracked launch-authorization step
may change the verdict to `AUTHORIZED`.

| Check                                   | Required state                | Current status in this session                      | Why it matters                                            |
| --------------------------------------- | ----------------------------- | --------------------------------------------------- | --------------------------------------------------------- |
| Working tree clean                      | Green                         | Red                                                 | provenance must remain reviewable before launch           |
| Config validation                       | Green / explicitly documented | Not yet documented green                            | warnings without explicit green evidence are insufficient |
| Preflight                               | Green                         | Red                                                 | current preflight fail blocks launch                      |
| Storage discipline under `resume=false` | Green                         | Red                                                 | existing DB may not be silently reused                    |
| Baseline / smoke before long run        | Green / documented            | Red                                                 | required by existing guardrails and best practices        |
| Research-only framing retained          | Green                         | Green only as packet intent, not as launch evidence | launch must stay inside the RI research lane              |

## Exact launch input artifact

If launch is later authorized in a separate tracked step, the exact launch artifact remains:

- `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice8_2024_v1.yaml`

This packet does not authorize launching any alternate YAML, any edited copy, any bridge JSON, or
any derived candidate file by substitution.

## Research-only run boundary

Any later launch under this lane remains strictly bounded as follows.

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

The bridge artifact may still support only the bounded claim:

- `RI is runnable`

It may not be upgraded by this packet or by any later run in this lane into comparison merit,
readiness support, or promotion support.

## Required output handling and artifact discipline after any later run

If a later separately tracked step eventually authorizes and executes the run, output handling must
remain disciplined as follows.

### Raw run artifacts

Raw run artifacts may remain under the expected local research output area, such as:

- `results/hparam_search/...`
- `results/hparam_search/storage/...`
- `results/hparam_search/.../validation/...`

These remain RI-family-internal research artifacts only.

They are not by themselves tracked proof of comparison, readiness, or promotion.

### Required provenance capture

Any later run report must record at minimum:

- exact config path launched
- git commit used for the run
- study name and storage path
- sample and validation windows
- actual launch-session env/flag surface
- outcome of preflight, validation, and baseline/smoke prerequisites

### Tracked summary discipline

If any tracked summary is created after the run, it must:

- remain explicitly research-only
- identify the run as RI-family-internal
- avoid comparison, readiness, and promotion framing
- avoid upgrading the bridge claim beyond `RI is runnable`

### Forbidden post-run handling in this lane

- no automatic champion update
- no automatic writeback
- no automatic comparison packet
- no automatic readiness packet
- no automatic promotion packet

## What must happen before a later authorization packet could say yes

Before a later packet may authorize launch, all of the following must be true and explicitly
documented as green:

1. the working tree is clean
2. the exact YAML above is still the intended launch subject
3. config validation is explicitly documented green
4. preflight is explicitly documented green
5. the `resume=false` storage conflict is resolved without silent reuse of the existing DB
6. baseline/smoke is documented in line with `optuna_run_guardrails` and
   `docs/optuna/OPTUNA_BEST_PRACTICES.md`
7. the run remains strictly inside the RI research lane

## Bottom line

This packet records the separate governed launch decision for the RI research / Optuna lane.

That decision is:

- **NOT AUTHORIZED NOW**

Reason:

- current launch prerequisites are not fully green, including a dirty working tree, a failed
  preflight due to existing storage under `resume=false`, and a missing recorded baseline/smoke
  prerequisite.

The setup packet remains setup-only prerequisite input.

No comparison, readiness, or promotion scope is reopened here.
