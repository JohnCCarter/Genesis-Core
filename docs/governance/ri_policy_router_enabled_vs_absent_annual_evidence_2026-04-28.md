# RI policy router enabled-vs-absent annual evidence

Date: 2026-04-28
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / read-only annual evidence / mixed verdict / no broader challenger advancement`

This slice extends the earlier bounded fail-B carrier proof into full-year annual evidence on the same fixed RI carrier.
It does not modify runtime/config/schema/authority surfaces and does not constitute promotion, readiness, or challenger-to-incumbent replacement evidence.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice runs deterministic full-year backtests on a high-sensitivity router carrier, but remains read-only and does not alter runtime or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the bounded fail-B contribution proof is already recorded, and the next honest question is whether that active router leaf remains net-useful on broader annual surfaces before any challenger advancement is considered.
- **Objective:** compare the same fixed RI carrier with `research_policy_router` enabled versus absent across `2024` and `2025` using canonical annual settings, and determine whether the active state-router leaf is strong enough to advance from local carrier evidence to broader annual challenger relevance.
- **Candidate:** `research_policy_router annual enabled-vs-absent evidence`
- **Base SHA:** `989308bf8a5ecabdfe684d2a16d92bfb0b77375a`

## Skill Usage

- **Applied repo-local spec:** `backtest_run`
  - reason: the slice must stay on canonical deterministic backtest settings with fixed env and traceable artifacts.
- **Applied repo-local spec:** `genesis_backtest_verify`
  - reason: the slice compares deterministic backtest outputs and must keep artifact generation reproducible.
- **Applied repo-local spec:** `decision_gate_debug`
  - reason: annual interpretation must remain tied to router behavior and action drift rather than top-line metrics alone.

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/governance/ri_policy_router_enabled_vs_absent_bounded_contribution_evidence_2026-04-28.md`
  - `docs/governance/ri_policy_router_reanchor_post_aged_weak_closeouts_2026-04-27.md`
  - `docs/analysis/tBTCUSD_3h_candidate_recommendation_2026-03-18.md`
- **Candidate / comparison surface:**
  - active router code in `src/core/strategy/ri_policy_router.py`
  - fixed carrier config `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
  - same carrier with `multi_timeframe.research_policy_router` absent
  - annual windows `2024` and `2025`
- **Vad ska förbättras:**
  - determine whether the active static state-router leaf helps the RI carrier beyond the exact fail-B carrier
  - determine whether annual evidence is strong enough to justify carrying the leaf forward as a broader RI subbaseline
- **Vad får inte brytas / drifta:**
  - no runtime edits
  - no fresh router tuning
  - no challenger-vs-incumbent promotion claim from mixed annual evidence alone
  - no reopening of the parked aged-weak or low-zone bars-8 runtime chains
- **Reproducerbar evidens som måste finnas:**
  - same fixed carrier config in both enabled and absent runs
  - canonical env with explicit seed and execution mode
  - annual artifacts for `2024` and `2025`
  - row-level action diff artifacts for both years

## Scope

### Scope IN

- one new annual read-only probe script under `tmp/policy_router_evidence/`
- one new annual governance evidence note
- annual JSON artifacts under `results/backtests/ri_policy_router_enabled_vs_absent_annual_20260428/`

### Scope OUT

- `src/**`
- `config/**`
- `tests/**`
- fresh runtime packets
- Optuna follow-up
- challenger-vs-incumbent promotion claim
- family/default/champion authority changes

## Canonical env for all runs

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_PRECOMPUTE_CACHE_WRITE=0`
- `GENESIS_MODE_EXPLICIT=1`
- `GENESIS_FAST_HASH=0`
- `GENESIS_SCORE_VERSION=v2`

## Fixed read-only evidence inputs

- `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- `tmp/policy_router_evidence/verify_router_enabled_vs_absent_annual_windows_20260428.py`

These inputs are fixed evidence carriers/scripts for this slice and are out of edit scope once recorded.

## Exact commands run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/policy_router_evidence/verify_router_enabled_vs_absent_annual_windows_20260428.py`

## Actual emitted artifacts

- `results/backtests/ri_policy_router_enabled_vs_absent_annual_20260428/enabled_vs_absent_annual_summary.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_annual_20260428/2024_enabled_vs_absent_action_diffs.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_annual_20260428/2025_enabled_vs_absent_action_diffs.json`

## Outcomes

### 2024 annual result

Enabled:

- total return: `4.7468%`
- profit factor: `2.1320`
- max drawdown: `2.2192%`
- trades: `109`
- position net PnL: `474.6816`

Absent:

- total return: `6.3425%`
- profit factor: `2.2528`
- max drawdown: `1.4280%`
- trades: `120`
- position net PnL: `634.2485`

2024 verdict:

- **enabled is worse than absent**

This fails a simple annual non-inferiority gate on:

- return
- profit factor
- drawdown
- net position PnL

### 2025 annual result

Enabled:

- total return: `2.9269%`
- profit factor: `2.1899`
- max drawdown: `2.6229%`
- trades: `100`
- position net PnL: `292.6866`

Absent:

- total return: `1.2314%`
- profit factor: `1.7242`
- max drawdown: `3.4890%`
- trades: `132`
- position net PnL: `123.1387`

2025 verdict:

- **enabled is better than absent**

This is a clean annual positive on:

- return
- profit factor
- drawdown
- net position PnL

## Row-level findings

### 1. The annual picture is genuinely mixed, not merely noisy

Action-diff counts remain large on both annual windows:

- `2024`: `753` action diffs, `2048` reason-only diffs
- `2025`: `740` action diffs, `2050` reason-only diffs

So the active state-router leaf is materially changing annual behavior on both years.
This is not a cosmetic tag-only effect.

### 2. 2024 deterioration is driven by repeated early router no-trade / defensive interventions

Representative `2024` action diffs show the enabled leaf repeatedly converting absent `LONG` entries into:

- `RESEARCH_POLICY_ROUTER_NO_TRADE`
- or reduced-size `RESEARCH_POLICY_ROUTER_DEFENSIVE`

Examples from `2024_enabled_vs_absent_action_diffs.json`:

- `2024-01-16T09:00:00+00:00`
  - enabled: `NONE / RESEARCH_POLICY_ROUTER_NO_TRADE`
  - absent: `LONG / ENTRY_LONG`
- `2024-01-17T06:00:00+00:00`
  - enabled: `LONG / RESEARCH_POLICY_ROUTER_DEFENSIVE / ENTRY_LONG`
  - absent: `NONE / COOLDOWN_ACTIVE`
- `2024-01-19T00:00:00+00:00`
  - enabled: `LONG / RESEARCH_POLICY_ROUTER_CONTINUATION / ENTRY_LONG`
  - absent: `NONE / COOLDOWN_ACTIVE`

This means the annual 2024 degradation is not a hidden artifact of the absent run.
It is the result of real router-driven state changes on the annual surface.

### 3. 2025 improvement is also real and not limited to the old fail-B carrier

Representative `2025` action diffs show the enabled leaf suppressing absent `LONG` entries via router no-trade state and also re-shaping later continuation behavior.

Examples from `2025_enabled_vs_absent_action_diffs.json`:

- `2025-01-16T09:00:00+00:00`
  - enabled: `NONE / RESEARCH_POLICY_ROUTER_NO_TRADE`
  - absent: `LONG / ENTRY_LONG`
- `2025-01-18T06:00:00+00:00`
  - enabled: `NONE / RESEARCH_POLICY_ROUTER_NO_TRADE`
  - absent: `LONG / ENTRY_LONG`
- `2025-01-20T03:00:00+00:00`
  - enabled: `LONG / RESEARCH_POLICY_ROUTER_CONTINUATION / ENTRY_LONG`
  - absent: `NONE / COOLDOWN_ACTIVE`

So the active leaf does carry beyond the exact December 2023 fail-B subject.
The problem is not absence of effect; the problem is lack of consistent annual benefit.

## Verdict

The annual enabled-vs-absent evidence is **mixed**:

- `2024`: negative
- `2025`: positive

Therefore the current annual evidence is **not strong enough** to advance the active router leaf from:

- bounded carrier contribution proof

To:

- broader annual RI subbaseline status
- or challenger-path advancement toward incumbent comparison

## Consequence

The correct current posture is:

- keep the earlier bounded fail-B contribution proof
- do **not** claim broader annual annualization success
- do **not** advance the active router leaf as a general RI annual subbaseline yet
- keep the broader RI-router runtime/tuning chain effectively **parked** for challenger advancement purposes

This is not because the leaf is inert.
It is because the annual evidence is materially inconsistent across the two full-year windows that are currently available on the canonical frozen surface.

## Next admissible move

If this line is reopened beyond the bounded carrier proof, the next admissible step should be one of these:

1. a **docs-only acceptance-rule packet** that explicitly defines what annual mixed evidence would need to look like to justify carrying the leaf forward despite a negative year, or
2. a **sharper read-only evidence slice** that isolates whether the `2024` regression is concentrated in one specific recurring state pocket rather than reflecting general annual harm.

What is **not** justified by this slice alone:

- new router tuning
- challenger-vs-incumbent promotion comparison using the enabled annual leaf as if it were already validated
- any claim that the static state-router leaf is broadly beneficial across the currently available annual windows
