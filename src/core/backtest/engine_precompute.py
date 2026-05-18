from __future__ import annotations

import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pandas as pd


def prepare_precomputed_features(
    *,
    candles_df: pd.DataFrame,
    htf_candles_df: pd.DataFrame | None,
    cache_path: Path,
    cache_write_enabled: bool,
    logger: Any,
    build_cache_metadata: Callable[[int], dict[str, Any]],
    validate_cache: Callable[[Any, int], tuple[bool, str | None]],
    load_cache_payload: Callable[[Any], dict[str, list[float]]],
) -> dict[str, list[float]] | None:
    """Load or build the precomputed feature payload used by BacktestEngine.

    This keeps the behavior owned by ``engine.py`` while moving the large
    precompute/cache orchestration block into a dedicated helper module.
    """

    try:
        closes_all = candles_df["close"].tolist()
        highs_all = candles_df["high"].tolist()
        lows_all = candles_df["low"].tolist()

        import numpy as _np

        from core.indicators.adx import calculate_adx as _calc_adx
        from core.indicators.atr import calculate_atr as _calc_atr
        from core.indicators.bollinger import bollinger_bands as _bb
        from core.indicators.ema import calculate_ema as _calc_ema
        from core.indicators.fibonacci import FibonacciConfig as _FibCfg
        from core.indicators.fibonacci import detect_swing_points as _detect_swings
        from core.indicators.rsi import calculate_rsi as _calc_rsi

        # Fib config is used both for LTF swing precompute and HTF mapping.
        # It must exist even when we load indicators from the on-disk cache.
        fib_cfg = _FibCfg(atr_depth=3.0, max_swings=8, min_swings=1)

        loaded = False
        pre: dict[str, list[float]] = {}
        if cache_path.exists():
            try:
                with _np.load(cache_path, allow_pickle=False) as npz:
                    cache_valid, invalid_reason = validate_cache(npz, len(closes_all))
                    if cache_valid:
                        pre = load_cache_payload(npz)
                        loaded = True
                        logger.debug(
                            "Loaded precomputed features from cache: %s",
                            cache_path.name,
                        )
                    else:
                        logger.warning(
                            "Ignoring precompute cache %s: %s",
                            cache_path.name,
                            invalid_reason,
                        )
            except Exception:
                loaded = False

        if not loaded:
            logger.info("Precompute: computing indicators")
            start_time = time.perf_counter()
            atr_14 = _calc_atr(highs_all, lows_all, closes_all, period=14)
            atr_50 = _calc_atr(highs_all, lows_all, closes_all, period=50)
            # Precompute two common EMA periods used by features
            ema_20 = _calc_ema(closes_all, period=20)
            ema_50 = _calc_ema(closes_all, period=50)
            rsi_14 = _calc_rsi(closes_all, period=14)
            bb_all = _bb(closes_all, period=20, std_dev=2.0)
            bb_pos = list(bb_all.get("position") or [])
            adx_14 = _calc_adx(highs_all, lows_all, closes_all, period=14)

            # Precompute Fibonacci swings (LTF) for reuse in feature calculation.
            # Use pandas only for Series conversion inside detect function to keep parity.
            import pandas as _pd

            fib_precompute_cfg = _FibCfg(
                levels=list(fib_cfg.levels),
                weights=dict(fib_cfg.weights),
                atr_depth=fib_cfg.atr_depth,
                max_swings=max(1, len(closes_all)),
                min_swings=fib_cfg.min_swings,
                max_lookback=max(fib_cfg.max_lookback, len(closes_all)),
                swing_threshold_multiple=fib_cfg.swing_threshold_multiple,
                swing_threshold_min=fib_cfg.swing_threshold_min,
                swing_threshold_step=fib_cfg.swing_threshold_step,
            )
            sh_idx, sl_idx, sh_px, sl_px = _detect_swings(
                _pd.Series(highs_all),
                _pd.Series(lows_all),
                _pd.Series(closes_all),
                fib_precompute_cfg,
            )

            elapsed = time.perf_counter() - start_time
            logger.info("Precompute: computed indicators in %.2fs", elapsed)

            if cache_write_enabled:
                try:
                    _np.savez_compressed(
                        cache_path,
                        cache_meta_json=json.dumps(
                            build_cache_metadata(len(closes_all)),
                            sort_keys=True,
                            separators=(",", ":"),
                            ensure_ascii=False,
                        ),
                        atr_14=_np.asarray(atr_14, dtype=float),
                        atr_50=_np.asarray(atr_50, dtype=float),
                        ema_20=_np.asarray(ema_20, dtype=float),
                        ema_50=_np.asarray(ema_50, dtype=float),
                        rsi_14=_np.asarray(rsi_14, dtype=float),
                        bb_position_20_2=_np.asarray(bb_pos, dtype=float),
                        adx_14=_np.asarray(adx_14, dtype=float),
                        fib_high_idx=_np.asarray(sh_idx, dtype=int),
                        fib_low_idx=_np.asarray(sl_idx, dtype=int),
                        fib_high_px=_np.asarray(sh_px, dtype=float),
                        fib_low_px=_np.asarray(sl_px, dtype=float),
                    )
                    logger.debug("Cached precomputed features: %s", cache_path.name)
                except Exception as cache_err:  # nosec B110
                    logger.warning(
                        "Failed to write precompute cache %s: %s",
                        cache_path,
                        cache_err,
                    )
            else:
                logger.debug(
                    "Precompute cache writes disabled via GENESIS_PRECOMPUTE_CACHE_WRITE; "
                    "using in-memory precomputed features only for this run"
                )

            pre = {
                "atr_14": atr_14,
                "atr_50": atr_50,
                "ema_20": ema_20,
                "ema_50": ema_50,
                "rsi_14": rsi_14,
                "bb_position_20_2": bb_pos,
                "adx_14": adx_14,
                "fib_high_idx": list(sh_idx),
                "fib_low_idx": list(sl_idx),
                "fib_high_px": list(sh_px),
                "fib_low_px": list(sl_px),
            }

        if htf_candles_df is not None:
            from core.indicators.htf_fibonacci import compute_htf_fibonacci_mapping

            logger.info("Precompute: mapping HTF Fibonacci levels")
            htf_map = compute_htf_fibonacci_mapping(htf_candles_df, candles_df, fib_cfg)
            for col in [
                "htf_fib_0382",
                "htf_fib_05",
                "htf_fib_0618",
                "htf_swing_high",
                "htf_swing_low",
            ]:
                if col in htf_map.columns:
                    pre[col] = htf_map[col].fillna(0.0).tolist()
            logger.info("Precompute: HTF Fibonacci mapping complete")

        logger.info("Precompute: features ready")
        return pre
    except Exception as e:
        logger.warning("Precomputation failed (non-fatal): %s", e)
        return None
