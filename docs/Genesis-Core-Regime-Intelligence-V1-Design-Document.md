📘 Genesis-Core
Regime Intelligence v1 – Design Document

Status: Historical design reference
Branch Target: feature/regime-intelligence-v1
Prerequisite: Phase 2 merged into master
Scope: Regime perception upgrade + adaptive risk curve
Non-goal: No rewrite of core execution engine

> [HISTORICAL 2026-05-05] This early RI v1 design document is retained for design provenance only.
> It is not the active execution or promotion guide on `feature/next-slice-2026-05-05`; use `GENESIS_WORKING_CONTRACT.md` and the later RI decision/analysis chain for current live anchors.

1. Purpose

Upgrade Genesis from a binary, volatility-dominated regime gate to a multi-dimensional, clarity-driven regime intelligence layer.

Goal:

Participate in all market climates

Scale risk proportionally to regime clarity

Maintain full determinism and auditability

Enable higher trade frequency (Phase 1 growth mode)

Keep max DD target ≈ 15%

2. Core Philosophy

Genesis remains:

Deterministic

Fail-closed

Auditable

Capital-preserving

Regime Intelligence v1 adds:

Perception (multi-factor regime detection)

Clarity scoring (0–100)

Risk curve mapping

DD feedback loop

3. Architectural Constraints

This implementation MUST:

Not modify execution invariants

Not alter composable decision pipeline logic

Not break champion loader compatibility

Not introduce stochastic runtime decisions

Not require ML in v1

ML overlay is optional Phase 2.

4. Regime Engine v1
   4.1 Regime Labels (Fixed Set)
   RegimeLabel = Enum(
   TREND_UP,
   TREND_DOWN,
   RANGE,
   TRANSITION,
   CHAOS
   )

No dynamic regime creation.

4.2 Feature Inputs
HTF Context (Primary – 4H/1D)

Trend slope (normalized)

MA separation magnitude

Structure consistency (HH/HL pattern stability)

Vol compression/expansion ratio

LTF Context (1H / 15m)

Breakout strength

Momentum expansion

Local structure alignment

4.3 Clarity Score (0–100)

Clarity is computed as weighted normalized combination:

clarity = weighted_sum(
trend_strength,
structure_cleanliness,
vol_alignment,
momentum_alignment
)

Constraints:

Fully deterministic

Normalized 0–100

Same input → same output

5. Policy Mapping Layer

Replace binary regime gate with clarity-driven modulation.

5.1 Risk Curve
def risk_multiplier(clarity):
if clarity < 30:
return 0.5
elif clarity < 50:
return 1.0
elif clarity < 70:
return 1.4
elif clarity < 85:
return 1.8
else:
return 2.2

Smooth interpolation preferred.

5.2 Threshold Modulation

Optional:

Slight EV threshold relaxation in high clarity

Slight tightening in low clarity

Bounds must be hardcoded.

No free scaling.

6. Drawdown Feedback Loop

Portfolio-level DD modifies aggression:

DD Level Action

> 8% Reduce multipliers by 50%
> 12% Disable high-risk tier
> 15% Kill switch

This overrides regime clarity.

Capital preservation > aggression.

7. Logging & Attribution

Each trade decision must log:

regime_label

clarity_score

risk_multiplier

HTF state summary

LTF confirmation state

DD_state

blocker attribution (if veto)

“No trades” must always be explainable.

8. Expected Behavioral Shift

From:

Binary gating

Conservative-only participation

Low trade frequency

To:

Multi-climate participation

Adaptive aggression

120–250 trades/year target

Controlled explosiveness

9. Phase Roadmap
   Phase 1 (v1)

Rule-based regime engine

Risk curve

DD feedback

Logging

Phase 2 (Optional)

ML classifier for regime label

ML confidence modifies clarity within bounds

Frozen model versioning

10. Non-Goals

Not included in v1:

MS-GARCH

Bayesian priors

Copula tail modeling

EVT modeling

NLP macro override

LLM-as-a-judge

Shadow evolutionary systems

These are future institutional-scale features.

11. Strategic Intent

Phase 1 objective:

Growth mode

Higher trade frequency

Explosive but calculated capital growth

Maintain ≤15% max DD

Genesis evolves from:

Composable correctness
→ Regime perception + adaptive capital allocation

12. Success Criteria

Implementation is successful if:

Trade frequency increases without randomization

DD remains within guardrails

Risk scales smoothly with clarity

Logs clearly explain every trade/no-trade

System remains deterministic

Closing Statement

Genesis-Core remains a deterministic capital allocation engine.

Regime Intelligent v1 upgrades perception, not structure.

We are increasing intelligence without increasing fragility.
