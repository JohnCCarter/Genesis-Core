from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import scripts.run.run_backtest as run_backtest
from core.backtest.engine import BacktestEngine
from core.backtest.intelligence_shadow import BacktestIntelligenceShadowRecorder
from core.strategy.family_registry import resolve_strategy_family


@pytest.fixture
def champion_shadow_params():
    return {
        "symbol": "tBTCUSD",
        "timeframe": "3h",
        "start_date": "2024-01-02",
        "end_date": "2024-02-20",
        "fast_window": True,
    }


def test_existing_champion_path_supports_shadow_without_decision_drift(
    tmp_path: Path,
    champion_shadow_params,
):
    os.environ["GENESIS_FAST_WINDOW"] = "1"
    os.environ["GENESIS_PRECOMPUTE_FEATURES"] = "1"
    os.environ["GENESIS_MODE_EXPLICIT"] = "1"
    os.environ["GENESIS_RANDOM_SEED"] = "42"

    control_rows: list[dict] = []
    shadow_rows: list[dict] = []

    control_engine = BacktestEngine(
        **champion_shadow_params,
        evaluation_hook=run_backtest._compose_decision_row_capture_hook(
            symbol=champion_shadow_params["symbol"],
            timeframe=champion_shadow_params["timeframe"],
            row_sink=control_rows,
            upstream_hook=None,
        ),
    )
    shadow_recorder = BacktestIntelligenceShadowRecorder(
        symbol=champion_shadow_params["symbol"],
        timeframe=champion_shadow_params["timeframe"],
        repo_root=tmp_path,
    )
    shadow_engine = BacktestEngine(
        **champion_shadow_params,
        evaluation_hook=run_backtest._compose_decision_row_capture_hook(
            symbol=champion_shadow_params["symbol"],
            timeframe=champion_shadow_params["timeframe"],
            row_sink=shadow_rows,
            upstream_hook=shadow_recorder.create_hook(upstream_hook=None),
        ),
    )

    loaded_control = control_engine.load_data()
    loaded_shadow = shadow_engine.load_data()
    if not loaded_control or not loaded_shadow:
        pytest.skip("Data not available for champion shadow integration test")

    control_results = control_engine.run()
    shadow_results = shadow_engine.run()
    champion_cfg = shadow_engine.champion_loader.load_cached(
        champion_shadow_params["symbol"], champion_shadow_params["timeframe"]
    ).config
    summary_path = (
        tmp_path
        / "results"
        / "intelligence_shadow"
        / "champion-shadow-test"
        / "shadow_summary.json"
    )
    summary = shadow_recorder.finalize(
        results=shadow_results,
        merged_config=champion_cfg,
        summary_path=summary_path,
    )
    expected_strategy_family = resolve_strategy_family(champion_cfg)

    assert control_rows == shadow_rows
    assert control_results["trades"] == shadow_results["trades"]
    assert control_results["summary"] == shadow_results["summary"]
    assert (
        control_results["backtest_info"]["effective_config_fingerprint"]
        == shadow_results["backtest_info"]["effective_config_fingerprint"]
    )

    loaded_summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert loaded_summary == summary
    assert summary["decision_drift_observed"] is False
    assert summary["derived_parameter_set"]["strategy_family"] == expected_strategy_family
    assert summary["derived_parameter_set"]["strategy_family_source"] == "family_registry_v1"
    assert summary["counts"]["captured_events"] == len(shadow_rows)
    assert summary["counts"]["captured_events"] > 0
    assert len(summary["persisted_event_ids"]) == summary["counts"]["normalized_events"]
    assert len(summary["ledger_entity_ids"]) == summary["counts"]["normalized_events"]
    assert (
        summary["top_advisory_parameter_set_id"]
        == summary["derived_parameter_set"]["parameter_set_id"]
    )
