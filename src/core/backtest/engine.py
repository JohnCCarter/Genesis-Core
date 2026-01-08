"""
Backtest engine for Genesis-Core.

Replays historical candle data bar-by-bar through the existing strategy pipeline.
"""

import os
import subprocess
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

from core.backtest.htf_exit_engine import ExitAction
from core.backtest.htf_exit_engine import HTFFibonacciExitEngine as LegacyExitEngine
from core.utils.logging_redaction import get_logger

try:
    from core.strategy.htf_exit_engine import HTFFibonacciExitEngine as NewExitEngine
except ImportError:
    NewExitEngine = None  # Fallback if not found

from core.backtest.position_tracker import PositionTracker
from core.indicators.exit_fibonacci import calculate_exit_fibonacci_levels
from core.strategy.champion_loader import ChampionLoader
from core.strategy.evaluate import evaluate_pipeline

_LOGGER = get_logger(__name__)


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

        # Validate mode consistency to prevent mixed-mode bugs
        self._validate_mode_consistency()

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

        # Precomputed features (set in load_data when precompute is enabled).
        # Must exist even when tests inject candles_df directly (bypassing load_data).
        self._precomputed_features: dict[str, list[float]] | None = None
        self.precompute_features = False
        self.position_tracker = PositionTracker(
            initial_capital=initial_capital,
            commission_rate=commission_rate,
            slippage_rate=slippage_rate,
        )

        self.state: dict = {}
        self.bar_count = 0

        self.champion_loader = ChampionLoader()
        # Initialize HTF exit engine configuration (moved out of _deep_merge)
        self._init_htf_exit_engine(htf_exit_config)

    def _validate_mode_consistency(self) -> None:
        """Validate that fast_window and GENESIS_PRECOMPUTE_FEATURES are consistent."""
        precompute = os.getenv("GENESIS_PRECOMPUTE_FEATURES") == "1"

        if self.fast_window and not precompute:
            raise ValueError(
                "BacktestEngine: fast_window=True requires GENESIS_PRECOMPUTE_FEATURES=1. "
                "Set the environment variable or use fast_window=False.\n"
                'Tip: Add \'os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"\' before creating engine.'
            )

        if not self.fast_window and precompute:
            warnings.warn(
                "BacktestEngine: GENESIS_PRECOMPUTE_FEATURES=1 is set but fast_window=False. "
                "This creates inconsistent execution paths. Consider using fast_window=True for determinism.",
                UserWarning,
                stacklevel=3,
            )

    def _deep_merge(self, base: dict, override: dict) -> dict:
        """Deep merge override dict into base dict, preserving nested structures."""
        merged = dict(base)
        for key, value in (override or {}).items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _init_htf_exit_engine(self, htf_exit_config: dict | None) -> None:
        """Initialize HTF Fibonacci Exit Engine with defaults + optional override."""
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

        use_new_engine = os.environ.get("GENESIS_HTF_EXITS") == "1"
        if use_new_engine and NewExitEngine:
            _LOGGER.info("Using NEW HTF Exit Engine (Phase 1)")
            self.htf_exit_engine = NewExitEngine(self.htf_exit_config)
            self._use_new_exit_engine = True
        else:
            _LOGGER.info("Using LEGACY HTF Exit Engine")
            self.htf_exit_engine = LegacyExitEngine(self.htf_exit_config)
            self._use_new_exit_engine = False

    def load_data(self) -> bool:
        """
        Load historical candle data from Parquet (two-layer structure support).

        Returns:
            True if data loaded successfully, False otherwise
        """
        # Find data file (try frozen first, then two-layer structure, fallback to legacy)
        base_dir = Path(__file__).parent.parent.parent.parent / "data"

        # 1. Frozen Data (Priority 1)
        data_file_frozen = base_dir / "raw" / f"{self.symbol}_{self.timeframe}_frozen.parquet"

        # 2. Curated Data (Priority 2)
        data_file_curated = (
            base_dir / "curated" / "v1" / "candles" / f"{self.symbol}_{self.timeframe}.parquet"
        )

        # 3. Legacy Data (Priority 3)
        data_file_legacy = base_dir / "candles" / f"{self.symbol}_{self.timeframe}.parquet"

        if data_file_frozen.exists():
            data_file = data_file_frozen
            _LOGGER.debug("Using frozen snapshot: %s", data_file.name)
        elif data_file_curated.exists():
            data_file = data_file_curated
        elif data_file_legacy.exists():
            data_file = data_file_legacy
        else:
            _LOGGER.error(
                "Data file not found. Tried frozen=%s curated=%s legacy=%s",
                data_file_frozen,
                data_file_curated,
                data_file_legacy,
            )
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
            _LOGGER.debug("Loaded %s candles from %s", f"{len(base_df):,}", data_file.name)
        else:
            _LOGGER.debug(
                "Reusing %s candles for %s %s",
                f"{len(base_df):,}",
                self.symbol,
                self.timeframe,
            )

        # Load HTF (1D) candles if new engine is enabled
        self.htf_candles_df = None
        if getattr(self, "_use_new_exit_engine", False):
            htf_timeframe = "1D"
            # Assuming HTF data follows same naming convention
            htf_file = (
                base_dir / "curated" / "v1" / "candles" / f"{self.symbol}_{htf_timeframe}.parquet"
            )
            if htf_file.exists():
                try:
                    self.htf_candles_df = pd.read_parquet(
                        htf_file,
                        columns=["timestamp", "open", "high", "low", "close"],
                        engine="pyarrow",
                    )
                    _LOGGER.debug(
                        "Loaded %s HTF candles from %s",
                        f"{len(self.htf_candles_df):,}",
                        htf_file.name,
                    )
                except Exception as e:
                    _LOGGER.warning("Failed to load HTF candles from %s: %s", htf_file, e)
            else:
                _LOGGER.debug("HTF candles file not found: %s", htf_file)

        # Work off cached DataFrame (avoid eager copy); filters below create sliced views/frames
        self.candles_df = base_df

        # Filter by date range if specified
        if self.start_date:
            start_dt = pd.to_datetime(self.start_date)
            self.candles_df = self.candles_df[self.candles_df["timestamp"] >= start_dt]
            _LOGGER.debug("Applied start_date filter: %s", self.start_date)

        if self.end_date:
            end_dt = pd.to_datetime(self.end_date)
            self.candles_df = self.candles_df[self.candles_df["timestamp"] <= end_dt]
            _LOGGER.debug("Applied end_date filter: %s", self.end_date)

        _LOGGER.debug("Filtered to %s candles", f"{len(self.candles_df):,}")

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
        # IMPORTANT: Treat GENESIS_PRECOMPUTE_FEATURES=1 as authoritative.
        # Some callers historically only set the env var; make sure we enable
        # engine-level precompute toggle consistently.
        if os.getenv("GENESIS_PRECOMPUTE_FEATURES") == "1":
            self.precompute_features = True

        self._precomputed_features: dict[str, list[float]] | None = None
        if getattr(self, "precompute_features", False):
            try:
                _LOGGER.info("Precompute enabled: starting feature precomputation")
                closes_all = self.candles_df["close"].tolist()
                highs_all = self.candles_df["high"].tolist()
                lows_all = self.candles_df["low"].tolist()
                import numpy as _np

                from core.indicators.adx import calculate_adx as _calc_adx
                from core.indicators.atr import calculate_atr as _calc_atr
                from core.indicators.bollinger import bollinger_bands as _bb
                from core.indicators.ema import calculate_ema as _calc_ema
                from core.indicators.fibonacci import FibonacciConfig as _FibCfg
                from core.indicators.fibonacci import detect_swing_points as _detect_swings
                from core.indicators.rsi import calculate_rsi as _calc_rsi

                # Try on-disk cache first
                cache_dir = Path(__file__).resolve().parents[3] / "cache" / "precomputed"
                cache_dir.mkdir(parents=True, exist_ok=True)
                # IMPORTANT:
                # Cache key must include data identity, not only length.
                # Different periods can have the same number of bars; reusing the wrong
                # cached features can drastically change strategy decisions.
                key = self._precompute_cache_key(self.candles_df)
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
                        _LOGGER.debug("Loaded precomputed features from cache: %s", cache_path.name)
                    except Exception:
                        loaded = False

                if not loaded:
                    _LOGGER.info("Precompute: computing indicators")
                    import time

                    start_time = time.perf_counter()
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

                    elapsed = time.perf_counter() - start_time
                    _LOGGER.info("Precompute: computed indicators in %.2fs", elapsed)

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
                        _LOGGER.debug("Cached precomputed features: %s", cache_path.name)
                    except Exception:  # nosec B110
                        pass  # Ignore cache write errors (not critical)

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

                # Precompute HTF Mapping if available
                if self.htf_candles_df is not None:
                    from core.indicators.htf_fibonacci import compute_htf_fibonacci_mapping

                    _LOGGER.info("Precompute: mapping HTF Fibonacci levels")
                    htf_map = compute_htf_fibonacci_mapping(
                        self.htf_candles_df, self.candles_df, fib_cfg
                    )
                    # Store in precomputed features (as lists)
                    for col in [
                        "htf_fib_0382",
                        "htf_fib_05",
                        "htf_fib_0618",
                        "htf_swing_high",
                        "htf_swing_low",
                    ]:
                        if col in htf_map.columns:
                            self._precomputed_features[col] = htf_map[col].fillna(0.0).tolist()
                    _LOGGER.info("Precompute: HTF Fibonacci mapping complete")

                _LOGGER.info("Precompute: features ready")
            except Exception as e:
                # Non-fatal: skip precompute if indicators unavailable
                _LOGGER.warning("Precomputation failed (non-fatal): %s", e)
                self._precomputed_features = None

        if len(self.candles_df) < self.warmup_bars:
            _LOGGER.warning(
                "Not enough data for warmup (%s < %s)",
                len(self.candles_df),
                self.warmup_bars,
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

    def _precompute_cache_key(self, df: pd.DataFrame) -> str:
        """Build a stable on-disk cache key for precomputed features.

        Why:
            A key based only on `len(df)` is unsafe because multiple date ranges can
            share the same number of bars, which would cause loading wrong cached
            indicators/fib swings.
        """

        if df is None or len(df) == 0:
            # Defensive fallback; should not happen in normal flow.
            return f"{self.symbol}_{self.timeframe}_empty"

        ts0 = df["timestamp"].iloc[0]
        ts1 = df["timestamp"].iloc[-1]
        # pandas.Timestamp.value is ns since epoch; stable and file-name friendly.
        start_ns = int(getattr(ts0, "value", 0))
        end_ns = int(getattr(ts1, "value", 0))
        return f"{self.symbol}_{self.timeframe}_{len(df)}_{start_ns}_{end_ns}"

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

        Performance optimizations:
        - Returns NumPy arrays directly (avoid .tolist() overhead)
        - Uses array slicing which creates views, not copies
        - Timestamp list only created when needed

        Args:
            end_idx: Current bar index (inclusive)
            window_size: Number of bars to include in window

        Returns:
            Candles dict with OHLCV as NumPy arrays or lists
        """
        start_idx = max(0, end_idx - window_size + 1)

        if self.fast_window and self._col_close is not None:
            # Slice precomputed arrays (fast path) - return NumPy views (zero-copy)
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

        # Optimized: use pre-computed numpy arrays WITHOUT converting to lists
        # NumPy arrays work directly with indicator functions and are much faster
        if self._np_arrays is not None:
            return {
                "open": self._np_arrays["open"][start_idx : end_idx + 1],
                "high": self._np_arrays["high"][start_idx : end_idx + 1],
                "low": self._np_arrays["low"][start_idx : end_idx + 1],
                "close": self._np_arrays["close"][start_idx : end_idx + 1],
                "volume": self._np_arrays["volume"][start_idx : end_idx + 1],
                "timestamp": self._np_arrays["timestamp"][start_idx : end_idx + 1].tolist(),
            }

        # Fallback: slice DataFrame window (slowest path)
        window = self.candles_df.iloc[start_idx : end_idx + 1]
        return {
            "open": window["open"].values,
            "high": window["high"].values,
            "low": window["low"].values,
            "close": window["close"].values,
            "volume": window["volume"].values,
            "timestamp": window["timestamp"].values.tolist(),
        }

    def run(
        self,
        policy: dict | None = None,
        configs: dict | None = None,
        verbose: bool = False,
        pruning_callback: Any | None = None,
    ) -> dict:
        """
        Run backtest.

        Args:
            policy: Strategy policy (symbol, timeframe)
            configs: Strategy configs (thresholds, risk, etc.)
            verbose: Print detailed progress
            pruning_callback: Optional callback(step, value) -> bool. If returns True, abort.

        Returns:
            Dict with backtest results
        """
        # Reset state for isolation (Step 3: Eliminate Hidden State)
        self.position_tracker = PositionTracker(
            initial_capital=self.position_tracker.initial_capital,
            commission_rate=self.position_tracker.commission_rate,
            slippage_rate=self.position_tracker.slippage_rate,
        )
        self.state = {}
        self.bar_count = 0

        if self.candles_df is None:
            _LOGGER.error("No data loaded. Call load_data() first.")
            return {"error": "no_data"}

        if len(self.candles_df) == 0:
            _LOGGER.error(
                "No candles available (empty dataset). Check date filters and data range."
            )
            return {"error": "no_data"}

        # Ensure numpy arrays are prepared for fast window extraction
        if self._np_arrays is None:
            self._prepare_numpy_arrays()

        # Default policy/configs
        policy = policy or {}
        policy.setdefault("symbol", self.symbol)
        policy.setdefault("timeframe", self.timeframe)

        configs = configs or {}

        champion_cfg = self.champion_loader.load_cached(self.symbol, self.timeframe)
        # Deep merge configs to preserve nested overrides
        configs = self._deep_merge(champion_cfg.config, configs)

        # IMPORTANT: Apply HTF exit config from merged runtime/trial configs.
        # The engine is constructed before configs are known (CLI loads config after create_engine),
        # so we must (re)initialize the HTF exit engine here per run to respect overrides.
        self._init_htf_exit_engine(configs.get("htf_exit_config"))

        # Inject precomputed features AFTER merge to ensure they're preserved
        if getattr(self, "precompute_features", False) and getattr(
            self, "_precomputed_features", None
        ):
            configs["precomputed_features"] = dict(self._precomputed_features)

        meta = configs.setdefault("meta", {})
        meta.setdefault("champion_source", champion_cfg.source)
        meta.setdefault("champion_version", champion_cfg.version)
        meta.setdefault("champion_checksum", champion_cfg.checksum)
        meta.setdefault("champion_loaded_at", champion_cfg.loaded_at)

        _LOGGER.info(
            "Running backtest: %s %s | period=%s..%s | bars=%s (warmup=%s) | capital=$%s",
            self.symbol,
            self.timeframe,
            self.candles_df["timestamp"].min(),
            self.candles_df["timestamp"].max(),
            f"{len(self.candles_df):,}",
            self.warmup_bars,
            f"{self.position_tracker.initial_capital:,.2f}",
        )

        # Progress bar
        pbar = tqdm(
            total=len(self.candles_df),
            desc="Backtest",
            unit="bars",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]",
        )

        # Track bars held for current position

        # Performance optimization: Pre-extract numpy arrays to avoid repeated iloc calls
        # This significantly speeds up the main backtest loop
        timestamps_array = self.candles_df["timestamp"].values
        open_prices_array = self.candles_df["open"].values
        high_prices_array = self.candles_df["high"].values
        low_prices_array = self.candles_df["low"].values
        close_prices_array = self.candles_df["close"].values
        volume_array = (
            self.candles_df["volume"].values if "volume" in self.candles_df.columns else None
        )
        num_bars = len(self.candles_df)

        # Replay bars
        for i in range(num_bars):
            # Fast-path: pull values from numpy buffers if available
            if self._np_arrays is not None:
                timestamp = pd.Timestamp(self._np_arrays["timestamp"][i])
                close_price = float(self._np_arrays["close"][i])
                open_price = float(self._np_arrays["open"][i])
                high_price = float(self._np_arrays["high"][i])
                low_price = float(self._np_arrays["low"][i])
                volume_val = float(
                    self._np_arrays.get("volume", [0.0])[i] if "volume" in self._np_arrays else 0.0
                )
            else:
                bar = self.candles_df.iloc[i]
                timestamp = timestamps_array[i]
                close_price = close_prices_array[i]
                open_price = open_prices_array[i]
                high_price = high_prices_array[i]
                low_price = low_prices_array[i]
                volume_val = bar.get("volume", 0.0)

            # Skip warmup period
            if i < self.warmup_bars:
                pbar.update(1)
                continue

            # Pruning check (every 100 bars to minimize overhead)
            if pruning_callback and i % 100 == 0:
                # Report current return as proxy for score
                current_equity = self.position_tracker.current_equity
                current_return = (
                    current_equity - self.position_tracker.initial_capital
                ) / self.position_tracker.initial_capital
                if pruning_callback(i, current_return):
                    pbar.close()
                    return {
                        "error": "pruned",
                        "pruned_at": i,
                        "metrics": {"total_return": current_return},
                    }

            # Build candles window for pipeline
            candles_window = self._build_candles_window(i)

            # Inject global index for precomputed features correctness
            # This ensures features_asof uses the correct index in precomputed arrays
            configs["_global_index"] = i

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

                # Extract decision metadata early so we can attach correct entry reasons.
                decision_meta = meta.get("decision", {}) or {}
                reasons = decision_meta.get("reasons") or []
                state_out = decision_meta.get("state_out", {}) or {}

                # Extract confidence (can be dict or float)
                # NOTE: confidence/regime may be needed for logging/debugging, but must never
                # throw during backtest. Keep parsing best-effort and side-effect free.
                conf_val = result.get("confidence", 0.5)
                if isinstance(conf_val, dict):
                    _conf_overall = conf_val.get("overall", 0.5)
                else:
                    try:
                        _conf_overall = float(conf_val) if conf_val is not None else 0.5
                    except (TypeError, ValueError):
                        _conf_overall = 0.5

                regime_val = result.get("regime", "BALANCED")
                if isinstance(regime_val, dict):
                    _regime_name = str(regime_val.get("name", "BALANCED") or "BALANCED")
                else:
                    _regime_name = str(regime_val) if regime_val is not None else "BALANCED"

                # === EXIT LOGIC (check BEFORE new entry) ===
                if self.position_tracker.has_position():
                    # Prepare bar data for exit engine (using pre-extracted arrays)
                    volume_snapshot = volume_array[i] if volume_array is not None else volume_val
                    bar_data = {
                        "timestamp": timestamp,
                        "open": open_price,
                        "high": high_price,
                        "low": low_price,
                        "close": close_price,
                        "volume": volume_snapshot,
                    }

                    exit_reason = self._check_htf_exit_conditions(
                        current_price=close_price,
                        timestamp=timestamp,
                        bar_data=bar_data,
                        result=result,
                        meta=meta,
                        configs=configs,
                        bar_index=i,
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
                    # Attach reasons for this bar BEFORE opening a position.
                    # PositionTracker consumes and clears these when opening a trade.
                    if hasattr(self.position_tracker, "set_pending_reasons"):
                        self.position_tracker.set_pending_reasons(reasons or [])

                    exec_result = self.position_tracker.execute_action(
                        action=action,
                        size=size,
                        price=close_price,
                        timestamp=timestamp,
                        symbol=self.symbol,
                        meta={"entry_regime": _regime_name},
                    )

                    # If we attempted an entry but did not open a new position, clear pending reasons
                    # to avoid leaking stale reasons into a later entry.
                    if not exec_result.get("executed") and hasattr(
                        self.position_tracker, "clear_pending_reasons"
                    ):
                        self.position_tracker.clear_pending_reasons()

                    if exec_result.get("executed"):
                        if getattr(self, "_use_new_exit_engine", False):
                            self.htf_exit_engine.reset_state()

                        # Initialize exit context for new position
                        self._initialize_position_exit_context(result, meta, close_price, timestamp)
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
                self.state = state_out
                self.bar_count += 1

            except Exception as e:
                if verbose or os.environ.get("GENESIS_DEBUG_BACKTEST"):
                    try:
                        import sys  # noqa: PLC0415
                        import traceback  # noqa: PLC0415

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

        # Report feature hit counts
        try:
            from core.strategy.features_asof import get_feature_hit_counts

            fast_hits, slow_hits = get_feature_hit_counts()
            _LOGGER.debug("Feature paths: fast=%s slow=%s", fast_hits, slow_hits)
        except ImportError:
            pass

        # Close all positions at end
        if self._np_arrays is not None:
            final_close = float(self._np_arrays["close"][-1])
            final_ts = pd.Timestamp(self._np_arrays["timestamp"][-1])
        else:
            final_bar = self.candles_df.iloc[-1]
            final_close = final_bar["close"]
            final_ts = final_bar["timestamp"]
        self.position_tracker.close_all_positions(final_close, final_ts)

        _LOGGER.info("Backtest complete - %s bars processed", self.bar_count)

        return self._build_results()

    def _check_htf_exit_conditions(
        self,
        current_price: float,
        timestamp: datetime,
        bar_data: dict,
        result: dict,
        meta: dict,
        configs: dict,
        bar_index: int | None = None,
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

        # Get exit config (top-level in merged configs)
        exit_cfg = configs.get("exit", {})
        enabled = exit_cfg.get("enabled", True)

        if not enabled:
            return None

        # Prefer explicit bar_index (passed from main loop). Fallback to configs['_global_index'].
        idx = bar_index
        if idx is None:
            try:
                idx = int(configs.get("_global_index"))
            except Exception:
                idx = None

        # Get HTF Fibonacci context - prefer precomputed if available
        htf_fib_context = {}
        if (
            idx is not None
            and self._precomputed_features
            and "htf_fib_0382" in self._precomputed_features
        ):
            # Fast path: use precomputed HTF mapping
            try:
                htf_fib_context = {
                    "available": True,
                    "levels": {
                        0.382: self._precomputed_features["htf_fib_0382"][idx],
                        0.5: self._precomputed_features["htf_fib_05"][idx],
                        0.618: self._precomputed_features["htf_fib_0618"][idx],
                    },
                    "swing_high": self._precomputed_features.get(
                        "htf_swing_high", [0.0] * (idx + 1)
                    )[idx],
                    "swing_low": self._precomputed_features.get("htf_swing_low", [0.0] * (idx + 1))[
                        idx
                    ],
                }
            except (IndexError, KeyError):
                htf_fib_context = {"available": False}
        else:
            # Fallback: use meta from evaluate_pipeline
            features_meta = meta.get("features", {})
            htf_fib_context = features_meta.get("htf_fibonacci", {})

        # Calculate ATR for exit logic (use last 14 bars AS OF current bar)
        from core.indicators.atr import calculate_atr

        current_atr = 100.0
        if idx is not None and self._np_arrays is not None:
            window_size = min(14, idx + 1)
            if window_size >= 2:
                i0 = max(0, idx - window_size + 1)
                i1 = idx + 1
                recent_highs = self._np_arrays["high"][i0:i1]
                recent_lows = self._np_arrays["low"][i0:i1]
                recent_closes = self._np_arrays["close"][i0:i1]
                atr_values = calculate_atr(recent_highs, recent_lows, recent_closes, period=14)
                current_atr = float(atr_values[-1]) if len(atr_values) > 0 else 100.0
        elif self.candles_df is not None:
            # Defensive fallback for callers that don't supply an index.
            window_size = min(14, len(self.candles_df))
            if window_size >= 2:
                recent_highs = self.candles_df["high"].iloc[-window_size:].values
                recent_lows = self.candles_df["low"].iloc[-window_size:].values
                recent_closes = self.candles_df["close"].iloc[-window_size:].values
                atr_values = calculate_atr(recent_highs, recent_lows, recent_closes, period=14)
                current_atr = float(atr_values[-1]) if len(atr_values) > 0 else 100.0

        # Prepare indicators for exit engine
        features = result.get("features", {})
        indicators = {
            "atr": current_atr,
            "ema50": features.get("ema", current_price),  # Use ema feature (EMA50)
            "ema_slope50_z": features.get("ema_slope50_z", 0.0),
        }

        # Check HTF exit conditions
        if getattr(self, "_use_new_exit_engine", False):
            # Adapter for New Engine (Phase 1)
            side_int = 1 if position.side == "LONG" else -1
            # Wrap dictionary in Series for compatibility
            htf_levels = htf_fib_context.get("levels", {})
            htf_data = pd.Series(htf_levels)

            signal = self.htf_exit_engine.check_exits(
                current_price=current_price,
                position_size=float(position.current_size),
                entry_price=float(position.entry_price),
                side=side_int,
                current_atr=current_atr,
                htf_data=htf_data,
            )

            exit_actions = []
            if signal.action in ["PARTIAL_EXIT", "FULL_EXIT"]:
                # Map to Legacy ExitAction
                # PARTIAL_EXIT usually implies a size. FULL_EXIT implies size=current.
                action_map = "PARTIAL" if signal.action == "PARTIAL_EXIT" else "FULL_EXIT"

                # Calculate size amount
                if signal.quantity_pct > 0:
                    size_val = float(position.current_size) * signal.quantity_pct
                else:
                    size_val = float(
                        position.current_size
                    )  # Default to full? No, use 0 if partial not specified.

                exit_actions.append(
                    ExitAction(action=action_map, size=size_val, reason=signal.reason)
                )

            elif signal.action == "UPDATE_STOP":
                exit_actions.append(
                    ExitAction(
                        action="TRAIL_UPDATE",
                        stop_price=signal.new_stop_price,
                        reason=signal.reason,
                    )
                )
        else:
            # Legacy Call
            exit_actions = self.htf_exit_engine.check_exits(
                position, bar_data, htf_fib_context, indicators
            )
        meta.setdefault("signal", {})
        meta["signal"]["current_atr"] = current_atr

        # Execute exit actions
        exit_cfg = configs.get("exit", {})
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
                    _LOGGER.info(
                        "PARTIAL exit: %s | size=%.3f @ $%s | pnl=$%s",
                        action.reason,
                        float(trade.size),
                        f"{float(trade.exit_price):,.0f}",
                        f"{float(trade.pnl):,.2f}",
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

        # Get exit config (top-level in merged configs)
        exit_cfg = configs.get("exit", {})
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
        conf_block = result.get("confidence_exit", result.get("confidence", 1.0))
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

        # Resolve git executable to an absolute path (Bandit B607) and keep failure non-fatal.
        git_hash = "unknown"
        try:
            import shutil

            git_exe = shutil.which("git")
            if git_exe:
                git_hash = subprocess.check_output(
                    [git_exe, "rev-parse", "HEAD"], text=True
                ).strip()
        except (OSError, subprocess.SubprocessError):
            git_hash = "unknown"

        return {
            "backtest_info": {
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "start_date": str(self.candles_df["timestamp"].min()),
                "end_date": str(self.candles_df["timestamp"].max()),
                "bars_total": len(self.candles_df),
                "bars_processed": self.bar_count,
                "warmup_bars": self.warmup_bars,
                "initial_capital": self.position_tracker.initial_capital,
                "commission_rate": self.position_tracker.commission_rate,
                "slippage_rate": self.position_tracker.slippage_rate,
                "execution_mode": {
                    "fast_window": bool(self.fast_window),
                    "env_precompute_features": os.environ.get("GENESIS_PRECOMPUTE_FEATURES"),
                    "precompute_enabled": bool(getattr(self, "precompute_features", False)),
                    "precomputed_ready": bool(getattr(self, "_precomputed_features", None)),
                    "mode_explicit": os.environ.get("GENESIS_MODE_EXPLICIT"),
                },
                "git_hash": git_hash,
                "seed": os.environ.get("GENESIS_RANDOM_SEED", "unknown"),
                "timestamp": datetime.now().isoformat(),
            },
            "summary": summary,
            # Add top-level metrics for convenience (duplicates summary fields)
            "metrics": {
                "total_trades": summary.get("num_trades", 0),
                "num_trades": summary.get("num_trades", 0),
                "total_return": summary.get("total_return", 0.0) / 100.0,  # Convert to fraction
                "total_return_pct": summary.get("total_return", 0.0),
                "win_rate": summary.get("win_rate", 0.0) / 100.0,  # Convert to fraction
                "profit_factor": summary.get("profit_factor", 0.0),
                "max_drawdown": summary.get("max_drawdown", 0.0) / 100.0,  # Convert to fraction
            },
            "trades": [
                {
                    "symbol": t.symbol,
                    "side": t.side,
                    "size": t.size,
                    "entry_price": t.entry_price,
                    "entry_time": t.entry_time.isoformat(),
                    "entry_regime": t.entry_regime,
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
            _LOGGER.debug("HTF not available (using fallback exits): %s", htf_fib_context)
            return

        # Extract swing from HTF context
        swing_high = htf_fib_context.get("swing_high", 0.0)
        swing_low = htf_fib_context.get("swing_low", 0.0)

        if swing_high <= swing_low or swing_high <= 0 or swing_low <= 0:
            # Invalid swing - position will use fallback exits
            _LOGGER.debug(
                "Invalid HTF swing (using fallback exits): high=%s, low=%s", swing_high, swing_low
            )
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
