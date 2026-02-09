"""Cooldown Component - Entry veto based on recent trade activity.

This component enforces a minimum number of bars between trades to prevent
overtrading and allow market conditions to develop.

**Phase 2 Scope**: Entry-veto only (does NOT affect exits or sizing)

**Stateful**: YES - tracks last trade bar per symbol

**ENTRY-ONLY Semantics**:
- Cooldown state updates ONLY on ENTRY actions (LONG or SHORT)
- Does NOT update on exit/close/TP/SL/management actions
- This ensures cooldown measures time between NEW positions, not trade management

**Context Requirements**:
- symbol: str (for multi-symbol state isolation)
- bar_index: int (current bar number for cooldown calculation)

**Configuration**:
- min_bars_between_trades: int (minimum bars required between consecutive trades)

**Veto Reasons**:
- COOLDOWN_ACTIVE: Trade was taken recently (within min_bars_between_trades)

**State Management**:
- State persists across bars within a single backtest
- State MUST be reset between separate backtests (via reset_state())
- record_trade() is called by ComposableBacktestEngine when action in ("LONG", "SHORT")
"""

from typing import Any

from .base import ComponentResult, StrategyComponent


class CooldownComponent(StrategyComponent):
    """Veto entry if a trade was taken recently (enforces minimum bars between trades).

    This is the FIRST stateful component in Phase 2. State management requirements:
    1. Track last_trade_bar per symbol (multi-symbol isolation)
    2. Implement reset_state() for clean backtest starts
    3. State must NOT leak between separate backtest runs

    Example:
        config = {"min_bars_between_trades": 24}  # 24 hours for 1h timeframe
        component = CooldownComponent(config)

        # First trade at bar 100
        decision = component.evaluate(context={"bar_index": 100, "symbol": "tBTCUSD"}, meta={})
        # decision.allowed = True (no prior trade)

        component.record_trade(symbol="tBTCUSD", bar_index=100)

        # Try to trade at bar 110 (within cooldown)
        decision = component.evaluate(context={"bar_index": 110, "symbol": "tBTCUSD"}, meta={})
        # decision.allowed = False (cooldown active, only 10 bars since last trade)

        # Trade at bar 124 (cooldown expired)
        decision = component.evaluate(context={"bar_index": 124, "symbol": "tBTCUSD"}, meta={})
        # decision.allowed = True (24 bars elapsed)
    """

    def __init__(self, config: dict[str, Any]):
        """Initialize CooldownComponent with minimum bars between trades.

        Args:
            config: Component configuration
                - min_bars_between_trades: int (required, > 0)

        Raises:
            ValueError: If min_bars_between_trades is missing or invalid
        """
        self._name = "cooldown"

        # Validate config
        if "min_bars_between_trades" not in config:
            raise ValueError("CooldownComponent requires 'min_bars_between_trades' in config")

        self._min_bars = int(config["min_bars_between_trades"])
        if self._min_bars <= 0:
            raise ValueError(f"min_bars_between_trades must be > 0, got {self._min_bars}")

        # State: {symbol: last_trade_bar_index}
        self._last_trade_bars: dict[str, int] = {}

    def name(self) -> str:
        """Return component name for attribution tracking."""
        return self._name

    def evaluate(self, context: dict[str, Any]) -> ComponentResult:
        """Evaluate whether entry is allowed based on cooldown period.

        Args:
            context: Component context from ComponentContextBuilder
                Required keys:
                - bar_index: int (current bar number)
                - symbol: str (for multi-symbol state isolation)

        Returns:
            ComponentResult with:
            - allowed: False if cooldown active, True otherwise
            - confidence: 1.0 if allowed, 0.0 if vetoed
            - reason: None if allowed, "COOLDOWN_ACTIVE" if vetoed
            - metadata: Component config + state info
        """
        # Defensive: handle missing context keys
        bar_index = context.get("bar_index")
        symbol = context.get("symbol")

        if bar_index is None:
            return ComponentResult(
                allowed=False,
                confidence=0.0,
                reason="COOLDOWN_BAR_INDEX_MISSING",
                metadata={
                    "component": self._name,
                    "min_bars_between_trades": self._min_bars,
                    "error": "bar_index missing from context",
                },
            )

        if symbol is None:
            return ComponentResult(
                allowed=False,
                confidence=0.0,
                reason="COOLDOWN_SYMBOL_MISSING",
                metadata={
                    "component": self._name,
                    "min_bars_between_trades": self._min_bars,
                    "error": "symbol missing from context",
                },
            )

        # Check if symbol has prior trade
        last_trade_bar = self._last_trade_bars.get(symbol)

        if last_trade_bar is None:
            # No prior trade for this symbol → allow
            return ComponentResult(
                allowed=True,
                confidence=1.0,
                reason=None,
                metadata={
                    "component": self._name,
                    "symbol": symbol,
                    "bar_index": bar_index,
                    "last_trade_bar": None,
                    "bars_since_trade": None,
                    "min_bars_required": self._min_bars,
                },
            )

        # Calculate bars since last trade
        bars_since_trade = bar_index - last_trade_bar

        if bars_since_trade < self._min_bars:
            # Cooldown still active → veto
            return ComponentResult(
                allowed=False,
                confidence=0.0,
                reason="COOLDOWN_ACTIVE",
                metadata={
                    "component": self._name,
                    "symbol": symbol,
                    "bar_index": bar_index,
                    "last_trade_bar": last_trade_bar,
                    "bars_since_trade": bars_since_trade,
                    "min_bars_required": self._min_bars,
                },
            )

        # Cooldown expired → allow
        return ComponentResult(
            allowed=True,
            confidence=1.0,
            reason=None,
            metadata={
                "component": self._name,
                "symbol": symbol,
                "bar_index": bar_index,
                "last_trade_bar": last_trade_bar,
                "bars_since_trade": bars_since_trade,
                "min_bars_required": self._min_bars,
            },
        )

    def record_trade(self, symbol: str, bar_index: int) -> None:
        """Record that a trade was taken (updates cooldown state).

        IMPORTANT: This method should ONLY be called on ENTRY actions (LONG/SHORT),
        NOT on exit/close/TP/SL actions. This ensures cooldown measures time between
        NEW positions, not trade management.

        Called by ComposableBacktestEngine when action in ("LONG", "SHORT").

        Args:
            symbol: Symbol that was traded
            bar_index: Bar index when trade was executed
        """
        self._last_trade_bars[symbol] = bar_index

    def reset_state(self) -> None:
        """Reset component state (clears last_trade_bars).

        MUST be called at the start of each backtest to prevent state leakage.
        """
        self._last_trade_bars.clear()
