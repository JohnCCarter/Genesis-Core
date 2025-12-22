import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from core.backtest.engine import BacktestEngine
from core.strategy.champion_loader import ChampionLoader


def run_verification():
    # Canonical mode for verification: 1/1
    os.environ["GENESIS_FAST_WINDOW"] = "1"
    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"

    symbol = "tBTCUSD"
    timeframe = "1h"

    print(f"Running verification backtest for {symbol} {timeframe}...")

    # Load champion config
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

    # Check data range
    print(f"Loaded {len(engine.candles_df)} bars")

    # Run
    results = engine.run(configs=config, verbose=True)

    trades = results.get("trades", [])
    print(f"\nTotal Trades: {len(trades)}")

    if len(trades) > 0:
        print("First trade entry reason:", trades[0].get("entry_reasons"))
        print("First trade exit reason:", trades[0].get("exit_reason"))
        print("First trade FIB debug (entry):", trades[0].get("entry_fib_debug"))
        print("First trade FIB debug (exit):", trades[0].get("exit_fib_debug"))
    else:
        print("No trades generated.")
        print("Check logs for 'HTF_FIB_BLOCK' or 'UNAVAILABLE'")


if __name__ == "__main__":
    run_verification()
