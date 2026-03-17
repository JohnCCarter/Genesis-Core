# RI P1 OFF parity governed baseline reset — execution prep

Date: 2026-03-17
Slice: `feature/regime-intelligence-cutover-analysis-v1`
Status: `prep-only / fallback path selected / execution not approved by this slice`

## Purpose

This document records the selected next path for `RI P1 OFF parity` sign-off work:

- stop evidence recovery as the preferred next step
- use the fallback path `governed baseline reset via parity rerun` under frozen spec `ri_p1_off_parity_v1`

This document prepares that future rerun path.

It does **not** execute the rerun.
It does **not** grant baseline approval.
It does **not** grant execution approval.

## Honest governance view

Given the current repository state, continuing to chase historical PASS artifacts across multiple local machines would add cost without improving the evidentiary quality of the eventual sign-off packet.

A governed baseline reset under a frozen spec is cleaner because it can produce:

- a canonical artifact at the locked path
- reviewable baseline / candidate provenance
- explicit run metadata
- a full green gate bundle tied to one reviewed packet

That makes the fallback path the more credible route for future sign-off.

## What is changing in decision posture

Previously documented paths allowed either:

- evidence recovery, or
- fallback governed rerun

This prep slice now records that the intended next route is the fallback path.

Evidence recovery is retired as the preferred next step.

That decision does **not** retroactively convert March sign-off text, ignored logs, or synthetic local artifacts into recovered baseline provenance.

## Locked future rerun contract

The future governed rerun must preserve all of the following:

- canonical artifact path: `results/evaluation/ri_p1_off_parity_v1_<run_id>.json`
- canonical baseline reference path: `results/evaluation/ri_p1_off_parity_v1_baseline.json`
- `results/evaluation/ri_p1_off_parity_v1_baseline.json` remains a reserved canonical reference path only; this prep slice does not treat it as a currently verified tracked baseline artifact.
- `window_spec_id=ri_p1_off_parity_v1`
- `mode=OFF`
- `symbol=tTESTBTC:TESTUSD`
- `timeframe=1h`
- `start_utc=2025-01-01T00:00:00Z`
- `end_utc=2025-01-31T23:59:59Z`
- `GENESIS_FAST_HASH=0`
- `size_tolerance=1e-12`

Required future run metadata remains mandatory:

- `git_sha`
- `run_id`
- `branch`
- `executed_at_utc`
- `window_spec_id`
- `symbol`
- `timeframe`
- `start_utc`
- `end_utc`
- `baseline_artifact_ref`
- `runtime_config_source`
- `compare_tool_path`

## Allowed future baseline path

The selected fallback route allows the future rerun packet to use the baseline classification:

- `newly approved baseline under explicit governance approval`

That phrase defines an allowed **future** approval path only.

This prep slice does not itself grant that approval.

## What the future execution packet must produce

Before any future PASS may count as governance sign-off, the future governed rerun packet must produce all of the following:

1. retained baseline rows evidence with SHA256 linkage
2. retained candidate rows evidence with SHA256 linkage
3. canonical parity artifact with required metadata fields
4. supplemental manifest linking baseline, candidate, commands, hashes, and canonical artifact
5. full green gate bundle, including:
   - smoke
   - determinism replay
   - feature cache invariance
   - pipeline invariant
   - evaluate/source invariant selectors
   - comparator selectors
   - decision-row serialization selector
   - named skill checks
6. parity verdict `PASS`
7. all mismatch counts equal to `0`
8. no runtime-default drift

## Execution approval remains separate

Even after this prep slice, execution remains separately unapproved until a future governance-reviewed rerun packet records:

- the locked window and metadata bundle
- the explicit baseline classification and approval anchor
- reviewable provenance for baseline and candidate evidence
- the canonical artifact and SHA256 links
- the full green gate bundle

Only then may a future review consider lifting the execution block.

## Stop conditions preserved

Stop and return for fresh governance review if any of the following occur:

- the future rerun packet changes the frozen spec
- the future rerun packet changes the canonical artifact contract
- the future rerun packet changes the named gate bundle
- the future rerun would require runtime/config/champion/default-authority changes
- the future evidence chain would live only under ignored paths such as `logs/**`, `tmp/**`, or `artifacts/**`
- March sign-off text or ignored logs are proposed as recovered baseline provenance
- synthetic `ri_p1_off_parity_v1_ri-20260303-003.json` is proposed as baseline, candidate, or sign-off evidence

## Current conclusion

The repository now has a defined and explicit fallback route for RI P1 OFF sign-off:

- implementation status remains unchanged: RI implementation is already complete
- default authority remains unchanged: `legacy`
- evidence recovery is no longer the preferred next step
- governed baseline reset via parity rerun is the selected next path
- execution approval is still separate and still future-scoped

No rerun has been started by this slice.
