"""
Composable Backtest Engine - Integrates component-based strategy with BacktestEngine.

Uses evaluation_hook to inject component evaluation without monkey-patching.
"""

from typing import Any

from core.backtest.engine import BacktestEngine
from core.strategy.components.attribution import AttributionTracker
from core.strategy.components.context_builder import ComponentContextBuilder
from core.strategy.components.strategy import ComposableStrategy
from core.utils.logging_redaction import get_logger

_LOGGER = get_logger(__name__)


class ComposableBacktestEngine:
    """
    Wrapper around BacktestEngine that integrates composable strategy.

    Uses evaluation_hook to inject component evaluation after evaluate_pipeline.
    No monkey-patching - clean and robust integration.
    """

    def __init__(
        self,
        symbol: str,
        timeframe: str,
        strategy: ComposableStrategy,
        start_date: str | None = None,
        end_date: str | None = None,
        initial_capital: float = 10000.0,
        commission_rate: float = 0.001,
        slippage_rate: float = 0.0005,
        warmup_bars: int = 120,
        htf_exit_config: dict | None = None,
        fast_window: bool = False,
    ):
        """
        Initialize composable backtest engine.

        Args:
            symbol: Trading symbol (e.g., 'tBTCUSD')
            timeframe: Candle timeframe (e.g., '1h')
            strategy: ComposableStrategy instance with configured components
            (all other args passed through to BacktestEngine)
        """
        self.strategy = strategy
        self.attribution_tracker = AttributionTracker()

        # Create evaluation hook that applies component filtering
        def component_evaluation_hook(result: dict, meta: dict, candles: dict):
            """Hook called after evaluate_pipeline to apply component filtering."""
            # Build component context from pipeline output
            context = ComponentContextBuilder.build(result, meta, candles=candles)

            # Evaluate strategy components
            decision = self.strategy.evaluate(context)

            # Track attribution
            self.attribution_tracker.record(decision)

            # If components veto, override action to NONE
            if not decision.allowed:
                _LOGGER.debug(
                    "Components vetoed: %s (confidence=%.2f)",
                    decision.reason,
                    decision.confidence,
                )
                result["action"] = "NONE"
                # Add component veto to metadata
                meta["component_veto"] = {
                    "reason": decision.reason,
                    "confidence": decision.confidence,
                    "components": [
                        {
                            "name": name,
                            "allowed": cr.allowed,
                            "confidence": cr.confidence,
                            "reason": cr.reason,
                        }
                        for name, cr in (decision.component_results or {}).items()
                    ],
                }
            else:
                # Components allowed - keep original action
                meta["component_approved"] = {
                    "confidence": decision.confidence,
                    "components": list((decision.component_results or {}).keys()),
                }

            return result, meta

        # Create BacktestEngine with component evaluation hook
        self.engine = BacktestEngine(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            slippage_rate=slippage_rate,
            warmup_bars=warmup_bars,
            htf_exit_config=htf_exit_config,
            fast_window=fast_window,
            evaluation_hook=component_evaluation_hook,
        )

    def load_data(self) -> bool:
        """Load data via wrapped engine."""
        return self.engine.load_data()

    def run(
        self,
        policy: dict | None = None,
        configs: dict | None = None,
        verbose: bool = False,
        pruning_callback: Any | None = None,
    ) -> dict:
        """
        Run backtest with component filtering.

        Uses evaluation_hook - no monkey-patching required.
        """
        # Reset state
        self.strategy.reset()
        self.attribution_tracker = AttributionTracker()

        # Run backtest (hook is already configured in __init__)
        results = self.engine.run(policy, configs, verbose, pruning_callback)

        # Add attribution to results
        results["attribution"] = self.attribution_tracker.get_report_dict()

        return results

    def get_attribution_report(self) -> dict:
        """Get attribution report from tracker."""
        return self.attribution_tracker.get_report_dict()
