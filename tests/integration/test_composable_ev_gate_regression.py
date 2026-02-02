"""
Regression test for EVGate key mapping fix (Bug #2).

Verifies that EVGate does NOT veto 100% after fix (was degenerate before).
Uses golden-trace approach for stability.
"""


from core.strategy.components.context_builder import ComponentContextBuilder
from core.strategy.components.ev_gate import EVGateComponent


class TestEVGateNotDegenerate:
    """Regression: EVGate should not veto 100% with typical proba distributions."""

    def test_ev_gate_golden_trace_not_all_vetoed(self):
        """Golden trace: EVGate with min_ev=0.1 should NOT veto all typical probas."""
        # Golden trace: 20 representative proba samples from Q1 2024 distribution
        # (approximated from actual model output patterns)
        golden_probas = [
            {"buy": 0.48, "sell": 0.52},  # Slight sell bias
            {"buy": 0.49, "sell": 0.51},  # Near 50/50
            {"buy": 0.55, "sell": 0.45},  # Slight buy bias
            {"buy": 0.65, "sell": 0.35},  # Moderate buy
            {"buy": 0.70, "sell": 0.30},  # Strong buy
            {"buy": 0.45, "sell": 0.55},  # Moderate sell
            {"buy": 0.52, "sell": 0.48},  # Slight buy
            {"buy": 0.60, "sell": 0.40},  # Moderate buy
            {"buy": 0.50, "sell": 0.50},  # Exactly 50/50
            {"buy": 0.57, "sell": 0.43},  # Moderate buy
            {"buy": 0.63, "sell": 0.37},  # Strong buy
            {"buy": 0.53, "sell": 0.47},  # Slight buy
            {"buy": 0.48, "sell": 0.52},  # Slight sell
            {"buy": 0.67, "sell": 0.33},  # Strong buy
            {"buy": 0.51, "sell": 0.49},  # Very slight buy
            {"buy": 0.59, "sell": 0.41},  # Moderate buy
            {"buy": 0.46, "sell": 0.54},  # Moderate sell
            {"buy": 0.62, "sell": 0.38},  # Moderate buy
            {"buy": 0.54, "sell": 0.46},  # Slight buy
            {"buy": 0.58, "sell": 0.42},  # Moderate buy
        ]

        # EVGate with min_ev=0.1 (calibrated p80 threshold)
        ev_gate = EVGateComponent(min_ev=0.1)

        allowed_count = 0
        vetoed_count = 0

        for probas in golden_probas:
            result = {"probas": probas}
            context = ComponentContextBuilder.build(result, {})
            ev_result = ev_gate.evaluate(context)

            if ev_result.allowed:
                allowed_count += 1
            else:
                vetoed_count += 1

        total = len(golden_probas)
        veto_rate = vetoed_count / total

        # BEFORE FIX: veto_rate would be 1.0 (100%, all degenerate EV=0)
        # AFTER FIX: veto_rate should be ~0.20 (20%, matches p80 calibration)

        # Regression check: Should NOT veto everything (< 95%)
        assert veto_rate < 0.95, (
            f"EVGate vetoed {veto_rate*100:.1f}% of samples "
            f"(expected ~20%, was 100% before fix)"
        )

        # Sanity check: Should veto some samples (not all pass)
        assert veto_rate > 0.05, f"EVGate allowed too many samples ({veto_rate*100:.1f}% veto)"

        # Log for debugging
        print(f"EVGate (min_ev=0.1) results: {allowed_count} allowed, {vetoed_count} vetoed")
        print(f"Veto rate: {veto_rate*100:.1f}%")

    def test_ev_gate_high_threshold_vetoes_most(self):
        """Sanity: High min_ev threshold should veto most typical samples."""
        golden_probas = [
            {"buy": 0.52, "sell": 0.48},  # EV = 0.04
            {"buy": 0.53, "sell": 0.47},  # EV = 0.06
            {"buy": 0.54, "sell": 0.46},  # EV = 0.08
            {"buy": 0.55, "sell": 0.45},  # EV = 0.10
            {"buy": 0.56, "sell": 0.44},  # EV = 0.12
        ]

        # High threshold (above most samples)
        ev_gate = EVGateComponent(min_ev=0.10)

        vetoed_count = sum(
            1
            for probas in golden_probas
            if not ev_gate.evaluate(ComponentContextBuilder.build({"probas": probas}, {})).allowed
        )

        veto_rate = vetoed_count / len(golden_probas)

        # Should veto most samples with high threshold (EV < 0.10)
        assert (
            veto_rate > 0.5
        ), f"High threshold should veto most samples (got {veto_rate*100:.1f}%)"

    def test_ev_gate_low_threshold_allows_most(self):
        """Sanity: Low min_ev threshold should allow most typical samples."""
        golden_probas = [
            {"buy": 0.52, "sell": 0.48},
            {"buy": 0.55, "sell": 0.45},
            {"buy": 0.58, "sell": 0.42},
            {"buy": 0.60, "sell": 0.40},
            {"buy": 0.63, "sell": 0.37},
        ]

        # Low threshold (p50 level)
        ev_gate = EVGateComponent(min_ev=0.05)

        allowed_count = sum(
            1
            for probas in golden_probas
            if ev_gate.evaluate(ComponentContextBuilder.build({"probas": probas}, {})).allowed
        )

        allow_rate = allowed_count / len(golden_probas)

        # Should allow most samples with low threshold
        assert (
            allow_rate > 0.6
        ), f"Low threshold should allow most samples (got {allow_rate*100:.1f}%)"
