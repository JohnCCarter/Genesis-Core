"""Tests for CooldownComponent (stateful entry-veto component)."""

import pytest

from core.strategy.components.cooldown import CooldownComponent


class TestCooldownComponent:
    """Test suite for CooldownComponent."""

    def test_init_requires_min_bars(self):
        """Test that __init__ requires min_bars_between_trades in config."""
        with pytest.raises(ValueError, match="requires 'min_bars_between_trades'"):
            CooldownComponent({})

    def test_init_requires_positive_min_bars(self):
        """Test that min_bars_between_trades must be > 0."""
        with pytest.raises(ValueError, match="must be > 0"):
            CooldownComponent({"min_bars_between_trades": 0})

        with pytest.raises(ValueError, match="must be > 0"):
            CooldownComponent({"min_bars_between_trades": -5})

    def test_name_returns_cooldown_component(self):
        """Test that name() returns component identifier."""
        component = CooldownComponent({"min_bars_between_trades": 10})
        assert component.name() == "CooldownComponent"

    def test_allow_when_no_prior_trade(self):
        """Test that component allows entry when no prior trade exists."""
        component = CooldownComponent({"min_bars_between_trades": 24})

        context = {"bar_index": 100, "symbol": "tBTCUSD"}
        decision = component.evaluate(context)

        assert decision.allowed is True
        assert decision.confidence == 1.0
        assert decision.reason is None
        assert decision.metadata["last_trade_bar"] is None
        assert decision.metadata["bars_since_trade"] is None

    def test_veto_when_cooldown_active(self):
        """Test that component vetoes when cooldown period has not elapsed."""
        component = CooldownComponent({"min_bars_between_trades": 24})

        # Record trade at bar 100
        component.record_trade(symbol="tBTCUSD", bar_index=100)

        # Try to trade at bar 110 (only 10 bars elapsed, need 24)
        context = {"bar_index": 110, "symbol": "tBTCUSD"}
        decision = component.evaluate(context)

        assert decision.allowed is False
        assert decision.confidence == 0.0
        assert decision.reason == "COOLDOWN_ACTIVE"
        assert decision.metadata["last_trade_bar"] == 100
        assert decision.metadata["bars_since_trade"] == 10
        assert decision.metadata["min_bars_required"] == 24

    def test_allow_when_cooldown_expired(self):
        """Test that component allows entry when cooldown has elapsed."""
        component = CooldownComponent({"min_bars_between_trades": 24})

        # Record trade at bar 100
        component.record_trade(symbol="tBTCUSD", bar_index=100)

        # Trade at bar 124 (exactly 24 bars elapsed)
        context = {"bar_index": 124, "symbol": "tBTCUSD"}
        decision = component.evaluate(context)

        assert decision.allowed is True
        assert decision.confidence == 1.0
        assert decision.reason is None
        assert decision.metadata["bars_since_trade"] == 24

    def test_allow_when_cooldown_exceeded(self):
        """Test that component allows entry when cooldown is well past threshold."""
        component = CooldownComponent({"min_bars_between_trades": 24})

        # Record trade at bar 100
        component.record_trade(symbol="tBTCUSD", bar_index=100)

        # Trade at bar 200 (100 bars elapsed, well past 24)
        context = {"bar_index": 200, "symbol": "tBTCUSD"}
        decision = component.evaluate(context)

        assert decision.allowed is True
        assert decision.confidence == 1.0
        assert decision.reason is None
        assert decision.metadata["bars_since_trade"] == 100

    def test_veto_missing_bar_index(self):
        """Test that component vetoes when bar_index is missing from context."""
        component = CooldownComponent({"min_bars_between_trades": 24})

        context = {"symbol": "tBTCUSD"}  # bar_index missing
        decision = component.evaluate(context)

        assert decision.allowed is False
        assert decision.confidence == 0.0
        assert decision.reason == "COOLDOWN_BAR_INDEX_MISSING"

    def test_veto_missing_symbol(self):
        """Test that component vetoes when symbol is missing from context."""
        component = CooldownComponent({"min_bars_between_trades": 24})

        context = {"bar_index": 100}  # symbol missing
        decision = component.evaluate(context)

        assert decision.allowed is False
        assert decision.confidence == 0.0
        assert decision.reason == "COOLDOWN_SYMBOL_MISSING"

    def test_multi_symbol_isolation(self):
        """Test that cooldown state is isolated per symbol."""
        component = CooldownComponent({"min_bars_between_trades": 24})

        # Record trade for tBTCUSD at bar 100
        component.record_trade(symbol="tBTCUSD", bar_index=100)

        # Try to trade tETHUSD at bar 110 (no prior trade for this symbol)
        context = {"bar_index": 110, "symbol": "tETHUSD"}
        decision = component.evaluate(context)

        assert decision.allowed is True  # tETHUSD has no cooldown
        assert decision.metadata["last_trade_bar"] is None

        # Try to trade tBTCUSD at bar 110 (cooldown active)
        context = {"bar_index": 110, "symbol": "tBTCUSD"}
        decision = component.evaluate(context)

        assert decision.allowed is False  # tBTCUSD has cooldown
        assert decision.reason == "COOLDOWN_ACTIVE"

    def test_reset_state_clears_trades(self):
        """Test that reset_state() clears last_trade_bars."""
        component = CooldownComponent({"min_bars_between_trades": 24})

        # Record trades
        component.record_trade(symbol="tBTCUSD", bar_index=100)
        component.record_trade(symbol="tETHUSD", bar_index=150)

        # Verify cooldowns active
        assert component.evaluate({"bar_index": 110, "symbol": "tBTCUSD"}).allowed is False

        # Reset state
        component.reset_state()

        # Verify cooldowns cleared (both symbols allow entry)
        assert component.evaluate({"bar_index": 110, "symbol": "tBTCUSD"}).allowed is True
        assert component.evaluate({"bar_index": 160, "symbol": "tETHUSD"}).allowed is True

    def test_stateless_behavior_per_symbol(self):
        """Test that same context produces same decision (given same state)."""
        component = CooldownComponent({"min_bars_between_trades": 24})

        # Record trade
        component.record_trade(symbol="tBTCUSD", bar_index=100)

        # Evaluate twice with same context
        context = {"bar_index": 110, "symbol": "tBTCUSD"}
        decision1 = component.evaluate(context)
        decision2 = component.evaluate(context)

        # Decisions should be identical (deterministic given state)
        assert decision1.allowed == decision2.allowed
        assert decision1.confidence == decision2.confidence
        assert decision1.reason == decision2.reason

    def test_metadata_includes_component_name(self):
        """Test that metadata includes component name for attribution."""
        component = CooldownComponent({"min_bars_between_trades": 24})

        context = {"bar_index": 100, "symbol": "tBTCUSD"}
        decision = component.evaluate(context)

        assert decision.metadata["component"] == "CooldownComponent"

    def test_record_trade_updates_state(self):
        """Test that record_trade() updates internal state correctly."""
        component = CooldownComponent({"min_bars_between_trades": 24})

        # Record first trade
        component.record_trade(symbol="tBTCUSD", bar_index=100)
        assert component._last_trade_bars["tBTCUSD"] == 100

        # Record second trade (overwrites previous)
        component.record_trade(symbol="tBTCUSD", bar_index=200)
        assert component._last_trade_bars["tBTCUSD"] == 200

    def test_boundary_case_exactly_min_bars(self):
        """Test cooldown behavior when exactly min_bars have elapsed."""
        component = CooldownComponent({"min_bars_between_trades": 10})

        component.record_trade(symbol="tBTCUSD", bar_index=100)

        # Exactly min_bars elapsed (should allow)
        context = {"bar_index": 110, "symbol": "tBTCUSD"}
        decision = component.evaluate(context)

        assert decision.allowed is True
        assert decision.metadata["bars_since_trade"] == 10

    def test_boundary_case_one_bar_before_min(self):
        """Test cooldown behavior when one bar short of min_bars."""
        component = CooldownComponent({"min_bars_between_trades": 10})

        component.record_trade(symbol="tBTCUSD", bar_index=100)

        # One bar short (should veto)
        context = {"bar_index": 109, "symbol": "tBTCUSD"}
        decision = component.evaluate(context)

        assert decision.allowed is False
        assert decision.reason == "COOLDOWN_ACTIVE"
        assert decision.metadata["bars_since_trade"] == 9

    def test_entry_only_semantics(self):
        """Test that Cooldown is designed for ENTRY-only tracking.

        This is a design/documentation test. The actual enforcement happens
        in ComposableBacktestEngine where record_trade() is called only when
        action in ("LONG", "SHORT"), not on exit/close actions.

        This test verifies the component's expectation: record_trade() should
        be called ONCE per entry bar, not on exits/management actions.
        """
        component = CooldownComponent({"min_bars_between_trades": 10})

        # Simulate: Entry at bar 100
        component.record_trade(symbol="tBTCUSD", bar_index=100)

        # Bars 101-109: cooldown active (would veto new entry)
        for bar in range(101, 110):
            decision = component.evaluate({"bar_index": bar, "symbol": "tBTCUSD"})
            assert decision.allowed is False, f"Bar {bar} should be in cooldown"

        # Bar 110: cooldown expired (would allow new entry)
        decision = component.evaluate({"bar_index": 110, "symbol": "tBTCUSD"})
        assert decision.allowed is True

        # Simulate: Exit/close action at bar 105 (should NOT record_trade)
        # This is handled by ComposableBacktestEngine - we just verify component
        # state remains unchanged if record_trade is NOT called
        # (i.e., state only updates when explicitly told via record_trade)

        # Verify last_trade_bar is still 100 (not affected by bar 105 non-entry)
        decision_after = component.evaluate({"bar_index": 112, "symbol": "tBTCUSD"})
        assert decision_after.allowed is True  # Still past cooldown from bar 100
        assert decision_after.metadata["last_trade_bar"] == 100
        assert decision_after.metadata["bars_since_trade"] == 12
