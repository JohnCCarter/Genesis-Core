from __future__ import annotations

import importlib

from core.strategy import evaluate as evaluate_mod
from core.utils.env_flags import env_flag_enabled


def test_env_flag_enabled_semantics() -> None:
    assert env_flag_enabled(None, default=False) is False
    assert env_flag_enabled(None, default=True) is True

    assert env_flag_enabled("", default=False) is False
    assert env_flag_enabled("   ", default=True) is True

    assert env_flag_enabled("0", default=True) is False
    assert env_flag_enabled("false", default=True) is False
    assert env_flag_enabled("off", default=True) is False
    assert env_flag_enabled("no", default=True) is False

    assert env_flag_enabled("1", default=False) is True
    assert env_flag_enabled("true", default=False) is True
    assert env_flag_enabled("YES", default=False) is True


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
