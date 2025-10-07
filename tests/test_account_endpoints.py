from __future__ import annotations

from typing import Any

from starlette.testclient import TestClient

from core.server import app


def test_account_wallets_ok(monkeypatch) -> None:
    async def _fake_wallets() -> Any:
        return [
            ["exchange", "USD", 100.0, 0.0, 80.0],
            ["margin", "USD", 50.0, 0.0, 30.0],
            ["exchange", "ETH", 2.0, 0.0, 1.5],
        ]

    import core.io.bitfinex.read_helpers as rh

    monkeypatch.setattr(rh, "get_wallets", _fake_wallets)

    c = TestClient(app)
    r = c.get("/account/wallets")
    assert r.status_code == 200
    data = r.json()
    items = data.get("items") or []
    # endast exchange-wallets
    assert all(i.get("type") == "exchange" for i in items)
    # USD och ETH finns med i items
    curr = sorted(i.get("currency") for i in items)
    assert curr == ["ETH", "USD"]


def test_account_positions_filters_test(monkeypatch) -> None:
    async def _fake_positions() -> Any:
        return [
            ["tBTCUSD", "ACTIVE", 0.1, 30000.0],  # real (ska filtreras bort)
            ["tTESTETH:TESTUSD", "ACTIVE", 1.2, 1500.0],  # TEST (ska med)
        ]

    import core.io.bitfinex.read_helpers as rh

    monkeypatch.setattr(rh, "get_positions", _fake_positions)

    c = TestClient(app)
    r = c.get("/account/positions")
    assert r.status_code == 200
    data = r.json()
    items = data.get("items") or []
    assert len(items) == 1 and items[0]["symbol"].startswith("tTEST")


def test_account_orders_filters_test(monkeypatch) -> None:
    async def _fake_orders() -> Any:
        # Minimal mock: plocka symbol på index 3, amount index 6, type index 8, status index 13
        real_order = [0, 0, 0, "tBTCUSD", 0, 0, 0.01, 0, "EXCHANGE MARKET", 0, 0, 0, 0, "ACTIVE"]
        test_order = [
            0,
            0,
            0,
            "tTESTDOGE:TESTUSD",
            0,
            0,
            25.0,
            0,
            "EXCHANGE MARKET",
            0,
            0,
            0,
            0,
            "ACTIVE",
        ]
        return [real_order, test_order]

    import core.io.bitfinex.read_helpers as rh

    monkeypatch.setattr(rh, "get_orders", _fake_orders)

    c = TestClient(app)
    r = c.get("/account/orders")
    assert r.status_code == 200
    data = r.json()
    items = data.get("items") or []
    assert len(items) == 1 and items[0]["symbol"].startswith("tTEST")
