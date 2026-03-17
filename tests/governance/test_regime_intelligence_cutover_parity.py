from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import pytest

from core.config.authority_mode_resolver import (
    AUTHORITY_MODE_SOURCE_ALIAS,
    AUTHORITY_MODE_SOURCE_ALIAS_INVALID_FALLBACK,
    AUTHORITY_MODE_SOURCE_CANONICAL,
    AUTHORITY_MODE_SOURCE_CANONICAL_INVALID_FALLBACK,
    AUTHORITY_MODE_SOURCE_DEFAULT,
    resolve_authority_mode_with_source_permissive,
)
from core.observability.metrics import (
    PIPELINE_COMPONENT_ORDER,
    pipeline_component_order_hash,
)
from core.strategy.evaluate import evaluate_pipeline

_ARTIFACT_PATH = (
    Path(__file__).resolve().parents[2]
    / "results"
    / "evaluation"
    / "ri_p1_off_parity_v1_ri-20260303-003.json"
)


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(merged.get(key), dict) and isinstance(value, dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def _clean_runtime_test_cfg(base_cfg: dict[str, Any]) -> dict[str, Any]:
    cfg = deepcopy(base_cfg)
    cfg.pop("precomputed_features", None)
    cfg.pop("_global_index", None)
    return cfg


def _projection(result: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    shadow_obs = meta["observability"]["shadow_regime"]
    decision = meta["decision"]
    return {
        "action": result["action"],
        "confidence": result["confidence"],
        "regime": result["regime"],
        "decision_size": decision.get("size"),
        "decision_reasons": decision.get("reasons"),
        "authority_mode": shadow_obs["authority_mode"],
        "authority_mode_source": shadow_obs["authority_mode_source"],
        "authoritative_source": shadow_obs["authoritative_source"],
        "authority": shadow_obs["authority"],
        "shadow": shadow_obs["shadow"],
        "mismatch": shadow_obs["mismatch"],
        "decision_input": shadow_obs["decision_input"],
    }


@pytest.mark.parametrize(
    ("cfg", "expected"),
    [
        ({}, ("legacy", AUTHORITY_MODE_SOURCE_DEFAULT)),
        (
            {"regime_unified": {"authority_mode": "regime_module"}},
            ("regime_module", AUTHORITY_MODE_SOURCE_ALIAS),
        ),
        (
            {
                "multi_timeframe": {"regime_intelligence": {"authority_mode": " legacy "}},
                "regime_unified": {"authority_mode": "regime_module"},
            },
            ("legacy", AUTHORITY_MODE_SOURCE_CANONICAL),
        ),
        (
            {
                "multi_timeframe": {"regime_intelligence": {"authority_mode": "invalid_mode"}},
                "regime_unified": {"authority_mode": "regime_module"},
            },
            ("legacy", AUTHORITY_MODE_SOURCE_CANONICAL_INVALID_FALLBACK),
        ),
        (
            {"regime_unified": {"authority_mode": "invalid_mode"}},
            ("legacy", AUTHORITY_MODE_SOURCE_ALIAS_INVALID_FALLBACK),
        ),
    ],
    ids=[
        "default_legacy",
        "alias_regime_module",
        "canonical_legacy_wins",
        "canonical_invalid_falls_back_to_legacy",
        "alias_invalid_falls_back_to_legacy",
    ],
)
def test_cutover_authority_precedence_and_fallback_invariants(
    cfg: dict[str, object], expected: tuple[str, str]
) -> None:
    """Observe the current authority precedence contract without changing it."""

    assert resolve_authority_mode_with_source_permissive(cfg) == expected


def test_cutover_legacy_and_regime_module_are_observably_distinct_but_deterministic(
    monkeypatch: pytest.MonkeyPatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
) -> None:
    """Observe the current authority-mode split without imposing cross-mode equality.

    This is intentionally observational only:
    - legacy mode must be deterministic across repeated identical inputs,
    - regime_module mode must be deterministic across repeated identical inputs,
    - metadata must expose the resolved authority-path difference.
    """

    from core.strategy import evaluate as ev
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "ranging")
    monkeypatch.setattr(ev, "_detect_shadow_regime_from_regime_module", lambda *_a, **_k: "bull")

    base_cfg = _clean_runtime_test_cfg(sample_configs)
    legacy_cfg = _merge(
        base_cfg,
        {"multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}}},
    )
    regime_cfg = _merge(
        base_cfg,
        {"multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}}},
    )

    legacy_runs = [
        _projection(
            *evaluate_pipeline(
                small_candle_history,
                policy=sample_policy,
                configs=legacy_cfg,
            )
        )
        for _ in range(2)
    ]
    regime_runs = [
        _projection(
            *evaluate_pipeline(
                small_candle_history,
                policy=sample_policy,
                configs=regime_cfg,
            )
        )
        for _ in range(2)
    ]

    assert legacy_runs[0] == legacy_runs[1]
    assert regime_runs[0] == regime_runs[1]

    legacy_obs = legacy_runs[0]
    regime_obs = regime_runs[0]

    assert legacy_obs["authority_mode"] == "legacy"
    assert (
        legacy_obs["authority_mode_source"] == "multi_timeframe.regime_intelligence.authority_mode"
    )
    assert legacy_obs["authoritative_source"] == "regime_unified.detect_regime_unified"
    assert legacy_obs["regime"] == "ranging"
    assert legacy_obs["authority"] == "ranging"
    assert legacy_obs["shadow"] == "bull"
    assert legacy_obs["decision_input"] is False

    assert regime_obs["authority_mode"] == "regime_module"
    assert (
        regime_obs["authority_mode_source"] == "multi_timeframe.regime_intelligence.authority_mode"
    )
    assert regime_obs["authoritative_source"] == "regime.detect_regime_from_candles"
    assert regime_obs["regime"] == "bull"
    assert regime_obs["authority"] == "bull"
    assert regime_obs["shadow"] == "bull"
    assert regime_obs["decision_input"] is False


@pytest.mark.parametrize(
    ("cfg_patch", "expected_mode", "expected_authoritative_source"),
    [
        ({}, "legacy", "regime_unified.detect_regime_unified"),
        (
            {"multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}}},
            "regime_module",
            "regime.detect_regime_from_candles",
        ),
    ],
    ids=["default_legacy_replay", "regime_module_replay"],
)
def test_cutover_identical_inputs_replay_identical_outputs_within_authority_mode(
    monkeypatch: pytest.MonkeyPatch,
    sample_policy: dict[str, Any],
    sample_configs: dict[str, Any],
    small_candle_history: dict[str, Any],
    cfg_patch: dict[str, Any],
    expected_mode: str,
    expected_authoritative_source: str,
) -> None:
    from core.strategy import evaluate as ev
    from core.strategy import regime_unified as ru

    monkeypatch.setattr(ru, "detect_regime_unified", lambda *_a, **_k: "ranging")
    monkeypatch.setattr(ev, "_detect_shadow_regime_from_regime_module", lambda *_a, **_k: "bull")

    cfg = _merge(_clean_runtime_test_cfg(sample_configs), cfg_patch)

    projections = [
        _projection(
            *evaluate_pipeline(
                small_candle_history,
                policy=sample_policy,
                configs=cfg,
            )
        )
        for _ in range(3)
    ]

    assert projections[0] == projections[1] == projections[2]
    assert projections[0]["authority_mode"] == expected_mode
    assert projections[0]["authoritative_source"] == expected_authoritative_source
    assert projections[0]["decision_input"] is False


def test_cutover_pipeline_hash_stability() -> None:
    assert PIPELINE_COMPONENT_ORDER == (
        "features",
        "proba",
        "confidence",
        "regime",
        "decision",
    )
    assert pipeline_component_order_hash() == "200a25070a6f7fe4"


def test_cutover_ri_parity_artifact_consistency() -> None:
    artifact = json.loads(_ARTIFACT_PATH.read_text(encoding="utf-8"))

    required_fields = {
        "action_mismatch_count",
        "added_row_count",
        "baseline_artifact_ref",
        "end_utc",
        "git_sha",
        "missing_row_count",
        "mode",
        "parity_verdict",
        "reason_mismatch_count",
        "run_id",
        "size_mismatch_count",
        "size_tolerance",
        "start_utc",
        "symbols",
        "timeframes",
        "window_spec_id",
    }

    assert required_fields.issubset(artifact.keys())
    assert artifact["window_spec_id"] == "ri_p1_off_parity_v1"
    assert artifact["mode"] == "OFF"
    assert artifact["parity_verdict"] in {"PASS", "FAIL"}
    assert artifact["size_tolerance"] == "1e-12"
    assert artifact["symbols"]
    assert artifact["timeframes"]
    assert (
        str(artifact["baseline_artifact_ref"])
        == "results/evaluation/ri_p1_off_parity_v1_baseline.json"
    )

    if artifact["parity_verdict"] == "FAIL":
        assert (
            int(artifact["action_mismatch_count"])
            + int(artifact["reason_mismatch_count"])
            + int(artifact["size_mismatch_count"])
            + int(artifact["added_row_count"])
            + int(artifact["missing_row_count"])
        ) > 0
