# SCPE RI V1 runtime/integration seam inventory

Date: 2026-04-20
Branch: `feature/ri-role-map-implementation-2026-03-24`
Status: `planning-only / inventory-only / no authorization`

This document is a planning artifact in `RESEARCH` and grants no implementation, runtime, readiness, cutover, launch, deployment, paper-trading, or promotion authority. It must not be used as approval to begin code, config, test, or operational changes. Any future lane identified here requires its own commit contract, its own command packet, explicit Opus review where required, and separate verification.

## Future packet scaffold (planning-only, non-executable placeholder)

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via branch mapping for `feature/ri-role-map-implementation-2026-03-24`
- **Category:** `docs`
- **Risk:** `LOW` — why: single-file docs-only seam inventory; main risk is governance or design wording drift that could be misread as implementation authority
- **Required Path:** `Quick`
- **Objective:** inventory the currently visible backtest, runtime-observability, runtime-authority, and paper-shadow seams that would matter for any future SCPE RI runtime/integration lane, while staying strictly below implementation approval
- **Candidate:** `future SCPE RI seam/compatibility inventory`
- **Base SHA:** `516553e7`

The scaffold below is a non-executable planning placeholder only. It contains no approved selectors, commands, gates, implementation scope, readiness claim, or authorization for future work.

### Scope

- **Scope IN:** one docs-only inventory note; candidate seam mapping; authority boundary mapping; artifact-home constraints; sequencing interpretation for future lanes; explicit stop conditions and non-authorization boundaries
- **Scope OUT:** all edits under `src/**`, `tests/**`, `config/**`, `scripts/**`, `results/**`, and `artifacts/**`; all runnable commands/selectors; all implementation design approval; all readiness/cutover/promotion framing
- **Expected changed files:** `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_integration_seam_inventory_2026-04-20.md`
- **Max files touched:** `1`

### Stop Conditions

- any wording that treats an inventoried seam as approved for implementation
- any wording that implies inherited runtime authority from the research closeout or roadmap
- any wording that selects an artifact schema, config shape, test set, or execution plan as already adopted
- any wording that treats paper-shadow as paper approval, or paper approval as live readiness
- any wording that places future artifacts in runtime-authoritative surfaces

## Purpose

This note answers one narrow governance question:

- what actual seams and authority boundaries are currently visible in the repository if a future SCPE RI runtime/integration lane is ever proposed?

This note is **inventory-only**.

It does **not**:

- select a future implementation
- authorize a future lane
- define commands, tests, or selectors
- define approved artifact schemas
- authorize backtest, runtime, or paper changes

## Starting point

This note is downstream of:

- `docs/decisions/scpe_ri_v1/scpe_ri_v1_research_closeout_report_2026-04-20.md`
- `docs/analysis/scpe_ri_v1/scpe_ri_v1_runtime_integration_roadmap_2026-04-20.md`

Those documents already fixed the following boundary:

1. the bounded SCPE RI research lane is closed
2. no runtime/integration approval is inherited
3. a seam inventory note is the first admissible follow-up before any implementation-adjacent lane is selected
4. shadow/backtest questions should remain earlier than runtime or paper-adjacent questions
5. any behavior-changing lane must remain distinctly later and separately governed

## Source surfaces inventoried

This note uses tracked repository surfaces only:

- `src/core/backtest/engine.py`
- `scripts/run/run_backtest.py`
- `src/core/api/strategy.py`
- `src/core/strategy/evaluate.py`
- `src/core/api/config.py`
- `src/core/server.py`
- `scripts/paper_trading_runner.py`
- `docs/audit/research_system/context_map_backtest_champion_shadow_intelligence_v1_2026-03-18.md`
- `docs/features/feature-champion-shadow-intelligence-1.md`
- `docs/architecture/ARCHITECTURE_VISUAL.md`
- `docs/paper_trading/runner_deployment.md`
- `docs/paper_trading/phase3_runbook.md`
- `docs/analysis/regime_intelligence/core/regime_intelligence_default_cutover_gap_analysis_2026-03-17.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`

## Seam inventory

### 1. Backtest shadow seam

This is the clearest currently visible implementation-adjacent seam.

#### Visible entrypoints and hooks

- `scripts/run/run_backtest.py`
  - already supports passive hook composition via `_compose_decision_row_capture_hook(...)`
  - already wires `BacktestIntelligenceShadowRecorder` through `engine.evaluation_hook`
  - already treats intelligence-shadow output as explicitly opt-in through `--intelligence-shadow-out`
- `src/core/backtest/engine.py`
  - exposes `evaluation_hook(result, meta, candles) -> (result, meta)`
  - applies the hook after `evaluate_pipeline(...)` and before downstream action handling

#### What this seam is good for

- deterministic shadow capture during backtest execution
- artifact generation without changing the decision path by default
- proving parity/no-drift claims in a bounded environment

#### Boundary already visible in repository precedent

Historical shadow planning surfaces consistently require:

- explicit opt-in only
- no mutation of `action`, `size`, `reasons`, trades, or exit behavior
- deterministic artifact output
- local backtest-domain placement rather than shared runtime-authority changes

#### Candidate artifact homes visible in precedent

Historical precedent references:

- summary artifacts under `results/intelligence_shadow/<run_id>/...`
- ledger or detailed artifacts under `artifacts/intelligence_shadow/<run_id>/research_ledger/...`

This note does **not** adopt those homes as authority for SCPE RI work. It records them only as the nearest existing pattern that stays outside runtime-config authority.

#### Inventory interpretation

Within this inventory-only snapshot, this appears to be the smallest currently visible implementation-adjacent seam in the repository. That is an observational scoping note only; it does not select a lane, authorize implementation, approve design, or satisfy readiness for any future runtime or paper path.

### 2. Runtime evaluation seam

This seam is visibly closer to authority and therefore materially riskier.

#### Visible entrypoints

- `src/core/api/strategy.py`
  - `POST /strategy/evaluate`
  - forwards request payload to `evaluate_pipeline(candles, policy, configs, state)`
- `src/core/strategy/evaluate.py`
  - merges request configs with champion config unless forced backtest mode applies
  - computes authoritative regime, shadow regime observability, features, probabilities, confidence, and decision output

#### Relevant observability already present

`evaluate.py` already emits an additive `meta["observability"]["shadow_regime"]` payload with:

- `authoritative_source`
- `shadow_source`
- `authority_mode`
- `authority_mode_source`
- `authority`
- `shadow`
- `mismatch`
- `decision_input = False`

#### Why this seam is not the first admissible integration candidate

Even though runtime-observability already exists, this seam sits directly beside:

- champion merge behavior
- live request evaluation
- authoritative regime selection
- decision output returned by the API

That makes it too close to runtime-authority semantics to be treated as a casual first integration step.

#### Inventory interpretation

This seam is a plausible **later observational lane**, but it should remain later than a backtest-shadow lane because it is adjacent to active authority and response semantics.

### 3. Runtime config-authority seam

This is not an integration seam to start with. It is an authority boundary to avoid unless a future lane explicitly escalates.

#### Visible surfaces

- `src/core/api/config.py`
  - `GET /config/runtime`
  - `POST /config/runtime/validate`
  - `POST /config/runtime/propose`
- `src/core/server.py`
  - reads runtime config at startup via `_AUTH.get()`
- `src/core/config/authority.py`
  - runtime SSOT behavior for `config/runtime.json`
- `docs/architecture/ARCHITECTURE_VISUAL.md`
  - documents config/runtime truth table and authority use across API, runner, and optimizer

#### Why this surface matters

Any future SCPE RI integration lane that begins to rely on:

- runtime toggles
- runtime writeback
- config proposal flow
- champion or candidate config mutation

would stop being a narrow observational/shadow lane and move toward explicit authority work.

#### Inventory interpretation

This seam is best treated as a **hard boundary** for early future lanes, not as a near-term candidate seam.

### 4. Paper-runner seam

This seam exists, but it is operationally closer to execution than the backtest seam and should therefore stay later.

#### Visible entrypoint

- `scripts/paper_trading_runner.py`
  - polls candles
  - loads runtime config from `/config/runtime`
  - calls `/strategy/evaluate`
  - optionally submits orders through `/paper/submit`
  - persists state and log outputs to runner-owned paths

#### Operational properties already visible

The runner already contains:

- default `--dry-run`
- explicit `--live-paper`
- fail-closed live-paper guardrails
- persistent state for idempotency
- champion verification on startup
- daily operational runbook expectations in `docs/paper_trading/phase3_runbook.md`

#### Why this seam is not an early future candidate

Even a paper-shadow interpretation of this seam sits next to:

- real polling loops
- operational state files
- API-driven live evaluation
- optional order submission path
- runbook and operational monitoring expectations

That makes it a later governance question than backtest shadow and likely later than runtime-observability too.

#### Inventory interpretation

This seam is a **later candidate** for an observational paper-shadow lane only after earlier observational lanes are closed successfully and operational controls are separately packeted.

## Authority boundary inventory

### Boundary A — Runtime default and write authority must remain untouched early

Visible authority surfaces:

- `config/runtime.json`
- `/config/runtime/*`
- startup config load in `src/core/server.py`
- merged runtime/champion behavior documented in `docs/architecture/ARCHITECTURE_VISUAL.md`

Interpretation:

- early SCPE RI lanes should avoid config-authority mutation entirely
- future artifact or observability work must not be smuggled in as runtime-config semantics

### Boundary B — Champion merge semantics are active runtime behavior

Visible in:

- `src/core/strategy/evaluate.py`
- `scripts/run/run_backtest.py`
- `src/core/backtest/engine.py`

Interpretation:

- anything that changes champion merge, champion provenance, or decision authority is no longer a low-risk observational lane
- early lanes should avoid merge-policy changes entirely

### Boundary C — Shadow observability is currently additive, not decision-authoritative

Visible in:

- `src/core/strategy/evaluate.py`

Interpretation:

- current shadow-regime payload is explicitly non-authoritative (`decision_input = False`)
- future runtime-observability work would need to preserve this additive/non-authoritative status unless separately escalated and re-approved

### Boundary D — Paper operations are already governed as operations, not just code

Visible in:

- `scripts/paper_trading_runner.py`
- `docs/paper_trading/runner_deployment.md`
- `docs/paper_trading/phase3_runbook.md`

Interpretation:

- paper-adjacent work carries operational burden, not just implementation burden
- that makes paper-shadow a later lane even if the code seam itself is technically visible now

This section inventories currently visible authority surfaces already present in the repository. It does not adopt a runtime design, approve a merge path, authorize decision-input changes, or define paper-operation procedure for future implementation work.

## Artifact-home inventory

The repository currently suggests three useful classes of non-authoritative artifact homes:

1. `results/**`
   - suitable for machine-readable summaries and observational outputs
2. `artifacts/**`
   - suitable for richer retained bundles, ledgers, or supporting payloads
3. `logs/**`
   - suitable for operational logs and runner state in existing paper-trading flows

Inventory conclusion:

- early future SCPE RI lanes should prefer `results/**` or `artifacts/**` for non-authoritative observational outputs
- they should avoid `config/**` and any runtime-authority path
- paper-runner state/log paths should not be treated as generic artifact homes for earlier backtest/runtime-observability lanes

Paths under `results/**`, `artifacts/**`, and `logs/**` are listed only as observed repository artifact-home classes. No storage schema, naming convention, retention policy, or adoption decision is established by this document.

This note does **not** choose exact homes for any future SCPE RI output. It only inventories the visible separation pattern.

## Compatibility interpretation

### What appears compatible with an early future lane

Most compatible with an early future lane:

- backtest-local passive hook composition
- explicitly opt-in shadow capture
- non-authoritative summary artifacts outside runtime config
- parity/no-drift framing

Compatible later, but not first:

- additive runtime-observability that remains outside decision authority
- runtime-adjacent summary emission that does not mutate config or responses by implication

Least compatible with an early lane:

- runtime-config mutation
- champion or candidate writeback
- paper-runner order-path adjacency
- anything that reads like cutover, readiness, or promotion

## Recommended sequencing interpretation

This inventory supports the following fail-closed interpretation of the roadmap:

1. any future implementation-adjacent work should begin with a separate packeted assessment of whether a **shadow-only backtest lane** is admissible
2. a **runtime-observability lane** should remain later and separately justified
3. a **paper-shadow lane** should remain later still because it is operationally closer to execution
4. any **behavior-changing lane** remains explicitly later than all of the above
5. runtime-config/champion/default-authority surfaces should remain out of scope until a much stricter lane is explicitly opened

This is not approval. It is only a sequencing interpretation from the currently visible seams.

## Stop conditions for future packet design

A future packet built from this inventory should stop immediately if it would require any of the following in its first implementation-adjacent lane:

- mutation of runtime default authority
- mutation of champion merge semantics
- mutation of decision outputs in `/strategy/evaluate`
- activation through implicit config rather than explicit opt-in
- artifact placement in runtime-authoritative paths
- paper/live operational semantics without a dedicated operational lane
- any wording that claims readiness, cutover, or promotion

## Bottom line

The repository does expose real seams for future SCPE RI integration work, but they are not equal in governance distance.

- the **backtest shadow seam** is the smallest currently visible implementation-adjacent seam in this inventory snapshot
- the **runtime evaluation seam** is real but closer to authority, so it belongs later
- the **runtime config-authority seam** is primarily a boundary to avoid early
- the **paper-runner seam** is visible but operationally too close to execution for an early lane

So the correct next move after this inventory is still fail-closed:

- if a future implementation-adjacent step is proposed at all, the smallest currently visible seam to evaluate first is the backtest-shadow seam, and that evaluation would still require a separate packet, separate approval, and separate verification.

Separate future packeting remains mandatory for every implementation-adjacent step identified here. Nothing in this document authorizes code change, config change, runtime instrumentation, paper deployment, behavior change, readiness, cutover, or promotion.
