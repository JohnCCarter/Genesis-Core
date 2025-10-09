"""
Vectorized indicator calculations for batch feature computation.

All functions operate on pandas Series/DataFrame for O(n) performance.
Used by precompute_features.py for efficient batch processing.
"""

import numpy as np
import pandas as pd


def calculate_ema_vectorized(series: pd.Series, period: int = 50) -> pd.Series:
    """Calculate EMA on entire series at once."""
    return series.ewm(span=period, adjust=False).mean()


def calculate_rsi_vectorized(series: pd.Series, period: int = 14) -> pd.Series:
    """Calculate RSI on entire series at once."""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))

    # Normalize to [-1, 1]
    return (rsi - 50) / 50


def calculate_adx_vectorized(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    """Calculate ADX on entire series."""
    # True Range
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # Directional Movement
    up_move = high - high.shift(1)
    down_move = low.shift(1) - low

    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

    # Smoothed indicators
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * pd.Series(plus_dm).rolling(window=period).mean() / atr
    minus_di = 100 * pd.Series(minus_dm).rolling(window=period).mean() / atr

    # ADX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di).replace(0, np.nan)
    adx = dx.rolling(window=period).mean()

    # Normalize to [0, 1]
    return adx / 100


def calculate_atr_vectorized(
    high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14
) -> pd.Series:
    """Calculate ATR on entire series."""
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    return tr.rolling(window=period).mean()


def calculate_bollinger_bands_vectorized(
    series: pd.Series, period: int = 20, std_dev: float = 2.0
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate Bollinger Bands on entire series."""
    middle = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()

    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)

    return upper, middle, lower


def calculate_bb_position_vectorized(
    close: pd.Series, period: int = 20, std_dev: float = 2.0
) -> pd.Series:
    """Calculate price position within Bollinger Bands [0, 1]."""
    upper, middle, lower = calculate_bollinger_bands_vectorized(close, period, std_dev)

    bb_width = upper - lower
    bb_position = (close - lower) / bb_width.replace(0, np.nan)

    return bb_position.clip(0, 1)


def calculate_macd_vectorized(
    series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate MACD on entire series."""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()

    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def calculate_volume_ratio_vectorized(volume: pd.Series, period: int = 20) -> pd.Series:
    """Calculate volume ratio vs moving average."""
    vol_ma = volume.rolling(window=period).mean()
    return (volume / vol_ma.replace(0, np.nan)).fillna(1.0)


def calculate_ema_slope_vectorized(series: pd.Series, period: int = 50) -> pd.Series:
    """Calculate EMA slope (rate of change)."""
    ema = calculate_ema_vectorized(series, period)
    return ema.pct_change(periods=1)  # 1-bar rate of change


def calculate_price_vs_ema_vectorized(close: pd.Series, period: int = 50) -> pd.Series:
    """Calculate price distance from EMA."""
    ema = calculate_ema_vectorized(close, period)
    return (close - ema) / close


def calculate_volatility_shift_vectorized(
    close: pd.Series, short_period: int = 10, long_period: int = 50
) -> pd.Series:
    """Calculate ratio of short-term to long-term volatility."""
    vol_short = close.pct_change().rolling(window=short_period).std()
    vol_long = close.pct_change().rolling(window=long_period).std()

    return (vol_short / vol_long.replace(0, np.nan)).fillna(1.0)


def calculate_all_features_vectorized(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate ALL features at once on entire DataFrame.

    Input: DataFrame with OHLCV columns
    Output: DataFrame with all feature columns

    This is O(n) instead of O(n²)!
    """
    features = pd.DataFrame(index=df.index)

    # === CORE INDICATORS ===
    rsi = calculate_rsi_vectorized(df["close"], period=14)

    # === BOLLINGER BANDS ===
    bb_position = calculate_bb_position_vectorized(df["close"], period=20, std_dev=2.0)

    # === MACD ===
    _, _, macd_histogram = calculate_macd_vectorized(df["close"], fast=12, slow=26, signal=9)

    # Normalize MACD histogram
    macd_histogram_norm = macd_histogram / df["close"]

    # === DERIVED FEATURES ===
    ema_slope = calculate_ema_slope_vectorized(df["close"], period=50)
    price_vs_ema = calculate_price_vs_ema_vectorized(df["close"], period=50)
    volatility_shift = calculate_volatility_shift_vectorized(df["close"], 10, 50)

    # === TOP 12 IC-SELECTED FEATURES (HighVol regime tested) ===
    # Rank 1: rsi_inv_ma3 (IC +0.0598, Spread +0.149%)
    features["rsi_inv_ma3"] = pd.Series(-rsi, index=df.index).rolling(3).mean().clip(-1.0, 1.0)
    
    # Rank 2: rsi_inv_lag1 (IC +0.0583, Spread +0.157%)
    features["rsi_inv_lag1"] = pd.Series(-rsi, index=df.index).shift(1).clip(-1.0, 1.0)
    
    # Rank 3: ema_slope_inv (IC +0.0574, Spread +0.236%)
    features["ema_slope_inv"] = (-ema_slope).clip(-0.05, 0.05)
    
    # Rank 4: price_vs_ema_inv (IC +0.0574, Spread +0.236%)
    features["price_vs_ema_inv"] = (-price_vs_ema).clip(-0.10, 0.10)
    
    # Rank 5: ema_slope_inv_ma3 (IC +0.0561, Spread +0.193%)
    features["ema_slope_inv_ma3"] = features["ema_slope_inv"].rolling(3).mean()
    
    # Rank 6: bb_position_inv_ma3 (IC +0.0555, Spread +0.145%)
    bb_pos_inv = (1.0 - bb_position).clip(0.0, 1.0)
    features["bb_position_inv_ma3"] = pd.Series(bb_pos_inv, index=df.index).rolling(3).mean()
    
    # Rank 7: ema_slope_inv_lag1 (IC +0.0547, Spread +0.192%)
    features["ema_slope_inv_lag1"] = features["ema_slope_inv"].shift(1)
    
    # Rank 8: volatility_shift_ma3 (IC +0.0520, Spread +0.248%) 🔥 BEST SPREAD!
    vol_shift = volatility_shift.clip(0.5, 2.0)
    features["volatility_shift_ma3"] = pd.Series(vol_shift, index=df.index).rolling(3).mean()
    
    # Rank 9: rsi_inv (IC +0.0512, Spread +0.144%)
    features["rsi_inv"] = (-rsi).clip(-1.0, 1.0)
    
    # Rank 10: volatility_shift_lag1 (IC +0.0508, Spread +0.182%)
    features["volatility_shift_lag1"] = pd.Series(vol_shift, index=df.index).shift(1)
    
    # Rank 11: bb_position_inv (IC +0.0486, Spread +0.148%)
    features["bb_position_inv"] = bb_pos_inv
    
    # Rank 12: volatility_shift (IC +0.0459, Spread +0.138%)
    features["volatility_shift"] = vol_shift

    # Fill NaN with 0.0 (from lookback periods)
    features = features.fillna(0.0)

    return features


def validate_features(features_df: pd.DataFrame) -> dict:
    """Validate computed features for quality checks."""
    checks = {
        "total_samples": len(features_df),
        "nan_count": features_df.isna().sum().sum(),
        "inf_count": np.isinf(features_df.select_dtypes(include=[np.number])).sum().sum(),
        "feature_count": len(features_df.columns),
        "valid_samples": len(features_df.dropna()),
    }

    return checks
