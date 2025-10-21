"""Walk-forward validering för optimerad champion."""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from core.backtest.engine import BacktestEngine
from core.strategy.champion_loader import ChampionLoader

ROOT = Path(__file__).resolve().parents[3]
WF_RESULTS_DIR = ROOT / "results" / "walk_forward"


def _split_periods(df: pd.DataFrame, windows: Iterable[tuple[str, str]]) -> list[pd.DataFrame]:
    frames: list[pd.DataFrame] = []
    for start, end in windows:
        mask = (df["timestamp"] >= pd.to_datetime(start)) & (df["timestamp"] <= pd.to_datetime(end))
        subset = df.loc[mask]
        if subset.empty:
            raise ValueError(f"Walk-forward period saknar data: {start} -> {end}")
        frames.append(subset.copy())
    return frames


def run_walk_forward(
    *,
    symbol: str,
    timeframe: str,
    windows: list[tuple[str, str]],
    warmup_bars: int = 150,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    output_dir = (output_dir or WF_RESULTS_DIR).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    loader = ChampionLoader()
    champion = loader.load_cached(symbol, timeframe)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_id = f"wf_{symbol}_{timeframe}_{timestamp}"
    run_dir = output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for idx, (start, end) in enumerate(windows, start=1):
        engine = BacktestEngine(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start,
            end_date=end,
            warmup_bars=warmup_bars,
        )
        if not engine.load_data():
            raise RuntimeError(f"Kunde inte läsa data för walk-forward period {start} -> {end}")
        res = engine.run(policy={}, configs=champion.config, verbose=False)
        res["walk_forward_info"] = {
            "window_index": idx,
            "start": start,
            "end": end,
            "champion_source": champion.source,
        }
        results.append(res)
        (run_dir / f"period_{idx:02d}.json").write_text(json.dumps(res, indent=2), encoding="utf-8")

    summary = {
        "run_id": run_id,
        "symbol": symbol,
        "timeframe": timeframe,
        "windows": windows,
        "champion_source": champion.source,
        "generated_at": datetime.utcnow().isoformat(),
        "periods": [
            {
                "index": res["walk_forward_info"]["window_index"],
                "start": res["walk_forward_info"]["start"],
                "end": res["walk_forward_info"]["end"],
                "summary": res["summary"],
            }
            for res in results
        ],
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary
