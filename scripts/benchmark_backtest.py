import argparse
import os
import time

from core.backtest.engine import BacktestEngine


def run_benchmark(symbol: str, timeframe: str, bars: int, warmup: int) -> None:
    os.environ.setdefault("GENESIS_FAST_WINDOW", "1")
    os.environ.setdefault("GENESIS_PRECOMPUTE_FEATURES", "1")

    engine = BacktestEngine(symbol=symbol, timeframe=timeframe, warmup_bars=warmup)
    engine.load_data()

    if bars and engine.candles_df is not None:
        # Trim to last N bars
        engine.candles_df = engine.candles_df.iloc[-bars:].reset_index(drop=True)

    t0 = time.perf_counter()
    result = engine.run(verbose=False)
    dt = time.perf_counter() - t0

    trades = result.get("summary", {}).get("num_trades", 0)
    print(
        f"[Benchmark] {symbol} {timeframe} bars={len(engine.candles_df)} -> {dt:.2f}s, trades={trades}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--symbol", default="tBTCUSD")
    parser.add_argument("--timeframe", default="1h")
    parser.add_argument("--bars", type=int, default=1000)
    parser.add_argument("--warmup", type=int, default=150)
    args = parser.parse_args()
    run_benchmark(args.symbol, args.timeframe, args.bars, args.warmup)


if __name__ == "__main__":
    main()
