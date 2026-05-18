# Next phase verkstad queue

Date: 2026-05-15
Branch: `feature/evidence-closeout-pilot`
Status: `initial queue closed / successor phase closed / docs-only / non-authorizing`

> Queue sync note (2026-05-18): This file remains a record of the 2026-05-15 queue state and its
> later closeout annotations. Entries below may be annotated as later consumed or narrowed by
> cited follow-up work, but this list is not the current execution queue or current priority order
> on branch state after the later 2026-05-18 closeouts and broader historical refresh.

This document records the initial post-premortem execution queue after the completed premortem closeout and evidence-manifest boundary work. The initial six-slice queue below is now historical, and the successor phase reopened from the branch premortem reading is now also historical and closed later in this document. This remains a sequencing artifact in `RESEARCH`; it grants no runtime, config-authority, paper/live, promotion, or champion authority by itself.

## Mode and lane

- **Mode:** `RESEARCH` — source: `docs/governance_mode.md` via `feature/* -> RESEARCH`
- **Lane:** `Research-evidence` for queue framing; future slices may open in `tooling`, `docs`, or `runtime-integration` lanes depending on the exact candidate
- **Base SHA:** `59c010c104903e49552608c15815aba1b9fa8fc3`

## Purpose

This queue answers one narrow question only:

- what is the next practical workshop loop now that the premortem plan and the evidence-manifest generalization decision are complete?

## Working loop

The operating loop for this phase is intentionally simple:

1. **Välj nästa enskilda risk/fynd att ta ned**
2. **Öppna en bounded slice**
3. **Implementera + verifiera**
4. **Repetera**

Interpretation boundary:

- one risk at a time
- one bounded slice at a time
- no framework jumps by convenience
- no pause between slices for ceremony when the next admissible step is already clear

## Current phase status

Already completed before this queue:

- premortem closeout
- runtime-config clarification line and bounded API/error-semantics follow-up
- decision-gate finite-numeric hardening
- EV-gate non-finite hardening
- execution-proxy manifest closeout
- edge-origin manifest closeout
- evidence-manifest candidate audit
- evidence-manifest generalization boundary (`defer generalization`)

That means this queue starts **after** the earlier premortem candidate set is closed.

## Current prioritized queue

### Slice 1 — editor-worker customization drift inventory

- **Status:** `selected and completed in this slice`
- **Why it comes first:** the premortem ranked agent/governance sprawl and stale instruction interpretation as a real operational risk, and this is the smallest low-risk way to reduce future orchestration mistakes
- **Artifact:** `docs/analysis/diagnostics/editor_worker_customization_drift_inventory_2026-05-15.md`
- **Outcome target:** clarify which customization surfaces are repo-local vs Claude-local support surfaces, confirm that `QUICK_REF` belongs in `.claude/`, and record what must be explicit in future worker dispatch

### Slice 2 — decision-influencing artifact replay smoke candidate selection

- **Status:** `selected and completed in this slice`
- **Why it is next:** the premortem still ranks determinism illusion from artifact/cache/env drift as a top failure mode, and the next useful move was to pick one decision-influencing artifact chain for a clean-checkout replay smoke candidate
- **Artifact(s):**
  - `docs/analysis/diagnostics/decision_influencing_replay_smoke_candidate_selection_2026-05-15.md`
  - `docs/decisions/governance/execution_proxy_clean_checkout_replay_smoke_boundary_packet_2026-05-15.md`
- **Outcome target:** select `execution_proxy_evidence` as the first bounded replay-smoke candidate and lock the current fixture-containment gap as a separate follow-up boundary instead of jumping straight to implementation

### Slice 3 — execution-proxy fixture containment packet

- **Status:** `selected and completed in this slice`
- **Why it is next:** the candidate-selection slice showed that the current `execution_proxy_evidence` input trace is locally present but ignored/untracked, so a clean-checkout replay smoke could not yet be implemented honestly from the tracked repo surface
- **Artifact:** `docs/decisions/governance/execution_proxy_fixture_containment_packet_2026-05-15.md`
- **Outcome target:** choose one exact commit-safe carrier strategy and keep the next implementation slice bounded to a tracked minimal fixture rather than results-root tracking or bundle-first expansion

### Slice 4 — execution-proxy tracked-fixture smoke implementation

- **Status:** `selected and completed in this slice`
- **Why it is next:** the carrier strategy became explicit, so the next smallest implementation move was to add one tracked minimal fixture and focused smoke coverage for `execution_proxy_evidence`
- **Artifact(s):**
  - `registry/fixtures/execution_proxy_baseline_current_minimal.json`
  - `tests/backtest/test_execution_proxy_evidence.py`
- **Outcome target:** prove that `execution_proxy_evidence` can run and reproduce deterministic outputs from one tracked commit-safe fixture without relying on ignored `results/research/**` inputs

### Slice 5 — transport/falsifier gate for RI/policy-router candidate promotion

- **Status:** `selected and completed in this slice`
- **Why it remains important:** the premortem explicitly warns against local-pocket overfitting and implied runtime-candidate promotion from exact-window research
- **Artifact:** `docs/decisions/governance/ri_policy_router_d1_transport_falsifier_evidence_boundary_packet_2026-05-15.md`
- **Outcome target:** record that the current D1 transport/falsifier chain remains an evidence-boundary line only and that no runtime, candidate-promotion, or config authority follows from Slice 5

### Slice 6 — paper-shadow / live-paper isolation seam check

- **Status:** `selected and completed in this slice`
- **Why it stays in queue:** paper/live boundary regression remains low-frequency but very high impact in the premortem ranking
- **Artifact:** `docs/decisions/scpe_ri_v1/scpe_ri_v1_paper_shadow_live_paper_isolation_boundary_packet_2026-05-15.md`
- **Outcome target:** record the currently cited RI paper-shadow vs live-paper isolation seam as a docs-only boundary and keep operational, readiness, deployment, and runtime semantics out of scope

## Selection rule for the next slice

When this queue advances, the next admissible slice should be the smallest candidate that satisfies all of the following:

- directly reduces one ranked premortem failure mode
- has an explicit Scope IN/OUT
- has a clear verification stack
- does not require a framework-first abstraction
- does not silently cross into stricter authority zones without reopening governance path

## What changed now

- the next phase is now framed as a workshop queue rather than as unfinished premortem work
- the first three post-closeout slices were selected and completed as bounded docs-only steps
- the fourth post-closeout slice landed as a bounded fixture + focused-test implementation for `execution_proxy_evidence`
- the fifth post-closeout slice closed the current RI/policy-router D1 transport/falsifier line as a docs-only evidence boundary without opening candidate-promotion semantics
- the sixth post-closeout slice closed the current SCPE RI paper-shadow / live-paper seam as a docs-only isolation boundary record without opening operational or readiness semantics
- the replay-smoke line is now narrowed to `execution_proxy_evidence`, and its carrier strategy is fixed to a tracked minimal fixture rather than ignored results inputs
- the initial six-slice workshop queue is now exhausted; any further slice selection should be reopened explicitly rather than inherited from this document
- the seventh post-closeout slice closed the current `execution_proxy_evidence` replay wording at `fixture-level` and recorded explicit prerequisites before `historical-trace-level` or `full-chain clean-checkout-level` wording could be used
- the eighth post-closeout slice chose one tracked minimal fixture pair under `registry/fixtures/` as the first commit-safe carrier strategy for `edge_origin_isolation` and kept ignored results roots out of replay portability claims
- the ninth post-closeout slice narrowed the SCPE-derived line to the exact `defensive_probe` two-row selected-defensive pocket as primary carrier instead of inheriting confidence from the broader replay root
- the tenth post-closeout slice tightened the mandatory minimum claim-header envelope for decision-influencing evidence in the existing template/runbook surfaces and made `Input carrier` explicit
- the eleventh post-closeout slice inventoried four representative ignored/local-only dependency families and ranked the next admissible carrier follow-ups behind them
- the twelfth post-closeout slice closed the current successor queue by defining one minimal same-slice freshness rule for queue truth, touched artifact framing, and touched next-step prose
- future work is ordered by risk-reduction payoff, not by nearby file proximity

## What did not change

- no runtime behavior
- no config-authority semantics
- no strategy/backtest behavior
- no paper/live semantics
- no broader replay authority from Slices 7-9
- no new SSOT or universal note mandate from Slice 10
- no carrier implementation or runtime authority from Slice 11
- no new status framework or archive-wide rewrite from Slice 12
- no promotion or readiness stance
- no runtime, candidate-promotion, or config authority from Slice 5
- no runtime, deployment, readiness, or paper/live authority from Slice 6

## Bottom line

The next phase is now explicit: reduce one real risk at a time through bounded slices, starting with orchestration/customization drift, then replay-smoke candidate selection, then the `execution_proxy_evidence` fixture-containment decision, then one landed tracked-fixture smoke implementation, then a docs-only RI/policy-router transport/falsifier evidence-boundary closeout, and finally a docs-only SCPE RI paper-shadow / live-paper isolation boundary record. The initial six-slice queue is now closed; any next slice should be selected explicitly rather than assumed from this document.

## Successor phase reopened from the branch premortem

The initial six-slice queue reduced real risk, but the next branch-level failure pattern is now clearer: narrow reproducibility wins can still be remembered broader than they prove.

The successor phase therefore stays in `RESEARCH`, remains docs/governance/tooling-first by default, and focuses on preventing five specific drifts:

- `execution_proxy_evidence` must not be overgeneralized from one tracked fixture-smoke into a repo-wide clean-checkout replay claim
- docs-only and evidence-only notes must not drift into implementation or approval authority
- RI/policy-router exact-window findings must remain behind transport/falsifier gates
- paper/live semantics must remain separate from replay/evidence-closeout semantics
- queue/status freshness must be treated as a risk control rather than as optional cosmetics

### Carry-forward constraints for the successor phase

- do not describe the current `execution_proxy_evidence` line as anything stronger than a bounded tracked-fixture smoke unless a later packet proves the stronger claim explicitly
- do not treat docs-only packets, diagnostics notes, or evidence summaries as implementation authority by citation drift
- do not reopen RI/policy-router candidate language without a fresh transport/falsifier packet
- do not cite replay or evidence-closeout work as paper/live readiness or operations safety
- update queue/status text whenever a slice changes what the actual next admissible step is

### Replay claim labels required in this phase

- **`fixture-level`**
  - one tracked compact carrier proves one bounded script/test path only
  - current `execution_proxy_evidence` proof remains here unless later evidence says otherwise
- **`historical-trace-level`**
  - the original historical trace or equivalent retained carrier is tracked and reproducibly rerun for the named claim-bearing chain
- **`full-chain clean-checkout-level`**
  - a clean checkout can regenerate the full named claim-bearing chain from tracked inputs under an explicitly stated envelope

These labels are interpretation discipline only. They do **not** authorize stronger replay claims by themselves.

## Successor prioritized queue

### Slice 7 — execution-proxy replay claim-level boundary

- **Status:** `selected and completed in this slice`
- **Why it came first:** the highest current branch risk was vocabulary compression from one tracked fixture-smoke into “clean-checkout replay solved”
- **Artifact:** `docs/decisions/governance/execution_proxy_replay_claim_level_boundary_packet_2026-05-15.md`
- **Outcome target:** record that the current `execution_proxy_evidence` line remains `fixture-level` only, define the minimum prerequisites before `historical-trace-level` or `full-chain clean-checkout-level` wording could be used, and keep broader replay authority out of scope

### Slice 8 — edge-origin isolation carrier decision

- **Status:** `selected and completed in this slice`
- **Why it came next:** `edge_origin_isolation` was the next obvious claim-bearing artifact chain that could inherit replay confidence without its own commit-safe carrier decision
- **Artifact:** `docs/decisions/governance/edge_origin_isolation_carrier_decision_packet_2026-05-15.md`
- **Outcome target:** choose one tracked minimal fixture pair under `registry/fixtures/` as the first commit-safe carrier strategy for `edge_origin_isolation` and keep ignored results roots and summary-only citations out of replay portability authority

### Slice 9 — SCPE replay-surface carrier decision

- **Status:** `selected and completed in this slice`
- **Why it came next:** SCPE replay-style surfaces could easily inherit replay confidence from unrelated artifact chains unless they received their own exact carrier boundary
- **Artifact:** `docs/decisions/governance/scpe_defensive_probe_carrier_decision_packet_2026-05-15.md`
- **Outcome target:** choose the exact `defensive_probe` two-row selected-defensive pocket as the first SCPE-derived commit-safe carrier and keep broader replay-root, runtime, paper/live, and integration semantics out of scope

### Slice 10 — decision-influencing claim-header discipline

- **Status:** `selected and completed in this slice`
- **Why it came next:** reproducibility claims stayed fragile as long as the evidence envelope could still be remembered informally instead of being named directly in every decision-influencing note
- **Artifact(s):**
  - `docs/decisions/governance/decision_influencing_claim_header_boundary_packet_2026-05-15.md`
  - `docs/governance/templates/evidence_claim_header.md`
  - `docs/governance/runbooks/evidence_claim_adoption.md`
- **Outcome target:** define the compact mandatory minimum for decision-influencing evidence in the existing template/runbook surfaces, including explicit `Input carrier`, while keeping adoption trigger-based rather than universal

### Slice 11 — ignored-artifact dependency inventory

- **Status:** `selected and completed in this slice`
- **Why it came next:** the branch had reduced one ignored-input dependency, but several later claim-bearing chains still relied on ignored `results/**`, caches, or workstation-local artifacts
- **Artifact:** `docs/analysis/diagnostics/ignored_artifact_dependency_inventory_2026-05-15.md`
- **Outcome target:** inventory four representative decision-influencing dependency families that still depend on ignored or local-only inputs and rank the next admissible carrier follow-ups behind them

### Slice 12 — queue/status freshness guard

- **Status:** `selected and completed in this slice`
- **Why it came next:** stale “next step” text remained a real steering hazard once multiple packets and diagnostics notes existed in parallel
- **Artifact:** `docs/decisions/governance/queue_status_freshness_guard_packet_2026-05-15.md`
- **Outcome target:** define the minimal same-slice freshness bundle for queue truth, touched artifact framing, and touched next-step prose so stale sequencing text cannot silently take control

## Later explicit reopen after successor closure

### Slice 13 — edge-origin manifest-pilot portability boundary

- **Status:** `selected and completed in this slice`
- **Why it came next:** after the later SCPE, router-replay, and volatility closeouts, the smallest remaining dependency/overclaim seam on this branch was the current manifest-backed `edge_origin_isolation` claim surface above its already-separated future fixture-pair carrier decision
- **Artifact:** `docs/decisions/governance/edge_origin_isolation_manifest_pilot_portability_boundary_packet_2026-05-18.md`
- **Outcome target:** pin the current manifest-pilot `edge_origin_isolation` surface to `same-local-checkout only`, keep stronger portability wording out of bounds, and preserve the future tracked-fixture carrier path as separately bounded

### Slice 14 — SCPE shadow-backtest execution-summary portability boundary

- **Status:** `selected and completed in this slice`
- **Why it came next:** after the edge-origin closeout, the smallest remaining runtime-adjacent inheritance seam was the historical 2026-04-21 SCPE shadow-backtest execution-summary surface, which already denied runtime/paper/readiness authority but still lacked a current-state portability label
- **Artifact:** `docs/decisions/scpe_ri_v1/scpe_ri_v1_shadow_backtest_execution_summary_current_state_portability_boundary_packet_2026-05-18.md`
- **Outcome target:** classify only the 2026-04-21 execution-summary surface as `same-local-checkout only`, keep the historical summary untouched, and leave the separate paper-shadow/live-paper isolation packet separate and unchanged

## Successor selection rule

When the successor phase advances, the next admissible slice should prefer the smallest move that:

- reduces overclaim or authority drift before expanding replay scope
- chooses a carrier boundary before making a stronger portability claim
- keeps RI/policy-router candidate language below transport/falsifier proof
- keeps paper/live semantics separate from replay semantics
- leaves historical packets clearly historical once a newer queue truth exists

## Successor bottom line

The initial six-slice queue is closed, and the successor phase is now closed as well. This successor phase landed a claim-discipline slice, two separate carrier decisions, the claim-header minimum for decision-influencing evidence, one bounded ignored-artifact dependency inventory, and a minimal freshness guard for queue truth. Any further slice should now be reopened explicitly from the latest branch state rather than inherited from stale “next” prose in this document.
