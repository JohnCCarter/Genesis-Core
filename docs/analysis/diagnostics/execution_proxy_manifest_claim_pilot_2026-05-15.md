# Execution proxy manifest claim pilot

> Current status note:
>
> - This note records the first manifest-backed claim-bearing pilot observed on `feature/editor-worker-orchestrator` at `ba6955a2` before the later branch split.
> - It is now carried on `feature/evidence-closeout-pilot` as one historical manifest-backed pilot in the evidence-closeout chain, not as a branch-current selector, runtime authority, or promotion authority.

## Claim header

- **Date:** `2026-05-15`
- **Branch:** `feature/editor-worker-orchestrator`
- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/editor-worker-orchestrator`
- **Lane:** `Research-evidence` — why: this note cites one fresh deterministic evidence root and records only bounded observational claims about that exact artifact set
- **Status:** `observational / evidence summary`
- **Authority level:** `bounded research-evidence`
- **Claim status:** `observed`
- **Objective:** pilot the new claim-header discipline against a fresh manifest-backed `execution_proxy_evidence` artifact root without overstating proxy evidence as realized execution authority
- **Baseline reference(s):** `docs/decisions/diagnostic_campaigns/execution_proxy_manifest_pilot_run_packet_2026-05-15.md`, `results/research/fa_v2_adaptation_off/trace_baseline_current.json`
- **Candidate / comparison surface:** `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/`
- **Runtime base SHA:** `ba6955a2`
- **Evidence commit SHA:** `ba6955a2`
- **Working-tree status:** `dirty` — new packet and this note are untracked in this slice; the generated pilot output root is under ignored `results/research/**`
- **Config path:** `not applicable` — this slice used a fixed trace artifact and did not mutate runtime config
- **Config hash:** `not applicable`
- **Symbol / timeframe:** `not restated in the emitted proxy artifacts; fixed by the cited baseline trace subject`
- **Window:** `baseline_current trace-defined window from the cited input artifact`
- **Warmup:** `not restated in the emitted proxy artifacts`
- **Data-source policy:** `fixed historical trace artifact only`
- **Symbol mode:** `not restated in the emitted proxy artifacts`
- **Env flags:** `no additional env flags were explicitly set in this slice`
- **Cache policy:** `bounded output write to the fixed pilot root only; no runtime cache authority is claimed`
- **Artifact path(s):**
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/execution_proxy_evidence.json`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/execution_proxy_summary.md`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/audit_execution_proxy_determinism.json`
  - `results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515/manifest.json`
- **Artifact hash(es):**
  - `input_payload_sha256 = 6481d6cd5ba988ff147ef3d9512d2b435e0b127e5f814cc04b8f0758526dafe8`
  - `execution_proxy_evidence.json = e30785d4f8d24d3d18f8e512e0e268a777798e3f82f75bedf1cdc1dcd80763cc`
  - `execution_proxy_summary.md = 9e4d77b3a6df89f442d46d9c43e6ec0f758576220e5923ae5e782babf04501e7`
  - `audit_execution_proxy_determinism.json = 2803fdd4b85bc10efff9b35f77454726c276260513cd4d9af46fec208766ef04`
  - `output_manifest_hash = 05175c1bb1cf03222eaa7bdaf2770a76918ecd787d28a6bfc7baadee11b790ba`
- **What changed:** `a fresh manifest-backed proxy evidence root was materialized and cited by one bounded pilot note`
- **What did not change:** `no runtime/config-authority/code surface changed; the historical phase10_execution_proxy_evidence root remained untouched`
- **Does not authorize:** `runtime/default changes, promotion claims, or realized execution conclusions`

## Observed

The bounded pilot run completed successfully against the fixed `baseline_current` trace.

Observed closeout facts from `manifest.json` and `audit_execution_proxy_determinism.json`:

- `determinism_match = true`
- `approved_output_files = [audit_execution_proxy_determinism.json, execution_proxy_evidence.json, execution_proxy_summary.md]`
- `manifest_file = manifest.json`
- `output_manifest_hash = 05175c1bb1cf03222eaa7bdaf2770a76918ecd787d28a6bfc7baadee11b790ba`
- `run1_hash = run2_hash = 1f44423e3cd17c701bf48738c7b7ddbef1f975c0cec8bc4c110e042ccc95c85c`

Observed proxy-surface facts from `execution_proxy_evidence.json` and `execution_proxy_summary.md`:

- `analysis_population.join_status = EXACT_ONE_MATCH_PER_TRADE`
- `analysis_population.matched_trade_count = 82`
- `analysis_population.exit_row_resolution_status = EXACT_ONE_EXIT_ROW_PER_TRADE`
- `proxy_surface.price_source = trace_rows.fib_phase.ltf_debug.price`
- `proxy_surface.window_semantics = inclusive_entry_exit_bar_index_window`
- `full_window_attested_trade_count = 42`
- `sparse_window_trade_count = 40`
- `exact_exit_proxy_price_count = 68`
- `omitted_exit_proxy_price_count = 14`
- fixed-horizon summaries remained populated and deterministic:
  - `1 bar: resolved_trade_count = 79, mean_proxy_price_delta = 300.73417721519`
  - `4 bars: resolved_trade_count = 77, mean_proxy_price_delta = 509.285714285714`
  - `8 bars: resolved_trade_count = 75, mean_proxy_price_delta = 831.773333333333`
- `mean_proxy_mae_price_delta = -910.841463414634`
- `mean_proxy_mfe_price_delta = 3013.219512195122`

Observed Git/reporting facts for this slice:

- `git status --short` reported the new packet as untracked
- `git status --short --ignored results/research/fa_v2_adaptation_off/phase10_execution_proxy_evidence_manifest_pilot_20260515` reported the new output root as ignored (`!!`)

## Inferred

- The new manifest output now provides a compact citation anchor for claim-bearing notes: one input hash plus one stable non-self output inventory/hash set is enough to point back to the exact proxy evidence root without reproducing the whole JSON payload in prose.
- This pilot shows the claim-header workflow can stay lightweight while still being concrete: the note can say exactly which artifact root was observed, which hashes were cited, and which authority boundary remained in force.
- The proxy surface remains materially populated rather than empty, but its own emitted limitations still make it an observational surface only.

## Unverified

- This pilot does **not** prove realized execution quality, slippage, latency, queue position, or venue behavior.
- This pilot does **not** prove or reject `execution_inefficiency` as a mechanism class.
- This pilot does **not** add symbol/timeframe/warmup metadata beyond what is directly available in the cited artifacts.
- This pilot does **not** establish a repo-wide manifest standard for all evidence scripts.

## Why this note matters

This note is intentionally small.
Its job is not to settle the execution question; its job is to prove that a claim-bearing note can now:

- cite a fresh deterministic manifest-backed artifact root
- separate `observed`, `inferred`, and `unverified`
- keep the non-authority boundary explicit
- remain reusable as evidence without pretending to be a packet or a runtime decision

## Bottom line

The first manifest-backed claim-bearing pilot succeeded.
It records one exact `execution_proxy_evidence` artifact root with stable hashes and an explicit observational boundary, while leaving realized execution questions unresolved and out of scope.
