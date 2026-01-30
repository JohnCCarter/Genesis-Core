"""
Composable Backtest Engine - Integrates component-based strategy with BacktestEngine.

Uses decorator pattern to inject component evaluation into evaluate_pipeline.
"""

import functools
from typing import Any

from core.backtest.engine import BacktestEngine
from core.strategy import evaluate  # Import module to allow monkey-patching
from core.strategy.components.attribution import AttributionTracker
from core.strategy.components.context_builder import ComponentContextBuilder
from core.strategy.components.strategy import ComposableStrategy
from core.utils.logging_redaction import get_logger

_LOGGER = get_logger(__name__)


def create_composable_pipeline(
    strategy: ComposableStrategy,
    attribution_tracker: AttributionTracker,
    original_pipeline: Any,
) -> Any:
    """
    Create a wrapper around evaluate_pipeline that injects component filtering.

    Args:
        strategy: ComposableStrategy to evaluate
        attribution_tracker: Tracker for component decisions
        original_pipeline: Original evaluate_pipeline function

    Returns:
        Wrapped function with same signature
    """

    @functools.wraps(original_pipeline)
    def composable_evaluate_pipeline(
        candles: dict, policy: dict, configs: dict, state: dict | None = None
    ) -> tuple[dict, dict]:
        """Wrapped evaluate_pipeline with component filtering."""
        # Call original pipeline
        result, meta = original_pipeline(candles, policy, configs, state)

        # Build component context from pipeline output
        context = ComponentContextBuilder.build(result, meta, candles=candles)

        # Evaluate strategy components
        decision = strategy.evaluate(context)

        # Track attribution
        attribution_tracker.record(decision)

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
                        "name": cr.component,
                        "allowed": cr.allowed,
                        "confidence": cr.confidence,
                        "reason": cr.reason,
                    }
                    for cr in decision.component_results
                ],
            }
        else:
            # Components allowed - keep original action
            # Optionally adjust size based on component confidence
            # (For MVP, we keep it simple and don't modify size)
            meta["component_approved"] = {
                "confidence": decision.confidence,
                "components": [cr.component for cr in decision.component_results],
            }

        return result, meta

    return composable_evaluate_pipeline


class ComposableBacktestEngine:
    """
    Wrapper around BacktestEngine that integrates composable strategy.

    Uses decorator pattern to inject component evaluation into evaluate_pipeline.
    Preserves all existing exit logic (HTF Fibonacci, etc.).
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
        )
        self.strategy = strategy
        self.attribution_tracker = AttributionTracker()
        self._original_pipeline = None

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

        Temporarily patches evaluate_pipeline to inject component evaluation,
        then delegates to BacktestEngine.run().
        """
        # Reset state
        self.strategy.reset()
        self.attribution_tracker = AttributionTracker()

        # Save original pipeline
        self._original_pipeline = evaluate.evaluate_pipeline

        # Create wrapped pipeline
        wrapped_pipeline = create_composable_pipeline(
            self.strategy, self.attribution_tracker, self._original_pipeline
        )

        try:
            # Monkey-patch evaluate_pipeline
            evaluate.evaluate_pipeline = wrapped_pipeline

            # Run backtest with patched pipeline
            results = self.engine.run(policy, configs, verbose, pruning_callback)

            # Add attribution to results
            results["attribution"] = self.attribution_tracker.get_report_dict()

            return results

        finally:
            # Restore original pipeline
            evaluate.evaluate_pipeline = self._original_pipeline

    def get_attribution_report(self) -> dict:
        """Get attribution report from tracker."""
        return self.attribution_tracker.get_report_dict()
