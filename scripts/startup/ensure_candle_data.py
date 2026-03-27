#!/usr/bin/env python3
"""
Ensure candle data is present before running an Optuna optimizer or preflight check.

Inspects an optimizer config YAML, determines which candle parquet files are required
(main timeframe + 1D HTF when htf_exit_config is present), checks whether they exist
and cover the required date range, and fetches missing data via the Bitfinex public API
using the existing fetch_historical.py tooling.

Usage:
    # Check and fetch missing data
    python scripts/startup/ensure_candle_data.py config/optimizer/3h/legacy_decision_slice1/tBTCUSD_3h_legacy_decision_slice1_2024_2025.yaml

    # Dry-run: report what is missing without fetching
    python scripts/startup/ensure_candle_data.py --dry-run config/optimizer/...yaml

    # Fail if API is unavailable instead of attempting a fetch
    python scripts/startup/ensure_candle_data.py --no-fetch config/optimizer/...yaml
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from script path")


ROOT = _find_repo_root(Path(__file__).resolve())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Warmup buffer in days added to the fetch start so the engine always has
# enough lookback bars before the requested sample_start.
_WARMUP_BUFFER_DAYS = 60

# Default months to fetch when no date range can be inferred from the config.
_DEFAULT_FETCH_MONTHS = 30


def _pick_data_file(symbol: str, timeframe: str) -> Path | None:
    """Return the first existing candle parquet path for symbol/timeframe."""
    base_dir = ROOT / "data"
    candidates = [
        base_dir / "raw" / f"{symbol}_{timeframe}_frozen.parquet",
        base_dir / "curated" / "v1" / "candles" / f"{symbol}_{timeframe}.parquet",
        base_dir / "candles" / f"{symbol}_{timeframe}.parquet",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def _get_time_range(path: Path) -> tuple[datetime, datetime] | None:
    """Return (min_ts, max_ts) for a candle parquet file."""
    try:
        import pandas as pd

        df = pd.read_parquet(path, columns=["timestamp"])
        if len(df) == 0 or "timestamp" not in df.columns:
            return None
        ts = df["timestamp"]
        min_ts = ts.min()
        max_ts = ts.max()
        if pd.isna(min_ts) or pd.isna(max_ts):
            return None
        return (pd.Timestamp(min_ts).to_pydatetime(), pd.Timestamp(max_ts).to_pydatetime())
    except Exception:
        return None


def _to_naive(dt: datetime) -> datetime:
    return dt.replace(tzinfo=None) if dt.tzinfo is not None else dt


def _parse_required_range(cfg: dict[str, Any]) -> tuple[datetime, datetime] | None:
    """
    Extract the widest required date range from a config dict.

    Covers both sample_start/sample_end and validation.sample_start/sample_end
    so we fetch enough data for all configured phases in one go.
    """
    meta = cfg.get("meta", {})
    runs = meta.get("runs", {})
    validation = runs.get("validation", {})

    dates: list[datetime] = []

    for key in ("sample_start", "sample_end"):
        val = runs.get(key)
        if val:
            try:
                dates.append(datetime.fromisoformat(str(val).strip()))
            except Exception:
                pass

    val_enabled = validation.get("enabled", False)
    if val_enabled:
        for key in ("sample_start", "sample_end"):
            val = validation.get(key)
            if val:
                try:
                    dates.append(datetime.fromisoformat(str(val).strip()))
                except Exception:
                    pass

    if not dates:
        return None

    return min(dates), max(dates)


def _resolve_param_value(value: Any) -> Any:
    """
    Unwrap optimizer parameter format ``{"type": "fixed", "value": X}`` to X.

    Plain values (str, int, float, bool, None) are returned as-is.
    """
    if isinstance(value, dict) and value.get("type") == "fixed" and "value" in value:
        return value["value"]
    return value


def _htf_timeframe(cfg: dict[str, Any]) -> str | None:
    """
    Return the HTF timeframe string if the config requires HTF data, else None.

    Two sources are checked:
    1. parameters.htf_exit_config (non-empty dict => requires HTF candles)
    2. parameters.multi_timeframe.htf_selector fallback_timeframe

    Handles both plain string values and optimizer param format
    ``{"type": "fixed", "value": "1D"}``.
    """
    parameters = cfg.get("parameters", {})
    htf_exit = parameters.get("htf_exit_config")
    if isinstance(htf_exit, dict) and len(htf_exit) > 0:
        # Check for an explicit per-timeframe mapping first
        mtf = parameters.get("multi_timeframe", {})
        selector = mtf.get("htf_selector", {})
        fallback_raw = selector.get("fallback_timeframe")
        if fallback_raw is not None:
            fallback = _resolve_param_value(fallback_raw)
            if fallback:
                return str(fallback)
        return "1D"
    return None


def _months_needed(start: datetime, end: datetime, buffer_days: int = _WARMUP_BUFFER_DAYS) -> int:
    """Calculate months to fetch to cover start..end plus a warmup buffer.

    Uses ``max(end, now)`` as the upper bound so the fetch always extends to
    the current date, even when the required range is already in the past.
    """
    effective_start = start - timedelta(days=buffer_days)
    upper_bound = max(end, datetime.now())
    delta_days = (upper_bound - effective_start).days
    months = max(1, (delta_days // 30) + 1)
    return months


def _data_covers_range(
    path: Path, required_start: datetime, required_end: datetime
) -> tuple[bool, str]:
    """Return (ok, message) indicating whether the parquet covers the required range."""
    tr = _get_time_range(path)
    if tr is None:
        return False, f"Cannot read timestamp range from {path.name}"

    data_start, data_end = _to_naive(tr[0]), _to_naive(tr[1])
    req_start = _to_naive(required_start)
    req_end = _to_naive(required_end)

    if req_start < data_start or req_end > data_end:
        return (
            False,
            (
                f"Data covers {data_start.date()}..{data_end.date()} "
                f"but {req_start.date()}..{req_end.date()} is required ({path.name})"
            ),
        )

    return True, f"OK ({data_start.date()}..{data_end.date()}, {path.name})"


def _fetch_candle_data(symbol: str, timeframe: str, months: int) -> bool:
    """
    Fetch candle data using the existing fetch_historical tooling.

    Returns True on success, False on failure (e.g. no outbound API access).
    """
    try:
        from scripts.fetch.fetch_historical import fetch_historical_data, save_metadata, save_to_parquet

        print(f"  [FETCH] Fetching {symbol} {timeframe} ({months} months)...")
        df = fetch_historical_data(symbol, timeframe, months)
        curated_path, raw_path = save_to_parquet(df, symbol, timeframe, use_two_layer=True)
        save_metadata(symbol, timeframe, df, months, raw_path=raw_path, use_two_layer=True)
        print(f"  [FETCH] Done: {curated_path} ({len(df):,} candles)")
        return True
    except Exception as exc:
        print(f"  [FETCH] FAILED ({type(exc).__name__}): {exc}")
        return False


def check_and_ensure(
    cfg: dict[str, Any],
    *,
    dry_run: bool = False,
    no_fetch: bool = False,
) -> tuple[bool, list[str]]:
    """
    Inspect config and ensure all required candle data is available.

    Args:
        cfg: Parsed optimizer config dict
        dry_run: If True, report what is missing but do not fetch
        no_fetch: If True, fail if data is missing instead of fetching

    Returns:
        (all_ok, messages) where messages contains one line per dataset checked
    """
    meta = cfg.get("meta", {})
    symbol: str = meta.get("symbol", "tBTCUSD")
    timeframe: str = meta.get("timeframe", "3h")

    required_range = _parse_required_range(cfg)
    htf_tf = _htf_timeframe(cfg)

    datasets: list[tuple[str, str]] = [(symbol, timeframe)]
    if htf_tf:
        datasets.append((symbol, htf_tf))

    all_ok = True
    messages: list[str] = []

    if required_range is None:
        messages.append(
            "[WARN] No sample_start/sample_end found in config — "
            "cannot validate date coverage; data files checked for existence only."
        )

    for sym, tf in datasets:
        label = f"{sym} {tf}"
        existing = _pick_data_file(sym, tf)

        if existing is not None and required_range is not None:
            covers, reason = _data_covers_range(existing, required_range[0], required_range[1])
            if covers:
                messages.append(f"[OK]   {label}: {reason}")
                continue
            else:
                messages.append(f"[MISS] {label}: {reason}")
        elif existing is not None:
            messages.append(f"[OK]   {label}: file exists ({existing.name}), coverage not verified")
            continue
        else:
            messages.append(f"[MISS] {label}: no parquet file found")

        # Data is missing or insufficient — decide what to do
        if dry_run:
            messages.append(
                f"       --dry-run active; skipping fetch for {label}. "
                "Run without --dry-run or use fetch_historical.py manually."
            )
            all_ok = False
            continue

        if no_fetch:
            hint = (
                f"python scripts/fetch/fetch_historical.py "
                f"--symbol {sym} --timeframe {tf} --months <N>"
            )
            messages.append(
                f"       --no-fetch active; cannot obtain {label} automatically. "
                f"Fetch manually:\n       {hint}"
            )
            all_ok = False
            continue

        # Attempt fetch
        months = (
            _months_needed(required_range[0], required_range[1])
            if required_range
            else _DEFAULT_FETCH_MONTHS
        )
        fetched = _fetch_candle_data(sym, tf, months)
        if fetched:
            # Re-verify after fetch
            existing2 = _pick_data_file(sym, tf)
            if existing2 is not None and required_range is not None:
                covers2, reason2 = _data_covers_range(
                    existing2, required_range[0], required_range[1]
                )
                if covers2:
                    messages.append(f"[OK]   {label}: fetched successfully — {reason2}")
                else:
                    messages.append(
                        f"[FAIL] {label}: fetched but coverage still insufficient — {reason2}"
                    )
                    all_ok = False
            else:
                messages.append(f"[OK]   {label}: fetched (coverage not re-verified)")
        else:
            hint = (
                f"python scripts/fetch/fetch_historical.py "
                f"--symbol {sym} --timeframe {tf} --months {months}"
            )
            messages.append(
                f"[FAIL] {label}: fetch failed. Check outbound access to "
                f"https://api-pub.bitfinex.com and retry:\n       {hint}"
            )
            all_ok = False

    return all_ok, messages


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Ensure candle parquet data exists and covers the date range required "
            "by an optimizer config YAML. Fetches missing data from the Bitfinex "
            "public API when needed."
        )
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Path to optimizer .yaml config file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report missing data but do not fetch anything",
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Fail with an error message instead of attempting a fetch",
    )
    args = parser.parse_args()

    config_path: Path = args.config
    if not config_path.is_absolute():
        config_path = ROOT / config_path

    if not config_path.exists():
        print(f"[ERROR] Config file not found: {config_path}")
        return 1

    cfg = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        print(f"[ERROR] Could not parse config as YAML dict: {config_path}")
        return 1

    meta = cfg.get("meta", {})
    symbol = meta.get("symbol", "tBTCUSD")
    timeframe = meta.get("timeframe", "3h")
    runs = meta.get("runs", {})
    sample_start = runs.get("sample_start", "?")
    sample_end = runs.get("sample_end", "?")
    htf_tf = _htf_timeframe(cfg)

    print("=" * 70)
    print("STARTUP DATA CHECK")
    print("=" * 70)
    print(f"Config:    {config_path.relative_to(ROOT)}")
    print(f"Symbol:    {symbol}  Timeframe: {timeframe}")
    print(f"Range:     {sample_start} -> {sample_end}")
    print(f"HTF data:  {'required (' + htf_tf + ')' if htf_tf else 'not required'}")
    if args.dry_run:
        print("Mode:      dry-run (no fetching)")
    elif args.no_fetch:
        print("Mode:      no-fetch (fail if missing)")
    else:
        print("Mode:      fetch-if-missing")
    print()

    all_ok, messages = check_and_ensure(
        cfg,
        dry_run=args.dry_run,
        no_fetch=args.no_fetch,
    )

    for msg in messages:
        print(msg)

    print()
    if all_ok:
        print("[PASS] All required candle data is available.")
        print(
            "\nNext step: run preflight check\n"
            f"  python scripts/preflight/preflight_optuna_check.py {config_path.relative_to(ROOT)}"
        )
        return 0
    else:
        print("[FAIL] Some required data is missing or could not be obtained.")
        if not args.dry_run and not args.no_fetch:
            print(
                "\nIf the Bitfinex public API is unavailable in your environment, "
                "copy the required parquet files to:\n"
                "  data/curated/v1/candles/{symbol}_{timeframe}.parquet\n"
                "and re-run this script with --no-fetch to verify coverage."
            )
        return 1


if __name__ == "__main__":
    sys.exit(main())
