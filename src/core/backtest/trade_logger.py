"""
Trade logger for backtest.

Exports trade history and results to JSON/CSV files.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd


def _atomic_write_json(path: Path, data: dict, *, encoding: str = "utf-8") -> None:
    """Atomically write JSON to disk to prevent corruption from concurrent writes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding=encoding, delete=False, dir=path.parent) as tmp:
        json.dump(data, tmp, indent=2, default=str)
    Path(tmp.name).replace(path)


class TradeLogger:
    """
    Logs and exports backtest trades and results.

    Features:
    - Export trades to CSV
    - Export full results to JSON
    - Organized output directory structure
    """

    def __init__(self, output_dir: str | Path = "results/backtests"):
        """
        Initialize trade logger.

        Args:
            output_dir: Directory to save results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_results(self, results: dict, filename_prefix: str | None = None) -> dict[str, Path]:
        """
        Save full backtest results to JSON.

        Args:
            results: Results dict from BacktestEngine.run()
            filename_prefix: Optional prefix for filename (e.g., 'tBTCUSD_15m')

        Returns:
            Dict with paths to saved files
        """
        # Generate filename
        if filename_prefix is None:
            info = results.get("backtest_info", {})
            symbol = info.get("symbol", "unknown")
            timeframe = info.get("timeframe", "unknown")
            filename_prefix = f"{symbol}_{timeframe}"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = self.output_dir / f"{filename_prefix}_{timestamp}.json"

        # Save results atomically to prevent corruption from concurrent writes
        _atomic_write_json(json_file, results)

        print(f"[SAVED] Results: {json_file}")

        return {"json": json_file}

    def save_trades_csv(self, results: dict, filename_prefix: str | None = None) -> Path:
        """
        Save trades to CSV.

        Args:
            results: Results dict from BacktestEngine.run()
            filename_prefix: Optional prefix for filename

        Returns:
            Path to saved CSV file
        """
        trades = results.get("trades", [])

        if not trades:
            print("[WARN] No trades to export")
            return None

        # Generate filename
        if filename_prefix is None:
            info = results.get("backtest_info", {})
            symbol = info.get("symbol", "unknown")
            timeframe = info.get("timeframe", "unknown")
            filename_prefix = f"{symbol}_{timeframe}"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.output_dir.parent / "trades" / f"{filename_prefix}_trades_{timestamp}.csv"
        csv_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to DataFrame and save
        trades_df = pd.DataFrame(trades)
        if "entry_reasons" in trades_df.columns:
            # Optimized: Use list comprehension instead of apply() for better performance
            # List comprehension with .values is faster than apply() for simple operations
            trades_df["entry_reasons"] = [
                ";".join(reasons) if isinstance(reasons, list) else reasons
                for reasons in trades_df["entry_reasons"].values
            ]
        trades_df.to_csv(csv_file, index=False)

        print(f"[SAVED] Trades CSV: {csv_file}")

        return csv_file

    def save_equity_curve_csv(self, results: dict, filename_prefix: str | None = None) -> Path:
        """
        Save equity curve to CSV.

        Args:
            results: Results dict from BacktestEngine.run()
            filename_prefix: Optional prefix for filename

        Returns:
            Path to saved CSV file
        """
        equity_curve = results.get("equity_curve", [])

        if not equity_curve:
            print("[WARN] No equity curve to export")
            return None

        # Generate filename
        if filename_prefix is None:
            info = results.get("backtest_info", {})
            symbol = info.get("symbol", "unknown")
            timeframe = info.get("timeframe", "unknown")
            filename_prefix = f"{symbol}_{timeframe}"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = self.output_dir / f"{filename_prefix}_equity_{timestamp}.csv"

        # Convert to DataFrame and save
        equity_df = pd.DataFrame(equity_curve)
        equity_df.to_csv(csv_file, index=False)

        print(f"[SAVED] Equity curve CSV: {csv_file}")

        return csv_file

    def save_all(self, results: dict, filename_prefix: str | None = None) -> dict:
        """
        Save all outputs (JSON, trades CSV, equity CSV).

        Args:
            results: Results dict from BacktestEngine.run()
            filename_prefix: Optional prefix for filenames

        Returns:
            Dict with paths to all saved files
        """
        paths = {}

        # Save JSON
        json_paths = self.save_results(results, filename_prefix)
        paths.update(json_paths)

        # Save trades CSV
        trades_csv = self.save_trades_csv(results, filename_prefix)
        if trades_csv:
            paths["trades_csv"] = trades_csv

        # Save equity CSV
        equity_csv = self.save_equity_curve_csv(results, filename_prefix)
        if equity_csv:
            paths["equity_csv"] = equity_csv

        return paths
