from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest

from scripts.build.build_auth_headers import (
    SENSITIVE_KEY_FRAGMENTS,
    _sanitize_for_logging,
    build_headers,
    main,
)

MOCK_API_TOKEN_A = "credential_alpha"
MOCK_API_TOKEN_B = "credential_beta"


@pytest.fixture()
def mock_settings():
    """Mock settings with test API credentials."""
    with patch("scripts.build.build_auth_headers.get_settings") as mock:
        settings_obj = Mock()
        settings_obj.BITFINEX_API_KEY = MOCK_API_TOKEN_A  # pragma: allowlist secret
        settings_obj.BITFINEX_API_SECRET = MOCK_API_TOKEN_B  # pragma: allowlist secret
        mock.return_value = settings_obj
        yield mock


@pytest.fixture()
def mock_nonce():
    """Mock nonce to return a fixed value."""
    with patch("scripts.build.build_auth_headers.get_nonce") as mock:
        mock.return_value = "1234567890000000"
        yield mock


def test_build_headers(mock_settings, mock_nonce):
    """Test that build_headers generates correct header structure."""
    _ = (mock_settings, mock_nonce)
    headers = build_headers("auth/r/alerts", {})

    assert "bfx-apikey" in headers
    assert "bfx-nonce" in headers
    assert "bfx-signature" in headers
    assert "Content-Type" in headers

    assert headers["bfx-apikey"] == MOCK_API_TOKEN_A
    assert headers["bfx-nonce"] == "1234567890000000"
    assert headers["Content-Type"] == "application/json"
    assert len(headers["bfx-signature"]) > 0  # Signature should be generated


def test_main_without_reveal(mock_settings, mock_nonce, capsys):
    """Test main function without --reveal flag masks sensitive values by default."""
    _ = (mock_settings, mock_nonce)
    result = main(["auth/r/alerts"])

    assert result == 0

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    # Without --reveal, sensitive values should be masked by default
    assert output["bfx-apikey"] == "***"
    assert output["bfx-signature"] == "***"
    assert output["bfx-nonce"] == "1234567890000000"
    assert output["Content-Type"] == "application/json"
    assert "info" in output


def test_main_with_reveal(mock_settings, mock_nonce, capsys):
    """Test main function with --reveal flag is blocked without explicit ack."""
    _ = (mock_settings, mock_nonce)
    result = main(["auth/r/alerts", "--reveal"])

    assert result == 3

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--reveal blocked" in captured.err
    assert MOCK_API_TOKEN_A not in captured.err
    assert MOCK_API_TOKEN_B not in captured.err


def test_main_with_pretty(mock_settings, mock_nonce, capsys):
    """Test main function with --pretty flag formats JSON nicely."""
    _ = (mock_settings, mock_nonce)
    result = main(["auth/r/alerts", "--pretty"])

    assert result == 0

    captured = capsys.readouterr()
    # Pretty-printed JSON should have indentation (newlines)
    assert "\n" in captured.out
    output = json.loads(captured.out)
    # Without --reveal, values should be masked
    assert output["bfx-apikey"] == "***"


def test_main_with_reveal_and_pretty(mock_settings, mock_nonce, capsys):
    """Test reveal+pretty is blocked without explicit ack."""
    _ = (mock_settings, mock_nonce)
    result = main(["auth/r/alerts", "--reveal", "--pretty"])

    assert result == 3

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--reveal blocked" in captured.err


def test_main_with_reveal_and_ack_masks_sensitive_values(
    mock_settings, mock_nonce, capsys, monkeypatch
):
    """Test reveal mode with explicit ack still masks secrets for safe logging."""
    _ = (mock_settings, mock_nonce)
    monkeypatch.setenv("GENESIS_ALLOW_SECRET_OUTPUT", "1")

    result = main(["auth/r/alerts", "--reveal"])

    assert result == 0

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    assert output["bfx-apikey"] == "***"
    assert output["bfx-signature"] == "***"
    assert output["bfx-nonce"] == "1234567890000000"
    assert output["Content-Type"] == "application/json"
    assert "info" in output


def test_main_with_reveal_and_wrong_ack_is_blocked(mock_settings, mock_nonce, capsys, monkeypatch):
    """Test reveal mode stays blocked when ack env var has incorrect value."""
    _ = (mock_settings, mock_nonce)
    monkeypatch.setenv("GENESIS_ALLOW_SECRET_OUTPUT", "0")

    result = main(["auth/r/alerts", "--reveal"])

    assert result == 3
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "--reveal blocked" in captured.err


def test_main_with_body(mock_settings, mock_nonce, capsys):
    """Test main function with custom JSON body."""
    _ = (mock_settings, mock_nonce)
    body_json = '{"type":"test","data":123}'
    result = main(["auth/r/alerts", "--body", body_json])

    assert result == 0

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert "bfx-apikey" in output


def test_main_with_invalid_json_body(mock_settings, mock_nonce, capsys):
    """Test main function with invalid JSON body returns error."""
    _ = (mock_settings, mock_nonce)
    result = main(["auth/r/alerts", "--body", "{invalid json}"])

    assert result == 2  # Error code for invalid JSON

    captured = capsys.readouterr()
    assert "Invalid JSON body" in captured.err


def test_build_headers_missing_credentials():
    """Test that build_headers raises error when credentials are missing."""
    with patch("scripts.build.build_auth_headers.get_settings") as mock:
        settings_obj = Mock()
        settings_obj.BITFINEX_API_KEY = None
        settings_obj.BITFINEX_API_SECRET = None
        mock.return_value = settings_obj

        with pytest.raises(RuntimeError, match="BITFINEX API credentials saknas"):
            build_headers("auth/r/alerts", {})


# ---------------------------------------------------------------------------
# _sanitize_for_logging tests
# ---------------------------------------------------------------------------


def test_sanitize_flat_dict_masks_sensitive_keys():
    """Sensitive keys in a flat dict are replaced with '***'.

    Keys are matched by fragment: any key whose lowercase form contains a
    fragment from SENSITIVE_KEY_FRAGMENTS is redacted.
    """
    # "apikey" and "secret" are exact members of SENSITIVE_KEY_FRAGMENTS
    assert "apikey" in SENSITIVE_KEY_FRAGMENTS
    assert "secret" in SENSITIVE_KEY_FRAGMENTS
    data = {
        "apikey": "real_key",  # pragma: allowlist secret
        "secret": "real_secret",  # pragma: allowlist secret
        "safe_field": "visible",
    }
    result = _sanitize_for_logging(data)
    assert result["apikey"] == "***"
    assert result["secret"] == "***"
    assert result["safe_field"] == "visible"


def test_sanitize_flat_dict_leaves_non_sensitive_keys_unchanged():
    """Non-sensitive keys are preserved with their original values."""
    data = {"endpoint": "/api/v2/auth", "nonce": "12345", "Content-Type": "application/json"}
    result = _sanitize_for_logging(data)
    assert result == data


def test_sanitize_nested_dict_masks_sensitive_keys_recursively():
    """Sensitive keys nested inside dicts are recursively masked."""
    data = {"outer": {"inner_password": "s3cr3t", "public_info": "ok"}}  # pragma: allowlist secret
    result = _sanitize_for_logging(data)
    assert result["outer"]["inner_password"] == "***"
    assert result["outer"]["public_info"] == "ok"


def test_sanitize_list_of_dicts():
    """Dicts inside a list are sanitized recursively."""
    data = [{"token": "abc123", "name": "test"}, {"value": 42}]
    result = _sanitize_for_logging(data)
    assert isinstance(result, list)
    assert result[0]["token"] == "***"
    assert result[0]["name"] == "test"
    assert result[1]["value"] == 42


def test_sanitize_tuple_of_dicts():
    """Dicts inside a tuple are sanitized recursively and result is a tuple."""
    data = ({"password": "hunter2"}, {"safe": "yes"})  # pragma: allowlist secret
    result = _sanitize_for_logging(data)
    assert isinstance(result, tuple)
    assert result[0]["password"] == "***"
    assert result[1]["safe"] == "yes"


def test_sanitize_fragment_based_key_matching():
    """Keys containing sensitive fragments (not exact matches) are masked."""
    data = {
        "bfx-apikey": "real_key",  # pragma: allowlist secret
        "x-auth-token": "bearer_xyz",
        "my_password_hash": "hashed",  # pragma: allowlist secret
        "normal_key": "value",
    }
    result = _sanitize_for_logging(data)
    assert result["bfx-apikey"] == "***"
    assert result["x-auth-token"] == "***"
    assert result["my_password_hash"] == "***"
    assert result["normal_key"] == "value"


def test_sanitize_does_not_overredact_embedded_substrings():
    """Generic fragments should not redact unrelated words like 'author'."""
    data = {
        "author": "visible",
        "authored_at": "2026-05-18",
        "tokenized": "visible",
        "x-auth-token": "masked",  # pragma: allowlist secret
    }
    result = _sanitize_for_logging(data)
    assert result["author"] == "visible"
    assert result["authored_at"] == "2026-05-18"
    assert result["tokenized"] == "visible"
    assert result["x-auth-token"] == "***"


def test_sanitize_mixed_nested_structure():
    """Mixed nesting of dicts, lists, and tuples is fully sanitized."""
    data = {
        "headers": [{"bfx-signature": "sig_value", "Content-Type": "application/json"}],
        "meta": {"info": "safe", "authorization": "Bearer token_abc"},
    }
    result = _sanitize_for_logging(data)
    assert result["headers"][0]["bfx-signature"] == "***"
    assert result["headers"][0]["Content-Type"] == "application/json"
    assert result["meta"]["info"] == "safe"
    assert result["meta"]["authorization"] == "***"


def test_sanitize_non_dict_scalar_passthrough():
    """Scalar values (int, str, None) pass through unchanged.

    Only dict *keys* trigger redaction; standalone scalars that look like
    secret values (e.g. "password123") are not masked because there is no
    key context — the sanitizer only redacts by dict key name.
    """
    assert _sanitize_for_logging(42) == 42
    assert _sanitize_for_logging("plain string") == "plain string"
    assert _sanitize_for_logging(None) is None
    # Scalar that *contains* a sensitive fragment in its own text is NOT masked
    assert _sanitize_for_logging("password123") == "password123"
    assert _sanitize_for_logging("my_secret_value") == "my_secret_value"


def test_sanitize_empty_structures():
    """Empty dict, list, and tuple return their empty equivalents."""
    assert _sanitize_for_logging({}) == {}
    assert _sanitize_for_logging([]) == []
    assert _sanitize_for_logging(()) == ()
