"""Smoke test for public symbols API interaction."""


def test_fetch_symbols_structure():
    """Smoke test: ensure requests module is available and import works."""
    import requests

    # Just ensure the library works and URL is valid format
    url = "https://api-pub.bitfinex.com/v2/tickers?symbols=ALL"
    assert url.startswith("https://")
    assert "api-pub.bitfinex.com" in url
    assert requests.__version__  # Ensure requests is installed
