from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest

from scripts.build_auth_headers import build_headers, main


@pytest.fixture()
def mock_settings():
    """Mock settings with test API credentials."""
    with patch("scripts.build_auth_headers.get_settings") as mock:
        settings_obj = Mock()
        settings_obj.BITFINEX_API_KEY = "test_api_key"
        settings_obj.BITFINEX_API_SECRET = "test_api_secret"
        mock.return_value = settings_obj
        yield mock


@pytest.fixture()
def mock_nonce():
    """Mock nonce to return a fixed value."""
    with patch("scripts.build_auth_headers.get_nonce") as mock:
        mock.return_value = "1234567890000000"
        yield mock


def test_build_headers(mock_settings, mock_nonce):
    """Test that build_headers generates correct header structure."""
    headers = build_headers("auth/r/alerts", {})

    assert "bfx-apikey" in headers
    assert "bfx-nonce" in headers
    assert "bfx-signature" in headers
    assert "Content-Type" in headers

    assert headers["bfx-apikey"] == "test_api_key"
    assert headers["bfx-nonce"] == "1234567890000000"
    assert headers["Content-Type"] == "application/json"
    assert len(headers["bfx-signature"]) > 0  # Signature should be generated


def test_main_without_reveal(mock_settings, mock_nonce, capsys):
    """Test main function without --reveal flag masks sensitive values by default."""
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
    """Test main function with --reveal flag shows actual values."""
    result = main(["auth/r/alerts", "--reveal"])

    assert result == 0

    captured = capsys.readouterr()
    output = json.loads(captured.out)

    # With --reveal, actual values should be shown
    assert output["bfx-apikey"] == "test_api_key"
    assert output["bfx-signature"] != "***"
    # Non-sensitive values should not be masked
    assert output["bfx-nonce"] == "1234567890000000"
    assert output["Content-Type"] == "application/json"


def test_main_with_pretty(mock_settings, mock_nonce, capsys):
    """Test main function with --pretty flag formats JSON nicely."""
    result = main(["auth/r/alerts", "--pretty"])

    assert result == 0

    captured = capsys.readouterr()
    # Pretty-printed JSON should have indentation (newlines)
    assert "\n" in captured.out
    output = json.loads(captured.out)
    # Without --reveal, values should be masked
    assert output["bfx-apikey"] == "***"


def test_main_with_reveal_and_pretty(mock_settings, mock_nonce, capsys):
    """Test main function with both --reveal and --pretty flags."""
    result = main(["auth/r/alerts", "--reveal", "--pretty"])

    assert result == 0

    captured = capsys.readouterr()
    # Should be pretty-printed
    assert "\n" in captured.out
    output = json.loads(captured.out)

    # Should show actual values with --reveal
    assert output["bfx-apikey"] == "test_api_key"
    assert output["bfx-signature"] != "***"


def test_main_with_body(mock_settings, mock_nonce, capsys):
    """Test main function with custom JSON body."""
    body_json = '{"type":"test","data":123}'
    result = main(["auth/r/alerts", "--body", body_json])

    assert result == 0

    captured = capsys.readouterr()
    output = json.loads(captured.out)
    assert "bfx-apikey" in output


def test_main_with_invalid_json_body(mock_settings, mock_nonce, capsys):
    """Test main function with invalid JSON body returns error."""
    result = main(["auth/r/alerts", "--body", "{invalid json}"])

    assert result == 2  # Error code for invalid JSON

    captured = capsys.readouterr()
    assert "Invalid JSON body" in captured.err


def test_build_headers_missing_credentials():
    """Test that build_headers raises error when credentials are missing."""
    with patch("scripts.build_auth_headers.get_settings") as mock:
        settings_obj = Mock()
        settings_obj.BITFINEX_API_KEY = None
        settings_obj.BITFINEX_API_SECRET = None
        mock.return_value = settings_obj

        with pytest.raises(RuntimeError, match="BITFINEX API credentials saknas"):
            build_headers("auth/r/alerts", {})
