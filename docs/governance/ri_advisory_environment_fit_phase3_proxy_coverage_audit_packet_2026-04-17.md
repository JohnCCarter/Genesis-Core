# RI advisory environment-fit Phase 3 proxy-coverage audit packet

Date: 2026-04-17
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `proposed / bounded observational proxy audit / results-only / default unchanged`

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `branch:feature/ri-role-map-implementation-2026-03-24`
- **Category:** `obs`
- **Risk:** `MED` — bounded research-only audit of realized-path proxy coverage and normalization-anchor compatibility on already tracked RI evidence; outputs confined to `tmp/`, `results/`, and one memo; no runtime/default/authority changes.
- **Required Path:** `Full`
- **Constraints:** `NO BEHAVIOR CHANGE`
- **Objective:** determine whether the provisional realized-path proxy family (`mfe_16_atr`, `fwd_16_atr`, `continuation_score`) can be materialized on the Phase C capture-v2 surface using an already captured observational ATR anchor, without reopening score logic or rewriting the Phase 2 label contract.
- **Candidate:** `RI advisory environment-fit Phase 3 proxy coverage audit`
- **Base SHA:** `e16e3f9fd68500dc741f8edd9757c709e22bf595`
- **Skill Usage:** `python_engineering`, `genesis_backtest_verify`
- **Opus pre-code verdict:** `APPROVED_WITH_NOTES`

### Scope

- **Scope IN:**
  - `docs/governance/ri_advisory_environment_fit_phase3_proxy_coverage_audit_packet_2026-04-17.md`
  - one bounded research script under `tmp/`
  - one results directory under `results/research/ri_advisory_environment_fit/`
  - one deterministic audit memo under `docs/analysis/`
- **Scope OUT:**
  - `src/**`
  - `tests/**`
  - `config/**`
  - `artifacts/**`
  - runtime authority changes
  - default behavior changes
  - any renewed score computation or bucket ranking
  - any exact supportive/hostile label claim
  - any `pnl_delta` reconstruction
  - any synthetic `active_uplift_cohort_membership`
  - any contradiction-year evaluation claim
  - any capture-v2 artifact mutation in place
  - ML/model work
- **Expected changed files:**
  - this packet
  - one `tmp/` script
  - one `docs/analysis/` memo
  - results artifacts confined to one new result subdirectory
- **Max files touched:** `8`

### Fixed evidence source

- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_2026-04-17/proxy_surface.json`
- `results/research/ri_advisory_environment_fit/phase3_provisional_evaluation_2026-04-17/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/entry_rows.ndjson`
- boundary SSOT:
  - `docs/analysis/ri_advisory_environment_fit_phase3_proxy_coverage_admissibility_2026-04-17.md`
  - `docs/analysis/ri_advisory_environment_fit_phase3_partial_baseline_label_gap_2026-04-17.md`

The label-gap memo is a governance boundary source only.
It is not an execution dependency, replacement label-surface artifact, or support for exact label authority in this slice.

### Allowed audit operations

This slice may only:

- compare `entry_atr` and `current_atr_used` on exactly matched historical rows from already tracked surfaces where both exist
- measure whether the old capture shows audited observational compatibility or bounded drift between those anchors on that overlap surface
- if the anchor audit passes, recompute only the provisional realized-path proxy family for the v2 rows into a separate results artifact set
- report coverage, equivalence, and materialization counts only

### Explicitly forbidden operations

- any score/rank/bucket output beyond proxy coverage and anchor-audit summaries
- any supportive/hostile label output
- any use of raw `total_pnl` sign as an evaluation shortcut
- any modification of tracked capture-v2 artifacts in place
- any claim that `current_atr_used` is semantically identical to `entry_atr` unless the audit evidence supports that statement directly

### Required outputs

- one normalization-audit artifact comparing `entry_atr` vs `current_atr_used` on the older capture surface
- one v2 proxy-coverage artifact showing whether provisional proxy fields can be materialized under the audited anchor rule
- one allowlist/assumption manifest that states the fallback rule explicitly
- one memo stating whether the audit cleared the proxy-coverage blocker or instead stopped on an anchor-authority gap
- one explicit statement that the separate Phase 2 `BLOCKED_LABEL_GAP` remains unresolved regardless of audit outcome

### Required audit acceptance rule

Before any v2 proxy materialization is allowed, the slice must define and enforce a deterministic overlap-surface acceptance rule that includes at minimum:

- exact row-matching keys for the anchor comparison surface
- minimum overlap coverage required for the audit to count as admissible
- bounded drift thresholds recorded in the output manifest
- fail-closed behavior if the overlap audit does not satisfy the declared thresholds

### Gates required

- `pre-commit run --files <packet> <tmp script> <analysis memo>`
- bounded execution of the proxy-coverage audit script itself
- bounded execution replay of the same audit script on identical inputs with identical summary/hash output
- explicit assertion that the script writes only to its approved result directory and memo targets

### Stop Conditions

- the old capture does not provide a clean enough observational relationship between `entry_atr` and `current_atr_used`
- the exact matched-row overlap surface does not satisfy the declared coverage/drift acceptance rule
- the v2 fallback would require rewriting the meaning of the provisional proxy family rather than reusing the same formulas with an audited anchor
- any attempt to turn restored proxy coverage into score output, label output, contradiction-year proof, or runtime recommendation
- any output write outside approved `tmp/`, `results/`, or docs surfaces
- any need to touch `src/**`, `tests/**`, `config/**`, or shared production-near helpers

## Bottom line

This packet proposes one narrow next step only:

- audit whether the proxy-coverage blocker is solvable as a read-only normalization-surface issue

It does not authorize renewed scoring, Phase 2 label substitution, contradiction-year claims, or runtime integration.
