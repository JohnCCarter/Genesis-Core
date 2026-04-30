Genesis-Core: Structural Improvements to Policy Activation
A deep-research note on payoff-risk detection, robust router gating, and state-machine design for a deterministic, replayable trading system. Focused on structure, not indicators. Every claim is tagged \[Observed\] (literature/known practice), \[Inferred\] (reasoning from your description), or \[Speculative\] (new hypotheses to test).

0. The diagnosis you may be missing
   Your symptom — "high winrate, defensive policies hurt good years, help bad years" — is the textbook signature of a payoff-shape (convexity) inversion, not a regime-detection problem.

A high-winrate system already has concave payoff (frequent small wins, rare large losses). \[Observed — Price Action Lab; convexity literature Heygotrade\]

Defensive policies (tighter stops, smaller size, earlier exits) cap MFE while leaving MAE topology intact. They make a concave payoff more concave. They help in mean-reverting/choppy regimes (where capping MFE costs little) and hurt in trending regimes (where MFE expansion is the entire edge). \[Inferred from your description + MAE/MFE literature QuantifiedStrategies\]

This means the router is solving the wrong problem: it is being asked to classify market regime, when what it actually needs to classify is payoff-shape regime — the expected MFE distribution of trades initiated now, conditional on current state. \[Inferred\]

Reframe: You do not have a regime classification problem. You have a switched-system control problem with asymmetric switching costs and a hidden state (payoff shape) that must be inferred from observable proxies in an as-of-correct way. \[Inferred\]

Once framed this way, most of the literature points the same direction: hybrid/supervisory control with hysteresis, dwell time, and SPC-style change detection — all interpretable, all deterministic.

1. State definition — what you may be missing
   Most routers are built over market state (trend, vol, breadth). The structural gap is that the quantity that actually distinguishes good and bad years is not market state but realized payoff-quality state of the live system.

1.1 The state vector should be three-layered, not flat
Layer What it captures Example dimensions
Exogenous market state What the market is doing trend strength, realized vol, dispersion
Endogenous payoff state What the system is producing right now rolling expectancy, MFE/MAE ratio, R-multiple skew, exit-quality
Policy-conditional state Which policy is active and how long it has been active dwell counter, time-since-last-switch, post-switch transient flag
\[Inferred\] The third layer is what most deterministic routers omit. Switching costs, transients, and bumpless-transfer behavior are all functions of policy-conditional state. Without it, the router is effectively memoryless and will chatter.

1.2 Concrete state additions worth testing
\[Observed/Inferred\] These are structural additions, not new indicators:

Rolling expectancy slope (sign of d/dt of trailing-N expectancy). Sign change is a far stronger payoff-degradation signal than expectancy level.

MFE/MAE asymmetry index over last N trades: median(MFE)/median(MAE). If this ratio is collapsing while winrate is steady, payoff is degrading silently. \[Observed — MAE/MFE literature\]

Realized-R distribution skewness (third moment of R-multiples). A high-winrate system with declining skewness is the direct fingerprint of "winrate good, payoff bad." \[Inferred\]

Lag-1 autocorrelation of R-multiples (AR(1)). Critical-slowing-down literature shows AR(1) rising and variance rising are joint early-warning signals before regime tipping. Apply to trade outcomes, not prices. \[Observed — Scheffer/Dakos critical slowing-down; novel to apply to R-multiples — Speculative on the trading application\]

Time-since-last-policy-switch (dwell counter). Required for any deterministic transition guard.

Distance-to-ruin in fractional-Kelly units rather than dollars. Defensive activation tied to this is both upside-preserving and downside-protecting because it scales with how much edge you can still afford to lose. \[Observed — Chan on Kelly + max DD subaccount\]

1.3 The non-obvious gap: as-of-correct payoff state
\[Inferred\] Trade outcomes are typically known only at trade close, not at decision time. So if your router uses realized expectancy, you have a mixed timing problem: state computed at close is being read at open of the next trade. This is technically as-of-correct, but it produces a hidden lag that grows in slow-trade regimes and shrinks in fast-trade regimes. The router becomes effectively faster in some regimes than others — which is itself a regime-coupled bias.

Mitigation: introduce a time-decay on payoff state (e.g., exponential downweight on age of last realized trade). Do not let stale payoff state drive a defensive switch.

2. Detecting payoff risk in real time (decision-time only)
   You need interpretable, deterministic sequential tests on payoff quality. Three primitives, all replayable:

2.1 CUSUM on R-multiples (decision-time edge degradation)
\[Observed — Page-Hinkley/CUSUM\] Page-Hinkley statistic on R_i - R_baseline:

text
m_t = sum(R_i - R_baseline - delta) for i=1..t
M_t = min(m_k for k=1..t)
PH_t = m_t - M_t
trigger if PH_t > lambda
Tuning insight not always discussed: delta and lambda directly encode false-alarm vs detection-delay tradeoff (ARL₀ vs ARL₁). For a do-no-harm router, you want ARL₀ ≫ cost-of-false-defensive. \[Inferred — set lambda by simulating false-defensive cost in good years rather than by detection sensitivity in bad years.\]

2.2 GLR on expectancy variance increase
\[Observed — GLR change-point\] When the mean R is stable but variance of R is rising, the GLR test for variance change is the right primitive. This is exactly the "winrate stable, payoff deteriorating" fingerprint.

2.3 SPRT on edge-still-positive
\[Observed — Wald SPRT\] Test continuously: H₀ = edge is still ≥ baseline; H₁ = edge has dropped to a defensive-warranting level. SPRT gives the smallest expected sample size for fixed error rates — the most decision-efficient sequential test that exists. Use it as the gate to defensive activation, not as a continuous router input.

2.4 Critical slowing down on per-trade outcomes
\[Observed in ecology, Speculative in trading\] Compute over a rolling window of last-N closed trades:

Rising lag-1 AR(1) of R-multiples

Rising variance of R-multiples

Rising |skewness| (flickering)

When two of three rise simultaneously, the trade-outcome process is approaching a tipping point. This is a leading signal for payoff degradation. \[Speculative — the application of CSD to R-multiples (rather than prices) is non-standard and worth direct backtesting\]

2.5 Exit/sizing-mismatch early signals
\[Inferred\] The most reliable decision-time signal of an exit/sizing mismatch is MFE-give-back ratio: (MFE - exit_price) / MFE. Compute the rolling distribution; a rightward shift means you are progressively leaving more on the table. This is independent of winrate — it can rise while winrate is stable, which is exactly your symptom.

A second, complementary signal: median MAE on winners vs losers. If MAE on winners approaches MAE on losers, your stop is no longer separating signal from noise — the entry edge has eroded silently.

3. Robust policy activation gates
   3.1 Hysteresis: the structural answer to chattering
   \[Observed — Schmitt trigger; volatility hysteresis example\] Use two thresholds, not one:

T_on → activate defensive policy

T_off (with T_off < T_on) → return to base policy

This eliminates chattering near a single threshold. Width of the band = noise floor of the signal.

3.2 Asymmetric hysteresis is the do-no-harm answer
\[Inferred\] Because false-positive defensive activation in good years costs more than false-negative in bad years (your symptom), the band must be asymmetric:

High T_on (hard to activate defensive) — protects upside

Low T_off close to noise floor (easy to deactivate) — bounded downside if you mis-activated

The standard symmetric hysteresis from EE textbooks is wrong here. The activation barrier should be tuned to switching cost, the deactivation barrier to noise.

3.3 Minimum dwell time / debounce

Each policy must be active for at least τ_min decisions before any switch is allowed (hard guard).

Average switching frequency over a window must remain below a threshold (soft guard).

\[Inferred\] τ_min is the structural dial that kills regime misclassification. A 1-bar regime mis-call cannot trigger a policy switch if τ_min ≥ 5 (for example). It is the simplest, most robust lever available, and it is independent of the indicators you use.

3.4 Quorum / two-of-three confirmation
\[Observed — 2-out-of-3 voting logic; medical-trial m-of-K stopping rules PMC\] Require defensive activation to be confirmed by ≥2 of ≥3 independent signals (e.g., CUSUM trigger, MFE-give-back rise, AR(1) of R rising). Each individual signal can be slightly trigger-happy; the AND structure raises specificity without sacrificing all sensitivity.

The "m consecutive rejections" pattern from clinical trials is also useful: require the activation condition to hold for m consecutive evaluations (a temporal AND).

3.5 Guard conditions written explicitly

text
state DEFENSIVE
on TRIGGER_BASE_RETURN
[PH_stat < lambda_off
AND dwell >= tau_min
AND distance_to_ruin > D_safe
AND time_since_last_switch >= tau_cool]
-> BASE
Every guard term is a falsifiable boolean. The router is then a finite, replayable transition table — not a scoring function. This is the deepest determinism you can achieve. \[Inferred\]

3.6 The do-no-harm acceptance criterion
\[Speculative, but principled\] A defensive policy D should activate only when, on the offline distribution conditioned on the current router state s:

text
E\[R | D, s\] - E\[R | base, s\] > switching_cost(s) + activation_threshold
The activation_threshold is your do-no-harm margin. Set it from the worst loss the defensive policy caused in 2024-like states, not from average behavior. This guarantees that if the router is mis-classifying state, the only outcome is a foregone improvement — not an active loss. \[Inferred from minimax/regret framing\]

4. Avoiding over-defensiveness
   4.1 Make defensive activation cost-aware
   \[Inferred\] The router should not score whether to be defensive but expected regret of activating defensive given current state. Concretely, maintain an offline lookup:

text
Δ(s) = E\[R | base, s\] - E\[R | defensive, s\]
Only activate defensive when Δ(s) ≤ 0 with high confidence. A point estimate is not enough; use a one-sided lower confidence bound. Bayesian beta-binomial on winrate per state, normal on expectancy per state — both interpretable, deterministic given fixed priors.

4.2 Asymmetric trigger / release (Schmitt with bias toward upside)
Already covered in §3.2. The structural rule: make the system biased toward base policy. Defensive is the exception, base is the default. Your symptom suggests the current router has it the other way around (defensive activates too easily).

4.3 Convexity-preserving defensive design
\[Speculative + Observed — DAR + trend-following blend\] Even structurally, a defensive policy is a tax on convexity. Two structural fixes:

Defensive policy applies to size only, not to exits. Cuts MAE proportionally without capping MFE. Preserves convexity. \[Inferred — direct from MFE/MAE algebra\]

Defensive policy is a parallel sleeve, not a replacement. The router blends weights between base and defensive rather than switching outright. Hard switches are most damaging; weighted blends preserve some upside even in the wrong regime.

4.4 Bumpless transfer
\[Observed — bumpless switching, state resetting, anti-windup\] The control-systems literature is unambiguous: when switching controllers, you must initialize the new controller's internal state from the old controller's trajectory, otherwise transients dominate the post-switch period. For Genesis-Core this means: when switching from base→defensive, do not re-evaluate open positions under the defensive rules from scratch; carry over their entry context (e.g., trailing-stop level, time-in-trade) so the defensive policy doesn't immediately exit positions that the base policy was correctly riding. \[Inferred this is likely part of the 2024 degradation: defensive activation closes winners that should have been left open.\]

5. State stability and transition detection
   5.1 Distinguish regime change from noise
   The two interpretable, deterministic primitives are:

CUSUM/Page-Hinkley: detects shifts in mean. \[Observed\]

GLR with rolling window: detects shifts in variance or distribution. \[Observed\]

Both are fully replayable and have closed-form ARL₀/ARL₁ — meaning false-alarm rate is tunable analytically.

5.2 The flicker problem (transient false-positives)
\[Observed — critical slowing down: flickering precedes tipping\] Near a true regime tipping point, the system flickers between states. Your router will see noisy multiple crossings exactly when a real transition is happening — this is the worst time for it to chatter.

Structural fix: dwell-time on each detection, not just on each policy. Require the change-detection statistic itself to remain above threshold for τ_detect evaluations before treating it as a confirmed regime change. This transforms flicker from a router liability into useful evidence (because flicker itself is an early warning). \[Inferred\]

5.3 Hysteresis on the detector, not just the policy
\[Inferred — non-obvious\] Most systems put hysteresis on policy switching. A more robust pattern is two-level hysteresis:

Detector hysteresis: the change-detection alarm latches with T_alarm_on / T_alarm_off.

Policy hysteresis: policy switching responds to the latched alarm with its own dwell time and band.

This decouples signal-of-change from response-to-change, allowing one to be tight and the other slow. Most failures are because both are mixed into one threshold.

5.4 Cooldown after switch
\[Observed — embedded systems pattern\] After any policy switch, freeze the router for τ_cool decisions. This prevents the pathological loop: defensive activates → realized expectancy briefly improves due to reduced exposure → router thinks regime is recovered → switches back → loses again.

6. Router design patterns
   6.1 Hierarchical state machine
   \[Observed — supervisory control\] Two layers:

Outer regime FSM with K macro-regimes, hard hysteresis, long dwell.

Inner policy selector within each regime, choosing among a small set of pre-defined policies.

Replayability is preserved because both layers are pure FSMs over observable state. \[Inferred\] The structural advantage: defensive escalation can be bounded by macro-regime — you can't deploy a tail-protection policy unless the outer FSM is in a regime where it has shown net-positive offline.

6.2 Hybrid control: continuous score → discrete decision
\[Observed — hybrid systems\] Compute a continuous "defensive pressure" score (e.g., weighted sum of CUSUM, AR(1), MFE-give-back). Apply hysteresis on the score, not on individual signals. This is the cleanest way to combine signals while keeping a single threshold pair to tune.

The trap: if the score is non-stationary (different scale in different regimes), thresholds will drift. Solution: rank-normalize within a long rolling window. The detector then compares percentile-positions, not raw values.

6.3 Witness / shadow policy
\[Speculative\] Maintain a paper-traded shadow of the alternative policy at every decision. Because the system is deterministic and replayable, this is essentially free. Track the shadow's realized expectancy in parallel. The router's switch criterion is then: switch to the alternative only when its 30-trade trailing expectancy strictly dominates the active policy's by a margin > switching cost.

This converts the router from a predictive problem ("will defensive be better?") into a measurement problem ("has defensive been better?"). Pure measurement is far more robust and entirely deterministic. The cost is τ_min-trade lag in switching — exactly the dwell time you want anyway.

6.4 Ratchet / one-way gates
\[Inferred\] For risk-of-ruin protection: some defensive activations should be ratcheted — easy to enter, but only released after a proof-of-recovery condition (e.g., 10 consecutive trades with PH below threshold AND drawdown recovered by X%). This is asymmetric on purpose: it puts a one-way valve between "risk preservation" mode and "edge harvesting" mode. Used carefully, it is the structural difference between drawdown-survival and drawdown-spiral.

7. Failure modes you may be missing
   7.1 Defensive policy contaminates the base policy's offline calibration
   \[Inferred — non-obvious\] If your offline winrate/expectancy was calibrated on base-only history, then activating defensive in production changes the trade-set the base policy ever sees. The base policy is no longer evaluated on the same distribution it was tuned on. This silently degrades the base policy's effective edge over time. The fix is to record per-policy state and evaluate each policy only on its own conditional state distribution.

7.2 Simpson's paradox in regime aggregates
\[Observed\] A defensive policy can show positive aggregate edge while losing in the largest regime sub-cluster. This happens when a small subset of regime-states with very strong defensive edge dominates the aggregate. Always evaluate per-state Δ(s), never aggregate Δ.

7.3 Policy lag induced by router lag
\[Inferred\] The router itself takes time to switch. If router latency (dwell + confirmation) exceeds the regime's autocorrelation time, you get systematic late switching. You'll always be defensive at the start of a recovery and aggressive at the start of a drawdown. Diagnostic: compare distribution of state-at-switch to distribution of state-at-payoff-realization. If they differ systematically, the router is structurally late.

7.4 The "good year" is what calibrates the defensive policy out of the model
\[Inferred — critical\] If 2024 is "good" partly because the system did not activate defensive often, your ability to evaluate the defensive policy on 2024-conditions is poor (small sample). This means defensive is least well-calibrated exactly where it does the most damage. Mitigation: the do-no-harm threshold (§3.6) should be wider in low-sample regions of state space (use confidence-interval width, not point estimate).

7.5 Exit-side mismatch is invisible at entry
\[Speculative — fits your symptom precisely\] You said "good direction, payoff issues." This strongly suggests the router activates defensive based on entry-time signals, but the damage happens on the exit-side: defensive's tighter exit kills MFE on what would have been a winner. Therefore your router should distinguish entry-conditioning state from exit-conditioning state and apply policies independently to each. A common bug: using one router for both — winrate is preserved (entries unchanged) but payoff collapses (exits prematurely tightened).

7.6 The flat-line trap
\[Inferred\] Defensive policies tend to produce low-variance output. If your router uses any variance-of-equity-curve term, defensive activation looks self-justifying. Avoid: never use realized P&L variance as a router input. Use R-multiple distribution shape, which is invariant to position size.

8. Alternative framings — which one is yours?
   Framing Best fit if your problem is… Tools it gives you
   Control theory / hybrid switched system Stability of switched policies, dwell time, bumpless transfer Average dwell time bounds, hysteresis design, anti-windup, supervisory FSM
   Signal-degradation / SPC Detecting that edge is decaying in real time CUSUM, EWMA, GLR, SPRT, ARL tuning
   Risk-of-ruin / Kelly How aggressive to be conditional on remaining capital Fractional-Kelly subaccount, drawdown-conditional scaling
   Meta-strategy selection Choosing among finite pre-built policies Bandit-style measurement (deterministic via shadow), regret-bounded switching
   Critical-transitions / EWS Detecting regime tipping vs noise AR(1), variance, skewness EWS on R-multiples
   \[Inferred\] Your description is most consistent with hybrid switched-system control + signal-degradation detection on the payoff state, with a secondary risk-of-ruin overlay. Meta-strategy is a useful lens but bandit/RL machinery violates your "no online learning" constraint — which is fine because the deterministic-shadow construction (§6.3) gives you the same selection logic without online updates.

9. Concrete structural recommendations (ranked)
   In rough order of expected payoff vs implementation effort:

Make the router asymmetric (high T_on, low T_off for defensive activation). Single highest-leverage structural change. \[§3.2\]

Add minimum dwell time τ_min to every state. Eliminates the chattering class of failures. \[§3.3\]

Move the router's input from price/vol regime to payoff-quality regime (rolling expectancy slope, MFE/MAE ratio, R-skew). This is the framing fix. \[§1, §2\]

Run a deterministic shadow of every alternative policy. Switch on measured, not predicted, dominance. \[§6.3\]

Compute per-state Δ(s) offline; require lower-confidence-bound > switching cost before activating. Do-no-harm criterion. \[§3.6, §4.1\]

Apply defensive to size, not exits, by default. Preserves MFE convexity. \[§4.3\]

Bumpless transfer on switch. Carry trade context across policy boundaries. \[§4.4\]

Two-of-three quorum on defensive activation triggers (CUSUM + MFE-give-back + AR(1)-of-R). \[§3.4\]

Cooldown after switch. Eliminates flip-flop loops. \[§5.4\]

Ratchet release on risk-of-ruin gates. Tied to drawdown recovery, not to current signal. \[§6.4\]

10. What you are likely actually missing
    \[Inferred — the integrative claim\]

You probably have:

a router defined over market regime, not payoff regime;

a single-threshold activation, not asymmetric hysteresis;

little or no dwell time, so the router responds to noise as if it were signal;

defensive policies that act on exits, capping MFE;

no bumpless transfer, so switching mid-trade kills good positions;

aggregate-level evaluation of defensive edge, hiding Simpson's paradox effects;

no shadow accounting of the alternative policy's measured (not predicted) edge.

If even three of these are true, the structural inversion you observe (good years hurt, bad years helped) is the predictable output of the system. None of these requires new indicators, new ML, or any non-determinism to fix — they are all rearrangements of the structure of state, gating, and switching.

Sources
Hespanha & Morse, Stability of switched systems with average dwell-time — Semantic Scholar

State Resetting for Bumpless Switching in Supervisory Control — PDF

Switching systems with dwell time — arXiv 1912.10214

Page-Hinkley method overview — GeeksforGeeks

GLR sequential change-point detection — Georgia Tech ISYE

Critical slowing down / EWS — Global Tipping Points 2023

MAE / MFE — Quantified Strategies

Convexity in trading — Heygotrade

Profit factor / payoff / winrate identity — Price Action Lab

Hysteresis in defensive rotation — Volatility Trading Strategies

Defensive overlays vs trend-following — Advisor Analyst

2-out-of-3 voting logic — JIWEI Auto

m-of-K sequential stopping rules — PMC 11990451

Embedded state-machine guards — Archimetric

Look-ahead bias / as-of correctness — Quantreo

Kelly + max-DD subaccount — E.P. Chan

EWMA control charts — Six Sigma Study Guide

Sliding-mode chattering avoidance — ScienceDirect

Trend-following in regime-switching — Alpha Architect
