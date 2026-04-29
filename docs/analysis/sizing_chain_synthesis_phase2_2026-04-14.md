# Sizing-chain synthesis — Phase 2

This note is observational only.
It synthesizes the current sizing-related evidence so the repository can decide whether the sizing chain materially narrows Genesis or whether it still remains subordinate to the broader `emergent_system_behavior` explanation.

Governance packet: `docs/decisions/sizing_chain_synthesis_phase2_packet_2026-04-14.md`

## Source surface used

This memo uses only already tracked or already generated evidence:

- `results/research/fa_v2_adaptation_off/survival_boundary_summary.md`
- `docs/decisions/survival_boundary_phase4_packet_2026-04-01.md`
- `plan/feature_attribution_post_phase14_reactivation_roadmap_2026-04-02.md`
- `docs/analysis/feature_attribution_post_phase14_rebaseline_reconciliation_2026-04-02.md`
- `results/research/feature_attribution_v1/reports/fa_v1_full_admitted_units_synthesis_20260331_01.md`
- `results/research/feature_attribution_v1/reports/fa_v1_cluster_implementation_handoff_20260331_01.md`
- `results/research/fa_v2_adaptation_off/EDGE_ORIGIN_REPORT.md`

## Why this slice was needed

After Phase 1, execution was left unresolved but bounded.
The strongest remaining live story on the current executable route is therefore the sizing path.

That still does **not** mean “sizing is the whole edge.”
This slice exists to decide whether the sizing evidence is strong enough to beat the current broader hypothesis, or whether it should instead be recorded as an important subsystem inside that broader hypothesis.

## What the sizing chain already shows

Two different kinds of sizing evidence now exist and must not be conflated.

### 1. Survival-boundary evidence

The Phase 4 survival-boundary lane established an exact observational preservation boundary:

- final selected rule: `ALL(base_size > 0)`
- coverage: `100%`
- accuracy: `100%`
- combined survivors: `626`
- combined collapses: `3598`

That result is strong, but its meaning is narrow:

- it proves that positive `base_size` is a deterministic preservation boundary on the locked sizing-eligible cohort
- it does **not** prove that `base_size` is the full source of edge
- it does **not** prove that the sizing chain is an exclusive mechanism

So the survival result is preservation authority, not full edge authority.

### 2. Current-route cluster activity evidence

The current executable-route marginal ranking shows that the most active live surfaces are heavily concentrated in the sizing path:

1. `Volatility sizing cluster` — `+0.9196103062`
2. `Regime sizing multiplier cluster` — `+0.6588756573`
3. `Signal-adaptation threshold cluster` — `+0.3948827769`
4. `HTF regime sizing multiplier cluster` — `+0.3152162047`

From the carried-forward feature-attribution synthesis:

- `Volatility sizing cluster` is the strongest current-route mover, but neutralization improves upside and PF while worsening DD materially
- `Regime sizing multiplier cluster` is clearly live, but remains mixed rather than cleanly positive or negative
- `HTF regime sizing multiplier cluster` is also live, but less decisive
- `Signal-adaptation threshold cluster` is the clearest harmful current-route surface

So the sizing story is clearly live.
But it is not automatically clean, isolated, or edge-exclusive.

## Implementation interaction context

The admitted sizing surfaces do not act independently in runtime shape.
The cluster-implementation handoff records that:

- regime sizing
- HTF regime sizing
- volatility sizing

are multiplicative contributors inside one combined size path.

That same handoff also makes two important points:

1. the sizing factors are multiplicative rather than clean one-at-a-time toggles
2. the final size path is also affected by neighboring non-admitted influences such as RI, clarity, and risk-state scaling

That means even when the sizing path is clearly active, some of the observed effect remains structurally confounded.

## Phase 2 driver ladder

Using the packet-authorized label set, the current best sizing-chain ladder is:

| Surface                                                                 | Label                      | Why                                                                                                                                                      |
| ----------------------------------------------------------------------- | -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `base_size > 0` survival boundary                                       | `direct driver candidate`  | It is the exact observational preservation boundary for survivor vs collapse rows, but only on the sizing-eligible cohort and not as proof of edge.      |
| `Volatility sizing cluster`                                             | `risk-shaping contributor` | It is the strongest current-route mover, but the effect is trade-off shaped: removing it improves return and PF while worsening DD materially.           |
| `Regime sizing multiplier cluster`                                      | `confounded mover`         | It is clearly live, but the observed effect remains mixed and sits inside a shared multiplicative size path rather than as a clean standalone mechanism. |
| `HTF regime sizing multiplier cluster`                                  | `confounded mover`         | It is live but less decisive than the stronger sizing surfaces and remains part of the same multiplicative interaction ladder.                           |
| `Signal-adaptation threshold cluster`                                   | `harmful surface`          | On the current route it is the clearest harmful surface in plain-language terms, improving return and PF when neutralized, with slightly worse DD.       |
| `Minimum-edge / Hysteresis / Cooldown / HTF block / LTF override seams` | `inert on current route`   | On the current executable route they show no measurable marginal delta in the carried-forward synthesis.                                                 |

## What this ladder does and does not mean

### What it does mean

- the sizing path is not a side note; it is one of the strongest live subsystems in the current route
- survival itself is governed by a deterministic sizing boundary on the locked cohort
- the strongest live positive mover on the current route sits in the sizing family
- the clearest harmful surface also sits adjacent to the threshold/sizing handoff story rather than in a separate validated signal-edge story

### What it does not mean

- it does not mean the sizing chain is a proved standalone edge mechanism
- it does not mean `base_size > 0` is the whole explanation for Genesis
- it does not mean the multiplicative sizing clusters have been cleanly separated from all neighboring confounders
- it does not beat the current broader system-level conclusion by itself

## Verdict

**Packet-authorized conclusion:** `sizing chain matters but does not beat emergent_system_behavior`

Why this is the most honest conclusion:

- `sizing chain materially narrows Genesis` would go too far because the best current sizing evidence still stops at preservation/risk-shaping and mixed cluster-marginal behavior
- the strongest single current-route mover (`Volatility sizing cluster`) is still best described as a protective or risk-shaping contributor, not a clean standalone mechanism
- the survival boundary is exact, but it is explicitly an observational preservation boundary rather than proof of edge
- the interaction ladder is real, but it remains multiplicative and partially confounded by neighboring non-admitted surfaces
- the broader Phase 14 synthesis still stands: no carried-forward admitted-unit finding yet downgrades `emergent_system_behavior` as the best-supported broader explanation

## What this slice changes

This slice does not replace the current broader hypothesis.
It does something narrower and still valuable:

- it upgrades the sizing path from “one candidate among many” to “the strongest bounded subsystem story after execution stalls”
- it clarifies that Genesis is not best described as signal-edge-first on the current surface
- it shows that preservation and risk-shaping are more central to the current evidence than a clean standalone predictive mechanism

## Consequence for the master roadmap

The roadmap consequence is:

1. keep `emergent_system_behavior` as the current best-supported broader hypothesis
2. carry forward that the sizing chain is the strongest bounded subsystem story currently available
3. continue to **Phase 3 — residual drift-separation** rather than reopening more proxy-only execution work or pretending the sizing path is already the exclusive answer

## What can now be said more precisely

- Genesis currently looks more like a preserved, risk-shaped system than a validated signal-edge machine
- the sizing path governs survival and materially shapes outcomes
- but the current evidence still does not justify collapsing the whole driver story into a standalone sizing explanation

## Bottom line

The sizing chain matters.
It is the strongest bounded subsystem story remaining after the execution-proxy partition.
But it still does not beat the broader Phase 14 answer.

So the correct Phase 2 closeout is:

- **the sizing chain is central to preservation and risk-shaping**
- **but `emergent_system_behavior` remains the best-supported broader explanation on the current evidence surface**
- **the next bounded move is Phase 3: residual drift-separation**.
