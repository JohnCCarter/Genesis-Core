"""Tests for scripts/startup/ensure_candle_data.py."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest
import yaml

from scripts.startup.ensure_candle_data import (
    _data_covers_range,
    _htf_timeframe,
    _months_needed,
    _parse_required_range,
    _pick_data_file,
    check_and_ensure,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_parquet(tmp_path: Path, start: str, end: str, symbol: str = "tTEST", tf: str = "3h") -> Path:
    """Write a minimal candle parquet with timestamps between start and end."""
    curated = tmp_path / "data" / "curated" / "v1" / "candles"
    curated.mkdir(parents=True)
    path = curated / f"{symbol}_{tf}.parquet"
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range(start, end, periods=10),
            "open": 1.0,
            "close": 1.0,
            "high": 1.0,
            "low": 1.0,
            "volume": 1.0,
        }
    )
    df.to_parquet(path, index=False, compression="snappy")
    return path


def _simple_cfg(
    symbol: str = "tTEST",
    timeframe: str = "3h",
    sample_start: str = "2024-01-01",
    sample_end: str = "2024-12-31",
    with_htf: bool = False,
    val_start: str | None = None,
    val_end: str | None = None,
) -> dict:
    runs: dict = {
        "use_sample_range": True,
        "sample_start": sample_start,
        "sample_end": sample_end,
        "strategy": "optuna",
    }
    if val_start and val_end:
        runs["validation"] = {
            "enabled": True,
            "sample_start": val_start,
            "sample_end": val_end,
        }
    cfg: dict = {
        "meta": {"symbol": symbol, "timeframe": timeframe, "runs": runs},
        "parameters": {},
    }
    if with_htf:
        cfg["parameters"]["htf_exit_config"] = {"enable_partials": {"type": "fixed", "value": True}}
    return cfg


# ---------------------------------------------------------------------------
# _parse_required_range
# ---------------------------------------------------------------------------


def test_parse_required_range_basic() -> None:
    cfg = _simple_cfg(sample_start="2024-01-01", sample_end="2024-12-31")
    result = _parse_required_range(cfg)
    assert result is not None
    start, end = result
    assert start.year == 2024 and start.month == 1 and start.day == 1
    assert end.year == 2024 and end.month == 12 and end.day == 31


def test_parse_required_range_extends_for_validation() -> None:
    cfg = _simple_cfg(
        sample_start="2024-01-01",
        sample_end="2024-12-31",
        val_start="2025-01-01",
        val_end="2025-12-31",
    )
    result = _parse_required_range(cfg)
    assert result is not None
    start, end = result
    assert start.year == 2024
    assert end.year == 2025 and end.month == 12 and end.day == 31


def test_parse_required_range_empty() -> None:
    cfg = {"meta": {}, "parameters": {}}
    assert _parse_required_range(cfg) is None


# ---------------------------------------------------------------------------
# _htf_timeframe
# ---------------------------------------------------------------------------


def test_htf_timeframe_not_required_without_config() -> None:
    cfg = _simple_cfg(with_htf=False)
    assert _htf_timeframe(cfg) is None


def test_htf_timeframe_returns_1d_by_default() -> None:
    cfg = _simple_cfg(with_htf=True)
    assert _htf_timeframe(cfg) == "1D"


def test_htf_timeframe_respects_fixed_param_format() -> None:
    """_htf_timeframe handles optimizer param format {"type": "fixed", "value": "1D"}."""
    cfg = _simple_cfg(with_htf=True)
    cfg["parameters"]["multi_timeframe"] = {
        "htf_selector": {
            "fallback_timeframe": {"type": "fixed", "value": "1D"},
        }
    }
    assert _htf_timeframe(cfg) == "1D"


def test_htf_timeframe_respects_fallback_timeframe() -> None:
    cfg = _simple_cfg(with_htf=True)
    cfg["parameters"]["multi_timeframe"] = {
        "htf_selector": {"fallback_timeframe": "1W"}
    }
    assert _htf_timeframe(cfg) == "1W"


def test_htf_timeframe_empty_htf_exit_config() -> None:
    cfg = _simple_cfg(with_htf=False)
    cfg["parameters"]["htf_exit_config"] = {}
    assert _htf_timeframe(cfg) is None


# ---------------------------------------------------------------------------
# _months_needed
# ---------------------------------------------------------------------------


def test_months_needed_covers_full_range() -> None:
    start = datetime(2024, 1, 1)
    end = datetime(2025, 12, 31)
    months = _months_needed(start, end)
    # Should be > 24 to include warmup buffer
    assert months > 24


def test_months_needed_minimum_one() -> None:
    start = datetime.now()
    end = datetime.now()
    months = _months_needed(start, end)
    assert months >= 1


# ---------------------------------------------------------------------------
# _data_covers_range
# ---------------------------------------------------------------------------


def test_data_covers_range_sufficient(tmp_path: Path) -> None:
    p = _make_parquet(tmp_path, "2023-01-01", "2025-12-31")
    ok, msg = _data_covers_range(p, datetime(2024, 1, 1), datetime(2025, 12, 31))
    assert ok is True
    assert "OK" in msg


def test_data_covers_range_insufficient_start(tmp_path: Path) -> None:
    p = _make_parquet(tmp_path, "2024-06-01", "2025-12-31")
    ok, msg = _data_covers_range(p, datetime(2024, 1, 1), datetime(2025, 12, 31))
    assert ok is False
    assert "required" in msg or "covers" in msg


def test_data_covers_range_insufficient_end(tmp_path: Path) -> None:
    p = _make_parquet(tmp_path, "2023-01-01", "2024-06-01")
    ok, msg = _data_covers_range(p, datetime(2024, 1, 1), datetime(2025, 12, 31))
    assert ok is False


# ---------------------------------------------------------------------------
# check_and_ensure (unit — no actual API calls)
# ---------------------------------------------------------------------------


def test_check_and_ensure_ok_when_data_present(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """check_and_ensure returns True when all data files cover the required range."""
    _make_parquet(tmp_path, "2023-01-01", "2025-12-31", symbol="tTEST", tf="3h")

    import scripts.startup.ensure_candle_data as mod

    monkeypatch.setattr(
        mod,
        "_pick_data_file",
        lambda sym, tf: tmp_path / "data" / "curated" / "v1" / "candles" / f"{sym}_{tf}.parquet"
        if (tmp_path / "data" / "curated" / "v1" / "candles" / f"{sym}_{tf}.parquet").exists()
        else None,
    )

    cfg = _simple_cfg(symbol="tTEST", timeframe="3h", sample_start="2024-01-01", sample_end="2024-12-31")
    ok, messages = mod.check_and_ensure(cfg, dry_run=True, no_fetch=True)
    assert ok is True
    assert any("[OK]" in m for m in messages)


def test_check_and_ensure_dry_run_reports_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    """check_and_ensure in dry-run mode does not fetch and returns False on missing data."""
    import scripts.startup.ensure_candle_data as mod

    monkeypatch.setattr(mod, "_pick_data_file", lambda sym, tf: None)

    cfg = _simple_cfg(symbol="tMISSING", timeframe="3h", sample_start="2024-01-01", sample_end="2024-12-31")
    ok, messages = mod.check_and_ensure(cfg, dry_run=True)
    assert ok is False
    assert any("dry-run" in m.lower() or "MISS" in m for m in messages)


def test_check_and_ensure_no_fetch_reports_hint(monkeypatch: pytest.MonkeyPatch) -> None:
    """check_and_ensure in no-fetch mode provides fetch command hint and returns False."""
    import scripts.startup.ensure_candle_data as mod

    monkeypatch.setattr(mod, "_pick_data_file", lambda sym, tf: None)

    cfg = _simple_cfg(symbol="tMISSING", timeframe="3h", sample_start="2024-01-01", sample_end="2024-12-31")
    ok, messages = mod.check_and_ensure(cfg, no_fetch=True)
    assert ok is False
    combined = "\n".join(messages)
    assert "fetch_historical.py" in combined


def test_check_and_ensure_htf_data_also_checked(monkeypatch: pytest.MonkeyPatch) -> None:
    """When htf_exit_config is present, 1D data is included in the check."""
    import scripts.startup.ensure_candle_data as mod

    monkeypatch.setattr(mod, "_pick_data_file", lambda sym, tf: None)

    cfg = _simple_cfg(
        symbol="tTEST",
        timeframe="3h",
        sample_start="2024-01-01",
        sample_end="2024-12-31",
        with_htf=True,
    )
    ok, messages = mod.check_and_ensure(cfg, dry_run=True)
    assert ok is False
    combined = "\n".join(messages)
    assert "1D" in combined


def test_check_and_ensure_no_range_warns(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """When config has no sample_start/end, a warning is emitted but data existence still checked."""
    import scripts.startup.ensure_candle_data as mod

    _make_parquet(tmp_path, "2023-01-01", "2025-12-31", symbol="tTEST", tf="3h")
    monkeypatch.setattr(
        mod,
        "_pick_data_file",
        lambda sym, tf: tmp_path / "data" / "curated" / "v1" / "candles" / f"{sym}_{tf}.parquet"
        if (tmp_path / "data" / "curated" / "v1" / "candles" / f"{sym}_{tf}.parquet").exists()
        else None,
    )

    cfg = {"meta": {"symbol": "tTEST", "timeframe": "3h", "runs": {}}, "parameters": {}}
    ok, messages = mod.check_and_ensure(cfg, dry_run=True)
    assert any("WARN" in m for m in messages)
