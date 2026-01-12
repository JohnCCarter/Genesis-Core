import logging
import os
from pathlib import Path
from typing import Any

import yaml

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None

from core.backtest.engine import BacktestEngine
from core.utils.optuna_helpers import set_global_seeds

logger = logging.getLogger(__name__)


class GenesisPipeline:
    """
    Unified pipeline for running backtests and optimizations.
    Ensures consistent setup, configuration, and execution environment.
    """

    def __init__(self):
        self.root_dir = Path(__file__).resolve().parents[2]

        # Load local .env once for CLI/dev convenience.
        # NOTE: We never override already-set environment variables.
        if load_dotenv is not None:
            try:
                load_dotenv(dotenv_path=self.root_dir / ".env", override=False)
            except Exception:
                # Defensive: never break runtime due to dotenv parsing.
                pass

        self.config_dir = self.root_dir / "config"
        self.defaults = self._load_defaults()

    def _load_defaults(self) -> dict:
        default_path = self.config_dir / "backtest_defaults.yaml"
        if default_path.exists():
            try:
                with open(default_path) as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Failed to load backtest defaults: {e}")
        return {}

    def setup_environment(self, seed: int | None = None):
        """Sets up the execution environment (seeds, env vars)."""
        if seed is None:
            try:
                seed = int(os.environ.get("GENESIS_RANDOM_SEED", "42"))
            except ValueError:
                seed = 42

        os.environ["GENESIS_RANDOM_SEED"] = str(seed)
        set_global_seeds(seed)

        # Canonical mode policy:
        # 1/1 (fast_window + precompute) is the SSOT for quality decisions.
        # Non-canonical modes are allowed ONLY when explicitly requested by the caller.
        explicit_mode = os.environ.get("GENESIS_MODE_EXPLICIT") == "1"

        if not explicit_mode:
            os.environ["GENESIS_FAST_WINDOW"] = "1"
            os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"
        else:
            # If caller marked mode explicit but left variables unset, keep sensible defaults.
            os.environ.setdefault("GENESIS_FAST_WINDOW", "1")
            os.environ.setdefault("GENESIS_PRECOMPUTE_FEATURES", "1")

        logger.info(f"Environment setup complete. Seed: {seed}")

    def create_engine(
        self,
        symbol: str,
        timeframe: str,
        start_date: str | None = None,
        end_date: str | None = None,
        capital: float | None = None,
        commission: float | None = None,
        slippage: float | None = None,
        warmup_bars: int | None = None,
    ) -> BacktestEngine:
        """Creates and initializes a BacktestEngine with defaults."""

        # Use defaults if not provided
        capital = capital if capital is not None else self.defaults.get("capital", 10000.0)
        commission = (
            commission if commission is not None else self.defaults.get("commission", 0.002)
        )
        slippage = slippage if slippage is not None else self.defaults.get("slippage", 0.0005)
        warmup_bars = warmup_bars if warmup_bars is not None else self.defaults.get("warmup", 120)

        use_fast_window = os.environ.get("GENESIS_FAST_WINDOW") == "1"

        engine = BacktestEngine(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            initial_capital=capital,
            commission_rate=commission,
            slippage_rate=slippage,
            warmup_bars=warmup_bars,
            fast_window=use_fast_window,
        )  # Precompute flag is handled by engine.load_data() checking env var or property
        # But we can set it explicitly if needed
        if os.environ.get("GENESIS_PRECOMPUTE_FEATURES") == "1":
            engine.precompute_features = True

        return engine

    def run_backtest(
        self, engine: BacktestEngine, overrides: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Runs the backtest with optional config overrides."""

        if engine.candles_df is None or len(engine.candles_df) == 0:
            logger.info("Loading data...")
            if not engine.load_data():
                raise RuntimeError("Failed to load data")

        logger.info("Running backtest...")
        results = engine.run(configs=overrides)
        return results
