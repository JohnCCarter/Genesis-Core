# COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Risk:** `MED` — read-only research slice using runtime hooks and curated backtest replay, but intended to avoid any runtime/default/config mutation
- **Required Path:** `Full`
- **Objective:** Build the smallest research-only ex-ante continuation proxy lane that tests whether entry-available fields can separate the already-validated `vol_mult_090 -> vol_mult_100` uplift into favorable vs harmful sizing contexts before entry.
- **Candidate:** `continuation ex-ante proxy / selective sizing discovery`
- **Base SHA:** `feature/ri-role-map-implementation-2026-03-24 (working tree)`

### Scope

- **Scope IN:**
  - `docs/decisions/continuation_ex_ante_proxy_packet_2026-04-15.md`
  - one new research-only script under `tmp/`
  - new research artifacts under `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/`
  - optional use of existing backtest evaluation hooks / trace-like capture inside the new script only
- **Scope OUT:**
  - all files under `src/`
  - all files under `tests/`
  - all files under `config/`
  - champion configs / runtime defaults
  - optimizer / paper/live execution logic
  - modifications to existing locked research conclusions except additive cross-links if strictly needed
- **Expected changed files:**
  - `docs/decisions/continuation_ex_ante_proxy_packet_2026-04-15.md`
  - `tmp/<new ex-ante analysis script>.py`
  - `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/<new analysis outputs>`
- **Max files touched:** `5`

### Pinned selectors

- **Dataset:** `data/curated/v1/candles/tBTCUSD_3h.parquet` + `data/curated/v1/candles/tBTCUSD_1D.parquet`
- **Symbol:** `tBTCUSD`
- **Timeframe:** `3h`
- **Baseline seam:** `min_size_base=0.001`, `high_vol_threshold=75`, `high_vol_multiplier=0.90`
- **Candidate seam:** `min_size_base=0.001`, `high_vol_threshold=75`, `high_vol_multiplier=1.00`
- **Year window:** `2017-01-01 .. 2025-12-31`
- **Output root:** `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/`

### Skill usage

- **Required skill coverage:** `python_engineering` discipline for the new research script.
- If the tmp script launches existing evaluation/backtest hooks rather than only reading produced artifacts, apply `genesis_backtest_verify` discipline as a verification reference.

### Planned behavior

- Re-run the locked `vol_mult_090` and `vol_mult_100` seam on curated `tBTCUSD 3h` data using research-only script orchestration.
- Capture entry-available fields only, using the same bar-time decision surface available before order entry.
- Match positions by deterministic entry identity / `position_id` parity and keep the analysis observational only.
- Build an ex-ante feature table for the active treatment subset where `vol_mult_100` increases size versus `vol_mult_090`.
- Quantify how well simple entry-time features (such as probabilities, edge, zone, ATR context, regime, sizing multipliers, and override metadata) separate favorable vs harmful uplift.
- Produce a first research recommendation for a selective `0.90/1.00` sizing rule candidate.
- Allowed hook usage is read-only import/call from the new tmp script only; no edits under `src/`, no monkeypatching, and no behavioral changes to existing evaluation hooks are allowed.

### Gates required

- `python <new tmp script>.py ...` smoke run must complete successfully
- all newly created research artifacts, excluding the authorized packet file under `docs/governance/` and the authorized tmp script under `tmp/`, must be confined to `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/`
- no edits outside packet scope
- observational wording discipline in new markdown outputs
- if any code outside `tmp/` / `docs/governance/` / `results/research/` becomes necessary, stop and escalate before implementing

### Stop Conditions

- Scope drift outside listed paths
- Need for runtime/default/config mutation to obtain entry features
- Evidence that entry-time fields are insufficient to propose even a provisional selective rule
- Any wording that upgrades observational separation into causal or deployment-ready proof
- Any write outside `results/research/fa_v2_adaptation_off/phase15_bull_high_persistence_override/`

### Output required

- **Implementation Report**
- **Research closeout note for the ex-ante proxy phase**

### Evidence wording discipline

- This slice is observational and research-only.
- Any separation found in entry-time features is evidence of association, not causal proof.
- Any candidate selective sizing rule remains a research recommendation until validated in separate replay comparisons.
