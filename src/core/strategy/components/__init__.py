"""
Composable Strategy Components (Phase 1 POC).

This package implements a component-based strategy architecture where individual
decision components (ML confidence, HTF gates, ATR filters, etc.) can be tested
independently and composed via configuration.
"""

from .base import ComponentResult, StrategyComponent
from .strategy import ComposableStrategy

__all__ = ["ComponentResult", "StrategyComponent", "ComposableStrategy"]
