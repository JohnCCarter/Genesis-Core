"""
FVG-based primary filter for meta-labeling.

This module implements the first stage of a 2-stage trading system:
1. FVG Filter (this module) → Generates trade opportunities
2. ML Model → Decides accept/reject for each opportunity

The filter looks for:
- Valid FVG (fair value gap)
- HTF trend confluence (4h EMA slope aligned with FVG direction)
- Entry zone (price near FVG midline for mean reversion)
- Quality metrics (size, displacement, volume confirmation)
"""

from typing import Any

import pandas as pd


def evaluate_fvg_signal(
    fvg_features: dict[str, float],
    min_fvg_size_atr: float = 0.5,
    max_distance_to_midline_atr: float = 2.0,
    min_trend_confluence: float = 0.5,
    min_displacement_strength: float = 0.3,
) -> tuple[str, dict[str, Any]]:
    """
    Evaluate if FVG presents a valid trade opportunity.

    This is the PRIMARY FILTER that generates signals for meta-labeling.
    Only trades that pass this filter will be sent to the ML model.

    Args:
        fvg_features: Dict with FVG features from extract_fvg_features
        min_fvg_size_atr: Minimum gap size (ATR-normalized)
        max_distance_to_midline_atr: Max distance from midline for entry
        min_trend_confluence: Minimum HTF trend alignment
        min_displacement_strength: Minimum displacement quality

    Returns:
        (signal, metadata) where signal is "LONG", "SHORT", or "NONE"
    """
    reasons = []

    # 1. Check if FVG exists
    if fvg_features.get("fvg_present", 0.0) < 0.5:
        reasons.append("NO_FVG")
        return "NONE", {"reasons": reasons}

    # 2. Check FVG quality (size)
    fvg_size_atr = fvg_features.get("fvg_size_atr", 0.0)
    if fvg_size_atr < min_fvg_size_atr:
        reasons.append("FVG_TOO_SMALL")
        return "NONE", {"reasons": reasons, "fvg_size_atr": fvg_size_atr}

    # 3. Check displacement quality
    displacement = fvg_features.get("displacement_strength", 0.0)
    if displacement < min_displacement_strength:
        reasons.append("WEAK_DISPLACEMENT")
        return "NONE", {"reasons": reasons, "displacement_strength": displacement}

    # 4. Check trend confluence
    trend_conf = fvg_features.get("trend_confluence", 0.0)
    if abs(trend_conf) < min_trend_confluence:
        reasons.append("NO_TREND_CONFLUENCE")
        return "NONE", {"reasons": reasons, "trend_confluence": trend_conf}

    # 5. Check entry zone (price near midline for mean reversion)
    distance_norm = abs(fvg_features.get("distance_to_midline_norm", 999.0))
    if distance_norm > max_distance_to_midline_atr:
        reasons.append("TOO_FAR_FROM_MIDLINE")
        return "NONE", {
            "reasons": reasons,
            "distance_to_midline_norm": distance_norm,
        }

    # 6. Determine direction from FVG type and trend
    fvg_bullish = fvg_features.get("fvg_bullish", 0.0)

    if fvg_bullish > 0 and trend_conf > 0:
        # Bullish FVG in uptrend → LONG opportunity
        signal = "LONG"
        reasons.append("BULLISH_FVG_CONFLUENCE")
    elif fvg_bullish < 0 and trend_conf < 0:
        # Bearish FVG in downtrend → SHORT opportunity
        signal = "SHORT"
        reasons.append("BEARISH_FVG_CONFLUENCE")
    else:
        # Counter-trend FVG → Skip
        reasons.append("COUNTER_TREND_FVG")
        return "NONE", {"reasons": reasons}

    # Signal generated!
    return signal, {
        "reasons": reasons,
        "fvg_size_atr": fvg_size_atr,
        "displacement_strength": displacement,
        "trend_confluence": trend_conf,
        "distance_to_midline_norm": distance_norm,
        "fvg_bullish": fvg_bullish,
    }


def generate_fvg_opportunities(
    features_df,
    min_fvg_size_atr: float = 0.5,
    max_distance_to_midline_atr: float = 2.0,
    min_trend_confluence: float = 0.5,
    min_displacement_strength: float = 0.3,
) -> list[dict[str, Any]]:
    """
    Generate list of FVG trade opportunities from features DataFrame.

    This scans through historical data and identifies all bars where
    the FVG filter would have generated a trade signal.

    Args:
        features_df: DataFrame with FVG features
        min_fvg_size_atr: Minimum gap size
        max_distance_to_midline_atr: Max distance for entry
        min_trend_confluence: Minimum trend alignment
        min_displacement_strength: Minimum displacement quality

    Returns:
        List of opportunities with index, signal, and metadata
    """
    opportunities = []

    for idx, row in features_df.iterrows():
        # Handle NaN values
        fvg_features = {
            "fvg_present": (
                float(row.get("fvg_present", 0.0)) if not pd.isna(row.get("fvg_present")) else 0.0
            ),
            "fvg_size_atr": (
                float(row.get("fvg_size_atr", 0.0)) if not pd.isna(row.get("fvg_size_atr")) else 0.0
            ),
            "displacement_strength": (
                float(row.get("displacement_strength", 0.0))
                if not pd.isna(row.get("displacement_strength"))
                else 0.0
            ),
            "trend_confluence": (
                float(row.get("trend_confluence", 0.0))
                if not pd.isna(row.get("trend_confluence"))
                else 0.0
            ),
            "distance_to_midline_norm": (
                float(row.get("distance_to_midline_norm", 999.0))
                if not pd.isna(row.get("distance_to_midline_norm"))
                else 999.0
            ),
            "fvg_bullish": (
                float(row.get("fvg_bullish", 0.0)) if not pd.isna(row.get("fvg_bullish")) else 0.0
            ),
        }

        signal, metadata = evaluate_fvg_signal(
            fvg_features,
            min_fvg_size_atr=min_fvg_size_atr,
            max_distance_to_midline_atr=max_distance_to_midline_atr,
            min_trend_confluence=min_trend_confluence,
            min_displacement_strength=min_displacement_strength,
        )

        if signal != "NONE":
            opportunities.append(
                {
                    "index": idx,
                    "signal": signal,
                    "metadata": metadata,
                }
            )

    return opportunities
