# RI router replay defensive-transition backtest launch authorization packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `launch authorization decision recorded / fail-closed / not authorized now`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet records an explicit launch-authorization decision for the exact paired defensive-transition backtest surface, but it must remain docs-only and must not reopen runtime integration, paper coupling, readiness, cutover, or promotion.
- **Required Path:** `Quick`
- **Objective:** convert the existing paired launch-boundary surface into a separate governed launch decision for the exact defensive-transition baseline-vs-candidate no-save decision-row capture subject.
- **Candidate:** `defensive-transition paired backtest launch authorization`
- **Base SHA:** `f6489eb6`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Boundary packet is prerequisite input only`
- `No runtime/paper/readiness/promotion reopening`
- `No writable-surface expansion by implication`

### Skill Usage

- **Consulted repo-local spec:** `backtest_run`
- **Reason:** the authorization decision depends on canonical mode discipline, explicit seed handling, and reproducible command shape.
- **Consulted repo-local spec:** `genesis_backtest_verify`
- **Reason:** any later execution must remain deterministic, non-secret-bearing, and separately verifiable.
- **No run-domain skill claimed as executed:** this packet records a docs-only launch decision and does not run any backtest.

### Scope

- **Scope IN:**
  - create one docs-only launch-authorization packet for the exact defensive-transition paired subject
  - record explicit `AUTHORIZED NOW` or `NOT AUTHORIZED NOW` verdict
  - align the paired launch-boundary packet and `GENESIS_WORKING_CONTRACT.md` to the same containment verdict
  - keep all reasoning below runtime/default authority
- **Scope OUT:**
  - no `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, or `artifacts/**` changes
  - no actual baseline run
  - no actual candidate run
  - no result comparison artifact
  - no runtime instrumentation approval
  - no paper coupling
  - no readiness/cutover/promotion reopening
- **Expected changed files:**
  - `docs/governance/ri_router_replay_defensive_transition_backtest_launch_authorization_packet_2026-04-23.md`
  - `docs/governance/ri_router_replay_defensive_transition_backtest_launch_boundary_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `3`

### Gates required

For this packet itself:

- markdown/file validation only

For interpretation discipline inside this packet:

- no sentence may treat the boundary packet as launch approval
- no sentence may authorize launch while bounded write containment is red
- no sentence may upgrade descriptive command targets into execution approval
- no sentence may widen writable surfaces beyond what is explicitly stated
- no sentence may imply execution was performed in this packet

### Stop Conditions

- any wording that collapses boundary and authorization into one decision
- any wording that treats `--no-save` as full containment proof by itself
- any wording that treats `cache/precomputed/*.npz` writes as implicitly approved
- any wording that upgrades the paired slice into runtime, paper, readiness, cutover, or promotion evidence
- any need to modify files outside the three scoped docs files

### Output required

- reviewable launch-authorization packet
- explicit authorization verdict
- explicit evidence matrix
- explicit RI-only run boundary
- explicit output handling and artifact discipline rules

## Purpose

This packet records a **separate launch-authorization decision** for the already-defined defensive-transition paired backtest surface.

This packet does **not** reinterpret the launch-boundary packet as launch approval.
The boundary packet is used only as prerequisite input to a distinct launch-authorization assessment.

Fail-closed interpretation:

> This packet uses the paired launch-boundary packet only as prerequisite input to a separate launch-authorization decision for the exact defensive-transition baseline-vs-candidate subject. It does not itself authorize execution unless all required preconditions are explicitly green.

## Upstream governed basis

This packet is downstream of the following tracked documents:

- `docs/governance/ri_router_replay_counterfactual_closeout_report_2026-04-23.md`
- `docs/governance/ri_router_replay_defensive_transition_semantics_packet_2026-04-23.md`
- `docs/governance/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`
- `docs/governance/ri_router_replay_defensive_transition_backtest_setup_only_packet_2026-04-23.md`
- `docs/governance/ri_router_replay_defensive_transition_backtest_launch_boundary_packet_2026-04-23.md`

Carried-forward meaning from that chain:

1. the exact defensive-transition paired subject is already fixed to one baseline bridge and one separate candidate bridge on `tBTCUSD`, `3h`, `2024-01-02 -> 2024-12-31`, warmup `120`
2. setup-only and launch-boundary framing never authorized launch by themselves
3. candidate expressibility is no longer the blocker
4. launch still requires both clean authorization logic and green bounded write containment

## Exact launch subject

The exact launch subject evaluated by this packet is the paired baseline-vs-candidate RI bridge surface:

### Baseline bridge

- path: `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- SHA256: `824E409D39B7E09A7B04FD2AEE9A34E4D0C3F010440FB6D68069764EB17A0BAD`

### Candidate bridge

- path: `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json`
- SHA256: `EF7661A673C3BFC89C1D60168163F4651EDA99D5937DD2163F5B666AD8ED51F7`

### Boundaried context

- symbol: `tBTCUSD`
- timeframe: `3h`
- date window: `2024-01-02 -> 2024-12-31`
- warmup bars: `120`
- data-source policy: `frozen_first`
- canonical mode intent: `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`, `GENESIS_RANDOM_SEED=42`, `GENESIS_FAST_HASH=0`, plus `--fast-window --precompute-features`

This packet authorizes or declines launch only for that exact paired subject and bounded context.
No alternate config, edited copy, bridge variant, or widened execution surface is authorized by implication.

## Authorization verdict

### Decision

- **NOT AUTHORIZED NOW**

### Why this is the correct fail-closed decision

The paired launch-boundary packet established that a later launch packet remains blocked unless all required preconditions are green.
That threshold is not met in the evidence observed in this session.

The durable blocker is:

1. **full bounded write containment is not green** because the canonical paired run shape keeps `GENESIS_PRECOMPUTE_FEATURES=1`, and `src/core/backtest/engine.py` can therefore create `cache/precomputed/` and attempt `_np.savez_compressed(...)` to `cache/precomputed/<key>.npz`, which lies outside the currently bounded output surface.

An additional transient blocker observed during this assessment was:

2. the tracked worktree was not clean at assessment time because the paired launch-boundary packet itself was in flight.

Even if the transient worktree issue is cleared after this docs-only slice, launch authorization still cannot be granted because the containment blocker remains red.

## Evidence observed in this session

### 1. Working tree status at assessment time

Observed state:

- dirty tracked worktree during packet drafting

Observed evidence:

- `git status --short` showed:
  - `M docs/governance/ri_router_replay_defensive_transition_backtest_launch_boundary_packet_2026-04-23.md`

Implication:

- the clean-working-tree precondition was not green at assessment time
- this is not the durable blocker, but it prevents a clean `AUTHORIZED NOW` conclusion for the drafting snapshot

### 2. Exact paired bridge identities

Observed state:

- green

Observed evidence:

- the baseline bridge exists at the fixed path with SHA256 `824E409D39B7E09A7B04FD2AEE9A34E4D0C3F010440FB6D68069764EB17A0BAD`
- the candidate bridge exists at the fixed path with SHA256 `EF7661A673C3BFC89C1D60168163F4651EDA99D5937DD2163F5B666AD8ED51F7`

Implication:

- the exact paired subject is stable enough to remain the only launch subject under consideration

### 3. Repo-visible CLI support

Observed state:

- green as current repo-visible surface only

Observed evidence:

- `scripts/run/run_backtest.py` currently exposes:
  - `--config-file`
  - `--warmup`
  - `--data-source-policy`
  - `--fast-window`
  - `--precompute-features`
  - `--decision-rows-out`
  - `--decision-rows-format`
  - `--no-save`

Implication:

- the descriptive paired command targets still map to current repo-visible flags
- this is not by itself launch approval or write-containment proof

### 4. Full bounded write-containment status

Observed state:

- **not green**

Observed evidence:

- the paired launch-boundary packet intentionally limited future explicit outputs to:
  - `results/backtests/ri_router_defensive_transition_backtest_20260423/baseline_decision_rows.ndjson`
  - `results/backtests/ri_router_defensive_transition_backtest_20260423/candidate_decision_rows.ndjson`
  - `docs/governance/ri_router_replay_defensive_transition_backtest_execution_summary_2026-04-23.md`
- `--no-save` suppresses `TradeLogger.save_all(...)`, but does **not** by itself prove full bounded containment
- inside `src/core/backtest/engine.py`, when precompute is enabled under canonical mode, the backtest engine currently does:
  - `cache_dir = Path(__file__).resolve().parents[3] / "cache" / "precomputed"`
  - `cache_dir.mkdir(parents=True, exist_ok=True)`
  - `cache_path = cache_dir / f"{key}.npz"`
  - attempts `_np.savez_compressed(cache_path, ...)`
- the canonical paired command shape fixed upstream still requires `GENESIS_PRECOMPUTE_FEATURES=1` and `--precompute-features`

Implication:

- the current canonical paired no-save surface can still create out-of-bound writes under `cache/precomputed/`
- full bounded write containment therefore remains red

### 5. Intelligence-shadow / ledger surfaces

Observed state:

- not applicable to this paired subject

Observed evidence:

- the paired baseline/candidate command targets do **not** request `--intelligence-shadow-out`
- the current blocker is therefore simpler than the earlier shadow slice: no shadow summary or ledger-root derivation is needed for this exact RI pair

Implication:

- shadow/ledger derivation is not the blocker here
- write containment is already red before any shadow-like surface would matter

## Exact preconditions and current status

| Check                                   | Required state | Current status in this session | Why it matters                                                                      |
| --------------------------------------- | -------------- | ------------------------------ | ----------------------------------------------------------------------------------- |
| Working tree clean at assessment time   | Green          | Red                            | provenance and exact-state launch discipline must remain reviewable                 |
| Exact baseline bridge identity          | Green          | Green                          | launch subject must remain exact and fingerprint-stable                             |
| Exact candidate bridge identity         | Green          | Green                          | candidate subject must remain exact and fingerprint-stable                          |
| Current repo-visible CLI flag support   | Green          | Green                          | descriptive paired command targets must still match current repo entrypoints        |
| Canonical mode discipline               | Green          | Green                          | the paired run must remain comparable and deterministic under the reviewed mode     |
| Full bounded write containment          | Green          | Red                            | launch may not leak writes outside the approved paired surface                      |
| RI-only observational boundary retained | Green          | Green                          | slice must stay below runtime integration, paper coupling, readiness, and promotion |

## Research-only run boundary

If launch is ever authorized later in a separate tracked step, the run boundary remains strictly limited as follows.

### Allowed boundary

- research only
- RI-only only
- observational-only only
- exact paired bridge subject only
- bounded to `tBTCUSD`, `3h`, `2024-01-02 -> 2024-12-31`, warmup `120`

### Disallowed boundary

- no runtime integration claims
- no paper or shadow claims
- no readiness or cutover claims
- no promotion claims
- no champion/default/config-authority claims
- no widened execution surface beyond the exact paired baseline/candidate no-save decision-row setup

## Output handling and artifact discipline after any later launch

If a later separately tracked step eventually authorizes and executes the pair, output handling must remain bounded as follows.

These listed paths remain conditional on a later separately tracked authorization and containment fix; listing them here is not approval proof.

### Intended explicit outputs

Only the following explicit paired outputs are candidates for later authorization:

- `results/backtests/ri_router_defensive_transition_backtest_20260423/baseline_decision_rows.ndjson`
- `results/backtests/ri_router_defensive_transition_backtest_20260423/candidate_decision_rows.ndjson`
- `docs/governance/ri_router_replay_defensive_transition_backtest_execution_summary_2026-04-23.md`

### Currently unauthorized side effects

The following surface is **not** currently authorized and is the reason launch remains blocked:

- `cache/precomputed/`
- any derived `cache/precomputed/<key>.npz`

### Forbidden post-run handling

- no automatic backtest result save outside the intended explicit outputs
- no automatic comparison packet
- no automatic runtime/paper/readiness/promotion packet
- no code/config/test/runtime widening in place

## What must happen before a later authorization packet could say yes

Before a later packet may change the verdict to `AUTHORIZED NOW`, all of the following must be explicitly documented green:

1. the working tree is clean for tracked files touching the paired bridges, runner entrypoint, or governed packet chain
2. the exact baseline and candidate bridge files still match the SHA256 values recorded above
3. the current repo-visible CLI flags still support the descriptive paired command targets
4. full bounded write containment is explicitly green for canonical paired execution, including the absence of unapproved `cache/precomputed/` writes, or a separately governed writable-surface decision exists (non-preferred path)
5. the run remains strictly inside the RI-only observational research lane with no widening
6. any later execution remains separate from metrics comparison, readiness, or promotion claims

## Preferred future remediation path

The preferred future remediation is:

- a **separately governed containment-fix packet** that removes or suppresses out-of-bound `cache/precomputed/*.npz` writes from the exact paired launch surface without reopening broader runtime/default authority

A writable-surface expansion to include `cache/precomputed/` remains:

- separate
- non-preferred
- not authorized by this packet

## Bottom line

This packet records the separate governed launch decision for the exact defensive-transition paired backtest subject.

That decision is:

- **NOT AUTHORIZED NOW**

Reason:

- the current canonical paired no-save run surface is not fully write-contained because `src/core/backtest/engine.py` can still create/write under `cache/precomputed/`, and the drafting snapshot also had an in-flight tracked docs change.

The launch-boundary packet remains prerequisite input only.
No execution, runtime integration, paper coupling, readiness, cutover, or promotion scope is opened here.
