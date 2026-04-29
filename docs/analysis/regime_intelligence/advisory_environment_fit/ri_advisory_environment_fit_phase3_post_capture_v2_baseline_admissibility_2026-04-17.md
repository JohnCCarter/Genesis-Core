# RI advisory environment-fit — Phase 3 post-capture-v2 baseline admissibility

This memo is docs-only and fail-closed.
It decides what kind of deterministic Phase 3 baseline is now admissible after the Phase C evidence-bundle capture v2 run.

Governance packet for the capture source: `docs/decisions/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_phaseC_evidence_capture_v2_packet_2026-04-17.md`

## Source surface used

This memo uses only already tracked surfaces:

- `plan/ri_advisory_environment_fit_roadmap_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase2_label_taxonomy_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_direct_baseline_admissibility_2026-04-16.md`
- `docs/analysis/regime_intelligence/advisory_environment_fit/ri_advisory_environment_fit_phase3_post_capture_admissibility_2026-04-16.md`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/capture_summary.json`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/entry_rows.ndjson`
- `results/research/ri_advisory_environment_fit/phase3_phasec_evidence_capture_v2_2026-04-17/closeout.md`

## Decision question

After the Phase C evidence-bundle capture v2 run, may the lane now open a deterministic Phase 3 baseline?

## Short answer

**Yes — but only as a bounded partial baseline.**

A full RI role-map baseline is still not honest on this evidence surface.
A limited deterministic baseline focused on **clarity / recency / reliability** is now admissible.
Admissibility in this slice is limited to a bounded partial baseline that emits only `decision_reliability_score` and a proxy `transition_risk_score`, both derived solely from Phase 2-admissible pre-entry fields.
Capture v2 does **not** admit use of `shadow_regime_*`, `authoritative_regime`, or `ri_risk_state_*` as evidentiary inputs for this slice, and `market_fit_score` remains deferred pending a separate admissibility review.

## What changed versus the earlier blocker

The earlier fixed-carrier capture was blocked mainly because the realized-entry evidence surface was too thin:

- no usable clarity coverage
- no disagreement variation
- no transition-multiplier variation

The Phase C evidence-bundle capture v2 materially changed that picture.

### Newly usable evidence

The new capture produced a clean, bounded RI evidence table with:

- `146` matched realized positions
- `0` unmatched realized positions
- `146 / 146` rows with `ri_clarity_enabled = true`
- `0` missing `ri_clarity_score` rows
- `146` unique `ri_clarity_raw` values
- `12` unique `ri_clarity_score` values
- `138` unique `bars_since_regime_change` values
- `146` unique `proba_edge` values
- `13` unique `decision_size` values
- unchanged evidence-bundle hash before/after the run
- containment `PASS` with no writes outside the approved results files

That is enough pre-entry variation to support a narrow deterministic score family built from already admissible Phase 2 scoring-time inputs.

## What is still degenerate or absent

The same capture also shows that several hoped-for RI axes are still flat or absent on realized entries:

- `shadow_regime_mismatch = 0` rows
- `ri_risk_state_transition_mult` absent on all rows
- `ri_risk_state_drawdown_mult` absent on all rows
- `ri_risk_state_multiplier = 1.0` on all rows
- `authority_mode = regime_module` on all rows
- `authoritative_regime = balanced` on all rows
- `shadow_regime` empty on all rows

This matters because the roadmap and Phase 2 taxonomy explicitly require honest handling of:

- transition-risk context
- authority disagreement
- ambiguity / low-reliability states

The capture now supports some of that space, but not all of it.

## Admissibility decision

### 1. Full role-map baseline is still **not** admissible

A full deterministic RI role-map baseline that claims to cover:

- supportive vs hostile market fit
- transition-risk handling
- disagreement / ambiguity handling

would currently overclaim.

Why:

1. disagreement-state evidence is still absent on realized rows
2. transition-multiplier evidence is still absent on realized rows
3. regime-role variation is still flat on this surface
4. forcing a full three-output map now would mostly be fabricating branches that the current evidence does not actually exercise

That would violate the lane’s own evidence discipline.

### 2. A bounded **partial baseline** is admissible

A narrow deterministic baseline is now admissible if it stays explicitly limited to the surfaces that do vary.

That next slice may use only pre-entry fields already allowed by Phase 2, especially:

- `ri_clarity_score`
- `ri_clarity_raw`
- `bars_since_regime_change`
- probability / confidence context already available pre-entry
- bounded sizing/context descriptors already available at entry time

The honest interpretation is:

- clarity can now support a **decision-reliability** axis
- regime-change recency can now support only a bounded **transition-proximity proxy** axis
- outcome labels may be evaluated ex post only where the Phase 2 supportive / hostile label contract can actually be materialized without substituting raw `total_pnl` for the required bounded label surface
- disagreement-aware or full market-role logic should remain deferred until the evidence surface actually contains those states

## Remaining evaluation-gap note

Capture v2 materially improved the **input** surface.
It did not automatically materialize every Phase 2 **evaluation** surface.

In particular, the Phase 2 supportive / hostile taxonomy was defined against a bounded outcome-label contract that references more than raw realized outcome columns alone.
That means the next slice must verify one of the following before claiming full supportive / hostile evaluation coverage:

1. the exact bounded label surface can be joined onto the capture-v2 evidence rows, or
2. a separate admissibility memo explicitly approves a narrower provisional outcome-proxy evaluation surface

What the next slice may **not** do is silently replace the bounded Phase 2 label contract with raw `total_pnl` sign alone.

## Exact next admissible step

The next admissible Phase 3 slice is **not** a full RI advisory score family.
It is one bounded deterministic partial-baseline slice that does only the following:

1. define a deterministic `decision_reliability_score` from clarity + pre-entry confidence structure
2. define a deterministic proxy `transition_risk_score` from regime-change recency and clarity degradation only
3. verify whether the exact Phase 2 supportive / hostile label surface is materialized on this evidence table; if not, stop and record the label-join gap explicitly
4. evaluate the bounded scores only against the subset of the Phase 2 taxonomy that is honestly materialized on the evidence surface
5. report explicit failure classes, especially `2025` contradiction behavior

### What that next slice should not do

- no use of `shadow_regime_*`, `authoritative_regime`, or `ri_risk_state_*` as evidentiary inputs on this surface
- no shadow/disagreement branch logic beyond reporting zero coverage
- no transition-multiplier logic, because that surface is absent here
- no claim that `market_fit_score` is solved yet
- no runtime integration
- no ML comparator yet
- no post-entry leakage into score inputs

## Consequence for the roadmap

The roadmap should now be interpreted as:

- Phase 1: complete
- Phase 2: complete
- direct full Phase 3: still blocked
- bounded partial Phase 3: now admissible

That is meaningful progress.
The lane now has enough RI-native evidence to test whether a narrow deterministic baseline is useful, without pretending that the whole RI role map is already observable.

## Bottom line

Capture v2 succeeded at the thing it actually needed to do:

- it replaced the earlier `no-clarity / thin-carrier` blocker with a richer, admissible RI evidence table

But it did **not** magically produce full disagreement and transition-role coverage.

So the honest verdict is:

- **full Phase 3 role-map baseline remains blocked**
- **bounded clarity/recency partial baseline is now admissible**

That is the next natural step for the lane.
