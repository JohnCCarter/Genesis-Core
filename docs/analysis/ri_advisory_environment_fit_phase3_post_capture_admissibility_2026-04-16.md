# RI advisory environment-fit — Phase 3 post-capture admissibility

This memo is docs-only and fail-closed.
It closes the newly completed fixed-carrier RI evidence-capture slice by deciding whether that evidence surface is now sufficient to open a direct deterministic advisory-baseline slice.

Governance packet: `docs/decisions/ri_advisory_environment_fit_phase3_post_capture_admissibility_packet_2026-04-16.md`

## Source surface used

This memo uses only the just-created bounded evidence-capture outputs and their governing packet:

- `docs/decisions/ri_advisory_environment_fit_phase3_ri_evidence_capture_packet_2026-04-16.md`
- `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/capture_summary.json`
- `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/manifest.json`
- `results/research/ri_advisory_environment_fit/phase3_ri_evidence_capture_2026-04-16/closeout.md`
- bounded key-column distribution summary from the captured `entry_rows.ndjson`

## Decision question

Does the fixed-carrier RI evidence table now provide enough RI observability variation to open a direct deterministic advisory-baseline slice?

## Short answer

**No — not yet.**

The capture slice succeeded operationally, but the fixed RI carrier is still too thin as a baseline surface.

## What the capture slice proved

### 1. The slice is operationally clean

The capture slice itself passed the important hygiene checks:

- the carrier hash stayed unchanged before and after the run
- containment passed with no unexpected writes outside the approved artifact set
- the deterministic join contract succeeded with:
  - `167` matched realized positions
  - `0` unmatched realized positions
  - a fixed join key of `normalize(entry_time)|side`

So the question is no longer “can we capture RI evidence cleanly?”

That answer is now:

- **yes, operationally**

### 2. The problem is now the evidence surface, not the capture mechanism

The same capture slice also produced the more important scientific answer:

- the fixed carrier does **not** expose enough informative RI variation on the realized-entry surface to justify a direct baseline implementation

That distinction matters.
The blocker moved from:

- “we do not yet have an RI evidence table”

to:

- “we now have one, but the chosen carrier still under-identifies the target RI advisory dimensions”

## What is missing or degenerate on the fixed carrier

### 3. Clarity is completely absent on the captured surface

The capture summary reports:

- `carrier_enabled_rows = 0`
- `runtime_enabled_rows = 0`
- `missing ri_clarity_score rows = 167`

So the fixed carrier gives the baseline lane **no realized-entry clarity coverage at all**.

This is not a small nuisance.
Clarity was one of the most important candidate ingredients for:

- `decision_reliability_score`

At this point the lane still cannot honestly claim that the fixed carrier exposes that dimension.

### 4. Shadow disagreement is degenerate on the captured realized surface

The bounded key-column summary shows:

- `shadow_regime_mismatch` has exactly one observed value
- that value is always `false`

So the fixed carrier provides no realized-entry variation for:

- authoritative-vs-shadow disagreement

That means one of the most important RI-specific ambiguity / disagreement surfaces is present in schema, but effectively absent in evidence for this carrier and window.

### 5. Transition-risk multiplier is also degenerate on the realized surface

The bounded key-column summary shows:

- `ri_risk_state_transition_mult` has exactly one observed value
- that value is always `1.0`

So the explicit transition guard does not contribute usable variation on the realized-entry evidence rows for this carrier.

There is still some movement in:

- `bars_since_regime_change`

But by itself that is not enough to claim that the lane has a real captured transition-risk surface in the form originally intended.

## What remains informative

### 6. Some context fields do vary

The capture is not empty.
At minimum, it preserves useful variation in:

- probability / confidence context
- `bars_since_regime_change`
- realized outcome columns recorded as raw evidence only
- entry timing and side on an RI-family surface

That is useful.
But it is **not** the same as saying the capture now spans the intended RI advisory dimensions well enough.

## Admissibility decision

Direct deterministic baseline implementation is still:

- **blocked / not admissible now**

Reason, now stated more precisely than before:

1. the RI evidence table exists and is clean
2. but the fixed carrier supplies zero clarity coverage
3. the realized-entry surface shows no disagreement variation
4. the realized-entry surface shows no transition-multiplier variation
5. only partial proxy movement remains, mainly `bars_since_regime_change` plus generic probability/confidence context

That is not yet a strong enough RI-only surface for the roadmap’s intended target outputs:

- `transition_risk_score`
- `decision_reliability_score`
- `market_fit_score`

## Exact next admissible step

The next admissible move is **not** baseline implementation.

The narrow next step should be one of these, in order of honesty:

1. **bounded RI carrier-adequacy / observability-enablement slice**
   - decide whether there is an admissible RI research carrier that exposes clarity and non-degenerate disagreement / transition evidence without violating `NO BEHAVIOR CHANGE`
   - if yes, open a new bounded capture slice on that surface
2. **lane close decision**
   - if no such admissible carrier exists without crossing into behavior-change territory, stop the lane rather than fabricate an advisory baseline from under-identified evidence

## What should not happen next

- no direct score authoring from this carrier
- no rebranding of raw outcome columns as labels
- no cross-family fallback to legacy evidence
- no ad hoc carrier mutation hidden as “just observability”
- no premature ML comparator lane

## Bottom line

The fixed-carrier RI evidence-capture slice succeeded technically but failed to unlock direct Phase 3.

That is still progress.
It means the roadmap has now isolated the real blocker precisely:

- **the capture mechanism is admissible**
- **the chosen fixed RI carrier is still not rich enough for direct baseline authoring**

So the honest state after capture is:

- **direct baseline remains blocked**
- **next admissible step is carrier adequacy / observability enablement review, or lane closeout if that cannot be done cleanly**
