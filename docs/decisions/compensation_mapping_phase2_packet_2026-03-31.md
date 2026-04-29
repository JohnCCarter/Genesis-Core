# COMMAND PACKET

- **Mode:** `STRICT` — source: explicit current user request for Phase 2 compensation mapping in STRICT mode
- **Risk:** `MED` — why: trace-only causal attribution over existing governed artifacts; no runtime logic changes allowed, but conclusions must be deterministic and reproducible
- **Required Path:** `Full`
- **Objective:** Build a deterministic compensation map that explains how different internal decision paths between `baseline_current` and `adaptation_off` collapse into the same trade ledger, using existing traces only
- **Candidate:** `baseline_current` vs `adaptation_off`
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_baseline_current.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_adaptation_off.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\compensation_map.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\compensation_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\convergence_statistics.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\compensation_mapping_phase2_packet_2026-03-31.md`
- **Scope OUT:**
  - All files under `src/`
  - All files under `tests/`
  - Any runtime/config authority changes
  - Any new backtest runs or parameter changes
  - `config/strategy/champions/**`
  - Existing trace files and prior FA v2 result files except read-only consumption
- **Expected changed files:**
  - `docs/decisions/compensation_mapping_phase2_packet_2026-03-31.md`
  - `results/research/fa_v2_adaptation_off/compensation_map.json`
  - `results/research/fa_v2_adaptation_off/compensation_summary.md`
  - `results/research/fa_v2_adaptation_off/convergence_statistics.json`
- **Max files touched:** `4`

### Implementation surface

- Scope IN is limited to the two named input traces, this packet, and the three named output artifacts.
- No repository code, tests, configs, notebooks, or additional committed helper files may be modified.
- If a committed helper file would be required, implementation must stop and the exact repository path must be added to Scope IN before continuing.

### Constraints

- Existing traces only; do not regenerate traces
- No strategy logic changes
- No new parameters, thresholds, or tuning
- Deterministic ordering and stable JSON formatting required
- Final interpretation must explain convergence behavior only, not edge

### Canonical analysis definitions

- **Bar alignment key:** compare rows in canonical ascending `bar_index` order; `timestamp` is used as a secondary consistency check, not as the primary join key.
- **Canonical trade identity:** `entry_timestamp + exit_timestamp + side + size + pnl` from the existing `trade_signatures` arrays.
- **Preserved trade:** a trade is preserved only when the canonical trade identity matches exactly across both traces.
- **Bucket assignment rule:** bucket assignment is mutually exclusive and exhaustive over exactly `2893` aligned bars. Any bar that matches zero or multiple buckets is a hard failure.
- **Decision tuple:** `decision_phase`
- **Action tuple:** `final.action`
- **Size tuple:** `final.size` plus `sizing_phase`
- **Gate tuple:** `fib_phase + post_fib_phase`

### Bucket truth table

- `FULL_MATCH`
  - decision tuple equal
  - action tuple equal
  - size tuple equal
  - gate tuple equal
- `DECISION_DIFF_ONLY`
  - decision tuple differs
  - action tuple equal
  - size tuple equal
  - gate tuple equal or differs only in metadata that does not change action/size
- `ACTION_DIFF_NO_TRADE`
  - action tuple differs
  - canonical trade ledger remains exactly preserved
  - no position/trade delta appears in canonical trade identity
- `SIZE_DIFF_NO_POSITION_CHANGE`
  - size tuple differs
  - canonical trade ledger remains exactly preserved
  - no trade identity delta appears
- `FULL_DIVERGENCE_WITHOUT_EFFECT`
  - decision tuple differs
  - action tuple differs
  - size tuple differs
  - canonical trade ledger remains exactly preserved

### Reconvergence ladder

- `first_reconvergence_layer` uses this fixed downstream order:
  1. `decision`
  2. `gate`
  3. `sizing`
  4. `execution`
  5. `trade_ledger`
- For divergent bars, record the earliest layer at which equality is re-established under the packet-defined tuples.
- If no reconvergence occurs before the preserved trade ledger boundary, record `NONE`.
- For `FULL_MATCH` bars, record `NOT_APPLICABLE`.
- `execution` in this slice is represented by equality in `final.action` and `final.size` because no lower-level execution event trace is available in-scope.

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- These anchors support evidence discipline and artifact integrity review only; they do not replace STRICT verification gates.

### Gates required

- Trace coverage assertions:
  - total bars processed == `2893`
  - sum of classification buckets == total bars
  - no missing bars
  - all divergences accounted for
- Bucket proof:
  - exactly one bucket per aligned bar
  - zero unclassified bars
  - zero multi-match bars
- Reconvergence proof:
  - every divergent bar has exactly one allowed reconvergence value or `NONE`
- Double-run output determinism:
  - regenerate the three outputs twice from the same two traces and verify identical content hashes
- Artifact validation:
  - JSON parse / file diagnostics clean for new outputs
- Determinism source constraint:
  - analysis reads only the two existing trace JSON files

### Stop Conditions

- Scope drift beyond trace-only artifacts
- Need to rerun backtests or modify runtime code to answer the question
- Missing bars or inconsistent trace lengths
- Any ambiguity that would require inferred/non-deterministic reconstruction beyond recorded trace content

### Output required

- `compensation_map.json`
- `compensation_summary.md`
- `convergence_statistics.json`
- Final completion summary including:
  - divergence coverage
  - convergence points identified
  - dominant compensation layer
  - trade preservation mechanism
