"""
Backtest engine for Genesis-Core.

Replays historical candle data bar-by-bar through the existing strategy pipeline.
"""

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from tqdm import tqdm

from core.backtest.htf_exit_engine import HTFFibonacciExitEngine
from core.backtest.position_tracker import PositionTracker
from core.indicators.exit_fibonacci import calculate_exit_fibonacci_levels
from core.strategy.champion_loader import ChampionLoader
from core.strategy.evaluate import evaluate_pipeline


class CandleCache:
    def __init__(self, max_size: int = 4):
        self._max_size = max_size
        self._store: dict[tuple[str, str], pd.DataFrame] = {}

    def get(self, key: tuple[str, str]) -> pd.DataFrame | None:
        return self._store.get(key)

    def put(self, key: tuple[str, str], value: pd.DataFrame) -> None:
        if key in self._store:
            self._store[key] = value
            return
        if len(self._store) >= self._max_size:
            oldest_key = next(iter(self._store))
            del self._store[oldest_key]
        self._store[key] = value

    def clear(self) -> None:
        self._store.clear()


class BacktestEngine:
    _candles_cache = CandleCache(max_size=4)

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
        fast_window: bool = False,  # Use precomputed NumPy arrays for window building
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
        self.fast_window = bool(fast_window)

        self.candles_df: pd.DataFrame | None = None
        # Precomputed column arrays (initialized on demand when fast_window=True)
        self._col_open = None
        self._col_high = None
        self._col_low = None
        self._col_close = None
        self._col_volume = None
        self._col_timestamp = None
        # Numpy arrays for fast window extraction (populated in load_data/_prepare_numpy_arrays)
        self._np_arrays: dict | None = None
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

        cache_key = (self.symbol, self.timeframe)
        base_df = self._candles_cache.get(cache_key)
        if base_df is None:
            # Read only required columns, prefer pyarrow engine and memory-mapped IO for speed
            read_columns = ["timestamp", "open", "high", "low", "close", "volume"]
            try:
                base_df = pd.read_parquet(
                    data_file, columns=read_columns, engine="pyarrow", memory_map=True
                )
            except Exception:
                # Fallback to default engine if pyarrow not available
                base_df = pd.read_parquet(data_file, columns=read_columns)
            self._candles_cache.put(cache_key, base_df)
            print(f"[OK] Loaded {len(base_df):,} candles from {data_file.name}")
        else:
            print(f"[CACHE] Reusing {len(base_df):,} candles for {self.symbol} {self.timeframe}")

        # Work off cached DataFrame (avoid eager copy); filters below create sliced views/frames
        self.candles_df = base_df

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

        # Initialize fast-window column arrays if enabled
        if self.fast_window:
            df = self.candles_df
            self._col_open = df["open"].to_numpy(copy=False)
            self._col_high = df["high"].to_numpy(copy=False)
            self._col_low = df["low"].to_numpy(copy=False)
            self._col_close = df["close"].to_numpy(copy=False)
            self._col_volume = df["volume"].to_numpy(copy=False)
            # timestamps kept as Python list for downstream expectations
            self._col_timestamp = df["timestamp"].tolist()

        # Optional: precompute common features for speed (consumed by features_asof via config)
        self._precomputed_features: dict[str, list[float]] | None = None
        if getattr(self, "precompute_features", False):
            try:
                closes_all = self.candles_df["close"].tolist()
                highs_all = self.candles_df["high"].tolist()
                lows_all = self.candles_df["low"].tolist()
                import numpy as _np

                from core.indicators.adx import calculate_adx as _calc_adx
                from core.indicators.atr import calculate_atr as _calc_atr
                from core.indicators.bollinger import bollinger_bands as _bb
                from core.indicators.ema import calculate_ema as _calc_ema
                from core.indicators.fibonacci import (
                    FibonacciConfig as _FibCfg,
                )
                from core.indicators.fibonacci import (
                    detect_swing_points as _detect_swings,
                )
                from core.indicators.rsi import calculate_rsi as _calc_rsi

                # Try on-disk cache first
                cache_dir = Path(__file__).resolve().parents[3] / "cache" / "precomputed"
                cache_dir.mkdir(parents=True, exist_ok=True)
                key = f"{self.symbol}_{self.timeframe}_{len(closes_all)}"
                cache_path = cache_dir / f"{key}.npz"
                loaded = False
                pre: dict[str, list[float]] = {}
                if cache_path.exists():
                    try:
                        npz = _np.load(cache_path, allow_pickle=False)
                        for name in npz.files:
                            pre[name] = npz[name].astype(float).tolist()
                        # Load swings if present (stored as float but indices are integers originally)
                        for swing_key in ("fib_high_idx", "fib_low_idx"):
                            if swing_key in npz.files:
                                pre[swing_key] = npz[swing_key].astype(int).tolist()
                        loaded = True
                        print(f"[CACHE] Loaded precomputed features from {cache_path.name}")
                    except Exception:
                        loaded = False

                if not loaded:
                    atr_14 = _calc_atr(highs_all, lows_all, closes_all, period=14)
                    atr_50 = _calc_atr(highs_all, lows_all, closes_all, period=50)
                    # Precompute two common EMA periods used by features
                    ema_20 = _calc_ema(closes_all, period=20)
                    ema_50 = _calc_ema(closes_all, period=50)
                    rsi_14 = _calc_rsi(closes_all, period=14)
                    bb_all = _bb(closes_all, period=20, std_dev=2.0)
                    bb_pos = list(bb_all.get("position") or [])
                    adx_14 = _calc_adx(highs_all, lows_all, closes_all, period=14)

                    # Precompute Fibonacci swings (LTF) for reuse in feature calculation
                    fib_cfg = _FibCfg(atr_depth=3.0, max_swings=8, min_swings=1)
                    # Use pandas only for Series conversion inside detect function to keep parity
                    import pandas as _pd

                    sh_idx, sl_idx, sh_px, sl_px = _detect_swings(
                        _pd.Series(highs_all), _pd.Series(lows_all), _pd.Series(closes_all), fib_cfg
                    )

                    # Optional on-disk cache for reuse between runs
                    try:
                        _np.savez_compressed(
                            cache_path,
                            atr_14=_np.asarray(atr_14, dtype=float),
                            atr_50=_np.asarray(atr_50, dtype=float),
                            ema_20=_np.asarray(ema_20, dtype=float),
                            ema_50=_np.asarray(ema_50, dtype=float),
                            rsi_14=_np.asarray(rsi_14, dtype=float),
                            bb_position_20_2=_np.asarray(bb_pos, dtype=float),
                            adx_14=_np.asarray(adx_14, dtype=float),
                            fib_high_idx=_np.asarray(sh_idx, dtype=int),
                            fib_low_idx=_np.asarray(sl_idx, dtype=int),
                            fib_high_px=_np.asarray(sh_px, dtype=float),
                            fib_low_px=_np.asarray(sl_px, dtype=float),
                        )
                        print(f"[OK] Precomputed features cached: {cache_path.name}")
                    except Exception:
                        pass

                    pre = {
                        "atr_14": atr_14,
                        "atr_50": atr_50,
                        "ema_20": ema_20,
                        "ema_50": ema_50,
                        "rsi_14": rsi_14,
                        "bb_position_20_2": bb_pos,
                        "adx_14": adx_14,
                        "fib_high_idx": list(sh_idx),
                        "fib_low_idx": list(sl_idx),
                        "fib_high_px": list(sh_px),
                        "fib_low_px": list(sl_px),
                    }

                self._precomputed_features = pre
                print("[OK] Precomputed features ready")
            except Exception as _:
                # Non-fatal: skip precompute if indicators unavailable
                self._precomputed_features = None

        if len(self.candles_df) < self.warmup_bars:
            print(
                f"[WARN] Not enough data for warmup "
                f"({len(self.candles_df)} < {self.warmup_bars})"
            )

        # Pre-convert DataFrame columns to numpy arrays for fast slicing
        self._np_arrays = {
            "open": self.candles_df["open"].values,
            "high": self.candles_df["high"].values,
            "low": self.candles_df["low"].values,
            "close": self.candles_df["close"].values,
            "volume": self.candles_df["volume"].values,
            "timestamp": self.candles_df["timestamp"].values,
        }

        return True

    def _prepare_numpy_arrays(self) -> None:
        """Prepare numpy arrays from candles_df for fast window extraction."""
        if self.candles_df is not None:
            self._np_arrays = {
                "open": self.candles_df["open"].values,
                "high": self.candles_df["high"].values,
                "low": self.candles_df["low"].values,
                "close": self.candles_df["close"].values,
                "volume": self.candles_df["volume"].values,
                "timestamp": self.candles_df["timestamp"].values,
            }

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

        if self.fast_window and self._col_close is not None:
            # Slice precomputed arrays (fast path) - return NumPy views
            i0 = start_idx
            i1 = end_idx + 1
            return {
                "open": self._col_open[i0:i1],
                "high": self._col_high[i0:i1],
                "low": self._col_low[i0:i1],
                "close": self._col_close[i0:i1],
                "volume": self._col_volume[i0:i1],
                "timestamp": self._col_timestamp[i0:i1],
            }

        # Optimized fallback: use pre-computed numpy arrays
        if self._np_arrays is not None:
            return {
                "open": self._np_arrays["open"][start_idx : end_idx + 1].tolist(),
                "high": self._np_arrays["high"][start_idx : end_idx + 1].tolist(),
                "low": self._np_arrays["low"][start_idx : end_idx + 1].tolist(),
                "close": self._np_arrays["close"][start_idx : end_idx + 1].tolist(),
                "volume": self._np_arrays["volume"][start_idx : end_idx + 1].tolist(),
                "timestamp": self._np_arrays["timestamp"][start_idx : end_idx + 1].tolist(),
            }

        # Fallback: slice DataFrame window
        window = self.candles_df.iloc[start_idx : end_idx + 1]
        return {
            "open": window["open"].values.tolist(),
            "high": window["high"].values.tolist(),
            "low": window["low"].values.tolist(),
            "close": window["close"].values.tolist(),
            "volume": window["volume"].values.tolist(),
            "timestamp": window["timestamp"].values.tolist(),
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

        # Ensure numpy arrays are prepared for fast window extraction
        if self._np_arrays is None:
            self._prepare_numpy_arrays()

        # Default policy/configs
        policy = policy or {}
        policy.setdefault("symbol", self.symbol)
        policy.setdefault("timeframe", self.timeframe)

        configs = configs or {}
        # Inject precomputed features for vectorized path
        if getattr(self, "precompute_features", False) and getattr(
            self, "_precomputed_features", None
        ):
            cfg_pre = dict(configs)
            cfg_pre["precomputed_features"] = dict(self._precomputed_features)
            configs = cfg_pre

        champion_cfg = self.champion_loader.load_cached(self.symbol, self.timeframe)
        configs = {**champion_cfg.config, **configs}
        meta = configs.setdefault("meta", {})
        meta.setdefault("champion_source", champion_cfg.source)
        meta.setdefault("champion_version", champion_cfg.version)
        meta.setdefault("champion_checksum", champion_cfg.checksum)
        meta.setdefault("champion_loaded_at", champion_cfg.loaded_at)

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
                        decision_meta = meta.get("decision") or {}
                        state_out = decision_meta.get("state_out") or {}
                        entry_debug = {
                            "timestamp": timestamp.isoformat(),
                            "summary": state_out.get("fib_gate_summary"),
                            "htf": state_out.get("htf_fib_entry_debug"),
                            "ltf": state_out.get("ltf_fib_entry_debug"),
                            "reasons": decision_meta.get("reasons"),
                        }
                        self.position_tracker.log_entry_fib_debug(entry_debug)

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
                if verbose or os.environ.get("GENESIS_DEBUG_BACKTEST"):
                    try:
                        import traceback, sys  # noqa: PLC0415

                        tb = traceback.extract_tb(sys.exc_info()[2])
                        where = ""
                        if tb:
                            last = tb[-1]
                            where = f" ({last.filename}:{last.lineno} in {last.name})"
                        print(f"\n[ERROR] Bar {i}: {e}{where}")
                    except Exception:
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
        decision_state = (meta.get("decision") or {}).get("state_out") or {}

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

        if exit_actions:
            meaningful_actions = [
                {
                    "action": action.action,
                    "size": action.size,
                    "stop_price": action.stop_price,
                    "reason": action.reason,
                }
                for action in exit_actions
                if action.action not in {"DEBUG", "TRAIL_UPDATE"}
            ]
            if meaningful_actions:
                exit_debug = {
                    "timestamp": timestamp.isoformat(),
                    "price": current_price,
                    "actions": meaningful_actions,
                    "position_side": position.side,
                    "current_atr": current_atr,
                    "fib_gate_summary": decision_state.get("fib_gate_summary"),
                    "htf_entry_debug": decision_state.get("htf_fib_entry_debug"),
                    "ltf_entry_debug": decision_state.get("ltf_fib_entry_debug"),
                    "htf_exit_config": {
                        "fib_threshold_atr": self.htf_exit_config.get("fib_threshold_atr"),
                        "trail_atr_multiplier": self.htf_exit_config.get("trail_atr_multiplier"),
                    },
                }
                self.position_tracker.append_exit_fib_debug(exit_debug)

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
                self.position_tracker.append_exit_fib_debug(
                    {
                        "timestamp": timestamp.isoformat(),
                        "price": current_price,
                        "reason": action.reason,
                        "source": "HTF_FULL_EXIT",
                        "fib_gate_summary": decision_state.get("fib_gate_summary"),
                    }
                )
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
            self.position_tracker.append_exit_fib_debug(
                {
                    "timestamp": timestamp.isoformat(),
                    "price": current_price,
                    "reason": "TRAIL_STOP",
                    "source": "TRAIL_STOP",
                    "fib_gate_summary": decision_state.get("fib_gate_summary"),
                }
            )
            return "TRAIL_STOP"

        # Fallback to traditional exit conditions for safety
        fallback_reason = self._check_traditional_exit_conditions(current_price, result, configs)
        if fallback_reason:
            self.position_tracker.append_exit_fib_debug(
                {
                    "timestamp": timestamp.isoformat(),
                    "price": current_price,
                    "reason": fallback_reason,
                    "source": "TRADITIONAL_EXIT",
                    "fib_gate_summary": decision_state.get("fib_gate_summary"),
                }
            )
        return fallback_reason

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
        stop_loss_pct = float(exit_cfg.get("stop_loss_pct", 0.02))
        take_profit_pct = float(exit_cfg.get("take_profit_pct", 0.05))
        exit_conf_threshold = float(exit_cfg.get("exit_conf_threshold", 0.45))

        # Emergency stop-loss
        pnl_pct = self.position_tracker.get_unrealized_pnl_pct(current_price) / 100.0
        if pnl_pct <= -stop_loss_pct:
            return "EMERGENCY_SL"

        # Emergency take-profit (for very large moves)
        if pnl_pct >= take_profit_pct * 2:  # 2x normal TP
            return "EMERGENCY_TP"

        # Confidence drop (use direction-aware confidence if dict)
        conf_block = result.get("confidence", 1.0)
        if isinstance(conf_block, dict):
            # Prefer confidence in the direction of the open position
            if position.side == "LONG":
                conf_value = float(conf_block.get("buy", conf_block.get("overall", 1.0) or 1.0))
            else:
                conf_value = float(conf_block.get("sell", conf_block.get("overall", 1.0) or 1.0))
        else:
            try:
                conf_value = float(conf_block)
            except Exception:
                conf_value = 1.0
        if conf_value < exit_conf_threshold:
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
                    "entry_fib_debug": t.entry_fib_debug,
                    "exit_fib_debug": t.exit_fib_debug,
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
