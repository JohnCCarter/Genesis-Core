from __future__ import annotations

from core.symbols.symbols import DEFAULT_MAP, SymbolMapper, SymbolMode


def test_normalize_inputs() -> None:
    m = SymbolMapper(SymbolMode.REALISTIC)
    assert m.normalize("BTCUSD") == "BTCUSD"
    assert m.normalize("BTC:USD") == "BTCUSD"
    assert m.normalize("tBTCUSD") == "BTCUSD"
    assert m.normalize("tTESTBTC:TESTUSD") == "BTCUSD"


def test_resolve_realistic() -> None:
    m = SymbolMapper(SymbolMode.REALISTIC)
    assert m.resolve("BTCUSD") == DEFAULT_MAP["BTCUSD"]["realistic"]


def test_resolve_synthetic() -> None:
    m = SymbolMapper(SymbolMode.SYNTHETIC)
    assert m.resolve("BTCUSD") == DEFAULT_MAP["BTCUSD"]["synthetic"]


def test_force_passthrough() -> None:
    m = SymbolMapper(SymbolMode.REALISTIC)
    assert m.force("tLTCUSD") == "tLTCUSD"


