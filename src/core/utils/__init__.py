from __future__ import annotations

import tempfile
from pathlib import Path


def timeframe_filename_suffix(timeframe: str) -> str:
    """Return filename-safe suffix (handles case collisions like 1m vs 1M)."""

    return "1mo" if timeframe == "1M" else timeframe


_CASE_SENSITIVE_DIR_CACHE: dict[str, bool] = {}


def is_case_sensitive_directory(directory: Path) -> bool:
    """Best-effort check if a directory's filesystem is case-sensitive.

    This matters for distinguishing monthly ("1M") vs minute ("1m") filenames.
    On case-insensitive filesystems (common on Windows/macOS default), we MUST NOT
    attempt to open "*_1M.*" as it can alias to "*_1m.*".
    """

    try:
        d = directory
        if not d.exists():
            d = d.parent
        d = d.resolve()
        key = str(d)
        cached = _CASE_SENSITIVE_DIR_CACHE.get(key)
        if cached is not None:
            return cached

        with tempfile.TemporaryDirectory(dir=d) as tmp:
            base = Path(tmp)
            probe = base / "MiXeDcAsE"
            probe.write_text("x", encoding="utf-8")
            case_sensitive = not (base / "mixedcase").exists()

        _CASE_SENSITIVE_DIR_CACHE[key] = case_sensitive
        return case_sensitive
    except Exception:
        # If we can't create a temp dir in the target directory (read-only, missing
        # perms, etc), fall back to probing the system temp directory.
        try:
            with tempfile.TemporaryDirectory() as tmp:
                base = Path(tmp)
                probe = base / "MiXeDcAsE"
                probe.write_text("x", encoding="utf-8")
                return not (base / "mixedcase").exists()
        except Exception:
            # Conservative default: treat as case-insensitive to avoid loading 1m data
            # when user asked for 1M/monthly.
            return False


def _month_suffix_candidates(timeframe: str) -> list[str]:
    if timeframe not in {"1M", "1mo"}:
        return [timeframe_filename_suffix(timeframe)]

    # Canonical, cross-platform-safe naming.
    suffixes = ["1mo"]

    # Only try the legacy/Bitfinex canonical suffix on case-sensitive filesystems.
    if is_case_sensitive_directory(Path("data")):
        suffixes.append("1M")
    return suffixes


def curated_candles_path(symbol: str, timeframe: str) -> Path:
    """Return path for curated candle parquet."""

    suffix = timeframe_filename_suffix(timeframe)
    return Path("data/curated/v1/candles") / f"{symbol}_{suffix}.parquet"


def legacy_candles_path(symbol: str, timeframe: str) -> Path:
    """Legacy path for candle parquet (deprecated)."""

    suffix = timeframe_filename_suffix(timeframe)
    return Path("data/candles") / f"{symbol}_{suffix}.parquet"


def raw_candles_dir() -> Path:
    """Return directory for raw Bitfinex candle dumps."""
    return Path("data/raw/bitfinex/candles")


def get_candles_path(symbol: str, timeframe: str, *, allow_legacy: bool = True) -> Path:
    """Return existing candle parquet for symbol/timeframe (curated preferred)."""
    suffixes = _month_suffix_candidates(timeframe)

    for suffix in suffixes:
        curated_path = Path("data/curated/v1/candles") / f"{symbol}_{suffix}.parquet"
        if curated_path.exists():
            return curated_path

    if allow_legacy:
        for suffix in suffixes:
            legacy_path = Path("data/candles") / f"{symbol}_{suffix}.parquet"
            if legacy_path.exists():
                return legacy_path

    curated_path = curated_candles_path(symbol, timeframe)

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
