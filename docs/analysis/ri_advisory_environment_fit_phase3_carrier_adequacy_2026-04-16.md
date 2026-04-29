# RI advisory environment-fit — Phase 3 carrier adequacy

This memo is docs-only and fail-closed.
It decides whether the repository already contains an admissible RI carrier rich enough to justify a second bounded RI evidence-capture slice after the fixed slice8 bridge proved too thin.

Governance packet: `docs/governance/ri_advisory_environment_fit_phase3_carrier_adequacy_packet_2026-04-16.md`

## Source surface used

This memo uses only already tracked carrier files, completed capture outputs, and related analysis notes:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`
- `docs/analysis/ri_advisory_environment_fit_phase3_post_capture_admissibility_2026-04-16.md`
- `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/capture_summary.json`
- `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json`
- `config/optimizer/3h/phased_v3/best_trials/phaseB_v2_best_trial.json`
- `tmp/ri_ablation_authority_clarity_tBTCUSD_3h_20260318.json`
- `docs/analysis/regime_intelligence_phase_bc_rerun_plan_2026-03-13.md`

## Decision question

Does the repository already contain an admissible RI carrier that is both:

1. rich enough in observability to justify another bounded capture slice, and
2. sufficiently carrier-like that the roadmap can move straight to capture rather than first opening a carrier-materialization decision?

## Short answer

**Not directly.**

The repository contains promising clarity-on RI artifacts, but it does **not** yet contain a clearly established fixed candidate carrier that can immediately replace the current slice8 runtime bridge as the next capture surface.

## Carrier classes now visible in-repo

### 1. Established fixed candidate carrier

The repository currently has one clearly established RI carrier in candidate form:

- `config/strategy/candidates/3h/tBTCUSD_3h_slice8_runtime_bridge_20260326.json`

What it is:

- explicitly `strategy_family = ri`
- explicitly a `runtime_bridge`
- explicitly described as a `Minimal runtime-valid RI bridge`
- explicitly described as `Backtest-only candidate artifact; not a champion, not promotion evidence`

What it is not:

- it is not clarity-enabled
- it is not evidence-rich enough for direct baseline authoring

The completed capture slice already proved this carrier is too thin on the realized-entry surface because it yielded:

- zero clarity coverage
- zero shadow mismatch variation
- zero transition-multiplier variation

So this carrier remains:

- **admissible for capture**
- **not adequate for the roadmap’s next baseline-oriented question**

### 2. Promising optimizer artifacts

The repository also contains RI best-trial artifacts with clarity enabled, especially:

- `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json`
- `config/optimizer/3h/phased_v3/best_trials/phaseB_v2_best_trial.json`

Why they matter:

- they are RI-family surfaces with `authority_mode = regime_module`
- they carry `clarity_score.enabled = true`
- `phaseC_oos_trial.json` also carries a nonzero `runtime_version = 375`
- the rerun plan explicitly describes `phaseC_oos_trial.json` as the corrected OOS artifact for the corrected RI best params

Why they are still not immediately a next capture carrier:

- they live under `config/optimizer/.../best_trials/`, not under `config/strategy/candidates/...`
- they are tracked as best-trial / OOS artifacts, not as already established fixed runtime-bridge candidates
- their `config_path` still points to trial-local materialization names such as `trial_001_config.json`
- using them directly as the next capture carrier would implicitly collapse the distinction between:
  - optimizer artifact
  - fixed research carrier
  - runtime-valid candidate surface

That distinction is exactly what this lane must keep explicit.

So these artifacts are best classified as:

- **promising donor / materialization candidates**
- **not yet direct replacement carriers by packet-free assertion**

### 3. Temporary observational configs

The repo also contains temporary RI clarity-on observational files, for example:

- `tmp/ri_ablation_authority_clarity_tBTCUSD_3h_20260318.json`

This file is useful as evidence that clarity-on RI surfaces have been explored.
But it is explicitly temporary and observational.
That means it is even less suitable than the optimizer best-trial artifacts as a direct next capture carrier.

It is best classified as:

- **evidence of prior exploratory work**
- **not an admissible carrier for the next bounded capture slice**

## Carrier adequacy verdict

### 4. There is no already-established clarity-on fixed carrier

The most important conclusion is simple:

- the repository does **not** currently expose a clarity-on RI carrier that is already both fixed and candidate-like in the same governance class as the slice8 runtime bridge

That means the lane cannot honestly say:

- “we already have the right carrier; just capture it next”

### 5. There is, however, a plausible next donor surface

Among the non-candidate surfaces, the strongest next donor is:

- `config/optimizer/3h/phased_v3/best_trials/phaseC_oos_trial.json`

Why this is the strongest donor:

- RI family and authority mode are aligned with the lane
- clarity is enabled
- it is an OOS artifact rather than a purely in-sample only best-trial snapshot
- it is already referenced in RI rerun documentation as corrected OOS evidence

But even here the honest boundary remains:

- promising donor does **not** equal ready carrier

## Admissibility decision

The next admissible move is **not** an immediate second capture run.

Instead, the next admissible move is:

- **one bounded carrier-materialization / admissibility slice**

That slice should answer only this narrower question:

> may one specific clarity-on RI optimizer artifact be materialized or promoted into a fixed research carrier without changing default behavior or blurring candidate vs artifact semantics?

That is narrower — and safer — than jumping directly into capture.

## What should not happen next

- no direct reuse of `phaseC_oos_trial.json` as if it were already a fixed candidate carrier
- no capture run directly against tmp observational configs
- no direct baseline authoring from optimizer artifacts
- no silent config conversion without a packeted carrier decision

## Fallback if carrier-materialization is not admissible

If no clarity-on RI artifact can be packeted into a clean fixed research carrier without semantics drift, the correct fallback is:

- **lane close**

That would be disappointing, but still governance-correct.
It is better than pretending a baseline exists on under-identified evidence.

## Bottom line

The lane is **not closed yet**, but it is also **not ready for another capture run immediately**.

The honest state is now:

- current fixed carrier = admissible but too thin
- clarity-on RI artifacts = promising but not yet established carriers
- next admissible step = **carrier-materialization / admissibility slice**, most likely centered on `phaseC_oos_trial.json`

So the roadmap should move forward one careful notch, not one leap:

- **do not open baseline authoring**
- **do not open capture v2 yet**
- **open one bounded carrier-materialization decision slice first**
