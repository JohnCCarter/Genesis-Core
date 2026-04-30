Genesis-Core router research — codebase-aware re-evaluation
Date: 2026-04-30
Status: synthesis note (read-only, no code changes proposed inline)
Companion to: genesis_core_router_research.md (generic research, dated 2026-04-30)
Scope: re-evaluate the generic research recommendations against the actual feature/ri-role-map-implementation-2026-03-24 branch you shared.

This note is descriptive and structural. It is not a runtime change proposal and does not bypass the packet workflow. Where it points at a candidate next step, that step is described as a future bounded RI-local pre-code packet, not as work to start now.

TL;DR
Most of the structural mechanisms my generic research recommended you already have in ri_policy_router.py: hysteresis, min_dwell, size-first defensive (defensive_size_multiplier=0.5), AGED_WEAK_CONTINUATION_GUARD, weak_pre_aged single-veto latch, bars-7 continuation persistence reconsideration, and — as of 2026-04-30 — asymmetric continuation_release_hysteresis.

The single most important finding is already in your own evidence, not in mine. The ri_policy_router_shared_pocket_outcome_quality_2026-04-28.md slice shows that the same blocked-baseline-long pocket has different ex-post quality in positive vs negative years: weaker in positive years (router correctly suppresses), flat / mildly positive in negative years (router incorrectly suppresses). That is the structural inversion the generic research framing predicted, observed in your own data.

Therefore the open gap is not activation/release semantics (already partly handled and one more brick — asymmetric release — was just merged). The open gap is conditional discrimination: the suppression criteria are environment-blind.

The smallest honest next step is research-evidence-lane work to confirm which features inside the shared pocket distinguish "should suppress" from "should not suppress", with the eventual deterministic, replayable runtime form being a per-state Δ(s) gate computed offline from admissible decision-time fields. Bumpless transfer / exit-side / cross-family routing should remain deferred per your 2026-04-30 payoff-state translation packet.

Section A — what generic research recommended vs what you already have
The generic research note ranked ten concrete recommendations. Here is the mapping.

A1. Asymmetric activation / release hysteresis (Observed)
Research: longer dwell / higher bar to leave defensive than to enter; classic supervisory-control pattern.

Repo: implemented as of 2026-04-30 via continuation_release_hysteresis in \_CONTINUATION_DEFAULTS / \_router_config, applied in \_resolve_switch_controls only on the DEFENSIVE→CONTINUATION edge. decisions/regime_intelligence/policy_router/ri_policy_router_continuation_release_hysteresis_runtime_packet_2026-04-30.md shows the Opus-approved diff and stop conditions.

Status: Done. This exact recommendation is now live.

A2. Minimum dwell (Observed)
Research: state must persist for k bars before any switch consideration (avoids flicker, matches dwell-time switching theory).

Repo: `\_SWITCH_DEFAULTS["min_dwell"] = 3` in `ri_policy_router.py`, normalized in `\_router_config`, enforced in switch logic.

Status: Done.

A3. Switch-counter / accumulator (Observed)
Research: require N consecutive votes for the new policy before switching (Schmitt-trigger / page accumulator analog).

Repo: `\_SWITCH_DEFAULTS["switch_threshold"] = 2`, with `hysteresis = 1` reducing the threshold for in-direction continuation.

Status: Done.

A4. Size-first defensiveness (Observed)
Research: prefer reducing size before flipping policy — recovers most of the loss-avoidance benefit without the cost of mis-suppressing good entries.

Repo: `\_SWITCH_DEFAULTS["defensive_size_multiplier"] = 0.5` and `decision_sizing.py` applies it in conjunction with clarity multiplier and `risk_state` (`drawdown_guard`, `transition_guard`).

Status: Done in size lane. Note from the 2026-04-30 payoff-state translation packet: size-first defensiveness is admissible early; cross-family routing and exit-side moves are explicitly deferred.

A5. Post-switch settling / transition guard (Observed)
Research: hold sized-down state for k bars after any switch, regardless of the new state's confidence — avoids re-entering full size into a still-noisy regime.

Repo: risk_state.py has transition_guard (post-switch dwell with size suppression) layered on top of drawdown_guard.

Status: Done.

A6. Aged-weak guard (Observed in repo, not in generic research)
Repo-specific: \_should_guard_aged_weak_continuation triggers AGED_WEAK_CONTINUATION_GUARD when bars_since_regime_change >= 2 × stable_bars_strong and continuation evidence is weak.

This is structurally consistent with the research's "expectancy-decay" framing (edge declines with state age) but is implemented locally as a deterministic guard, not a payoff statistic. That matches your "no payoff at runtime" constraint.

Status: Implemented and currently the dominant suppressive reason in the negative-year regression pocket, per ri_policy_router_2024_regression_pocket_isolation_2026-04-30.md and ri_policy_router_negative_year_pocket_isolation_2026-04-28.md.

A7. Single-veto latch / one-shot suppressors (Inferred)
Research did not name this; it is a more careful pattern than what I described.

Repo: weak_pre_aged_single_veto_latch (in ri_policy_router.py) lets the weak-pre-aged release block fire once and then remembers it has fired. This is a deterministic anti-flicker pattern that doesn't need any payoff input. It's a strong primitive.

Status: Already a building block that can be reused for any future "suppress once, don't keep suppressing" mechanism.

A8. Detector-state vs policy-state separation (Inferred)
Research: separate the change-detector's posterior from the active policy so policy lag is intentional rather than accidental.

Repo: ri_policy_router.py already keeps raw_decision (raw evidence-driven proposal) separate from the dwell/hysteresis-resolved emitted decision, with both visible in debug. The conceptual split exists.

Status: Already architected. Could be hardened by exposing the gap explicitly as a packet output.

A9. Risk_state veto layer (Observed)
Research: keep an independent veto layer outside the router so policy never overrides hard risk constraints.

Repo: risk_state.py (drawdown_guard, transition_guard) sits as a downstream multiplier in decision_sizing.py.

Status: Done.

A10. Cross-family routing / bumpless transfer / exit-side (Observed)
Research: classic supervisory-control add-ons.

Repo: explicitly deferred in ri_policy_router_payoff_state_translation_precode_packet_2026-04-30.md. RI is the chosen lane, decision-time state is the runtime carrier, payoff-state is research truth (not yet runtime input).

Status: Correctly deferred. Don't reopen.

Net of Section A
Of the ten generic recommendations, eight are already implemented (A1–A5, A7–A9), one is correctly deferred (A10), and one (A6) was solved in a way the generic research did not name — a deterministic age-based guard rather than an expectancy-decay statistic. Your code is structurally ahead of the generic research note in three places:

The single-veto latch primitive (A7).

The detector-vs-policy separation already living in \_PreviousRouterState and raw_decision (A8).

The aged-weak guard implemented in admissible-state form (A6) instead of in payoff form.

This is why simply re-applying the generic research note won't move the needle further. The structural rooms it described are mostly built.

Section B — the empirical inversion in your own evidence
This is the part to keep.

analysis/regime_intelligence/policy_router/ri_policy_router_shared_pocket_outcome_quality_2026-04-28.md reports timestamp-close fwd_16 proxies for the same shared pocket (zone=low, bars_since_regime_change >= 8, candidate LONG, suppressive reasons in {AGED_WEAK_CONTINUATION_GUARD, insufficient_evidence}), split across clearly negative and clearly positive curated years.

Blocked baseline longs (the cohort the router suppresses):

Negative years (2019, 2021, 2024): n=648, fwd_16 mean +0.36 %, median +0.08 %, positive share 51 %.

Positive years (2018, 2020, 2022, 2025): n=811, fwd_16 mean −0.17 %, median −0.26 %, positive share 46 %.

Substituted continuation longs (the cohort the router would replace them with):

Negative years: n=415, fwd_16 mean +0.46 %, median +0.18 %, positive share 53 %.

Positive years: n=698, fwd_16 mean −0.31 %, median +0.21 %, positive share 52 %.

The proxy is descriptive (timestamp-close, not fill-aware) and the slice is honest about that. But the structural shape is unambiguous on the suppressed side: the same suppression rule is hitting genuinely weak longs in good years and roughly-flat longs in bad years. The pocket "exists" symmetrically (per the 2026-04-28 positive-vs-negative-pocket-comparison note); the outcome quality of what's inside it does not.

This is exactly the structural inversion the generic research framing predicted: the router's activation criterion is environment-blind with respect to whether the suppressed entries actually deserve suppression. In good years that environment-blindness happens to align with truth. In bad years it inverts.

This reframes the entire problem. It is not "we need better activation thresholds" — those have been tuned and asymmetrized. It is "the suppression criterion does not condition on the right state to know whether suppression is warranted."

Section C — what is therefore the open structural gap
Restating in the language of the generic research note:

The router has good Δ(s) (do-no-harm) properties in the positive year group and inverted Δ(s) properties in the negative year group, on the suppressed-cohort side, while the substituted-cohort side does not yet show a clean group separation on the same proxy.

In other words, the suppression branch has a confounded conditional expected value with respect to year-group context, and the substitution branch is approximately neutral on the same proxy surface.

Three corollaries follow:

C1. Tightening continuation activation further or strengthening defensive activation further will not close the gap. Either move makes the suppression branch fire more, and that branch is the one with the inverted conditional sign.

C2. Loosening the activation gates will recover negative-year performance at the cost of positive-year performance, because then the router stops suppressing the genuinely weak longs in positive years. This is the symmetric trap visible in the 2024 vs 2025 split that started the project.

C3. The only escape that keeps both year groups non-degraded is to make the suppression rule itself state-conditional — i.e., the same shared pocket should suppress in the positive-year-style sub-state and not suppress in the negative-year-style sub-state, with both sub-states defined in admissible decision-time fields.

C3 is the "structure not indicators" answer.

Section D — bounded next steps consistent with the packet workflow
These are not implementation proposals. They are candidate future research-evidence-lane pre-code packets, ranked by smallest first.

D1. Conditional-quality discriminator slice (research-evidence lane)
A read-only follow-up to ri_policy_router_shared_pocket_outcome_quality_2026-04-28.md that, inside the same shared low-zone bars-≥8 pocket, asks which decision-time admissible features correlate with the sign flip on fwd_16 between positive and negative year groups.

Lane: Research-evidence. Risk: LOW. No runtime change.

Inputs: same evidence inputs already used in the 2026-04-28 slice.

Constraints: features restricted to fields actually present in the action-diff JSON / RI snapshot at decision time. No payoff-state, no MFE/MAE, no future leakage.

Output: one analysis note describing whether any single admissible field, or any small ordered split, separates the "router-was-right-to-suppress" subset from the "router-was-wrong-to-suppress" subset within the shared pocket.

Stop condition: if no admissible single-field or shallow split achieves a meaningful descriptive separation, this lane should not advance to runtime.

This is the cheapest honest next step. It directly tests C3.

D2. Per-state Δ(s) confidence-bound gate (concept-only pre-code packet)
If D1 surfaces an admissible-state separator, the natural runtime form is a deterministic per-state suppression gate, where the gate is computed offline from a calibration window and stored as a static lookup keyed by quantized decision-time state.

Lane: Research-evidence first (offline calibration), then Concept-only packet for runtime application.

Constraint: still strictly deterministic and replayable; the lookup table itself is a static, version-pinned artifact, not learned in runtime.

Conceptually equivalent to: replace the boolean \_should_guard_aged_weak_continuation with a state-conditional confidence-bound gate — same primitive, but conditioned on the discriminator from D1.

Status: do not write this packet until D1 is done.

D3. Rank-normalized within-state thresholds (concept-only pre-code packet)
A robust alternative to absolute thresholds (clarity_floor, conf_floor, edge_floor): replace each absolute floor with a per-state rolling-quantile floor, computed offline. This still satisfies determinism and replayability if the quantile tables are pinned artifacts.

Reason this is structural and not an indicator: it changes how the existing thresholds adapt across different background regimes without changing what's being measured.

Status: lower priority than D1+D2 because it changes more surface for less direct attack on the inversion.

D4. Defensive_probe personality (already a deferred concept packet)
decisions/regime_intelligence/policy_router/ri_policy_router_defensive_probe_concept_precode_packet_2026-04-29.md is the right home for a future "small-size probe instead of full suppression" personality. It is structurally complementary to D2 — D2 chooses when to suppress; defensive_probe chooses how heavily to suppress. They should not be designed simultaneously; D2 first.

D5. Hardening the detector-vs-policy split as a packet output (read-only)
Optional research note that exports, per row, both raw_decision and the dwell/hysteresis-resolved emitted decision into the action-diff dump explicitly. This makes future asymmetric-release-style work cheaper to instrument. Strictly observability; no runtime change.

Section E — what the generic research note got wrong against the codebase
Two corrections worth noting so the original note isn't over-trusted:

The original note framed activation/release hysteresis as the highest-leverage missing brick. Against the actual repo, that brick was already mostly present and the last asymmetric piece was added on the same day the research was written. The actual highest-leverage missing brick is conditional suppression discrimination, not activation tuning.

The original note recommended payoff-decay statistics (expectancy decay, MAE/MFE-based age proxies) as candidate state inputs. Against your ri_policy_router_payoff_state_translation_precode_packet_2026-04-30.md, payoff-state is research truth, not runtime input. The deterministic equivalent — the aged-weak admissible-state guard — is what your repo already uses, and that is the right form. Keep payoff-state out of runtime.

Section F — where the generic research note still applies
These four points from the original note remain intact even after grounding:

F1. Detector-state vs policy-state separation as a design principle (already in your code; worth keeping explicit).

F2. Single-veto / one-shot latch primitives are the right deterministic form of "soft suppression" and should be reused.

F3. Risk_state should remain the outermost veto layer; never let the router override it.

F4. Cross-family routing, exit-side moves, and bumpless transfer should stay deferred. Don't reopen them while the conditional-discrimination question is still open.

Section G — Observed / Inferred / Speculative tags
Observed (in your repo or your evidence):

All of Section A's "implemented" mappings (citations to specific files).

The shared-pocket outcome-quality inversion in Section B (the 2026-04-28 analysis note).

The deferral decisions in the 2026-04-30 payoff-state translation packet.

Inferred (my reasoning from your evidence):

Section C1, C2, C3 — corollaries from the inversion.

Section E1 — that activation tuning will not close the gap.

Speculative (hypotheses, not yet tested):

Section D1's premise that an admissible single-field or shallow split exists inside the shared pocket. This is exactly what D1 is designed to test honestly.

Section D2's runtime form. Conditional on D1 surfacing a separator.

Section D3 (rank-normalized thresholds) as a partial substitute.

Section H — what I am not recommending
To stay disciplined:

I am not recommending writing a runtime packet right now.

I am not recommending changing any threshold in \_CONTINUATION_DEFAULTS, \_NO_TRADE_DEFAULTS, or \_SWITCH_DEFAULTS.

I am not recommending touching risk_state.py or decision_sizing.py.

I am not recommending introducing new indicators.

I am not recommending payoff-state, MFE, or MAE as runtime inputs.

The single thing I am recommending is: the next pre-code packet, when one is opened, should be D1, framed as a Research-evidence-lane read-only descriptive slice that asks which admissible decision-time field, if any, distinguishes "router-was-right-to-suppress" from "router-was-wrong-to-suppress" within the already-isolated shared pocket.
