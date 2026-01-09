from __future__ import annotations

import os
import sys
from pathlib import Path


def _bootstrap_src_on_path() -> None:
    """Make `import core` work when running without editable install."""

    try:
        import core  # noqa: F401

        return
    except Exception:
        repo_root = Path(__file__).resolve().parents[1]
        src_dir = repo_root / "src"
        if src_dir.is_dir() and str(src_dir) not in sys.path:
            sys.path.insert(0, str(src_dir))


_bootstrap_src_on_path()

from core.backtest.engine import BacktestEngine
from core.strategy.champion_loader import ChampionLoader


def run_verification() -> None:
    # Canonical mode for verification: 1/1
    os.environ["GENESIS_FAST_WINDOW"] = "1"
    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

    symbol = "tBTCUSD"
    timeframe = "1h"

    print(f"Running verification backtest for {symbol} {timeframe}...")

    loader = ChampionLoader()
    champion_cfg = loader.load(symbol, timeframe)
    config = champion_cfg.config

    print(f"Loaded config for {symbol} {timeframe} from SOURCE: {champion_cfg.source}")

    engine = BacktestEngine(
        symbol=symbol,
        timeframe=timeframe,
        # start_date="2024-01-01",
        # end_date="2024-02-01",  # 1 month test
        fast_window=True,
    )

    # Mirror pipeline/runner behavior explicitly.
    engine.precompute_features = True

    if not engine.load_data():
        print("Failed to load data")
        return

    print(f"Loaded {len(engine.candles_df)} bars")

    results = engine.run(configs=config, verbose=True)

    trades = results.get("trades", [])
    print(f"\nTotal Trades: {len(trades)}")

    if trades:
        print("First trade entry reason:", trades[0].get("entry_reasons"))
        print("First trade exit reason:", trades[0].get("exit_reason"))
        print("First trade FIB debug (entry):", trades[0].get("entry_fib_debug"))
        print("First trade FIB debug (exit):", trades[0].get("exit_fib_debug"))
    else:
        print("No trades generated.")
        print("Check logs for 'HTF_FIB_BLOCK' or 'UNAVAILABLE'")


if __name__ == "__main__":
    run_verification()
