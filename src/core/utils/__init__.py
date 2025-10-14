from pathlib import Path


def curated_candles_path(symbol: str, timeframe: str) -> Path:
    """Return path for curated candle parquet."""
    return Path("data/curated/v1/candles") / f"{symbol}_{timeframe}.parquet"


def legacy_candles_path(symbol: str, timeframe: str) -> Path:
    """Legacy path for candle parquet (deprecated)."""
    return Path("data/candles") / f"{symbol}_{timeframe}.parquet"


def raw_candles_dir() -> Path:
    """Return directory for raw Bitfinex candle dumps."""
    return Path("data/raw/bitfinex/candles")


def get_candles_path(symbol: str, timeframe: str, *, allow_legacy: bool = True) -> Path:
    """Return existing candle parquet for symbol/timeframe (curated preferred)."""
    curated_path = curated_candles_path(symbol, timeframe)
    if curated_path.exists():
        return curated_path

    if allow_legacy:
        legacy_path = legacy_candles_path(symbol, timeframe)
        if legacy_path.exists():
            return legacy_path

    raise FileNotFoundError(
        "Candle data not found. Expected curated dataset at "
        f"{curated_path}. Run fetch_historical.py first."
    )


def iter_available_candles(include_legacy: bool = True):
    """Yield Paths to available candle files (curated first)."""
    curated_dir = Path("data/curated/v1/candles")
    if curated_dir.exists():
        yield from sorted(curated_dir.glob("*.parquet"))

    if include_legacy:
        legacy_dir = Path("data/candles")
        if legacy_dir.exists():
            for path in sorted(legacy_dir.glob("*.parquet")):
                if not curated_dir.exists() or path.name not in {
                    p.name for p in curated_dir.glob("*.parquet")
                }:
                    yield path
