# RI policy router continuation_release_hysteresis local packet candidate 2020-06 — 2026-05-26

## Scope

Bounded RESEARCH widening follow-up after retiring `2021-04` as an exhausted candidate on the artifact/debug path.

Question:

> when the next negative-like widening candidate `2020-06` is rerun against the already-characterized positive control `2023-05` on the same carrier, does the new candidate preserve more of the frozen negative local asymmetry than the control?

This slice is observational only.

It does **not** claim local equity divergence already exists for `2020-06`, does **not** reopen the exhausted `2021-04` candidate, and does **not** promote `2020-06` past the local-packet stage.

## Inputs

- monthly inventory windows: `results/backtests/ri_policy_router_continuation_release_hysteresis_monthly_inventory_20260504/continuation_release_hysteresis_monthly_inventory_windows.json`
- intra-band sign candidates artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_intra_band_sign_candidates_2026-05-26.json`
- widening candidate inventory artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_widening_candidate_inventory_2026-05-26.json`
- carrier: `tmp/policy_router_evidence/tBTCUSD_3h_slice8_runtime_bridge_weak_pre_aged_release_guard_20260424.json`
- emitted artifact: `results/evaluation/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2020_06_2026-05-26.json`
- helper: `scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2020_06_20260526.py`

## What changed and what did not

- **Changed:** one thin wrapper reused the landed local-packet machinery but replaced the exhausted `2021-04` candidate with the next widening target `2020-06`, while keeping the established positive control `2023-05` fixed.
- **Did not change:** no runtime/config files changed, no new ranking heuristic was introduced, and no local envelope or execution-surface claims were made for `2020-06` yet.

## Observed

### 1. `2020-06` beats the control on the frozen local negative rules

The packet summary is:

- candidate subject: `2020-06`
- control subject: `2023-05`
- candidate negative-rule hit count: `6 / 9`
- control negative-rule hit count: `4 / 9`

Artifact status:

> `negative_like_candidate_preserves_more_triad_local_asymmetry_than_control`

So the widening step survives the candidate swap.

The new candidate still looks materially more negative-like than the control on the frozen local rule surface.

### 2. `2020-06` is locally sharper than the earlier `2021-04` packet on key compression features

Compared with the previously landed `2021-04` packet, `2020-06` shows:

- lower release retention ratio: `0.333333` vs `0.5625`
- span compression: `18h` vs `21h`
- same size-diff count: `2`
- same policy-diff count: `6`
- same switch-reason-diff count: `6`
- higher frozen negative-rule hit count: `6` vs `5`

So the next widening candidate is not weaker than the retired one.

On the packet surface, it is at least as interesting and arguably cleaner.

### 3. The decisive row arrives immediately at cluster start

For `2020-06`:

- cluster row count: `9`
- first decisive timestamp: `2020-06-17T18:00:00+00:00`
- decisive rank pct: `0.0`
- decisive hours from cluster start: `0.0`

That means the packet does not need a long local incubation period before the candidate looks different.

The local negative-like separation appears at the first decisive row.

### 4. The candidate's strongest retained differences are structural, not confidence-quality based

`2020-06` satisfies these frozen negative separators:

- `release_retention_ratio`
- `decisive_rank_pct`
- `decisive_hours_from_cluster_start`
- `cluster_policy_diff_rows`
- `cluster_switch_diff_rows`
- `cluster_size_diff_rows`

It does **not** satisfy:

- `decisive_action_edge`
- `decisive_confidence_gate`
- `decisive_clarity_score`

So the candidate looks negative-like because its local cluster is compressed, early-decisive, and structurally asymmetric — not because it reproduces the most pessimistic action-edge or clarity values from the frozen negative anchor.

### 5. `2023-05` remains useful as a stable positive control

The control stays unchanged on the same carrier:

- hit count: `4 / 9`
- release retention ratio: `1.0`
- span compression: `0h`
- cluster size diff rows: `1`

So keeping `2023-05` fixed was useful.

It lets the widening step isolate the candidate change instead of changing both sides of the pair at once.

## Inferred

### 1. `2020-06` is the first credible successor to the exhausted `2021-04` candidate

The smallest honest inference is:

> once `2021-04` is retired on the artifact/debug path, `2020-06` becomes the next admissible local-window candidate because it still preserves more of the frozen negative asymmetry than the same established control.

That is enough to justify continuing the chain on `2020-06`.

### 2. The next question should move inward again, not outward

The packet has already done its job:

- the new candidate is still negative-like
- the control is still less negative-like

So the next honest question is no longer “is `2020-06` worth localizing?”

It is:

> inside the exact `2020-06` local envelope, does this new candidate also collapse before execution, or does it carry a different local decay path than `2021-04`?

### 3. The widening chain remains productive

This matters because the `2021-04` retirement could have killed the whole widening path.

Instead, the path remains live:

> a second negative-like month still carries a stronger local packet than the positive control.

So the widening shortlist is still useful, not just historical scaffolding.

## Unverified

The following remain open:

1. whether the `2020-06` local packet also stays economically invariant inside its exact local envelope
2. whether `2020-06` reaches execution-surface divergence where `2021-04` did not
3. whether `2020-06` collapses to the same `switch_control_mode` breadcrumb pattern or follows a different dormant-state path

## Verification

- `python scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2020_06_20260526.py` -> emitted artifact with status `negative_like_candidate_preserves_more_triad_local_asymmetry_than_control`
- `ruff check scripts/analyze/ri_policy_router_continuation_release_hysteresis_local_packet_candidate_2020_06_20260526.py` -> pass

## Bottom line

This slice successfully widens past the exhausted `2021-04` case.

What is now supported is:

> `2020-06` preserves more of the frozen negative local asymmetry than the established `2023-05` control on the same carrier, with `6 / 9` negative-rule hits versus the control's `4 / 9`.

So the next honest continuation is clear:

> localize inward again around the exact `2020-06` envelope, not back out to another broad monthly scan.
