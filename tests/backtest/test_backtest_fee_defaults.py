from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import core.optimizer.runner_config as runner_config
from core.pipeline import GenesisPipeline

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKTEST_DEFAULTS_PATH = REPO_ROOT / "config" / "backtest_defaults.yaml"


def test_backtest_defaults_yaml_sets_zero_commission() -> None:
    defaults = yaml.safe_load(BACKTEST_DEFAULTS_PATH.read_text(encoding="utf-8"))

    assert defaults["commission"] == pytest.approx(0.0)
    assert defaults["slippage"] == pytest.approx(0.0005)


def test_genesis_pipeline_create_engine_uses_zero_commission_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("GENESIS_PRECOMPUTE_FEATURES", "1")

    pipeline = GenesisPipeline()
    engine = pipeline.create_engine(symbol="tBTCUSD", timeframe="3h")

    assert engine.position_tracker.commission_rate == pytest.approx(0.0)
    assert engine.position_tracker.slippage_rate == pytest.approx(0.0005)


def test_optimizer_runner_config_reads_zero_commission_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(runner_config, "_BACKTEST_DEFAULTS_CACHE", None)

    capital, commission, slippage = runner_config._get_backtest_economics()

    assert capital == pytest.approx(10000.0)
    assert commission == pytest.approx(0.0)
    assert slippage == pytest.approx(0.0005)
