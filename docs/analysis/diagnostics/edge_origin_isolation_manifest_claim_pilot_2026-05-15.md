# Edge-origin isolation manifest claim pilot

## Claim header

- **Date:** `2026-05-15`
- **Branch:** `feature/evidence-closeout-pilot`
- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/evidence-closeout-pilot`
- **Lane:** `Research-evidence` — why: this note cites one fresh deterministic edge-origin artifact root and records only bounded observational claims about that exact artifact set
- **Status:** `observational / evidence summary`
- **Authority level:** `bounded research-evidence`
- **Claim status:** `observed`
- **Objective:** pilot the claim-header discipline against a fresh manifest-backed `edge_origin_isolation` artifact root without overstating observational Phase 10 outputs as runtime or promotion authority
- **Baseline reference(s):** `docs/decisions/diagnostic_campaigns/edge_origin_isolation_manifest_pilot_run_packet_2026-05-15.md`, `results/research/fa_v2_adaptation_off/trace_baseline_current.json`, `results/research/fa_v2_adaptation_off/trace_adaptation_off.json`
- **Candidate / comparison surface:** `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/`
- **Runtime base SHA:** `4dc9fbba3fdcec63bd933c182a862438c9151fcd`
- **Evidence commit SHA:** `4dc9fbba3fdcec63bd933c182a862438c9151fcd`
- **Working-tree status:** `dirty` — the run packet and this note are untracked in this slice; the generated pilot output root is under ignored `results/research/**`
- **Config path:** `not applicable` — this slice used fixed trace artifacts and did not mutate runtime config
- **Config hash:** `not applicable`
- **Symbol / timeframe:** `not restated in the emitted Phase 10 artifacts; fixed by the cited trace subject`
- **Window:** `fixed historical Phase 10 trace window from the cited baseline_current and adaptation_off inputs`
- **Warmup:** `not restated in the emitted Phase 10 artifacts`
- **Data-source policy:** `fixed historical trace artifacts only`
- **Symbol mode:** `not restated in the emitted Phase 10 artifacts`
- **Env flags:** `no additional env flags were explicitly set in this slice`
- **Cache policy:** `bounded output write to the fixed pilot root only; no runtime cache or authority is claimed`
- **Artifact path(s):**
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/execution_attribution.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/execution_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/sizing_attribution.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/sizing_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/path_dependency.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/path_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/selection_attribution.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/selection_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/counterfactual_matrix.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/audit_phase10_determinism.json`
  - `results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515/manifest.json`
- **Artifact hash(es):**
  - `baseline_current_sha256 = 6481d6cd5ba988ff147ef3d9512d2b435e0b127e5f814cc04b8f0758526dafe8`
  - `adaptation_off_sha256 = 3a6d256b7e48d44d048b5a066d7914b21eff9903fe19520263d6bebbda2ecc16`
  - `execution_attribution.json = b89faea017c32bdf1d36b36f281d2f866f9a2309f2f64b355fd2055c87ffca1b`
  - `sizing_attribution.json = acb79fa2af1fad585516aa461e2039e40431449e03a342bf8156b52840416a87`
  - `path_dependency.json = f63545870c5fcd6dce9e9143001f354060f9f7737ebc11a94e999765b6b8d677`
  - `selection_attribution.json = 9e129d8e2f230104a3343d1b7b81c8a9356fa96d670d23424c9cd337e907e535`
  - `counterfactual_matrix.json = 9ca7bfecc4f0ac45cd209990036ded34ff8d144fb3044ade97300b89abd81c97`
  - `audit_phase10_determinism.json = cd70d54254e48b0c6db18b892821df5fbd927c6396ee20e271572e1076eb6a1c`
  - `output_manifest_hash = 2c6ff808c86273ecb5d390e79c8f690e645c8000ee6d73060b2219b5cbec9d30`
- **What changed:** `a fresh manifest-backed edge-origin artifact root was materialized and cited by one bounded pilot note`
- **What did not change:** `no runtime/config-authority/code surface changed; the historical phase10_edge_origin_isolation root remained untouched`
- **Does not authorize:** `runtime/default changes, promotion claims, or causal runtime conclusions`

## Observed

The bounded pilot run completed successfully against the fixed `baseline_current` and `adaptation_off` trace artifacts.

Observed closeout facts from `manifest.json` and `audit_phase10_determinism.json`:

- `determinism_match = true`
- `approved_output_files = [audit_phase10_determinism.json, counterfactual_matrix.json, execution_attribution.json, execution_summary.md, path_dependency.json, path_summary.md, selection_attribution.json, selection_summary.md, sizing_attribution.json, sizing_summary.md]`
- `manifest_file = manifest.json`
- `seed = 20260402`
- `shuffle_iterations = 5000`
- `output_manifest_hash = 2c6ff808c86273ecb5d390e79c8f690e645c8000ee6d73060b2219b5cbec9d30`
- `run1_hash = run2_hash = bba91f1cb2342bb4ffb7ad04eefa5b871113de8615a630d2e950fa46e34f43a7`

Observed Phase 10 surface facts from the emitted JSON artifacts:

- `execution_attribution.analysis_population.join_status = EXACT_ONE_MATCH_PER_TRADE`
- `execution_attribution.analysis_population.matched_trade_count = 82`
- `execution_attribution.baseline_metrics.expectancy = 7.078436519139`
- `execution_attribution.baseline_metrics.profit_factor = 2.3190143283018045`
- `execution_attribution.baseline_metrics.win_rate = 0.743902439024`
- `execution_attribution.baseline_metrics.holding_period_bars.mean = 38.329268292683`
- `selection_attribution.selection_surface_status = CONTRAST_AVAILABLE`
- `selection_attribution.selection_metrics.shared_opportunity_count = 1800`
- `selection_attribution.selection_metrics.baseline_only_opportunity_count = 279`
- `selection_attribution.selection_metrics.adaptation_off_only_opportunity_count = 345`
- `path_dependency.path_dependency_detected = NO`
- `path_dependency.shuffle_distribution_summary.max_drawdown_p_value = 0.727654469106`
- `sizing_attribution.deltas.expectancy_delta_actual_minus_unit = -3370.317690113048`
- `sizing_attribution.deltas.profit_factor_delta_actual_minus_unit = -4.130902213984`
- `counterfactual_matrix` emitted exactly two packet-authorized controls, both with `status = PASS`:
  - `unit_size_normalization`
  - `trade_order_shuffle`

Observed Git/reporting facts for this slice:

- `git status --short` reported the new run packet as untracked
- `git status --short --ignored results/research/fa_v2_adaptation_off/phase10_edge_origin_isolation_manifest_pilot_20260515` reported the new output root as ignored (`!!`)

## Inferred

- The new manifest output now provides a compact citation anchor for multi-output Phase 10 lanes: two fixed input hashes plus one stable non-self output inventory/hash set are enough to point back to the exact artifact root without reproducing each payload inline.
- This pilot shows the claim-header workflow still stays lightweight even when the evidence surface is broader than execution-proxy: the note can cite exact deterministic facts across execution, sizing, path, selection, and counterfactual outputs without pretending to be a packet or a runtime decision.
- The emitted artifact set remains observational only; the manifest improves provenance and closeout discipline, not authority.

## Unverified

- This pilot does **not** prove runtime causality, production readiness, promotion readiness, or champion suitability.
- This pilot does **not** prove that unit-size normalization or trade-order shuffling explain a deployable runtime edge; it records observational contrasts on the locked artifact surface only.
- This pilot does **not** prove that shared or differing opportunity counts between `baseline_current` and `adaptation_off` imply a stronger causal selection mechanism.
- This pilot does **not** establish a repo-wide manifest standard for all evidence scripts.

## Why this note matters

This note is intentionally small.
Its job is not to settle the full edge-origin question; its job is to prove that a claim-bearing note can now:

- cite a fresh deterministic manifest-backed artifact root
- separate `observed`, `inferred`, and `unverified`
- keep the non-authority boundary explicit
- remain reusable as evidence without pretending to be a packet or a runtime decision

## Bottom line

The manifest-backed edge-origin pilot succeeded.
It records one exact `edge_origin_isolation` artifact root with stable input hashes, stable output hashes, and an explicit observational boundary, while leaving runtime causality and promotion questions unresolved and out of scope.
