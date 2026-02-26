"""
Regression test for Bug #1: CooldownComponent phantom trades.

Verifies that CooldownComponent only updates state when trades are ACTUALLY
executed, not just when signals are generated.

Bug #1 root cause: record_trade() was called based on action from evaluate_pipeline
(signal), not based on exec_result["executed"] (actual trade). This created "phantom
trades" where Cooldown state updated for signals that BacktestEngine rejected.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from core.strategy.components.cooldown import CooldownComponent


class TestCooldownPhantomTradesRegression:
    """Regression: Cooldown must NOT update on signals if trade not executed."""

    def test_signal_without_execution_no_phantom_veto(self):
        """Phantom trade regression: Signal (LONG) without execution must NOT update cooldown."""
        cooldown = CooldownComponent({"min_bars_between_trades": 24})

        # Simulate: Signal at bar 100, but trade NOT executed
        # (BacktestEngine rejected: position already open, size=0, etc.)
        # OLD BUG: record_trade() was called based on signal → phantom trade
        # FIXED: record_trade() only called when executed=True

        # Bar 100: Signal LONG, but NOT executed → NO cooldown update
        context_100 = {"symbol": "tBTCUSD", "bar_index": 100}
        result_100 = cooldown.evaluate(context_100)
        assert result_100.allowed is True, "First signal should be allowed (no prior trade)"

        # DO NOT call record_trade() (mimics fixed behavior: no execution)

        # Bar 101: Another signal → Should ALLOW (no phantom trade recorded)
        context_101 = {"symbol": "tBTCUSD", "bar_index": 101}
        result_101 = cooldown.evaluate(context_101)
        assert result_101.allowed is True, (
            "Signal at bar 101 should be allowed (no actual trade at bar 100). "
            "If vetoed, phantom trade bug is present."
        )

    def test_signal_with_execution_creates_real_cooldown(self):
        """Real trade: Signal with execution must update cooldown and veto subsequent signals."""
        cooldown = CooldownComponent({"min_bars_between_trades": 24})

        # Bar 100: Signal LONG, trade EXECUTED
        context_100 = {"symbol": "tBTCUSD", "bar_index": 100}
        result_100 = cooldown.evaluate(context_100)
        assert result_100.allowed is True, "First signal should be allowed"

        # Simulate execution: BacktestEngine opened position → call record_trade()
        cooldown.record_trade(symbol="tBTCUSD", bar_index=100)

        # Bar 101: Another signal → Should VETO (cooldown active)
        context_101 = {"symbol": "tBTCUSD", "bar_index": 101}
        result_101 = cooldown.evaluate(context_101)
        assert result_101.allowed is False, "Signal at bar 101 should be vetoed (cooldown active)"
        assert result_101.reason == "COOLDOWN_ACTIVE"

        # Bar 124: Cooldown expired → Should ALLOW
        context_124 = {"symbol": "tBTCUSD", "bar_index": 124}
        result_124 = cooldown.evaluate(context_124)
        assert result_124.allowed is True, "Signal at bar 124 should be allowed (cooldown expired)"

    def test_multiple_signals_no_execution_no_phantom_vetoes(self):
        """Stress test: Multiple signals without execution must NOT accumulate phantom vetoes."""
        cooldown = CooldownComponent({"min_bars_between_trades": 24})

        # Simulate: 100 signals, NONE executed (all rejected by BacktestEngine)
        # OLD BUG: Each signal would call record_trade() → 100 phantom trades → massive vetoes
        # FIXED: No record_trade() calls → no phantom trades

        for bar_index in range(100, 200):
            context = {"symbol": "tBTCUSD", "bar_index": bar_index}
            result = cooldown.evaluate(context)
            # All should be allowed (no actual trades recorded)
            assert result.allowed is True, (
                f"Signal at bar {bar_index} should be allowed (no prior trades). "
                f"If vetoed, phantom trade accumulation is present."
            )

    def test_execution_layer_rejection_does_not_update_cooldown(self):
        """Realistic scenario: Components allow, but BacktestEngine rejects (position open)."""
        cooldown = CooldownComponent({"min_bars_between_trades": 24})

        # Bar 100: Components allow, BacktestEngine OPENS position
        context_100 = {"symbol": "tBTCUSD", "bar_index": 100}
        result_100 = cooldown.evaluate(context_100)
        assert result_100.allowed is True
        cooldown.record_trade(symbol="tBTCUSD", bar_index=100)  # Trade executed

        # Bars 101-110: Components allow, but BacktestEngine REJECTS (position already open)
        # OLD BUG: record_trade() called on each signal → 10 phantom trades
        # FIXED: record_trade() only called on actual execution → 0 phantom trades

        for bar_index in range(101, 111):
            context = {"symbol": "tBTCUSD", "bar_index": bar_index}
            result = cooldown.evaluate(context)
            # Should veto due to REAL trade at bar 100, not phantom trades
            assert (
                result.allowed is False
            ), f"Bar {bar_index} should be vetoed (cooldown from bar 100)"
            assert result.reason == "COOLDOWN_ACTIVE"
            # DO NOT call record_trade() (mimics fixed behavior: execution rejected)

        # Bar 124: Cooldown from REAL trade expired → Allow
        context_124 = {"symbol": "tBTCUSD", "bar_index": 124}
        result_124 = cooldown.evaluate(context_124)
        assert result_124.allowed is True, "Bar 124 should allow (cooldown from bar 100 expired)"

        # Bar 125: Should still allow (no phantom trades accumulated during 101-110)
        context_125 = {"symbol": "tBTCUSD", "bar_index": 125}
        result_125 = cooldown.evaluate(context_125)
        assert result_125.allowed is True, (
            "Bar 125 should allow (only 1 real trade at bar 100, no phantom trades). "
            "If vetoed, phantom trade accumulation during 101-110 is present."
        )

    def test_multi_symbol_phantom_isolation(self):
        """Multi-symbol: Phantom trades on one symbol must NOT affect another symbol."""
        cooldown = CooldownComponent({"min_bars_between_trades": 24})

        # Symbol A: Signal without execution (phantom scenario)
        context_a = {"symbol": "tBTCUSD", "bar_index": 100}
        result_a = cooldown.evaluate(context_a)
        assert result_a.allowed is True
        # DO NOT call record_trade() for tBTCUSD (no execution)

        # Symbol B: Should be unaffected by Symbol A's phantom signal
        context_b = {"symbol": "tETHUSD", "bar_index": 100}
        result_b = cooldown.evaluate(context_b)
        assert result_b.allowed is True, (
            "tETHUSD should be unaffected by tBTCUSD phantom signal. "
            "If vetoed, state is leaking between symbols."
        )

        # Symbol B: Real trade
        cooldown.record_trade(symbol="tETHUSD", bar_index=100)

        # Symbol B: Subsequent signal should veto (real cooldown)
        context_b_101 = {"symbol": "tETHUSD", "bar_index": 101}
        result_b_101 = cooldown.evaluate(context_b_101)
        assert result_b_101.allowed is False, "tETHUSD bar 101 should veto (real cooldown)"

        # Symbol A: Should still allow (no real trade on tBTCUSD)
        context_a_101 = {"symbol": "tBTCUSD", "bar_index": 101}
        result_a_101 = cooldown.evaluate(context_a_101)
        assert result_a_101.allowed is True, (
            "tBTCUSD bar 101 should allow (no real trade, only phantom signal). "
            "If vetoed, phantom trade was recorded or state leaked from tETHUSD."
        )
