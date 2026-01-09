from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.backtest.walk_forward import run_walk_forward


@pytest.fixture()
def sample_windows() -> list[tuple[str, str]]:
    return [("2024-10-22", "2024-11-01"), ("2024-11-02", "2024-11-10")]


def test_run_walk_forward(tmp_path: Path, sample_windows: list[tuple[str, str]]) -> None:
    results_dir = tmp_path / "results"

    def fake_load(self) -> bool:  # type: ignore[override]
        data = {
            "timestamp": ["2024-10-22", "2024-10-23", "2024-11-02", "2024-11-03"],
            "open": [50000, 50100, 50200, 50300],
            "high": [50200, 50300, 50400, 50500],
            "low": [49800, 49900, 50000, 50100],
            "close": [50100, 50200, 50300, 50400],
            "volume": [10, 12, 11, 9],
        }
        import pandas as pd

        self.candles_df = pd.DataFrame(data)
        self.candles_df["timestamp"] = pd.to_datetime(self.candles_df["timestamp"])
        return True

    def fake_run(self, policy=None, configs=None, verbose=False):  # type: ignore[override]
        return {
            "summary": {"total_return": 5.0},
            "walk_forward_info": {},
        }

    with (
        patch("src.core.backtest.walk_forward.BacktestEngine.load_data", fake_load),
        patch("src.core.backtest.walk_forward.BacktestEngine.run", fake_run),
        patch("src.core.backtest.walk_forward.ChampionLoader.load_cached") as load_cached,
    ):
        load_cached.return_value.config = {}
        load_cached.return_value.source = "baseline"

        summary = run_walk_forward(
            symbol="tTEST",
            timeframe="1h",
            windows=sample_windows,
            warmup_bars=1,
            output_dir=results_dir,
        )

    assert summary["symbol"] == "tTEST"
    assert len(summary["periods"]) == len(sample_windows)
    assert summary["champion_source"] == "baseline"
