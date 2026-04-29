# RI policy router enabled-vs-absent bounded contribution evidence

Date: 2026-04-28
Branch: `feature/ri-role-map-implementation-2026-03-24`
Mode: `RESEARCH`
Status: `completed / read-only carrier A-B evidence / bounded positive contribution`

This slice records a bounded read-only A/B probe on the exact December fail-B carrier used by the recent RI-policy-router work.
It does not modify runtime/config/schema/authority surfaces and does not constitute promotion, readiness, champion, or broad robustness evidence.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — why: this slice runs bounded deterministic read-only backtest/replay evidence on a high-sensitivity router carrier, but does not modify runtime or authority surfaces.
- **Required Path:** `Quick`
- **Lane:** `Research-evidence` — why this is the cheapest admissible lane now: the runtime chain is parked, the retained positive bars-7 helper is already implemented, and the next honest question is whether the active policy leaf contributes measurably on the exact carrier without reopening runtime tuning.
- **Objective:** verify whether the active `research_policy_router` leaf contributes measurably on the pinned fail-B carrier by comparing the same subject with the leaf enabled versus absent, while preserving the already-verified exact bars-7 helper-hit proof.
- **Candidate:** `research_policy_router enabled-vs-absent carrier A-B`
- **Base SHA:** `989308bf8a5ecabdfe684d2a16d92bfb0b77375a`

## Skill Usage

- **Applied repo-local spec:** `backtest_run`
  - reason: the slice must stay on canonical deterministic backtest settings and a fixed evidence carrier.
- **Applied repo-local spec:** `decision_gate_debug`
  - reason: the conclusion depends on row-level router interpretation, not top-line summary metrics alone.

### Research-evidence lane

- **Baseline / frozen references:**
  - `docs/decisions/ri_policy_router_bars7_continuation_persistence_runtime_closeout_2026-04-27.md`
  - `docs/decisions/ri_policy_router_reanchor_post_aged_weak_closeouts_2026-04-27.md`
  - `results/backtests/ri_policy_router_bars7_continuation_20260427/fail_b_helper_hit_timestamps.json`
- **Candidate / comparison surface:**
  - active router code in `src/core/strategy/ri_policy_router.py`
  - fixed carrier config `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
  - same carrier with `multi_timeframe.research_policy_router` absent for the A/B baseline
- **Vad ska förbättras:**
  - establish whether the current enabled policy leaf has measurable effect on the exact carrier
  - distinguish direct bars-7 row effects from later state/cooldown propagation
- **Vad får inte brytas / drifta:**
  - no runtime edits
  - no reopening of the parked aged-weak or low-zone bars-8 runtime chains
  - no promotion/default/champion/readiness claims from this slice alone
- **Reproducerbar evidens som måste finnas:**
  - exact helper-hit proof remains `{2023-12-20T03:00:00+00:00}`
  - one reproducible enabled-vs-absent A/B probe on the same subject
  - row-level diff artifact showing where the two runs diverge

## Scope

### Scope IN

- one new read-only probe script under `tmp/policy_router_evidence/`
- one new governance evidence note
- two emitted JSON artifacts under `results/backtests/ri_policy_router_enabled_vs_absent_20260428/`

### Scope OUT

- `src/**`
- `config/**`
- `tests/**`
- new runtime packets
- Optuna follow-up
- annual `2024` / `2025` challenger-vs-incumbent comparisons
- promotion/readiness/champion decisions

## Canonical env for all runs

- `GENESIS_RANDOM_SEED=42`
- `GENESIS_FAST_WINDOW=1`
- `GENESIS_PRECOMPUTE_FEATURES=1`
- `GENESIS_PRECOMPUTE_CACHE_WRITE=0`
- `GENESIS_MODE_EXPLICIT=1`

## Fixed read-only evidence inputs

- `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- `tmp/policy_router_evidence/verify_bars7_continuation_helper_hits_20260427.py`
- `tmp/policy_router_evidence/verify_router_enabled_vs_absent_carrier_20260428.py`

These inputs are fixed evidence carriers/scripts for this slice and are out of edit scope once recorded.

## Exact commands run

- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/policy_router_evidence/verify_bars7_continuation_helper_hits_20260427.py`
- `C:/Users/fa06662/Projects/Genesis-Core/.venv/Scripts/python.exe tmp/policy_router_evidence/verify_router_enabled_vs_absent_carrier_20260428.py`

## Actual emitted artifacts

- `results/backtests/ri_policy_router_bars7_continuation_20260427/fail_b_helper_hit_timestamps.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_20260428/enabled_vs_absent_summary.json`
- `results/backtests/ri_policy_router_enabled_vs_absent_20260428/enabled_vs_absent_row_diffs.json`

## Outcomes

### Exact helper-hit proof remains green

The retained bounded bars-7 helper-hit artifact still equals exactly:

- `2023-12-20T03:00:00+00:00`

So the previously retained positive slice remains intact on current branch.

### Enabled-vs-absent top-line A/B result on the exact fail-B carrier

Subject:

- `tBTCUSD`
- `3h`
- `2023-12-01 -> 2023-12-31`
- `warmup=120`
- `data_source_policy=curated_only`
- same fixed RI carrier config except the router leaf was removed in the absent run

Enabled (`research_policy_router` present):

- final capital: `9998.7501`
- total return: `-0.0125%`
- trades: `13`
- winning trades: `12`
- losing trades: `1`
- profit factor: `1.8926`
- position count: `6`
- net position PnL: `-1.2499`

Absent (`research_policy_router` removed):

- final capital: `9990.3194`
- total return: `-0.0968%`
- trades: `15`
- winning trades: `12`
- losing trades: `3`
- profit factor: `1.3776`
- position count: `8`
- net position PnL: `-9.6806`

Verdict on this bounded carrier:

- **enabled is materially better than absent**

This is sufficient to say the policy leaf contributes on the exact carrier, even though it is not broader promotion evidence.

## Row-level findings

### 1. The exact bars-7 row is a stateful contribution, not an immediate action flip

At the retained authoritative row `2023-12-20T03:00:00+00:00`:

Enabled:

- action: `LONG`
- reasons: `ZONE:low@0.160`, `RESEARCH_POLICY_ROUTER_CONTINUATION`, `ENTRY_LONG`
- router debug:
  - `raw_target_policy = RI_defensive_transition_policy`
  - `selected_policy = RI_continuation_policy`
  - `switch_reason = confidence_below_threshold`
  - `bars7_continuation_persistence_reconsideration_applied = true`

Absent:

- action: `LONG`
- reasons: `ZONE:low@0.160`, `ENTRY_LONG`
- no router state/debug materialized

So the retained bars-7 helper does **not** show up here as a direct `NONE -> LONG` action flip.
Instead it shows up as an enabled-path router-state intervention that preserves continuation semantics on the exact bounded row.

### 2. The enabled-path contribution propagates into later rows

The emitted A/B summary artifact reports:

- all row diffs: `121`
- action diffs: `34`
- reason-only diffs: `87`

Representative action-changing rows from `enabled_vs_absent_summary.json`:

- `2023-12-24T21:00:00+00:00`
  - enabled: `LONG / RESEARCH_POLICY_ROUTER_CONTINUATION / ENTRY_LONG`
  - absent: `NONE / COOLDOWN_ACTIVE`
- `2023-12-28T09:00:00+00:00`
  - enabled: `NONE / RESEARCH_POLICY_ROUTER_NO_TRADE`
  - absent: `LONG / ENTRY_LONG`
  - enabled router reason: `AGED_WEAK_CONTINUATION_GUARD`
- `2023-12-30T21:00:00+00:00`
  - enabled: `NONE / RESEARCH_POLICY_ROUTER_NO_TRADE`
  - absent: `LONG / ENTRY_LONG`
  - enabled router reason: `AGED_WEAK_CONTINUATION_GUARD`

So the contribution is not confined to a cosmetic tag on one row.
It propagates through later continuation / no-trade / cooldown behavior on the same subject.

### 3. The contribution is for the active policy leaf, not proof that every retained submechanism is independently sufficient

This slice compares the full active `research_policy_router` leaf against the same carrier with the leaf absent.
Therefore the positive A/B result proves:

- the active policy leaf contributes on the exact carrier

It does **not** prove by itself that:

- the retained bars-7 helper alone explains the full improvement, or
- the parked aged-weak runtime family is reopened or validated

## Interpretation

The current evidence now supports the following bounded statement:

- the active `research_policy_router` leaf is **functionally active** on the exact fail-B carrier,
- the retained bars-7 continuation-persistence helper still fires on its exact approved row,
- and the enabled leaf produces a measurably different and better bounded result than the absent leaf on that carrier.

That is enough to say:

- the policy **works** on the bounded carrier,
- and it **contributes** on the bounded carrier.

It is **not** enough to say:

- the router chain should be reopened for new runtime tuning,
- the policy is promotion-ready,
- or the policy is already proven robust across broader annual or challenger-governed comparisons.

## Consequence

This note upgrades the current proof posture from:

- `exact retained local helper proof only`

To:

- `exact retained local helper proof + bounded enabled-vs-absent carrier contribution proof`

The RI-router chain nevertheless remains parked outside this bounded evidence conclusion, exactly as recorded in:

- `docs/decisions/ri_policy_router_reanchor_post_aged_weak_closeouts_2026-04-27.md`
