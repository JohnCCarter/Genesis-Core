from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_runner_module():
    repo_root = Path(__file__).resolve().parents[1]
    runner_path = repo_root / "scripts" / "paper_trading_runner.py"
    spec = importlib.util.spec_from_file_location("paper_trading_runner", runner_path)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


class _FakeClient:
    def __init__(self, payload):
        self._payload = payload
        self.last_url = None
        self.last_params = None
        self.last_timeout = None

    def get(self, url, params=None, timeout=None):
        self.last_url = url
        self.last_params = params
        self.last_timeout = timeout
        return _FakeResponse(self._payload)


class _FakeLogger:
    def error(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None


def test_fetch_candles_window_reverses_descending_payload_to_chronological_order():
    mod = _load_runner_module()

    # Simulate Bitfinex payload with sort=-1 (descending): newest candle first.
    rows_desc = [
        [2000, 2.0, 20.0, 22.0, 18.0, 100.0],
        [1000, 1.0, 10.0, 12.0, 8.0, 50.0],
    ]

    client = _FakeClient(rows_desc)
    logger = _FakeLogger()

    out = mod.fetch_candles_window(
        symbol="tBTCUSD",
        timeframe="1h",
        end_ms=2000,
        client=client,
        logger=logger,
        limit=2,
    )

    assert out is not None

    # Ensure we requested the *newest* candles (descending) and then normalized to chronological order.
    assert client.last_params["sort"] == -1
    assert out["close"] == [10.0, 20.0]
    assert out["open"] == [1.0, 2.0]
    assert out["high"] == [12.0, 22.0]
    assert out["low"] == [8.0, 18.0]
    assert out["volume"] == [50.0, 100.0]


def test_maybe_reset_pipeline_state_resets_on_large_last_close_mismatch():
    mod = _load_runner_module()
    logger = _FakeLogger()

    state_in = {"last_close": 999.0, "some_other_key": "kept?"}
    out = mod._maybe_reset_pipeline_state(state_in, live_close=100.0, logger=logger)

    assert out == {}
