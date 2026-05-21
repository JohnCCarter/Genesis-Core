"""Internal helpers for backtest result payload assembly."""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.backtest.engine import BacktestEngine


def _build_backtest_results_payload(engine: BacktestEngine) -> dict:
    """Return the final backtest results payload for an engine instance."""

    summary = engine.position_tracker.get_summary()
    position_summary = engine.position_tracker.get_position_summary()

    # Resolve git executable to an absolute path (Bandit B607) and keep failure non-fatal.
    git_hash = "unknown"
    try:
        git_exe = shutil.which("git")
        if git_exe:
            git_hash = subprocess.check_output([git_exe, "rev-parse", "HEAD"], text=True).strip()
    except (OSError, subprocess.SubprocessError):
        git_hash = "unknown"

    return {
        "backtest_info": {
            "symbol": engine.symbol,
            "timeframe": engine.timeframe,
            "data_source_policy": engine.data_source_policy,
            "ltf_candles_source": engine.candles_source,
            "start_date": str(engine.candles_df["timestamp"].min()),
            "end_date": str(engine.candles_df["timestamp"].max()),
            "bars_total": len(engine.candles_df),
            "bars_processed": engine.bar_count,
            "warmup_bars": engine.warmup_bars,
            "initial_capital": engine.position_tracker.initial_capital,
            "commission_rate": engine.position_tracker.commission_rate,
            "slippage_rate": engine.position_tracker.slippage_rate,
            "execution_mode": {
                "fast_window": bool(engine.fast_window),
                "env_precompute_features": os.environ.get("GENESIS_PRECOMPUTE_FEATURES"),
                "precompute_enabled": bool(getattr(engine, "precompute_features", False)),
                "precomputed_ready": bool(getattr(engine, "_precomputed_features", None)),
                "mode_explicit": os.environ.get("GENESIS_MODE_EXPLICIT"),
            },
            "htf": {
                "env_htf_exits": os.environ.get("GENESIS_HTF_EXITS"),
                "use_new_exit_engine": bool(getattr(engine, "_use_new_exit_engine", False)),
                "htf_candles_loaded": bool(engine.htf_candles_df is not None),
                "htf_candles_source": engine.htf_candles_source,
                "htf_context_seen": bool(getattr(engine, "_htf_context_seen", False)),
            },
            "effective_config_fingerprint": getattr(engine, "_effective_config_fingerprint", None),
            "git_hash": git_hash,
            "seed": os.environ.get("GENESIS_RANDOM_SEED", "unknown"),
            "timestamp": datetime.now().isoformat(),
        },
        "summary": summary,
        "position_summary": position_summary,
        # Add top-level metrics for convenience (duplicates summary fields)
        "metrics": {
            "total_trades": summary.get("num_trades", 0),
            "num_trades": summary.get("num_trades", 0),
            "total_return": summary.get("total_return", 0.0) / 100.0,
            "total_return_pct": summary.get("total_return", 0.0),
            "win_rate": summary.get("win_rate", 0.0) / 100.0,
            "profit_factor": summary.get("profit_factor", 0.0),
            "max_drawdown": summary.get("max_drawdown", 0.0) / 100.0,
        },
        "trades": [
            {
                "symbol": trade.symbol,
                "side": trade.side,
                "size": trade.size,
                "entry_price": trade.entry_price,
                "entry_time": trade.entry_time.isoformat(),
                "entry_regime": trade.entry_regime,
                "exit_price": trade.exit_price,
                "exit_time": trade.exit_time.isoformat(),
                "pnl": trade.pnl,
                "pnl_pct": trade.pnl_pct,
                "commission": trade.commission,
                "exit_reason": trade.exit_reason,
                "is_partial": trade.is_partial,
                "remaining_size": trade.remaining_size,
                "position_id": trade.position_id,
                "entry_reasons": trade.entry_reasons,
                "entry_fib_debug": trade.entry_fib_debug,
                "exit_fib_debug": trade.exit_fib_debug,
            }
            for trade in engine.position_tracker.trades
        ],
        "equity_curve": engine.position_tracker.equity_curve,
    }
