from core.utils.logging_redaction import get_logger, redact_mapping, redact_text


def test_redact_mapping_masks_sensitive_keys():
    data = {
        "bfx-apikey": "ABCDEF123456",  # pragma: allowlist secret (testdata)
        "ok": "value",
        "bfx-signature": "deadbeefcafebabe",  # pragma: allowlist secret (testdata)
    }
    out = redact_mapping(data)
    assert out["ok"] == "value"
    assert out["bfx-apikey"] != data["bfx-apikey"]
    assert out["bfx-signature"] != data["bfx-signature"]


def test_redact_text_masks_headers():
    t = "bfx-apikey: ABCDEF123456 bfx-signature: 001122"  # pragma: allowlist secret (testdata)
    r = redact_text(t)
    assert "ABCDEF" not in r
    assert "001122" not in r


def test_logger_filter_does_not_crash():
    logger = get_logger("test")
    logger.info("bfx-apikey: SECRET123")  # pragma: allowlist secret (testdata)
    assert True
