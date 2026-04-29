# RI router replay defensive-transition bridge-activation pre-code packet

Date: 2026-04-23
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `pre-code-defined / config-slice-defined / no implementation authorization`

This packet records the next smallest admissible step after the bounded candidate-gate carrier implementation.

It does **not** authorize code changes, execution, launch, runtime-default drift, family widening, or promotion claims.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: this packet is docs-only and defines one bounded future config-only candidate-activation slice without opening launch or runtime-authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the runtime carrier already exists and is validated, but the candidate is still not expressible as a separate bounded backtest artifact because no dedicated bridge config activates the new default-off research leaf.
- **Objective:** define one exact future config-only candidate-activation slice that would make the defensive-transition carrier expressible on the fixed RI bridge subject without changing the baseline bridge file, runtime defaults, CLI surfaces, or launch authority.
- **Candidate:** `defensive-transition bridge activation`
- **Base SHA:** `2dc6df79`

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/governance/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`
  - `docs/governance/ri_router_replay_defensive_transition_backtest_setup_only_packet_2026-04-23.md`
  - `docs/governance/ri_router_replay_defensive_transition_candidate_gate_carrier_precode_packet_2026-04-23.md`
  - `docs/governance/ri_router_replay_defensive_transition_candidate_gate_carrier_implementation_packet_2026-04-23.md`
  - `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- **Candidate / comparison surface:**
  - preserve the current bridge file as the baseline reference,
  - define one future candidate bridge file that differs only by explicit activation of `multi_timeframe.research_defensive_transition_override`.
- **Vad ska förbättras:**
  - make the validated carrier expressible as a separate repo-visible candidate artifact,
  - keep baseline-vs-candidate comparability bounded,
  - avoid reopening runner, launch, or default-authority surfaces.
- **Vad får inte brytas / drifta:**
  - the existing bridge anchor path and meaning,
  - untouched default behavior,
  - canonical config-authority semantics,
  - CLI/backtest entrypoint shape,
  - family identity,
  - launch separation.
- **Reproducerbar evidens som måste finnas om nästa steg öppnas:**
  - one exact candidate config path,
  - one exact field delta versus the baseline bridge file,
  - proof that only the new research leaf is added,
  - proof that baseline bridge identity remains unchanged,
  - explicit statement that launch remains separately governed.

### Constraints

- `NO BEHAVIOR CHANGE`
- `docs-only`
- `Config-slice framing only`
- `No bridge-file creation in this packet`
- `No launch authorization`
- `No runtime-default / family / promotion reopening`

### Skill Usage

- **Applied repo-local skill:** none
- **Reason:** this packet is docs-only and does not itself execute a config-authority, runtime, or backtest workflow.
- **Deferred:** `python_engineering`, `decision_gate_debug`, `backtest_run`, and `genesis_backtest_verify` remain relevant only if a later config or execution slice is separately opened.

### Scope

- **Scope IN:**
  - create one docs-only pre-code packet for one future config-only candidate-activation slice
  - fix the exact future candidate bridge-config path
  - fix the exact intended leaf delta relative to the baseline bridge file
  - re-anchor `GENESIS_WORKING_CONTRACT.md` to the post-implementation / pre-activation state
- **Scope OUT:**
  - no `src/**` edits
  - no `tests/**` edits
  - no `config/**` file edits
  - no `scripts/**` edits
  - no launch packet
  - no backtest execution
  - no result/artifact generation
  - no runtime-default, family-rule, or bridge-baseline mutation
- **Expected changed files:**
  - `docs/governance/ri_router_replay_defensive_transition_bridge_activation_precode_packet_2026-04-23.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

### Gates required

For this packet itself:

1. markdown/file validation only

For interpretation discipline inside this packet:

- no sentence may treat runtime support as equivalent to candidate activation
- no sentence may treat the future candidate config file as already created
- no sentence may treat config activation as launch authorization
- no sentence may permit editing the existing baseline bridge file in place
- no sentence may reopen runner, paper, readiness, cutover, or promotion surfaces

### Stop Conditions

- any wording that treats the validated runtime carrier as implicit launch authority
- any wording that edits or redefines the current baseline bridge file rather than creating a future candidate artifact
- any wording that widens from one exact candidate config delta into generic threshold tuning
- any wording that assumes a backtest may now be run without a separate launch packet
- any need to modify files outside the two scoped docs files

### Output required

- reviewable bridge-activation pre-code packet
- exact future candidate config path
- exact intended config delta
- explicit launch-separation reminder

## Purpose

This packet defines the smallest honest next step after the bounded carrier implementation.

The problem it isolates is no longer whether a runtime carrier exists.
That question is now answered locally and positively.

The problem it isolates is now:

- what is the smallest separate repo-visible artifact that would make the new carrier expressible as a bounded baseline-vs-candidate backtest subject without widening launch authority?

Fail-closed interpretation:

> Preferred next step: if a bounded next slice is opened, it should first create one separate candidate bridge config artifact derived from the fixed bridge baseline and differing only by explicit activation of `multi_timeframe.research_defensive_transition_override`. If more than that is needed, the slice must stop and re-packet rather than broaden in place.

## Upstream governed basis

This packet is downstream of the following tracked documents and verified facts:

- `docs/governance/ri_router_replay_defensive_transition_backtest_precode_packet_2026-04-23.md`
- `docs/governance/ri_router_replay_defensive_transition_backtest_setup_only_packet_2026-04-23.md`
- `docs/governance/ri_router_replay_defensive_transition_candidate_gate_carrier_precode_packet_2026-04-23.md`
- `docs/governance/ri_router_replay_defensive_transition_candidate_gate_carrier_implementation_packet_2026-04-23.md`
- the implemented runtime/config-authority support in:
  - `src/core/strategy/decision_gates.py`
  - `src/core/config/schema.py`
  - `src/core/config/authority.py`
- the validated proof surfaces:
  - `tests/utils/test_decision_gates_contract.py`
  - `tests/utils/test_decision_scenario_behavior.py`
  - `tests/governance/test_config_schema_backcompat.py`
  - `tests/integration/test_golden_trace_runtime_semantics.py`

Carried-forward meaning from that chain:

1. the default path remains unchanged unless one new research leaf is explicitly enabled
2. absent leaf and explicit disabled leaf are canonically identical
3. untouched authority/default outputs do not materialize the new leaf
4. the fixed bridge baseline still does not include the new leaf, so no separate candidate artifact exists yet

## Exact baseline anchor to preserve

The baseline bridge artifact that must remain unchanged is:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

The candidate-activation slice defined by this packet must treat that file as preserved baseline input only.
It must not be edited in place.

## Exact future candidate artifact under consideration

If a later config-only slice is separately authorized, the preferred exact candidate artifact path is:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_defensive_transition_20260423.json`

This packet does **not** create that file.
It only defines the preferred future artifact boundary.

## Exact intended config delta

If the later config-only slice is opened, the candidate artifact should differ from the baseline bridge file only by adding:

- `cfg.multi_timeframe.research_defensive_transition_override.enabled = true`
- `cfg.multi_timeframe.research_defensive_transition_override.guard_bars = 3`
- `cfg.multi_timeframe.research_defensive_transition_override.max_probability_gap = 0.05`

No other field should change in that future slice unless a fresh packet explicitly reopens the boundary.

### Why these exact leaf values are the current preferred candidate

These values are the smallest currently grounded candidate because they align with the bounded enabled-path proof already validated in the in-scope test surfaces:

- `guard_bars = 3`
- `max_probability_gap = 0.05`

This packet does **not** claim these values are globally optimal.
It claims only that they are the current bounded, repo-visible candidate settings already exercised by the local proof surface.

## Why this is the next smallest admissible step

This packet intentionally does **not** jump directly to:

- launch authorization
- actual baseline execution
- actual candidate execution
- runner edits
- baseline bridge mutation
- generic threshold-family exploration

Those moves would either widen authority too early or collapse activation and launch into one step.

The smallest honest next step is instead:

- define one exact candidate config artifact
- keep baseline and candidate as separate files
- keep launch separately governed

## Required proof before any later config-only slice may proceed

No config-only activation slice may proceed from this packet unless that later slice proves all of the following:

1. the baseline bridge file remains byte-for-byte unchanged
2. the candidate file differs only by the explicit research leaf above
3. the candidate file validates cleanly through current config-authority/runtime parsing surfaces
4. the slice does not widen into runner, launch, result-path, or family-rule edits
5. launch remains blocked until a separate packet explicitly re-verifies the execution surface

## Non-goals

This packet does **not** define or authorize:

- code changes
- baseline bridge edits
- a launch packet
- a backtest execution
- candidate result claims
- optimizer-like widening
- runtime-default activation
- readiness, cutover, or promotion semantics

## Bottom line

The bounded carrier now exists, but it is not yet expressible as a separate backtest candidate artifact.

The next smallest admissible step is therefore not launch and not more runtime code.
It is one docs-defined future config-only bridge-activation slice that would create a separate candidate bridge file, keep the existing bridge untouched as baseline, and activate only the already-validated `research_defensive_transition_override` leaf.
