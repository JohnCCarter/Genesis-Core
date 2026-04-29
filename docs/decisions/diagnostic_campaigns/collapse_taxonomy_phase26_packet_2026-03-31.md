# COMMAND PACKET

- **Mode:** `STRICT` — source: explicit current user request for Phase 2.6 collapse taxonomy in STRICT mode
- **Risk:** `MED` — why: trace-only causal attribution over existing compensation artifacts; no runtime behavior changes allowed, but family assignment must be deterministic and fail-closed
- **Required Path:** `Full`
- **Objective:** Build a deterministic collapse taxonomy that explains which sizing sub-mechanisms neutralize divergent decision paths, and in what proportions, using existing artifacts only
- **Candidate:** `baseline_current` vs `adaptation_off` Phase 2.6 collapse taxonomy
- **Base SHA:** `68537da2`

### Scope

- **Scope IN:**
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_baseline_current.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\trace_adaptation_off.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\compensation_map.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\convergence_statistics.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\collapse_taxonomy.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\collapse_taxonomy_statistics.json`
  - `c:\Users\fa06662\Projects\Genesis-Core\results\research\fa_v2_adaptation_off\collapse_taxonomy_summary.md`
  - `c:\Users\fa06662\Projects\Genesis-Core\docs\governance\collapse_taxonomy_phase26_packet_2026-03-31.md`
- **Scope OUT:**
  - All files under `src/`
  - All files under `tests/`
  - Any runtime/config authority changes
  - Any backtest reruns
  - Any threshold/config/parameter changes
  - Any architecture changes
  - `config/strategy/champions/**`
  - Existing trace/compensation artifacts except read-only consumption
- **Expected changed files:**
  - `docs/decisions/diagnostic_campaigns/collapse_taxonomy_phase26_packet_2026-03-31.md`
  - `results/research/fa_v2_adaptation_off/collapse_taxonomy.json`
  - `results/research/fa_v2_adaptation_off/collapse_taxonomy_statistics.json`
  - `results/research/fa_v2_adaptation_off/collapse_taxonomy_summary.md`
- **Max files touched:** `4`

### Implementation surface

- Scope IN is limited to the four named read-only inputs, this packet, and the three named output artifacts.
- No repository code, tests, notebooks, configs, or additional committed helper files may be modified.
- If a committed helper file would be required, implementation must stop and the exact path must be added to Scope IN before continuing.

### Constraints

- Existing artifacts only; do not regenerate traces or rerun backtests
- No strategy logic changes
- No new parameters, thresholds, tuning, or redesign
- Deterministic ordering and stable JSON formatting required
- Final interpretation must explain collapse inside sizing only, not edge or performance

### Canonical analysis definitions

- **Bar alignment key:** canonical ascending `bar_index`; `timestamp` is a secondary consistency check only.
- **Canonical trade identity:** `entry_timestamp + exit_timestamp + side + size + pnl` as recorded in Phase 2 artifacts.
- **Divergent bar set:** bars from `compensation_map.json` whose Phase 2 bucket is not `FULL_MATCH`. Current expected count is `2893`, but implementation must verify from artifacts rather than assume blindly.
- **Coverage denominator:** exactly the `Divergent bar set` defined above, derived only from `compensation_map.json`; not all rows from any other artifact.
- **Family assignment rule:** exactly one collapse family per divergent bar. Zero or multiple matches is a hard failure.
- **Stable precedence:** `ZERO_SIZE > HTF_MULTIPLIER > REGIME_MULTIPLIER > VOLATILITY > MULTIPLIER_CHAIN > LATE_LEDGER > MIXED`
- **Dominant factor field:** the first satisfied family condition under the packet-defined precedence.
- **Observational-only rule:** Phase 2.6 family labels are observational classifications derived only from the four packet-locked Phase 2 artifacts. If those artifacts do not uniquely support one earlier family, the row must fail closed to `MIXED`; no causal reconstruction from code, config, or reruns is allowed.
- **No-overlap semantics:** `no overlap` applies to final assigned family labels after precedence resolution, not necessarily to raw predicate hits before precedence.

### Collapse family truth rules

- `ZERO_SIZE_SUPPRESSION`
  - final size is zero-equivalent in the collapse representation, or the compared sizing state collapses to zero before any execution delta
  - treated as an observed terminal outcome, not an inferred upstream primary cause
- `HTF_MULTIPLIER_SUPPRESSION`
  - not `ZERO_SIZE_SUPPRESSION`
  - HTF multiplier differs from neutral (`1.0`) and is the first matching suppressor under precedence
- `REGIME_MULTIPLIER_SUPPRESSION`
  - not any higher-precedence family
  - regime multiplier differs from neutral (`1.0`) and is the first matching suppressor under precedence
- `VOLATILITY_NEUTRALIZATION`
  - not any higher-precedence family
  - volatility adjustment differs from neutral (`1.0`) and is the first matching suppressor under precedence
- `MULTIPLIER_SUPPRESSION`
  - not any higher-precedence family
  - combined multiplier differs from neutral (`1.0`) or multiplier-chain collapse is present without a more specific dominant suppressor
  - requires a non-zero final size outcome together with multiplier-chain evidence from the packet-locked artifacts
  - if more than one multiplier family is implicated and no earlier family has unique ownership from packet-locked evidence, fail closed to `MIXED_SUPPRESSION`
- `LATE_LEDGER_RECONVERGENCE`
  - not any higher-precedence family
  - Phase 2 reconvergence layer is `trade_ledger`
  - assign only when late/post-candidate ledger-side suppression is explicitly observable in the packet-locked artifacts; otherwise do not infer late-ledger causality
- `MIXED_SUPPRESSION`
  - used when ambiguity remains after evaluating all higher-precedence rules, with explicit ambiguity reason recorded
  - mandatory fallback for underdetermined rows or rows lacking unique family ownership from packet-locked evidence

### Skill anchors

- Applicable repo-local skill anchors:
  - `.github/skills/feature_parity_check.json`
  - `.github/skills/ri_off_parity_artifact_check.json`
- These anchors support evidence discipline and artifact integrity only; they do not replace STRICT verification gates.

### Gates required

- Coverage assertions:
  - total classified bars == exact divergent-bar denominator derived from `compensation_map.json` (currently expected `2893`)
  - every divergent bar assigned exactly one family
  - no overlap in final assigned family labels after precedence resolution
  - no missing bars
- Artifact consistency:
  - collapse-family counts sum to classified divergent bars
  - dominant family matches statistics output
  - `LATE_LEDGER_RECONVERGENCE` count must include an explicit-evidence count in statistics output
- Double-run output determinism:
  - regenerate the three outputs twice from the same inputs and verify identical content hashes
- Artifact validation:
  - JSON parse / file diagnostics clean for new outputs
- Determinism source constraint:
  - analysis reads only the four named input artifacts
- Fail-closed validation:
  - rows without unique packet-locked family ownership must resolve to `MIXED_SUPPRESSION`

### Stop Conditions

- Scope drift beyond trace/compensation artifacts
- Need to rerun backtests or modify runtime code to answer the question
- Ambiguity that cannot be resolved by packet-defined precedence
- Missing or inconsistent artifact counts
- Any result phrased as edge, alpha, or optimization claim

### Output required

- `collapse_taxonomy.json`
- `collapse_taxonomy_statistics.json`
- `collapse_taxonomy_summary.md`
- Final completion summary including:
  - coverage
  - families identified
  - dominant collapse family
  - secondary mechanisms
  - late reconvergence explained
