# RI policy router continuation tuning candidate packet

Date: 2026-04-24
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `pre-code reviewed / APPROVED_WITH_NOTES / docs-only candidate preservation`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice preserves the first bounded continuation-tuning candidate and its accept/veto rules, but does not yet modify runtime code, config authority, or candidate artifacts.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the late-December failure mode is now localized to continuation-entry substitution/timing drift, and the next honest step is to freeze one narrow candidate hypothesis plus guardrails before any high-sensitivity runtime edit is attempted.
- **Objective:** preserve the first narrow continuation-tuning candidate in repo-visible form so that future runtime work can target the verified late-December substitution seam without drifting into broad global tuning.
- **Candidate:** `aged weak continuation guard`
- **Base SHA:** `HEAD`

## Review status

- `Opus 4.6 Governance Reviewer`: `APPROVED_WITH_NOTES`
- review scope: pre-code governance review for a future high-sensitivity runtime slice
- review lock: next runtime slice is admissible only if it remains one bounded weak-continuation admission guard in `src/core/strategy/ri_policy_router.py` with no new authority surface

## Skill Usage

- **Applied repo-local spec:** `python_engineering`
  - reason: any follow-up runtime slice must stay typed, small, test-backed, and gate-complete
- **Applied repo-local spec:** `decision_gate_debug`
  - reason: the failure mode is a decision-path substitution/timing problem and must be diagnosed through explicit gate/state reasoning rather than blind parameter tweaks
- **Conditional repo-local spec:** `feature_parity_check`
  - reason: use only if a later runtime slice relies on parity/replay selectors that touch feature-computation comparability; not required for this docs-only packet by itself

### Research-evidence lane

- **Baseline / frozen references:**
  - `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
  - `results/backtests/policy_router_split_20260424/2023_Dec_H2/baseline_decision_rows.ndjson`
  - `results/backtests/policy_router_split_20260424/2023_Dec_H2/router_enabled_decision_rows.ndjson`
  - late-December trade attribution on the already generated Dec H2 artifacts (`2023-12-16 -> 2023-12-31`)
- **Candidate / comparison surface:**
  - a future runtime slice may tune only the continuation-admission seam in `src/core/strategy/ri_policy_router.py`
  - the initial candidate must remain below default/champion/family authority and must not widen into `decision_gates.py`, `decision_sizing.py`, or family-rule surfaces
- **Vad ska förbättras:**
  - reduce late-December continuation-entry substitution / timing drift
  - specifically reduce cases where router no-trade suppression is followed by weaker later continuation entries that replace earlier baseline entries
- **Vad får inte brytas / drifta:**
  - no default-path change
  - no widening into `DEFENSIVE`, sizing, exits, or unrelated router thresholds as the first tuning step
  - no degradation on the protected keep-set (`2024`, `2025`)
  - no new tail-risk on the stress-set (`2018`, `2020 H1`)
- **Reproducerbar evidens som måste finnas:**
  - paired canonical runs on the fail-set (`2023-12-20 -> 2023-12-24`, `2023-12-16 -> 2023-12-31`, `2023 Q4`)
  - paired canonical runs on the keep-set (`2024`, `2025`)
  - paired canonical runs on the stress-set (`2018`, `2020 H1`)
  - trade-attribution and decision-row comparison proving whether candidate improvement comes from reduced late continuation substitution rather than broad trade-set churn

## Localized evidence that motivates this candidate

### Observed late-December mechanism

From the existing Dec H2 decision-row artifacts:

- baseline takes `ENTRY_LONG` at `2023-12-20T03:00:00+00:00` (`ZONE:low@0.160`)
- router path instead emits `RESEARCH_POLICY_ROUTER_NO_TRADE` at the same timestamp and remains in router-driven no-trade through several subsequent low-zone bars
- later, router path admits continuation entries at:
  - `2023-12-22T15:00:00+00:00` (`ZONE:low@0.160`, `RESEARCH_POLICY_ROUTER_CONTINUATION`, later observed as a large loser)
  - `2023-12-24T21:00:00+00:00` (`ZONE:mid@0.400`, `RESEARCH_POLICY_ROUTER_CONTINUATION`, later observed as a larger loser)
- baseline path is on cooldown at those two timestamps, which means the router is not merely degrading the same entries; it is selecting a different late continuation sequence

### Interpretation lock

The first tuning candidate must therefore target **weak, aged continuation admission** rather than:

- `DEFENSIVE`
- sizing
- exits
- global threshold retuning
- broad router switch controls (`switch_threshold`, `hysteresis`, `min_dwell`)

## First candidate hypothesis

### Candidate name

`aged weak continuation guard`

### Candidate intent

When the router is in an aged, stable regime context, **weak continuation** should not be admitted as easily as strong continuation.
The candidate is intentionally narrow:

- affect only continuation selection
- affect only the weaker continuation path (`continuation_state_supported` / mandate-level-2 class)
- preserve strong continuation (`stable_continuation_state` / mandate-level-3 class)
- leave `DEFENSIVE` and `NO_TRADE` semantics otherwise unchanged

### Behavior-change contract for any follow-up runtime slice

This is a **Behavior change candidate** limited to weak continuation admission in
`src/core/strategy/ri_policy_router.py::_raw_router_decision(...)`.

Any follow-up runtime implementation may only:

- suppress already-classified weak continuation entries
- use an existing age-related signal already present in the router seam

Any follow-up runtime implementation must not:

- alter strong continuation
- alter defensive routing
- alter exits
- alter sizing
- alter cooldown semantics
- alter switch controls
- alter route ordering
- alter config/env interpretation
- introduce a new authority surface

### Candidate seam

The smallest plausible seam is inside `src/core/strategy/ri_policy_router.py::_raw_router_decision(...)`.

The future runtime slice should test whether a bounded guard on **aged weak continuation admission** reduces the late-December substitution pattern without disturbing already good years.

The guard is only admissible if the runtime slice can pin:

- the exact existing age signal it uses: `bars_since_regime_change`
- the exact weak-continuation selector it suppresses: the raw continuation branch with `raw_switch_reason = "continuation_state_supported"` and `mandate_level = 2`
- one bounded proof that direct decision-row deltas remain confined to weak-continuation admission behavior

### Intended falsifier

This candidate should be rejected if any of the following occurs:

- it only improves Dec H2 by broadening trade-set churn elsewhere
- it requires changes outside continuation admission as its primary mechanism
- it degrades `2024` or `2025`
- it improves fail-set metrics only by collapsing back to generic no-trade behavior without improving the specific substitution pattern

## Accept / veto protocol for any future runtime implementation

### Protected keep-set

- `2024-01-01 -> 2024-12-31`
- `2025-01-01 -> 2025-12-31`

Veto if either year shows:

- lower net PnL
- materially higher drawdown
- materially broader trade-set churn without a clearly bounded explanation

### Required fail-set improvement

- micro-window anchor: `2023-12-20 -> 2023-12-24`
- local failure window: `2023-12-16 -> 2023-12-31`
- stability check: `2023 Q4`

Any runtime implementation must show that the late continuation substitution pattern weakens on these windows.
Examples of acceptable evidence:

- at least one of the known late continuation losers disappears
- or the corresponding late continuation entries shift earlier into materially better timing
- or an earlier baseline-like entry is recovered without replacing it with another comparably poor late continuation entry

### Stress-set veto

- `2018`
- `2020 H1`

Reject the candidate if it introduces clear new tail-risk in these windows.

## Scope

- **Scope IN:**
  - `docs/governance/ri_policy_router_continuation_tuning_candidate_packet_2026-04-24.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `results/**`
  - `registry/**`
  - any runtime/default/champion/promotion/family-rule surface
- **Expected changed files:**
  - `docs/governance/ri_policy_router_continuation_tuning_candidate_packet_2026-04-24.md`
  - `GENESIS_WORKING_CONTRACT.md`
- **Max files touched:** `2`

## Gates required

- minimal docs validation on the changed files

## Stop Conditions

- the candidate cannot be stated without widening beyond continuation admission
- the next step requires touching strict-only surfaces or default/champion authority
- the next step requires simultaneous tuning of `DEFENSIVE`, sizing, or exits
- late-December evidence turns out to be primarily same-trade degradation rather than trade substitution

## Output required

- one preserved first-candidate hypothesis
- one explicit accept/veto frame for future runtime work
- one updated working anchor pointing to this packet as the next admissible step before high-sensitivity edits
