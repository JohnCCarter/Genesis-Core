"""
Backtest engine for Genesis-Core.

Replays historical candle data bar-by-bar through the existing strategy pipeline.
"""

from pathlib import Path

import pandas as pd
from tqdm import tqdm

from core.backtest.position_tracker import PositionTracker
from core.strategy.evaluate import evaluate_pipeline


class BacktestEngine:
    """
    Core backtest engine.

    Loads historical candles from Parquet and replays them bar-by-bar,
    executing the strategy pipeline for each bar.

    Features:
    - Bar-by-bar replay (no lookahead bias)
    - State persistence between bars
    - Integration with existing pipeline (evaluate_pipeline)
    - Position tracking with PnL
    - Progress tracking
    """

    def __init__(
        self,
        symbol: str,
        timeframe: str,
        start_date: str | None = None,
        end_date: str | None = None,
        initial_capital: float = 10000.0,
        commission_rate: float = 0.001,
        slippage_rate: float = 0.0005,
        warmup_bars: int = 120,  # Bars needed for indicators (EMA, RSI, etc.)
    ):
        """
        Initialize backtest engine.

        Args:
            symbol: Trading symbol (e.g., 'tBTCUSD')
            timeframe: Candle timeframe (e.g., '15m', '1h')
            start_date: Start date for backtest (YYYY-MM-DD) or None for all
            end_date: End date for backtest (YYYY-MM-DD) or None for all
            initial_capital: Starting capital in USD
            commission_rate: Commission per trade (e.g., 0.001 = 0.1%)
            slippage_rate: Slippage per trade (e.g., 0.0005 = 0.05%)
            warmup_bars: Number of bars to skip for indicator warmup
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.start_date = start_date
        self.end_date = end_date
        self.warmup_bars = warmup_bars

        self.candles_df: pd.DataFrame | None = None
        self.position_tracker = PositionTracker(
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            slippage_rate=slippage_rate,
        )

        self.state: dict = {}
        self.bar_count = 0

    def load_data(self) -> bool:
        """
        Load historical candle data from Parquet.

        Returns:
            True if data loaded successfully, False otherwise
        """
        # Find data file
        data_file = (
            Path(__file__).parent.parent.parent.parent
            / "data"
            / "candles"
            / f"{self.symbol}_{self.timeframe}.parquet"
        )

        if not data_file.exists():
            print(f"[ERROR] Data file not found: {data_file}")
            return False

        # Load data
        self.candles_df = pd.read_parquet(data_file)
        print(f"[OK] Loaded {len(self.candles_df):,} candles from {data_file.name}")

        # Filter by date range if specified
        if self.start_date:
            start_dt = pd.to_datetime(self.start_date)
            self.candles_df = self.candles_df[self.candles_df["timestamp"] >= start_dt]
            print(f"[FILTER] Start date: {self.start_date}")

        if self.end_date:
            end_dt = pd.to_datetime(self.end_date)
            self.candles_df = self.candles_df[self.candles_df["timestamp"] <= end_dt]
            print(f"[FILTER] End date: {self.end_date}")

        print(f"[OK] Filtered to {len(self.candles_df):,} candles")

        if len(self.candles_df) < self.warmup_bars:
            print(
                f"[WARN] Not enough data for warmup "
                f"({len(self.candles_df)} < {self.warmup_bars})"
            )

        return True

    def _build_candles_window(self, end_idx: int, window_size: int = 200) -> dict:
        """
        Build candles dict for pipeline (last N bars up to end_idx).

        Args:
            end_idx: Current bar index (inclusive)
            window_size: Number of bars to include in window

        Returns:
            Candles dict with OHLCV lists
        """
        start_idx = max(0, end_idx - window_size + 1)
        window = self.candles_df.iloc[start_idx : end_idx + 1]

        return {
            "open": window["open"].tolist(),
            "high": window["high"].tolist(),
            "low": window["low"].tolist(),
            "close": window["close"].tolist(),
            "volume": window["volume"].tolist(),
        }

    def run(
        self,
        policy: dict | None = None,
        configs: dict | None = None,
        verbose: bool = False,
    ) -> dict:
        """
        Run backtest.

        Args:
            policy: Strategy policy (symbol, timeframe)
            configs: Strategy configs (thresholds, risk, etc.)
            verbose: Print detailed progress

        Returns:
            Dict with backtest results
        """
        if self.candles_df is None:
            print("[ERROR] No data loaded. Call load_data() first.")
            return {"error": "no_data"}

        # Default policy/configs
        policy = policy or {}
        policy.setdefault("symbol", self.symbol)
        policy.setdefault("timeframe", self.timeframe)

        configs = configs or {}

        print(f"\n{'='*70}")
        print(f"Running Backtest: {self.symbol} {self.timeframe}")
        print(f"{'='*70}")
        print(
            f"Period:  {self.candles_df['timestamp'].min()} to "
            f"{self.candles_df['timestamp'].max()}"
        )
        print(f"Bars:    {len(self.candles_df):,} (warmup: {self.warmup_bars})")
        print(f"Capital: ${self.position_tracker.initial_capital:,.2f}")
        print(f"{'='*70}\n")

        # Progress bar
        pbar = tqdm(
            total=len(self.candles_df),
            desc="Backtest",
            unit="bars",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )

        # Replay bars
        for i in range(len(self.candles_df)):
            bar = self.candles_df.iloc[i]
            timestamp = bar["timestamp"]
            close_price = bar["close"]

            # Skip warmup period
            if i < self.warmup_bars:
                pbar.update(1)
                continue

            # Build candles window for pipeline
            candles_window = self._build_candles_window(i)

            # Run pipeline (uses existing evaluate_pipeline from strategy/)
            try:
                result, meta = evaluate_pipeline(
                    candles=candles_window,
                    policy=policy,
                    configs=configs,
                    state=self.state,
                )

                # Extract action and size
                action = result.get("action", "NONE")
                size = result.get("size", 0.0)

                # Execute action
                if action != "NONE" and size > 0:
                    exec_result = self.position_tracker.execute_action(
                        action=action,
                        size=size,
                        price=close_price,
                        timestamp=timestamp,
                        symbol=self.symbol,
                    )

                    if verbose and exec_result.get("executed"):
                        print(f"\n[{timestamp}] {action} {size:.4f} @ ${close_price:.2f}")

                # Update equity curve
                self.position_tracker.update_equity(close_price, timestamp)

                # Update state
                self.state = result.get("state", {})
                self.bar_count += 1

            except Exception as e:
                if verbose:
                    print(f"\n[ERROR] Bar {i}: {e}")
                # Continue on error (robust backtest)

            pbar.update(1)

        pbar.close()

        # Close all positions at end
        final_bar = self.candles_df.iloc[-1]
        self.position_tracker.close_all_positions(final_bar["close"], final_bar["timestamp"])

        print(f"\n[OK] Backtest complete - {self.bar_count} bars processed")

        return self._build_results()

    def _build_results(self) -> dict:
        """Build final backtest results."""
        summary = self.position_tracker.get_summary()

        return {
            "backtest_info": {
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "start_date": str(self.candles_df["timestamp"].min()),
                "end_date": str(self.candles_df["timestamp"].max()),
                "bars_total": len(self.candles_df),
                "bars_processed": self.bar_count,
                "warmup_bars": self.warmup_bars,
            },
            "summary": summary,
            "trades": [
                {
                    "symbol": t.symbol,
                    "side": t.side,
                    "size": t.size,
                    "entry_price": t.entry_price,
                    "entry_time": t.entry_time.isoformat(),
                    "exit_price": t.exit_price,
                    "exit_time": t.exit_time.isoformat(),
                    "pnl": t.pnl,
                    "pnl_pct": t.pnl_pct,
                    "commission": t.commission,
                }
                for t in self.position_tracker.trades
            ],
            "equity_curve": self.position_tracker.equity_curve,
        }
