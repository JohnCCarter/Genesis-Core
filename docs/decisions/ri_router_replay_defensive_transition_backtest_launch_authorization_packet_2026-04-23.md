# RI router replay defensive-transition backtest launch authorization packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `launch authorization refreshed / pre-execution only / authorized now`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `MED` — why: this packet records an explicit launch-authorization decision for the exact paired defensive-transition backtest surface, but it must remain docs-only and must not reopen runtime integration, paper coupling, readiness, cutover, or promotion.
- **Required Path:** `Lite`
- **Objective:** refresh the existing paired launch decision so that it evaluates the exact defensive-transition baseline-vs-candidate no-save decision-row capture subject on the explicit suppressed-write command surface that sets `GENESIS_PRECOMPUTE_CACHE_WRITE=0`.
- **Candidate:** `defensive-transition paired backtest launch authorization`
- **Base SHA:** `4690e9d8`

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Research lane only`
- `Boundary packet is prerequisite input only`
- `No runtime/paper/readiness/promotion reopening`
- `No writable-surface expansion by implication`
- `Exact suppressed-write surface only`

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
  - `docs/decisions/ri_router_replay_defensive_transition_backtest_launch_authorization_packet_2026-04-23.md`
  - `docs/decisions/ri_router_replay_defensive_transition_backtest_launch_boundary_packet_2026-04-23.md`
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

- `docs/decisions/ri_router_replay_counterfactual_closeout_report_2026-04-23.md`
- `docs/decisions/ri_router_replay_defensive_transition_semantics_packet_2026-04-23.md`
- `docs/decisions/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`
- `docs/decisions/ri_router_replay_defensive_transition_backtest_setup_only_packet_2026-04-23.md`
- `docs/decisions/ri_router_replay_defensive_transition_backtest_launch_boundary_packet_2026-04-23.md`
- `docs/decisions/ri_router_replay_defensive_transition_backtest_precompute_containment_implementation_packet_2026-04-23.md`

Carried-forward meaning from that chain:

1. the exact defensive-transition paired subject is already fixed to one baseline bridge and one separate candidate bridge on `tBTCUSD`, `3h`, `2024-01-02 -> 2024-12-31`, warmup `120`
2. setup-only and launch-boundary framing never authorized launch by themselves
3. candidate expressibility is no longer the blocker
4. launch requires both clean authorization logic and green bounded write containment on the exact command surface under review

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
- canonical mode intent: `GENESIS_FAST_WINDOW=1`, `GENESIS_PRECOMPUTE_FEATURES=1`, `GENESIS_RANDOM_SEED=42`, `GENESIS_FAST_HASH=0`, `GENESIS_PRECOMPUTE_CACHE_WRITE=0`, plus `--fast-window --precompute-features`

This packet authorizes or declines launch only for that exact paired subject and bounded context.
No alternate config, edited copy, bridge variant, or widened execution surface is authorized by implication.

Authorization in this packet applies only to the exact command targets fixed in the refreshed boundary packet, including the explicit containment qualifier `GENESIS_PRECOMPUTE_CACHE_WRITE=0` and the bounded output surface listed there.

`AUTHORIZED NOW` applies only to the exact suppressed-write execution surface defined in this packet. It is not a claim that the current repository worktree is globally clean, nor that execution has already occurred; launch must begin from a clean or separately reviewed snapshot of the governed paired surface, and any env/command/output/repo-state drift requires fresh review.

Known unrelated tracked diff at assessment time: `data/DATA_FORMAT.md` is outside this packet's governed surface and is not covered by this authorization or boundary assessment.

## Authorization verdict

### Decision

- **AUTHORIZED NOW**

### Why this is the correct fail-closed decision

The paired launch-boundary packet established that a later launch packet may only turn green when all required preconditions are explicitly green.
That threshold is now met for the exact paired pre-execution surface documented here.

In particular:

1. the paired subject/runtime surfaces remain stable outside this docs-only refresh
2. the exact paired bridge identities remain unchanged
3. the current repo-visible runner surface still supports the required flags and explicit decision-row outputs
4. the exact suppressed-write command surface now keeps bounded write containment green by combining `--no-save`, no `--intelligence-shadow-out`, and `GENESIS_PRECOMPUTE_CACHE_WRITE=0`
5. the authorization remains strictly bounded to RI-only observational execution and does not widen into readiness, promotion, or runtime-default authority

## Evidence observed in this session

### 1. Paired subject/runtime surface status at assessment time

Observed state:

- green on the paired subject/runtime surfaces; this docs-only refresh is in flight and unrelated workspace edits remain outside scope

Observed evidence:

- current tracked changes are limited to this docs-only packet refresh plus unrelated `data/DATA_FORMAT.md`
- no current diff touches the paired bridge files, `scripts/run/run_backtest.py`, `src/core/backtest/engine.py`, or `src/core/config/authority.py`

Implication:

- the exact launch subject and containment anchors are stable for this authorization decision
- any later execution should still start from a clean or separately reviewed snapshot of the governed paired surface

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

- **green for the exact suppressed-write surface**

Observed evidence:

- the refreshed paired launch-boundary packet intentionally limits the explicit outputs to:
  - `results/backtests/ri_router_defensive_transition_backtest_20260423/baseline_decision_rows.ndjson`
  - `results/backtests/ri_router_defensive_transition_backtest_20260423/candidate_decision_rows.ndjson`
  - `docs/analysis/ri_router_replay_defensive_transition_backtest_execution_summary_2026-04-23.md`
- `scripts/run/run_backtest.py::_write_decision_rows(...)` writes only to the explicit decision-row output path
- `TradeLogger.save_all(...)` remains behind `if not args.no_save`, so `--no-save` suppresses timestamp-driven result/trade/equity writes
- no `--intelligence-shadow-out` path is used for this exact pair
- inside `src/core/backtest/engine.py`, `GENESIS_PRECOMPUTE_CACHE_WRITE=0` now suppresses `cache_dir.mkdir(...)` plus `_np.savez_compressed(...)` on cache miss while preserving existing cache reads and in-memory precompute for the run
- the containment implementation gates passed, including focused engine coverage for cache-miss suppression, cache-hit read-only behavior, and cache-miss parity between env-absent and `GENESIS_PRECOMPUTE_CACHE_WRITE=0`

Implication:

- the exact paired command surface documented here may stay confined to the explicit decision-row outputs plus a later human-written execution summary
- cache reads may still occur, but this authorization does **not** claim zero cache or zero filesystem interaction; it claims only that unapproved cache writes on miss are suppressed for the exact surface under review

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

| Check                                                     | Required state | Current status in this session               | Why it matters                                                                           |
| --------------------------------------------------------- | -------------- | -------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Paired subject/runtime surfaces stable at assessment time | Green          | Green                                        | provenance and exact-state launch discipline must remain reviewable                      |
| Exact baseline bridge identity                            | Green          | Green                                        | launch subject must remain exact and fingerprint-stable                                  |
| Exact candidate bridge identity                           | Green          | Green                                        | candidate subject must remain exact and fingerprint-stable                               |
| Current repo-visible CLI flag support                     | Green          | Green                                        | descriptive paired command targets must still match current repo entrypoints             |
| Explicit suppressed-write env qualifier                   | Green          | Green                                        | authorization is bound to `GENESIS_PRECOMPUTE_CACHE_WRITE=0`, not to env-absent variants |
| Canonical mode discipline                                 | Green          | Green                                        | the paired run must remain comparable and deterministic under the reviewed mode          |
| Full bounded write containment                            | Green          | Green for the exact suppressed-write surface | launch may not leak writes outside the approved paired surface                           |
| RI-only observational boundary retained                   | Green          | Green                                        | slice must stay below runtime integration, paper coupling, readiness, and promotion      |

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

These listed paths remain conditional on a later separately tracked execution step; listing them here is not proof that execution already happened.

### Intended explicit outputs

Only the following explicit paired outputs are candidates for later authorization:

- `results/backtests/ri_router_defensive_transition_backtest_20260423/baseline_decision_rows.ndjson`
- `results/backtests/ri_router_defensive_transition_backtest_20260423/candidate_decision_rows.ndjson`
- `docs/analysis/ri_router_replay_defensive_transition_backtest_execution_summary_2026-04-23.md`

### Currently unauthorized side effects

The following surface remains unauthorized by implication and is kept out of scope by the exact command shape approved here:

- `cache/precomputed/` writes on cache miss
- any derived `cache/precomputed/<key>.npz` write on cache miss

This authorization depends on explicit suppression of those writes via `GENESIS_PRECOMPUTE_CACHE_WRITE=0`; it does **not** widen them into approved writable surfaces.

### Forbidden post-run handling

- no automatic backtest result save outside the intended explicit outputs
- no automatic comparison packet
- no automatic runtime/paper/readiness/promotion packet
- no code/config/test/runtime widening in place

## What must remain true for this `AUTHORIZED NOW` decision to stay valid

This authorization remains valid only while all of the following stay true:

1. the working tree is clean for tracked files touching the paired bridges, runner entrypoint, or governed packet chain at execution start
2. the exact baseline and candidate bridge files still match the SHA256 values recorded above
3. the current repo-visible CLI flags still support the descriptive paired command targets
4. the exact execution surface still includes `GENESIS_PRECOMPUTE_CACHE_WRITE=0`, `--no-save`, and no `--intelligence-shadow-out`
5. the bounded output surface remains limited to the explicit decision-row captures plus the later human-written execution summary documented here and in the refreshed boundary packet
6. the run remains strictly inside the RI-only observational research lane with no widening
7. any command-shape, env-surface, output-surface, or repo-state drift requires fresh review rather than silent carry-forward

## Preferred future remediation path

The containment-fix step is now complete.

The next operational step, if the user wants to proceed, is a separate execution slice on the exact authorized suppressed-write surface documented here and in the refreshed boundary packet.

## Bottom line

This packet records the separate governed launch decision for the exact defensive-transition paired backtest subject on the explicit suppressed-write command surface.

That decision is:

- **AUTHORIZED NOW**

Reason:

- the exact paired pre-execution surface is now fully bounded for launch authorization purposes when it explicitly sets `GENESIS_PRECOMPUTE_CACHE_WRITE=0`, keeps `--no-save`, omits `--intelligence-shadow-out`, and limits outputs to the documented decision-row captures plus the later human-written execution summary.

The launch-boundary packet remains prerequisite input only.
No execution has happened in this packet, and no runtime integration, paper coupling, readiness, cutover, or promotion scope is opened here.
