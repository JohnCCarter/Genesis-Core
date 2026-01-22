from __future__ import annotations

import warnings
from collections.abc import Iterable
from typing import Any

from core.strategy.features_asof import extract_features as _extract_features_asof


def extract_features(
    candles: dict[str, Iterable[float]] | list[tuple[float, float, float, float, float, float]],
    *,
    config: dict[str, Any] | None = None,
    now_index: int | None = None,
    timeframe: str | None = None,
    symbol: str | None = None,
) -> tuple[dict[str, float], dict[str, Any]]:
    """DEPRECATED: Legacy feature-engine.

    Denna modul finns kvar för bakåtkompatibilitet, men SSOT är
    `core.strategy.features_asof`.

    För att undvika att olika delar av systemet råkar använda olika feature-sets
    delegaterar vi nu till ASOF-implementationen.
    """

    warnings.warn(
        "core.strategy.features.extract_features är deprecated; använd core.strategy.features_asof. "
        "(Det här anropet delegaterar nu till SSOT.)",
        DeprecationWarning,
        stacklevel=2,
    )

    return _extract_features_asof(
        candles,
        config=config,
        now_index=now_index,
        timeframe=timeframe,
        symbol=symbol,
    )
