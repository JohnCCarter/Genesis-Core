from __future__ import annotations


def simple_signal(features: dict[str, float]) -> str:
    """Exempelstrategi: returnera buy/sell/hold baserat på enkel regel."""
    rsi = float(features.get("rsi", 50.0))
    if rsi < 30:
        return "buy"
    if rsi > 70:
        return "sell"
    return "hold"
