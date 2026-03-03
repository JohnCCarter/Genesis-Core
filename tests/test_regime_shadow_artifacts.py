from __future__ import annotations

import json
import os
from copy import deepcopy
from pathlib import Path
from statistics import fmean, pstdev
from typing import Any


def _clarity_score(confidence: dict[str, Any]) -> int:
    value = confidence.get("overall", 0.0)
    try:
        numeric = float(value)
    except Exception:
        numeric = 0.0
    clamped = max(0.0, min(1.0, numeric))
    return int(round(clamped * 100.0))


def _percentile(sorted_values: list[int], q: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return float(sorted_values[0])

    index = (len(sorted_values) - 1) * q
    lo = int(index)
    hi = min(lo + 1, len(sorted_values) - 1)
    frac = index - lo
    return float(sorted_values[lo] + (sorted_values[hi] - sorted_values[lo]) * frac)


def _clarity_histogram(scores: list[int]) -> dict[str, int]:
    labels = [
        "0-9",
        "10-19",
        "20-29",
        "30-39",
        "40-49",
        "50-59",
        "60-69",
        "70-79",
        "80-89",
        "90-100",
    ]
    histogram = dict.fromkeys(labels, 0)

    for score in scores:
        bucket = min(score // 10, 9)
        histogram[labels[bucket]] += 1

    return histogram


def test_regime_shadow_artifacts_smoke(
    monkeypatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    """Smoke-test shadow regime observability in OFF/default authority mode.

    Contract:
    - Default/OFF path is decision-safe (no authority change),
    - `meta.observability.shadow_regime` keeps a stable shape,
    - Optional artifacts are written only when REGIME_EVIDENCE_DIR is set.
    """

    from core.strategy import evaluate as ev
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "ranging")
    monkeypatch.setattr(ev, "_detect_shadow_regime_from_regime_module", lambda *_a, **_k: "bull")

    base_cfg = deepcopy(sample_configs)
    base_cfg.pop("precomputed_features", None)
    base_cfg.pop("_global_index", None)
    base_cfg.setdefault("multi_timeframe", {})

    explicit_off_cfg = deepcopy(base_cfg)
    explicit_off_cfg["multi_timeframe"]["regime_intelligence"] = {"authority_mode": "legacy"}

    result_default, meta_default = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(base_cfg),
    )
    result_off, meta_off = ev.evaluate_pipeline(
        small_candle_history,
        policy=sample_policy,
        configs=deepcopy(explicit_off_cfg),
    )

    assert {
        "action": result_default["action"],
        "confidence": result_default["confidence"],
        "regime": result_default["regime"],
    } == {
        "action": result_off["action"],
        "confidence": result_off["confidence"],
        "regime": result_off["regime"],
    }

    expected_shadow_keys = {
        "authoritative_source",
        "shadow_source",
        "authority_mode",
        "authority_mode_source",
        "authority",
        "shadow",
        "mismatch",
        "decision_input",
    }

    shadow_default = meta_default["observability"]["shadow_regime"]
    shadow_off = meta_off["observability"]["shadow_regime"]

    assert expected_shadow_keys.issubset(shadow_default.keys())
    assert expected_shadow_keys.issubset(shadow_off.keys())
    assert tuple(sorted(shadow_default.keys())) == tuple(sorted(shadow_off.keys()))
    assert shadow_default["authority_mode"] == "legacy"
    assert shadow_off["authority_mode"] == "legacy"
    assert shadow_default["decision_input"] is False
    assert shadow_off["decision_input"] is False

    samples: list[dict[str, Any]] = []
    observed_shape: tuple[str, ...] | None = None

    timestamps = small_candle_history.get("timestamp")
    sample_timestamp = timestamps[-1] if isinstance(timestamps, list) and timestamps else None

    for bar_index in range(220):
        result, meta = ev.evaluate_pipeline(
            small_candle_history,
            policy=sample_policy,
            configs=deepcopy(base_cfg),
        )

        shadow_obs = meta["observability"]["shadow_regime"]
        current_shape = tuple(sorted(shadow_obs.keys()))
        if observed_shape is None:
            observed_shape = current_shape
        else:
            assert current_shape == observed_shape

        confidence = result.get("confidence") if isinstance(result.get("confidence"), dict) else {}
        clarity = _clarity_score(confidence)

        samples.append(
            {
                "symbol": sample_policy.get("symbol", "tBTCUSD"),
                "timeframe": sample_policy.get("timeframe", "1m"),
                "bar_index": bar_index,
                "timestamp": sample_timestamp,
                "authoritative_regime": result["regime"],
                "shadow_regime": shadow_obs["shadow"],
                "clarity_score": clarity,
                "mismatch": shadow_obs["mismatch"],
                "authority_mode": shadow_obs["authority_mode"],
            }
        )

    preferred_min_samples = 200
    fallback_min_samples = 50
    minimum_required = (
        preferred_min_samples if len(samples) >= preferred_min_samples else fallback_min_samples
    )
    assert len(samples) >= minimum_required

    clarity_scores = [int(sample["clarity_score"]) for sample in samples]
    assert all(isinstance(score, int) and 0 <= score <= 100 for score in clarity_scores)
    assert all(
        isinstance(sample.get("authoritative_regime"), str) and bool(sample["authoritative_regime"])
        for sample in samples
    )
    assert all(
        isinstance(sample.get("shadow_regime"), str) and bool(sample["shadow_regime"])
        for sample in samples
    )

    evidence_dir_raw = os.getenv("REGIME_EVIDENCE_DIR")
    if not evidence_dir_raw:
        return

    evidence_dir = Path(evidence_dir_raw)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    clarity_sorted = sorted(clarity_scores)
    histogram_payload = _clarity_histogram(clarity_scores)
    quantiles_payload = {
        "p50": _percentile(clarity_sorted, 0.50),
        "p80": _percentile(clarity_sorted, 0.80),
        "p90": _percentile(clarity_sorted, 0.90),
        "p95": _percentile(clarity_sorted, 0.95),
        "top20_threshold": _percentile(clarity_sorted, 0.80),
        "mean": float(fmean(clarity_scores)),
        "std": float(pstdev(clarity_scores)) if len(clarity_scores) > 1 else 0.0,
        "total": len(clarity_scores),
    }

    histogram_path = evidence_dir / "clarity_histogram.json"
    quantiles_path = evidence_dir / "clarity_quantiles.json"
    samples_path = evidence_dir / "shadow_samples.ndjson"

    histogram_path.write_text(
        json.dumps(histogram_payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    quantiles_path.write_text(
        json.dumps(quantiles_payload, indent=2, sort_keys=True), encoding="utf-8"
    )
    with samples_path.open("w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, separators=(",", ":"), sort_keys=True))
            handle.write("\n")

    assert histogram_path.exists()
    assert quantiles_path.exists()
    assert samples_path.exists()

    loaded_histogram = json.loads(histogram_path.read_text(encoding="utf-8"))
    loaded_quantiles = json.loads(quantiles_path.read_text(encoding="utf-8"))

    assert isinstance(loaded_histogram, dict)
    assert sum(int(v) for v in loaded_histogram.values()) == len(samples)
    assert loaded_quantiles["total"] == len(samples)
    assert loaded_quantiles["p80"] == loaded_quantiles["top20_threshold"]
