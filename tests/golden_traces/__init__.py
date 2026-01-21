"""
Golden Trace Tests - Semantic Drift Detection

These tests lock the causal chain from parameters to PnL by asserting
that identical inputs produce identical outputs at each stage:
1. Parameters → Features
2. Features → Decisions
3. Full Backtest → PnL/Metrics

Re-baseline snapshots only when intentionally changing logic.
"""
