"""Tests for scripts/build_auth_headers.py masking functionality."""

from __future__ import annotations

import json

from scripts.build_auth_headers import main


def test_mask_flag_not_provided_shows_plain_values(monkeypatch):
    """Test that without --mask flag, sensitive values are shown in plain text."""
    # Set up test credentials
    monkeypatch.setenv("BITFINEX_API_KEY", "test_key_abc123")
    monkeypatch.setenv("BITFINEX_API_SECRET", "test_secret_xyz789")

    # Capture output
    import io
    import sys

    captured_output = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured_output)

    # Call main without --mask flag
    result = main(["auth/r/alerts"])

    # Verify exit code
    assert result == 0

    # Parse output
    output = captured_output.getvalue()
    headers = json.loads(output)

    # Verify sensitive values are NOT masked
    assert headers["bfx-apikey"] == "test_key_abc123"
    assert headers["bfx-signature"] != "***"  # Should be actual signature
    assert headers["bfx-signature"] != ""
    assert len(headers["bfx-signature"]) > 10  # Should be a real signature hash


def test_mask_flag_provided_masks_sensitive_values(monkeypatch):
    """Test that with --mask flag, sensitive values are masked."""
    # Set up test credentials
    monkeypatch.setenv("BITFINEX_API_KEY", "test_key_abc123")
    monkeypatch.setenv("BITFINEX_API_SECRET", "test_secret_xyz789")

    # Capture output
    import io
    import sys

    captured_output = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured_output)

    # Call main WITH --mask flag
    result = main(["auth/r/alerts", "--mask"])

    # Verify exit code
    assert result == 0

    # Parse output
    output = captured_output.getvalue()
    headers = json.loads(output)

    # Verify sensitive values ARE masked
    assert headers["bfx-apikey"] == "***"
    assert headers["bfx-signature"] == "***"


def test_mask_flag_does_not_mask_other_fields(monkeypatch):
    """Test that --mask flag only masks bfx-apikey and bfx-signature."""
    # Set up test credentials
    monkeypatch.setenv("BITFINEX_API_KEY", "test_key_abc123")
    monkeypatch.setenv("BITFINEX_API_SECRET", "test_secret_xyz789")

    # Capture output
    import io
    import sys

    captured_output = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured_output)

    # Call main WITH --mask flag
    result = main(["auth/r/alerts", "--mask"])

    # Verify exit code
    assert result == 0

    # Parse output
    output = captured_output.getvalue()
    headers = json.loads(output)

    # Verify non-sensitive fields are not masked
    assert headers["bfx-nonce"] != "***"
    assert headers["Content-Type"] == "application/json"


def test_without_mask_shows_different_signatures_for_different_requests(monkeypatch):
    """Test that without --mask, actual signatures are generated and differ between requests."""
    # Set up test credentials
    monkeypatch.setenv("BITFINEX_API_KEY", "test_key_abc123")
    monkeypatch.setenv("BITFINEX_API_SECRET", "test_secret_xyz789")

    # Capture first call output
    import io
    import sys

    captured_output1 = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured_output1)
    result1 = main(["auth/r/alerts"])
    assert result1 == 0
    headers1 = json.loads(captured_output1.getvalue())

    # Capture second call output with different endpoint
    captured_output2 = io.StringIO()
    monkeypatch.setattr(sys, "stdout", captured_output2)
    result2 = main(["auth/r/orders"])
    assert result2 == 0
    headers2 = json.loads(captured_output2.getvalue())

    # Signatures should be different for different endpoints
    assert headers1["bfx-signature"] != headers2["bfx-signature"]
    assert headers1["bfx-signature"] != "***"
    assert headers2["bfx-signature"] != "***"
