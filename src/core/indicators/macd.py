"""MACD (Moving Average Convergence Divergence) indicator."""

from core.indicators.ema import calculate_ema


def calculate_macd(
    closes: list[float],
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
) -> dict[str, list[float]]:
    """
    Calculate MACD indicator.

    MACD = EMA(fast) - EMA(slow)
    Signal = EMA(MACD, signal_period)
    Histogram = MACD - Signal

    Args:
        closes: Close prices
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line EMA period (default: 9)

    Returns:
        Dict with 'macd', 'signal', 'histogram' lists
    """
    if len(closes) < slow_period:
        return {
            "macd": [0.0] * len(closes),
            "signal": [0.0] * len(closes),
            "histogram": [0.0] * len(closes),
        }

    # Calculate EMAs
    ema_fast = calculate_ema(closes, period=fast_period)
    ema_slow = calculate_ema(closes, period=slow_period)

    # MACD line = EMA(fast) - EMA(slow)
    macd_line = []
    for i in range(len(closes)):
        if i < len(ema_fast) and i < len(ema_slow):
            macd_line.append(ema_fast[i] - ema_slow[i])
        else:
            macd_line.append(0.0)

    # Signal line = EMA of MACD
    signal_line = calculate_ema(macd_line, period=signal_period)

    # Histogram = MACD - Signal
    histogram = []
    for i in range(len(closes)):
        if i < len(macd_line) and i < len(signal_line):
            histogram.append(macd_line[i] - signal_line[i])
        else:
            histogram.append(0.0)

    return {
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram,
    }
