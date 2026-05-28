from __future__ import annotations

import ast
from pathlib import Path

import pytest


def test_deprecated_features_module_delegates_to_features_asof(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Runtime-bevis: legacy-blocket i core.strategy.features ska vara oexekverbart.

    Vi verifierar detta genom att monkeypatcha aliaset `_extract_features_asof` i
    `core.strategy.features` och kräva att `extract_features()` returnerar exakt
    vad den delegationen returnerar.

    Om legacy-koden efter `return` av misstag skulle aktiveras i framtiden, kommer
    detta test sannolikt att börja faila (antingen p.g.a. annan returform eller
    att patched funktion inte anropas).
    """

    import core.strategy.features as legacy

    sentinel_features = {"_sentinel": 1.0}
    sentinel_meta = {"_sentinel": True}

    calls: dict[str, int] = {"n": 0}

    def _fake_asof(*_args, **_kwargs):  # type: ignore[no-untyped-def]
        calls["n"] += 1
        return sentinel_features, sentinel_meta

    monkeypatch.setattr(legacy, "_extract_features_asof", _fake_asof)

    candles = {
        "open": [1.0, 2.0],
        "high": [2.0, 3.0],
        "low": [0.5, 1.5],
        "close": [1.5, 2.5],
        "volume": [10.0, 11.0],
    }
    feats, meta = legacy.extract_features(candles, config={}, timeframe="1h", symbol="tBTCUSD")

    assert calls["n"] == 1
    assert feats is sentinel_features
    assert meta is sentinel_meta


def test_deprecated_features_module_ast_delegation_contract() -> None:
    """Tripwire: legacy-shim ska vara en ren delegator till features_asof."""

    repo_root = Path(__file__).resolve().parents[2]
    shim_path = repo_root / "src" / "core" / "strategy" / "features.py"

    tree = ast.parse(shim_path.read_text(encoding="utf-8"), filename=str(shim_path))

    has_expected_import = False
    extract_fn: ast.FunctionDef | None = None
    public_functions: list[str] = []

    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == "core.strategy.features_asof":
            if any(
                alias.name == "extract_features" and alias.asname == "_extract_features_asof"
                for alias in node.names
            ):
                has_expected_import = True
        elif isinstance(node, ast.FunctionDef):
            if not node.name.startswith("_"):
                public_functions.append(node.name)
            if node.name == "extract_features":
                extract_fn = node

    assert has_expected_import, "Expected shim import alias from features_asof to exist"
    assert public_functions == [
        "extract_features"
    ], "Legacy shim should expose only extract_features as public function"
    assert extract_fn is not None, "Expected extract_features to exist in legacy shim"

    returns = [node for node in ast.walk(extract_fn) if isinstance(node, ast.Return)]
    assert returns, "Expected extract_features to have a return statement"

    return_expr = returns[-1].value
    assert isinstance(return_expr, ast.Call), "Expected final return to call delegator"
    assert isinstance(return_expr.func, ast.Name), "Expected delegator call by local alias"
    assert (
        return_expr.func.id == "_extract_features_asof"
    ), "Expected final return to delegate to _extract_features_asof"
