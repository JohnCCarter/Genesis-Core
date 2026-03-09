from __future__ import annotations

import importlib

import pytest

from core.strategy import evaluate as evaluate_mod
from core.utils.env_flags import env_flag_enabled


@pytest.mark.parametrize(
    ("value", "default", "expected"),
    [
        pytest.param(None, False, False, id="none-default-false"),
        pytest.param(None, True, True, id="none-default-true"),
        pytest.param("", False, False, id="empty-default-false"),
        pytest.param("   ", True, True, id="whitespace-default-true"),
        pytest.param("0", True, False, id="zero-false"),
        pytest.param("false", True, False, id="false-token"),
        pytest.param("off", True, False, id="off-token"),
        pytest.param("no", True, False, id="no-token"),
        pytest.param("1", False, True, id="one-true"),
        pytest.param("true", False, True, id="true-token"),
        pytest.param("YES", False, True, id="yes-token-uppercase"),
    ],
)
def test_env_flag_enabled_semantics(value, default, expected) -> None:
    assert env_flag_enabled(value, default=default) is expected


def test_metrics_disable_flag_parsing(monkeypatch) -> None:
    monkeypatch.delenv("GENESIS_DISABLE_METRICS", raising=False)
    assert evaluate_mod._metrics_enabled() is True

    monkeypatch.setenv("GENESIS_DISABLE_METRICS", "1")
    assert evaluate_mod._metrics_enabled() is False

    # Footgun regression: '0' should NOT disable metrics.
    monkeypatch.setenv("GENESIS_DISABLE_METRICS", "0")
    assert evaluate_mod._metrics_enabled() is True

    # Empty should behave like unset.
    monkeypatch.setenv("GENESIS_DISABLE_METRICS", "")
    assert evaluate_mod._metrics_enabled() is True


def test_indicator_cache_disable_flag_parsing(monkeypatch) -> None:
    # NOTE: features_asof reads this env flag at import time.
    import core.strategy.features_asof as features_asof

    monkeypatch.setenv("GENESIS_DISABLE_INDICATOR_CACHE", "0")
    features_asof = importlib.reload(features_asof)
    assert features_asof._INDICATOR_CACHE_ENABLED is True

    monkeypatch.setenv("GENESIS_DISABLE_INDICATOR_CACHE", "1")
    features_asof = importlib.reload(features_asof)
    assert features_asof._INDICATOR_CACHE_ENABLED is False

    monkeypatch.setenv("GENESIS_DISABLE_INDICATOR_CACHE", "")
    features_asof = importlib.reload(features_asof)
    assert features_asof._INDICATOR_CACHE_ENABLED is True
