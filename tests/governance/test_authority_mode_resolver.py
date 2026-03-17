from __future__ import annotations

import pytest

from core.config.authority_mode_resolver import (
    AUTHORITY_MODE_SOURCE_ALIAS,
    AUTHORITY_MODE_SOURCE_ALIAS_INVALID_FALLBACK,
    AUTHORITY_MODE_SOURCE_CANONICAL,
    AUTHORITY_MODE_SOURCE_CANONICAL_INVALID_FALLBACK,
    AUTHORITY_MODE_SOURCE_DEFAULT,
    canonicalize_authority_mode_alias_strict,
    resolve_authority_mode_with_source_permissive,
)


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
                "multi_timeframe": {"regime_intelligence": {"authority_mode": " LEGACY "}},
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
)
def test_authority_mode_precedence_matrix_parity(
    cfg: dict[str, object], expected: tuple[str, str]
) -> None:
    assert resolve_authority_mode_with_source_permissive(cfg) == expected


@pytest.mark.parametrize(
    ("cfg", "expected_source", "expected_error"),
    [
        (
            {"multi_timeframe": {"regime_intelligence": {"authority_mode": None}}},
            AUTHORITY_MODE_SOURCE_CANONICAL,
            "invalid_value:regime_intelligence.authority_mode",
        ),
        (
            {"regime_unified": {"authority_mode": None}},
            AUTHORITY_MODE_SOURCE_ALIAS,
            "invalid_value:regime_unified.authority_mode",
        ),
    ],
)
def test_strict_vs_permissive_asymmetry_none_value(
    cfg: dict[str, object], expected_source: str, expected_error: str
) -> None:
    assert resolve_authority_mode_with_source_permissive(cfg) == (
        "legacy",
        expected_source,
    )

    with pytest.raises(ValueError) as exc:
        canonicalize_authority_mode_alias_strict(cfg)
    assert str(exc.value) == expected_error


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        (
            {"regime_unified": {"authority_mode": "regime_module"}},
            {"multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}}},
        ),
        (
            {
                "multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}},
                "regime_unified": {"authority_mode": "regime_module"},
            },
            {"multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}}},
        ),
    ],
    ids=["alias_only_is_canonicalized", "canonical_wins_conflict"],
)
def test_strict_canonicalization_normalization_cases(
    payload: dict[str, object], expected: dict[str, object]
) -> None:
    out = canonicalize_authority_mode_alias_strict(payload)

    assert "regime_unified" not in out
    assert out == expected


@pytest.mark.parametrize(
    ("payload", "expected_message"),
    [
        (
            {"multi_timeframe": {"regime_intelligence": {"authority_mode": "invalid_mode"}}},
            "invalid_value:regime_intelligence.authority_mode",
        ),
        (
            {
                "multi_timeframe": {"regime_intelligence": {"authority_mode": "invalid_mode"}},
                "regime_unified": {"authority_mode": "regime_module"},
            },
            "invalid_value:regime_intelligence.authority_mode",
        ),
        (
            {"regime_unified": {"authority_mode": "invalid_mode"}},
            "invalid_value:regime_unified.authority_mode",
        ),
        ({"regime_unified": "legacy"}, "non_whitelisted_field:regime_unified"),
        (
            {"regime_unified": {"authority_mode": "legacy", "extra": 1}},
            "non_whitelisted_field:regime_unified",
        ),
    ],
)
def test_strict_canonicalization_exact_exception_message_parity(
    payload: dict[str, object], expected_message: str
) -> None:
    with pytest.raises(ValueError) as exc:
        canonicalize_authority_mode_alias_strict(payload)
    assert str(exc.value) == expected_message
