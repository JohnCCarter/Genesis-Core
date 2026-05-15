# Decision-influencing replay smoke candidate selection

## Claim header

- **Date:** `2026-05-15`
- **Branch:** `feature/evidence-closeout-pilot`
- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Lane:** `Research-evidence` — why: this note selects one bounded decision-influencing artifact chain as the next clean-checkout replay smoke candidate and records only observational candidate-selection findings
- **Status:** `observational / candidate selection`
- **Authority level:** `bounded research-evidence`
- **Claim status:** `observed`
- **Objective:** choose the first decision-influencing artifact chain for a future clean-checkout replay smoke candidate after the completed evidence-manifest pilot and generalization-boundary work
- **Baseline reference(s):** `artifacts/diagnostics/genesis_core_premortem_2026-05-15.md`, `docs/analysis/diagnostics/next_phase_verkstad_queue_2026-05-15.md`, `docs/governance/runbooks/evidence_claim_adoption.md`
- **Representative surfaces reviewed:** `scripts/analyze/execution_proxy_evidence.py`, `tests/backtest/test_execution_proxy_evidence.py`, `docs/analysis/diagnostics/execution_proxy_manifest_claim_pilot_2026-05-15.md`, `scripts/analyze/edge_origin_isolation.py`, `tests/backtest/test_edge_origin_isolation.py`, `docs/analysis/diagnostics/edge_origin_isolation_manifest_claim_pilot_2026-05-15.md`, `scripts/analyze/scpe_ri_v1_router_replay.py`
- **Runtime base SHA:** `57ce4bd8`
- **Evidence commit SHA:** `57ce4bd8`
- **Working-tree status:** `clean at selection start`
- **Config path:** `not applicable`
- **Config hash:** `not applicable`
- **Data-source policy:** `tracked docs/scripts/tests plus terminal verification of candidate input-path tracking status`
- **Env flags:** `no additional env flags were set for this docs-only slice`
- **Artifact path(s):**
  - `docs/analysis/diagnostics/decision_influencing_replay_smoke_candidate_selection_2026-05-15.md`
  - `docs/decisions/governance/execution_proxy_clean_checkout_replay_smoke_boundary_packet_2026-05-15.md`
- **What changed:** `one bounded selection note and one companion boundary packet record the first clean-checkout replay smoke candidate and the current fixture-containment gap`
- **What did not change:** `no script/test/runtime/config-authority/artifact-chain behavior changed; no replay smoke was implemented yet`
- **Does not authorize:** `runtime changes, replay automation rollout, fixture imports, or clean-checkout claims by implication`

## Observed

### Candidate A — `execution_proxy_evidence` is the smallest manifest-backed claim chain

The `execution_proxy_evidence` chain has the smallest currently visible shape among the manifest-backed claim-bearing candidates reviewed in this slice:

- one locked input trace
- one deterministic analysis script: `scripts/analyze/execution_proxy_evidence.py`
- one focused nearby test file: `tests/backtest/test_execution_proxy_evidence.py`
- explicit manifest output and deterministic CLI repeatability assertions
- one claim-bearing note already framed as observational evidence: `docs/analysis/diagnostics/execution_proxy_manifest_claim_pilot_2026-05-15.md`

Observed focused test coverage from the tracked test file includes:

- required output-surface assertions
- manifest non-self/repeatability assertions
- CLI smoke assertions
- CLI repeatable-output assertions

### Candidate B — `edge_origin_isolation` is same-shaped but materially broader

The `edge_origin_isolation` chain is also a strong manifest-backed candidate, but it is broader than `execution_proxy_evidence`:

- two locked inputs instead of one
- eleven approved output files instead of four
- broader observational surface spanning execution, sizing, path, selection, and counterfactual outputs
- one focused nearby test file: `tests/backtest/test_edge_origin_isolation.py`

This makes it a credible later candidate, but not the smallest first one.

### Candidate C — `scpe_ri_v1_router_replay` is stronger provenance, but a broader first move

`scpe_ri_v1_router_replay.py` already exposes a richer replay-root contract than the two May 15 manifest pilots:

- fixed input-manifest handling
- approved output inventory
- replay metrics and manifest outputs
- explicit containment-style replay posture

That makes it important, but it is a larger first clean-checkout target than `execution_proxy_evidence`.

### Current clean-checkout blocker is real across all representative candidates

Terminal verification in this slice showed that the inspected candidate input artifacts are present locally **but are not tracked**:

- `results/research/fa_v2_adaptation_off/trace_baseline_current.json` → present locally, `tracked=False`, `ignored=True`
- `results/research/fa_v2_adaptation_off/trace_adaptation_off.json` → present locally, `tracked=False`, `ignored=True`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson` → present locally, `tracked=False`, `ignored=True`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json` → present locally, `tracked=False`, `ignored=True`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/manifest.json` → present locally, `tracked=False`, `ignored=True`

That means the current repo state does **not** yet support an honest clean-checkout replay-smoke claim for these chains merely by reusing the locally present research inputs.

## Inferred

- The first candidate should be `execution_proxy_evidence`, because it is the smallest same-shaped decision-influencing chain with a manifest-backed claim note, a single locked input, and focused deterministic test coverage.
- `edge_origin_isolation` remains a viable later follow-up, but it is broader and therefore not the cheapest first clean-checkout candidate.
- `scpe_ri_v1_router_replay` remains highly relevant, but it is a larger replay-root surface and therefore not the first bounded clean-checkout candidate to open from the current queue.
- Because the inspected inputs are ignored/untracked, the next admissible step is **not** direct clean-checkout smoke implementation. The next admissible step is a separate bounded fixture-containment decision for the selected `execution_proxy_evidence` chain.

## Unverified

- This slice does **not** decide whether the future `execution_proxy_evidence` clean-checkout input should be a tracked minimal fixture, a curated bundle pointer, or another commit-safe reproducibility carrier.
- This slice does **not** prove that `execution_proxy_evidence` is the best candidate for every later replay-smoke need; it proves only that it is the best first bounded candidate from the currently reviewed set.
- This slice does **not** implement or validate a clean-checkout replay smoke itself.

## Why this note matters

The queue asked for a first candidate, not for a framework.

This note answers that precisely:

- choose the smallest useful first chain
- reject broader first moves by scope, not by taste
- expose the real blocker that prevents an honest clean-checkout claim today

That keeps the next implementation slice grounded in repo reality instead of in whichever local ignored artifact happened to exist on one machine.

## Bottom line

`execution_proxy_evidence` is the first bounded decision-influencing artifact chain that should be considered for a future clean-checkout replay smoke. But the current input artifact for that chain is ignored/untracked, so the next honest step is a separate fixture-containment packet for `execution_proxy_evidence`, not a premature replay-smoke implementation or repo-wide automation jump.
