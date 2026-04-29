## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `HIGH` — why: optimizer experiment scaffolding in a high-sensitivity decision domain; no runtime/default/champion behavior changes allowed
- **Required Path:** `Full`
- **Objective:** Create a seventh RI challenger-family Optuna slice for `tBTCUSD 3h` that preserves RI family identity, freezes a deterministic slice-6 anchor, and reopens only bounded gating-cadence levers to test whether cadence—not broader selectivity or exit breadth—is the next meaningful RI mechanism surface.
- **Run intent:** `research_slice` (explicit; required for `strategy_family=ri` admission in validator/preflight)
- **Candidate:** `ri challenger family slice7`
- **Base SHA:** `601efdd00552a4de9e5d6cce54a58c84725e593c`
- **Applied repo-local skill:** `optuna_run_guardrails`

### Scope

- **Scope IN:**
  - `config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice7_2026-03-24.md`
  - `docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice7_2026-03-24.md`
  - `docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice7_execution_2026-03-24.md`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/runtime.json`
  - `config/strategy/champions/**`
  - committed `results/**`
  - `tmp/**` smoke YAMLs / temp DBs / run-launch artifacts
  - blind-2025 execution
  - promotion/default/cutover semantics
  - legacy-authority reopening
  - clarity search reopening
  - renewed risk_state breadth
  - renewed exit/override cadence
  - renewed selectivity breadth
  - broad threshold-topology reopening
- **Expected changed files:** `4`
- **Max files touched:** `4`

### Baseline anchor

Slice-7 must freeze a single explicit slice-6 anchor:

- source run: `results/hparam_search/run_20260324_155438`
- source validation plateau: `0.23646934335498004`
- deterministic tie-break rule: among the tied validation winners, choose the member with highest train score; if train also ties, choose the lexicographically smallest trial id
- selected anchor: `trial_005`

The slice-7 YAML must freeze exactly these slice-6 anchor-derived values:

- `thresholds.entry_conf_overall = 0.28`
- `thresholds.regime_proba.balanced = 0.36`
- `thresholds.signal_adaptation.zones.low.entry_conf_overall = 0.14`
- `thresholds.signal_adaptation.zones.mid.entry_conf_overall = 0.42`
- `thresholds.signal_adaptation.zones.high.entry_conf_overall = 0.34`
- `thresholds.signal_adaptation.zones.low.regime_proba = 0.32`
- `thresholds.signal_adaptation.zones.mid.regime_proba = 0.52`
- `thresholds.signal_adaptation.zones.high.regime_proba = 0.58`
- plus the previously fixed RI identity, risk_state, exit/override cadence, HTF exit, and Fib anchor values carried unchanged from slice 6

### Hypothesis whitelist

Slice-7 may **only** open these tunables:

1. Gating cadence
   - `gates.hysteresis_steps`
   - `gates.cooldown_bars`

Exact allowed search ranges:

- `gates.hysteresis_steps = 2..4` with `step=1`
- `gates.cooldown_bars = 1..3` with `step=1`

Everything else stays fixed to the deterministic slice-6 anchor baseline.

### Gates required

- `pre-commit run --files docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice7_2026-03-24.md docs/audit/refactor/regime_intelligence/context_map_regime_intelligence_optuna_challenger_family_slice7_2026-03-24.md docs/audit/refactor/regime_intelligence/command_packet_regime_intelligence_optuna_challenger_family_slice7_execution_2026-03-24.md config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`
- `python scripts/validate/validate_optimizer_config.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`
- `python scripts/preflight/preflight_optuna_check.py config/optimizer/3h/ri_challenger_family_v1/tBTCUSD_3h_ri_challenger_family_slice7_2024_v1.yaml`

### Stop Conditions

- Stop if more than the four scoped files need to change.
- Stop if any `tmp/**`, committed `results/**`, DB, smoke artifact, or run launch becomes necessary before post-diff audit.
- Stop if any edit is needed under `src/**`, `tests/**`, `config/runtime.json`, or `config/strategy/champions/**`.
- Stop if the slice-6 anchor cannot be represented exactly in the YAML.
- Stop if the hypothesis requires reopening legacy authority, clarity, risk_state breadth, exit/override cadence, selectivity breadth, or broad threshold-topology search.
- Stop if validator or preflight indicates that the YAML semantics require code or test changes.

### Output required

- **Implementation Report**
- **PR evidence template**
- committed slice-7 YAML path
- committed command packet path
- committed context map path
- committed execution packet path

### Constraints

- **Default constraint:** `NO BEHAVIOR CHANGE`
- Slice-7 YAML must declare `meta.runs.run_intent: research_slice` explicitly; implicit defaulting is not allowed.
- Slice-7 is experiment scaffolding only; it must not alter runtime defaults, incumbent champion behavior, or production authority semantics.
- Preserve RI family identity: `authority_mode=regime_module`, RI `v2`, `clarity_score.enabled=false`, `risk_state.enabled=true`, `atr_period=14`.
- Preserve train `2023-12-21..2024-06-30` and validation `2024-07-01..2024-12-31`.
- Use fresh `study_name`, fresh `storage`, `resume=false`, `promotion.enabled=false`, and `n_jobs=1`.
- Launch is **not** approved by this packet alone; any execution remains gated by the separate execution packet, post-diff audit, and green validation/preflight evidence.
