# RI router replay defensive-transition backtest pre-code packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code-defined / planning-only / no execution authorization`

This packet defines the first exact bounded backtest question that may be considered after the RI router replay counterfactual closeout and the defensive-transition semantics packet.

It does **not** authorize execution, code changes, config changes, runtime integration, default changes, family authority, promotion claims, or paper/live coupling.

Any runnable backtest step still requires a separate follow-up packet with fresh scope approval and explicit launch-time verification.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: this packet is docs-only and defines one bounded future backtest comparison question without opening execution or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — the semantics question is already narrowed; the next admissible move is to define one exact backtest comparison that can later test whether the replay-local finding survives on a bounded runtime-bridge subject.
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** define one future bounded baseline-vs-candidate backtest comparison for the `defensive_transition_state` mandate-2 candidate on a fixed RI bridge subject.
- **Candidate:** `future defensive-transition mandate-2 backtest comparison`
- **Base SHA:** `2dc6df79`

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/decisions/ri_router_replay_counterfactual_closeout_report_2026-04-23.md`
  - `docs/decisions/ri_router_replay_defensive_transition_semantics_packet_2026-04-23.md`
  - `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
  - `.github/skills/backtest_run.json`
  - `.github/skills/genesis_backtest_verify.json`
  - `docs/features/FEATURE_COMPUTATION_MODES.md`
- **Candidate / comparison surface:**
  - exact current bridge behavior as baseline versus one candidate that differs only by treating `defensive_transition_state` as a mandate/confidence-2 candidate instead of mandate/confidence-1.
- **Vad ska förbättras:**
  - determine whether the replay-local defensive-transition finding survives on a bounded backtest subject,
  - keep the candidate semantically local instead of reopening broad global gate tuning,
  - preserve canonical comparability and deterministic interpretation.
- **Vad får inte brytas / drifta:**
  - symbol/timeframe/date window,
  - canonical execution mode,
  - seed discipline,
  - warmup discipline,
  - baseline bridge identity,
  - runtime/default/family authority boundaries,
  - broad gate semantics outside the exact candidate under test.
- **Reproducerbar evidens som måste finnas om nästa steg öppnas:**
  - one baseline backtest result on the exact fixed subject,
  - one candidate backtest result on the exact same subject,
  - explicit symbol/timeframe/start/end/warmup/seed/execution_mode metadata for both runs,
  - deterministic or at least comparability-safe result handling under canonical mode,
  - one bounded comparison summary that states whether the replay-local finding survives, weakens, or fails.

## Purpose

This packet answers one narrow question only:

- what exact bounded backtest subject should be used first if we want to test the `defensive_transition_state mandate-2` hypothesis beyond the frozen replay surface?

This packet is **planning-only governance**.

It does **not**:

- authorize a runnable backtest yet
- authorize code changes
- authorize config changes
- authorize default-path changes
- authorize runtime integration
- authorize optimizer or parameter-sweep work
- authorize readiness, cutover, or promotion claims

## Why this packet exists now

The closed counterfactual lane established the following bounded conclusion:

1. `switch_threshold: 2 -> 1` materially improves defensive selection on the frozen replay surface.
2. `defensive_transition_state mandate/confidence: 1 -> 2` produces the same routed outcome as `switch_threshold: 2 -> 1` on that surface.
3. `min_dwell` and `hysteresis` no longer appear to be the best explanatory frontier for the current lane.

Interpretation:

- The next useful step is no longer another replay-only gate toggle.
- The next useful step is one exact bounded backtest comparison that can test whether the semantically narrower candidate survives outside the replay-only surface.

## Exact future subject boundary

The exact future backtest subject is fixed as follows:

### Exact config anchor

- path: `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- SHA256: `824E409D39B7E09A7B04FD2AEE9A34E4D0C3F010440FB6D68069764EB17A0BAD`

This file is already described by its own metadata as:

- `strategy_family = ri`
- backtest-only runtime bridge
- not a champion
- not promotion evidence

### Exact observational context

- symbol: `tBTCUSD`
- timeframe: `3h`
- date window: `2024-01-02 -> 2024-12-31`
- warmup bars: `120`

### Exact canonical execution expectations

Any future runnable comparison under a separate packet must keep the following fixed unless a later packet explicitly says otherwise:

- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_HASH=0`
- explicit CLI flags `--fast-window --precompute-features`
- execution mode comparability discipline per `.github/skills/backtest_run.json`

## Exact future comparison shape

If a later runnable step is separately authorized, the first exact comparison should be:

### Baseline

- current bridge behavior with no semantics change

### Candidate

- the same exact bridge subject,
- the same exact symbol/timeframe/date window,
- the same exact canonical execution mode,
- with one local candidate difference only:
  - `defensive_transition_state` treated as a mandate/confidence-2 candidate instead of mandate/confidence-1

### What remains fixed between baseline and candidate

- all non-candidate bridge config fields
- symbol/timeframe/date window
- warmup bars
- seed
- canonical execution flags
- data-source policy unless separately reopened later
- result-comparison discipline

## Future evidence classes if execution is later authorized

If a later runnable slice is separately authorized, it should produce only bounded evidence classes such as:

1. one baseline backtest artifact under `results/backtests/`
2. one candidate backtest artifact under `results/backtests/`
3. one bounded comparison artifact or execution summary under a tracked research/governance surface

This packet does **not** yet authorize or freeze the exact writable paths for those outputs.
That must be handled by a later setup/launch packet once the execution surface is explicitly approved.

## Prove-or-stop hypothesis

The exact bounded hypothesis for a later run is:

- the semantically local candidate (`defensive_transition_state mandate/confidence 2`) should preserve bounded comparability while showing candidate behavior that remains directionally consistent with the replay-local improvement, without requiring broader gate-stack changes.

This is a prove-or-stop hypothesis only.
If the later backtest comparison requires broader runtime/config/code widening to look coherent, the lane should stop rather than widen in place.

## Scope

- **Scope IN:**
  - `docs/decisions/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `scripts/**`
  - `results/**`
  - `artifacts/**`
  - any runnable backtest
  - any optimizer or sweep packet
  - runtime integration
  - default-authority changes
  - family-rule changes
  - readiness / promotion semantics
- **Expected changed files:**
  - `docs/decisions/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Mode proof

- **Why this mode applies:** branch mapping from `feature/*` resolves to `RESEARCH` per `docs/governance_mode.md`.
- **What RESEARCH allows here:** one small docs-only packet that defines a bounded future backtest question below runtime/default authority.
- **What remains forbidden here:** runnable backtest execution, runtime integration, family-rule changes, readiness/promotion framing, champion/default changes, and optimizer-like widening.
- **What would force STRICT escalation:** touching `config/strategy/champions/`, `.github/workflows/champion-freeze-guard.yml`, runtime-default authority surfaces, family-rule surfaces, or promotion/readiness surfaces.

## Gates required for this packet

Choose the minimum docs-only gates appropriate to the current scope:

1. `pre-commit run --files GENESIS_WORKING_CONTRACT.md docs/decisions/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`
2. basic file diagnostics for both markdown files

No runtime-classified gates are required for this packet itself because it is docs-only and opens no runnable surface by itself.

## Stop Conditions

- the packet starts implicitly authorizing execution rather than scoping the future slice
- the packet widens from one exact candidate into multiple candidates or a sweep
- the packet stops being local to the `defensive_transition_state` mandate question
- the packet starts assuming the mandate-2 candidate is already proven instead of merely packet-worthy
- any need to modify files outside the two scoped docs files

## Output required

- one backtest pre-code packet
- one updated working anchor

## Bottom line

The replay and semantics lanes have already localized the next useful question. The next admissible move is not another generic replay slice, but one exact bounded backtest comparison between the current bridge baseline and the semantically local `defensive_transition_state mandate-2` candidate. This packet defines that backtest subject only; it does not authorize execution by itself.
