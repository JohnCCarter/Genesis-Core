# Execution proxy fixture containment packet

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `packet-defined / docs-only / non-authorizing`

This document records the exact commit-safe carrier strategy to use if the `execution_proxy_evidence` clean-checkout replay-smoke line is reopened. It grants no source, test, runtime, config-authority, paper/live, promotion, or replay-attestation authority by itself.

## COMMAND PACKET

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Category:** `docs`
- **Risk:** `LOW` — why: this slice chooses one bounded carrier strategy only and does not modify scripts, tests, runtime behavior, or results semantics
- **Required Path:** `Quick path / docs-only pre-code packet`
- **Lane:** `Research-evidence` — why: the packet narrows one reproducibility carrier for a future smoke slice without authorizing implementation
- **Objective:** choose the smallest admissible commit-safe carrier for a future `execution_proxy_evidence` clean-checkout replay smoke
- **Base SHA:** `19436c17`
- **Related boundary:** `docs/decisions/governance/execution_proxy_clean_checkout_replay_smoke_boundary_packet_2026-05-15.md`

### Scope

- **Scope IN:** this packet; queue sync that records the selected carrier strategy and the next implementation slice
- **Scope OUT:** all script/test changes; all bundle creation; all `results/research/**` tracking changes; all edge-origin or SCPE replay carrier decisions; all CI rollout; all runtime/config-authority/paper/live/promotion changes
- **Max files touched:** `2`

### Gates required

For this packet itself:

- targeted docs validation for this packet and queue sync
- manual wording audit that the packet stays non-authorizing
- manual wording audit that the carrier choice remains exact and bounded to `execution_proxy_evidence`

## Purpose

This packet answers one narrow question only:

- what exact commit-safe carrier should the first `execution_proxy_evidence` clean-checkout replay smoke use?

## Governing basis

### Observed

1. The selected clean-checkout replay-smoke candidate is `execution_proxy_evidence`.
2. The currently used historical input trace under `results/research/fa_v2_adaptation_off/trace_baseline_current.json` is locally present but ignored/untracked.
3. `tests/backtest/test_execution_proxy_evidence.py` already proves that the script can run deterministically from a compact JSON payload built inside the tracked test surface and written to a temporary path.
4. `scripts/analyze/execution_proxy_evidence.py` already accepts an arbitrary baseline JSON path through its CLI and does not require the ignored historical artifact root as a special runtime location.
5. The repository already uses an explicit tracked fixture-like zone under `registry/fixtures/`, for example `registry/fixtures/backtest_sample.json`.
6. `.gitignore` intentionally excludes `results/**` broadly while allowing only narrow archival/evaluation exceptions, so placing the new carrier under `results/research/**` would fight the current repo policy instead of fitting it.

### Inferred

- The smallest admissible carrier is **one tracked minimal JSON fixture** rather than a bundle, archive, or broader retained research root.
- The most repo-consistent home for that carrier is **`registry/fixtures/`**, because that zone already signals explicit fixture-like tracked assets.
- The future implementation slice can likely stay bounded to:
  - one new tracked fixture JSON under `registry/fixtures/`
  - focused additions in `tests/backtest/test_execution_proxy_evidence.py`
- `scripts/analyze/execution_proxy_evidence.py` should remain **OUT** for the first implementation slice unless inspection proves a strictly necessary helper seam.
- A bundle/LFS carrier is not the cheapest admissible first move because the current execution-proxy payload shape is already compact and test-proven.

### Unverified in this packet

- whether a later stronger replay-attestation line will still need a curated bundle tied to the original ignored historical trace
- whether the future implementation slice should add one tracked-fixture smoke test or both smoke and repeatability selectors against that carrier

## Boundary decision

### Current standing conclusion

If the `execution_proxy_evidence` clean-checkout replay-smoke line is reopened, the exact first carrier strategy should be:

- **one tracked minimal JSON fixture under `registry/fixtures/`**

This is a carrier-selection conclusion only. It is **not** approval to implement the smoke yet.

### Likely future implementation scope

If this line is reopened as a real implementation slice, the smallest honest starting scope is likely:

- `registry/fixtures/execution_proxy_baseline_current_minimal.json`
- `tests/backtest/test_execution_proxy_evidence.py`

### Likely future implementation scope OUT

A future implementation slice should keep the following out of scope unless separately reopened:

- `scripts/analyze/execution_proxy_evidence.py`
- `results/research/**`
- `results/archive/bundles/**`
- `edge_origin_isolation`
- `scpe_ri_v1_router_replay`
- repo-wide replay-smoke helpers or framework extraction

## Hard stop and reopen rule

If the future implementation slice discovers any of the following, it must stop and reopen as a separate bounded packet:

- the minimal tracked fixture cannot honestly preserve the needed execution-proxy contract
- the carrier must become large enough to justify archival bundle handling
- the script itself needs behavior changes beyond simple smoke/test reuse
- multiple replay chains need to be solved together

## Bottom line

The first `execution_proxy_evidence` clean-checkout replay-smoke should not depend on ignored research artifacts and should not start with bundles. The smallest admissible carrier is one tracked minimal JSON fixture under `registry/fixtures/`, paired with focused test-level smoke coverage and no broader replay-framework widening.
