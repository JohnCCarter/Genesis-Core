"""
Backtest engine for Genesis-Core.

Replays historical candle data bar-by-bar through the existing strategy pipeline.
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from core.backtest.htf_exit_engine import HTFFibonacciExitEngine
from core.backtest.position_tracker import PositionTracker
from core.indicators.exit_fibonacci import calculate_exit_fibonacci_levels
from core.strategy.champion_loader import ChampionLoader
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
        htf_exit_config: dict | None = None,  # HTF Exit Engine configuration
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

        self.champion_loader = ChampionLoader()

        # Initialize HTF Exit Engine
        default_htf_config = {
            "partial_1_pct": 0.50,
            "partial_2_pct": 0.30,
            "fib_threshold_atr": 0.3,
            "trail_atr_multiplier": 1.6,
            "enable_partials": True,
            "enable_trailing": True,
            "enable_structure_breaks": True,
        }
        self.htf_exit_config = {**default_htf_config, **(htf_exit_config or {})}
        self.htf_exit_engine = HTFFibonacciExitEngine(self.htf_exit_config)

    def load_data(self) -> bool:
        """
        Load historical candle data from Parquet (two-layer structure support).

        Returns:
            True if data loaded successfully, False otherwise
        """
        # Find data file (try two-layer structure first, fallback to legacy)
        base_dir = Path(__file__).parent.parent.parent.parent / "data"
        data_file_curated = (
            base_dir / "curated" / "v1" / "candles" / f"{self.symbol}_{self.timeframe}.parquet"
        )
        data_file_legacy = base_dir / "candles" / f"{self.symbol}_{self.timeframe}.parquet"

        if data_file_curated.exists():
            data_file = data_file_curated
        elif data_file_legacy.exists():
            data_file = data_file_legacy
        else:
            print("[ERROR] Data file not found:")
            print(f"  Tried curated: {data_file_curated}")
            print(f"  Tried legacy: {data_file_legacy}")
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

        champion_cfg = self.champion_loader.load_cached(self.symbol, self.timeframe)
        merged_configs = {**champion_cfg.config, **configs}
        merged_configs.setdefault("meta", {})["champion_source"] = champion_cfg.source
        configs = merged_configs

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

        # Track bars held for current position

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

                # Extract action, size, confidence, regime
                action = result.get("action", "NONE")
                size = meta.get("decision", {}).get("size", 0.0)

                # Extract confidence (can be dict or float)
                conf_val = result.get("confidence", 0.5)
                if isinstance(conf_val, dict):
                    conf_val.get("overall", 0.5)
                else:
                    float(conf_val) if conf_val else 0.5

                # Extract regime (can be dict or string)
                regime_val = result.get("regime", "BALANCED")
                if isinstance(regime_val, dict):
                    regime_val.get("name", "BALANCED")
                else:
                    str(regime_val) if regime_val else "BALANCED"

                # === EXIT LOGIC (check BEFORE new entry) ===
                if self.position_tracker.has_position():
                    # Prepare bar data for exit engine
                    bar_data = {
                        "timestamp": timestamp,
                        "open": bar["open"],
                        "high": bar["high"],
                        "low": bar["low"],
                        "close": close_price,
                        "volume": bar.get("volume", 0.0),
                    }

                    exit_reason = self._check_htf_exit_conditions(
                        current_price=close_price,
                        timestamp=timestamp,
                        bar_data=bar_data,
                        result=result,
                        meta=meta,
                        configs=configs,
                    )

                    if exit_reason:
                        trade = self.position_tracker.close_position_with_reason(
                            price=close_price, timestamp=timestamp, reason=exit_reason
                        )
                        if verbose and trade:
                            pnl_sign = "+" if trade.pnl > 0 else ""
                            print(
                                f"\n[{timestamp}] EXIT ({exit_reason}): "
                                f"{trade.side} closed @ ${close_price:.2f} | "
                                f"PnL: {pnl_sign}{trade.pnl_pct:.2f}%"
                            )

                # === ENTRY LOGIC ===
                if action != "NONE" and size > 0:
                    exec_result = self.position_tracker.execute_action(
                        action=action,
                        size=size,
                        price=close_price,
                        timestamp=timestamp,
                        symbol=self.symbol,
                    )

                    if exec_result.get("executed"):

                        # Initialize exit context for new position
                        self._initialize_position_exit_context(result, meta, close_price, timestamp)

                        if verbose:
                            print(
                                f"\n[{timestamp}] ENTRY: {action} {size:.4f} @ ${close_price:.2f}"
                            )

                # Update equity curve
                self.position_tracker.update_equity(close_price, timestamp)

                # Update state
                decision_meta = meta.get("decision", {}) or {}
                reasons = decision_meta.get("reasons") or []
                state_out = decision_meta.get("state_out", {}) or {}
                if hasattr(self.position_tracker, "set_pending_reasons"):
                    self.position_tracker.set_pending_reasons(reasons or [])
                self.state = state_out
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

    def _check_htf_exit_conditions(
        self,
        current_price: float,
        timestamp: datetime,
        bar_data: dict,
        result: dict,
        meta: dict,
        configs: dict,
    ) -> str | None:
        """
        Check HTF Fibonacci exit conditions.

        Returns:
            Exit reason string if should exit, None otherwise
        """
        if not self.position_tracker.has_position():
            return None

        position = self.position_tracker.position

        # Get exit config
        exit_cfg = configs.get("cfg", {}).get("exit", {})
        enabled = exit_cfg.get("enabled", True)

        if not enabled:
            return None

        # Get HTF Fibonacci context from meta
        # HTF context is in meta['features']['htf_fibonacci']
        features_meta = meta.get("features", {})
        htf_fib_context = features_meta.get("htf_fibonacci", {})

        # Calculate ATR for exit logic (use last 14 bars)
        from core.indicators.atr import calculate_atr

        window_size = min(14, len(self.candles_df))
        if window_size >= 2:
            recent_highs = self.candles_df["high"].iloc[-window_size:].values
            recent_lows = self.candles_df["low"].iloc[-window_size:].values
            recent_closes = self.candles_df["close"].iloc[-window_size:].values
            atr_values = calculate_atr(recent_highs, recent_lows, recent_closes, period=14)
            current_atr = float(atr_values[-1]) if len(atr_values) > 0 else 100.0
        else:
            current_atr = 100.0

        # Prepare indicators for exit engine
        features = result.get("features", {})
        indicators = {
            "atr": current_atr,
            "ema50": features.get("ema", current_price),  # Use ema feature (EMA50)
            "ema_slope50_z": features.get("ema_slope50_z", 0.0),
        }

        # Check HTF exit conditions
        exit_actions = self.htf_exit_engine.check_exits(
            position, bar_data, htf_fib_context, indicators
        )
        meta.setdefault("signal", {})
        meta["signal"]["current_atr"] = current_atr

        # Execute exit actions
        exit_cfg = configs.get("cfg", {}).get("exit", {})
        break_even_trigger = exit_cfg.get("break_even_trigger")
        break_even_offset = exit_cfg.get("break_even_offset", 0.0)
        partial_break_even = exit_cfg.get("partial_break_even", False)
        partial_break_even_offset = exit_cfg.get("partial_break_even_offset", break_even_offset)

        for action in exit_actions:
            if action.action == "PARTIAL":
                # Execute partial exit
                trade = self.position_tracker.partial_close(
                    close_size=action.size,
                    price=current_price,
                    timestamp=timestamp,
                    reason=action.reason,
                )
                if trade:  # Always log partial exits
                    print(
                        f"  [PARTIAL] {action.reason}: {trade.size:.3f} @ ${trade.exit_price:,.0f} = ${trade.pnl:,.2f}"
                    )
                    if partial_break_even and trade.remaining_size > 0:
                        if position.side == "LONG":
                            be_price = position.entry_price * (1 + partial_break_even_offset)
                            position.trail_stop = max(
                                position.trail_stop or -float("inf"), be_price
                            )
                        else:
                            be_price = position.entry_price * (1 - partial_break_even_offset)
                            position.trail_stop = min(position.trail_stop or float("inf"), be_price)

            elif action.action == "TRAIL_UPDATE":
                # Update trailing stop (store in position for next bar)
                if hasattr(position, "trail_stop"):
                    position.trail_stop = action.stop_price
                else:
                    # Add trail_stop attribute if not exists
                    position.trail_stop = action.stop_price
                # Break-even promotion if configured
                if break_even_trigger is not None:
                    pnl_pct = self.position_tracker.get_unrealized_pnl_pct(current_price) / 100.0
                    if pnl_pct >= break_even_trigger:
                        if position.side == "LONG":
                            be_price = position.entry_price * (1 + break_even_offset)
                            position.trail_stop = max(position.trail_stop, be_price)
                        else:
                            be_price = position.entry_price * (1 - break_even_offset)
                            position.trail_stop = min(position.trail_stop, be_price)

            elif action.action == "FULL_EXIT":
                # Full exit - return reason to trigger standard exit logic
                return action.reason

        # Check if trail stop hit (from previous bars)
        if (
            hasattr(position, "trail_stop")
            and position.trail_stop
            and (
                (position.side == "LONG" and current_price <= position.trail_stop)
                or (position.side == "SHORT" and current_price >= position.trail_stop)
            )
        ):
            return "TRAIL_STOP"

        # Fallback to traditional exit conditions for safety
        return self._check_traditional_exit_conditions(current_price, result, configs)

    def _check_traditional_exit_conditions(
        self,
        current_price: float,
        result: dict,
        configs: dict,
    ) -> str | None:
        """Fallback traditional exit conditions."""
        position = self.position_tracker.position

        # Get exit config
        exit_cfg = configs.get("cfg", {}).get("exit", {})
        stop_loss_pct = exit_cfg.get("stop_loss_pct", 0.02)
        take_profit_pct = exit_cfg.get("take_profit_pct", 0.05)
        exit_conf_threshold = exit_cfg.get("exit_conf_threshold", 0.45)

        # Emergency stop-loss
        pnl_pct = self.position_tracker.get_unrealized_pnl_pct(current_price) / 100.0
        if pnl_pct <= -stop_loss_pct:
            return "EMERGENCY_SL"

        # Emergency take-profit (for very large moves)
        if pnl_pct >= take_profit_pct * 2:  # 2x normal TP
            return "EMERGENCY_TP"

        # Confidence drop
        confidence = result.get("confidence", 1.0)
        if confidence < exit_conf_threshold:
            return "CONF_DROP"

        # Regime change
        regime = result.get("regime", "NEUTRAL")
        if position.side == "SHORT" and regime == "BULL":
            return "REGIME_CHANGE"
        if position.side == "LONG" and regime == "BEAR":
            return "REGIME_CHANGE"

        return None

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
                    "exit_reason": t.exit_reason,
                    "is_partial": t.is_partial,
                    "remaining_size": t.remaining_size,
                    "position_id": t.position_id,
                    "entry_reasons": t.entry_reasons,
                }
                for t in self.position_tracker.trades
            ],
            "equity_curve": self.position_tracker.equity_curve,
        }

    def _initialize_position_exit_context(
        self, result: dict, meta: dict, entry_price: float, timestamp: datetime
    ) -> None:
        """
        Initialize exit context for a newly opened position.

        Args:
            result: Pipeline result with features and indicators
            meta: Meta data including HTF Fibonacci context
            entry_price: Entry price of the position
            timestamp: Entry timestamp
        """
        if not self.position_tracker.position:
            return

        position = self.position_tracker.position

        # Try to get HTF Fibonacci context
        features_meta = meta.get("features", {})
        htf_fib_context = features_meta.get("htf_fibonacci", {})

        if not htf_fib_context.get("available"):
            # No HTF data available - position will use fallback exits
            print(f"[DEBUG] HTF not available: {htf_fib_context}")
            return

        # Extract swing from HTF context
        swing_high = htf_fib_context.get("swing_high", 0.0)
        swing_low = htf_fib_context.get("swing_low", 0.0)

        if swing_high <= swing_low or swing_high <= 0 or swing_low <= 0:
            # Invalid swing - position will use fallback exits
            print(f"[DEBUG] Invalid swing: high={swing_high}, low={swing_low}")
            return

        # Get indicators for validation
        features = result.get("features", {})
        features.get("atr", 100.0)

        # Skip swing validation at entry - we'll use frozen context approach
        # The swing will be validated when actually used for exits

        # Calculate exit Fibonacci levels using symmetric logic
        exit_levels = calculate_exit_fibonacci_levels(
            side=position.side,
            swing_high=swing_high,
            swing_low=swing_low,
            levels=[0.786, 0.618, 0.5, 0.382],  # Inverterade nivåer för exit
        )

        # Store in position for exit engine
        position.exit_swing_high = swing_high
        position.exit_swing_low = swing_low
        position.exit_fib_levels = exit_levels
        position.exit_swing_timestamp = timestamp

        # Arm exit context with frozen HTF data
        htf_context_for_arm = {
            "swing_id": f"swing_{timestamp.isoformat()}_{swing_high}_{swing_low}",
            "levels": exit_levels,
            "swing_low": swing_low,
            "swing_high": swing_high,
        }
        position.arm_exit_context(htf_context_for_arm)
