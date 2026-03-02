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
from core.strategy.regime_intelligence import resolve_authority_mode_with_source


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
    assert resolve_authority_mode_with_source(cfg) == expected


def test_strict_vs_permissive_asymmetry_canonical_none_value() -> None:
    cfg = {"multi_timeframe": {"regime_intelligence": {"authority_mode": None}}}

    assert resolve_authority_mode_with_source_permissive(cfg) == (
        "legacy",
        AUTHORITY_MODE_SOURCE_CANONICAL,
    )

    with pytest.raises(ValueError) as exc:
        canonicalize_authority_mode_alias_strict(cfg)
    assert str(exc.value) == "invalid_value:regime_intelligence.authority_mode"


def test_strict_vs_permissive_asymmetry_alias_none_value() -> None:
    cfg = {"regime_unified": {"authority_mode": None}}

    assert resolve_authority_mode_with_source_permissive(cfg) == (
        "legacy",
        AUTHORITY_MODE_SOURCE_ALIAS,
    )

    with pytest.raises(ValueError) as exc:
        canonicalize_authority_mode_alias_strict(cfg)
    assert str(exc.value) == "invalid_value:regime_unified.authority_mode"


def test_strict_alias_only_is_canonicalized() -> None:
    out = canonicalize_authority_mode_alias_strict(
        {"regime_unified": {"authority_mode": "regime_module"}}
    )

    assert "regime_unified" not in out
    assert out == {"multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}}}


def test_strict_conflict_canonical_wins() -> None:
    out = canonicalize_authority_mode_alias_strict(
        {
            "multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}},
            "regime_unified": {"authority_mode": "regime_module"},
        }
    )

    assert "regime_unified" not in out
    assert out == {"multi_timeframe": {"regime_intelligence": {"authority_mode": "legacy"}}}


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
