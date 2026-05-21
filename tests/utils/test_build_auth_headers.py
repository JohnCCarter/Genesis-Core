from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest

from scripts.build.build_auth_headers import _sanitize_for_logging, build_headers, main

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
    assert output["bfx-nonce"] == "<generated>"
    assert output["Content-Type"] == "application/json"
    assert "info" in output
    assert MOCK_API_TOKEN_A not in captured.out
    assert MOCK_API_TOKEN_B not in captured.out
    assert "1234567890000000" not in captured.out


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
    assert output["bfx-nonce"] == "<generated>"
    assert output["Content-Type"] == "application/json"
    assert "info" in output
    assert MOCK_API_TOKEN_A not in captured.out
    assert MOCK_API_TOKEN_B not in captured.out
    assert "1234567890000000" not in captured.out


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


def test_sanitize_for_logging_masks_nested_sensitive_keys():
    payload = {
        "api_key": "top_level_key",  # pragma: allowlist secret
        "nested": {
            "TokenValue": "nested_token",  # pragma: allowlist secret
            "items": [
                {"userPassword": "pw1"},  # pragma: allowlist secret
                {"safe": "ok"},
            ],
            "tuple_data": (
                {"authorizationHeader": "Bearer secret"},  # pragma: allowlist secret
                {"safe_key": "safe_value"},
            ),
        },
    }

    sanitized = _sanitize_for_logging(payload)

    assert sanitized["api_key"] == "***"
    assert sanitized["nested"]["TokenValue"] == "***"
    assert sanitized["nested"]["items"][0]["userPassword"] == "***"
    assert sanitized["nested"]["items"][1]["safe"] == "ok"
    assert sanitized["nested"]["tuple_data"][0]["authorizationHeader"] == "***"
    assert sanitized["nested"]["tuple_data"][1]["safe_key"] == "safe_value"


def test_sanitize_for_logging_masks_camel_case_sensitive_keys():
    data = {
        "apiSecret": "super_secret_value",  # pragma: allowlist secret
        "normal_key": "value",
    }

    sanitized = _sanitize_for_logging(data)

    assert sanitized["apiSecret"] == "***"
    assert sanitized["normal_key"] == "value"


def test_sanitize_for_logging_does_not_overredact_embedded_substrings():
    data = {
        "author": "visible",
        "authored_at": "2026-05-18",
        "tokenized": "visible",
        "x-auth-token": "masked",  # pragma: allowlist secret
    }

    sanitized = _sanitize_for_logging(data)

    assert sanitized["author"] == "visible"
    assert sanitized["authored_at"] == "2026-05-18"
    assert sanitized["tokenized"] == "visible"
    assert sanitized["x-auth-token"] == "***"


def test_sanitize_for_logging_scalar_passthrough():
    assert _sanitize_for_logging(42) == 42
    assert _sanitize_for_logging("plain string") == "plain string"
    assert _sanitize_for_logging(None) is None
    assert _sanitize_for_logging("password123") == "password123"
