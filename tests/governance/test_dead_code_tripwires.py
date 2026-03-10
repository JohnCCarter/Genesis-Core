from __future__ import annotations

import ast
from datetime import UTC, datetime
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


def test_position_tracker_does_not_use_legacy_close_method(monkeypatch: pytest.MonkeyPatch) -> None:
    """Runtime-bevis: legacy-symbolen finns inte och _close_position är enda close-path.

    Testet verifierar explicit att `_close_position_legacy` inte längre existerar,
    samt att opposite-signal close går via `_close_position` och därefter
    `close_position_with_reason(..., reason="OPPOSITE_SIGNAL")`.
    """

    from core.backtest.position_tracker import PositionTracker

    assert not hasattr(PositionTracker, "_close_position_legacy")

    pt = PositionTracker(initial_capital=1000.0)

    calls = {
        "_close_position": 0,
        "close_position_with_reason": 0,
        "reasons": [],
    }

    original_close_position = pt._close_position
    original_close_with_reason = pt.close_position_with_reason

    def _wrapped_close_position(price: float, timestamp: datetime):
        calls["_close_position"] += 1
        return original_close_position(price, timestamp)

    def _wrapped_close_with_reason(price: float, timestamp: datetime, reason: str = "MANUAL"):
        calls["close_position_with_reason"] += 1
        calls["reasons"].append(reason)
        return original_close_with_reason(price, timestamp, reason=reason)

    monkeypatch.setattr(pt, "_close_position", _wrapped_close_position)
    monkeypatch.setattr(pt, "close_position_with_reason", _wrapped_close_with_reason)

    ts0 = datetime(2020, 1, 1, tzinfo=UTC)
    ts1 = datetime(2020, 1, 2, tzinfo=UTC)

    # Open LONG
    r0 = pt.execute_action("LONG", size=1.0, price=100.0, timestamp=ts0, symbol="tTESTBTC:TESTUSD")
    assert r0["executed"] is True

    # Close by opposite signal (this uses _close_position -> close_position_with_reason)
    r1 = pt.execute_action("SHORT", size=1.0, price=101.0, timestamp=ts1, symbol="tTESTBTC:TESTUSD")
    assert r1["executed"] is True

    # execute_action() overwrites the intermediate close reason with "opened" after opening the new position.
    assert pt.position is not None
    assert pt.position.side == "SHORT"

    # Ensure we recorded at least one trade
    assert len(pt.trades) >= 1
    assert any(t.exit_reason == "OPPOSITE_SIGNAL" for t in pt.trades)
    assert calls["_close_position"] == 1
    assert calls["close_position_with_reason"] == 1
    assert calls["reasons"] == ["OPPOSITE_SIGNAL"]


def test_backtest_engine_prefers_new_htf_exit_engine_when_config_present_and_env_unset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tripwire: Om GENESIS_HTF_EXITS saknas men htf_exit_config är satt ska NEW-engine väljas.

    Detta minskar risken för "spökkod" där manual backtest råkar gå en annan väg än optimizer.
    """

    import core.backtest.engine as engine_mod

    if engine_mod.NewExitEngine is None:
        pytest.skip("NewExitEngine not available in this environment")

    monkeypatch.delenv("GENESIS_HTF_EXITS", raising=False)

    engine = engine_mod.BacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        start_date="2020-01-01",
        end_date="2020-01-02",
        htf_exit_config={"enable_partials": True},
        fast_window=False,
    )

    assert getattr(engine, "_use_new_exit_engine", False) is True


def test_backtest_engine_warns_on_unknown_htf_exit_env_flag(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Tripwire: Okända GENESIS_HTF_EXITS-värden ska ge varning (typo-skydd)."""

    import core.backtest.engine as engine_mod

    caplog.set_level("WARNING")
    monkeypatch.setenv("GENESIS_HTF_EXITS", "true")

    _ = engine_mod.BacktestEngine(
        symbol="tBTCUSD",
        timeframe="1h",
        start_date="2020-01-01",
        end_date="2020-01-02",
        htf_exit_config={"enable_partials": True},
        fast_window=False,
    )

    assert any("GENESIS_HTF_EXITS expected '0' or '1'" in rec.message for rec in caplog.records)


def test_runtime_source_must_not_import_core_config_validator() -> None:
    """Tripwire: runtime source får inte bero på core.config.validator."""

    repo_root = Path(__file__).resolve().parents[2]
    src_root = repo_root / "src"
    assert src_root.exists(), f"Expected source root to exist: {src_root}"

    py_files = list(src_root.rglob("*.py"))
    assert py_files, f"Expected at least one Python file under: {src_root}"

    validator_path = (src_root / "core" / "config" / "validator.py").resolve()

    violations: list[str] = []

    for py_file in py_files:
        resolved = py_file.resolve()
        if resolved == validator_path:
            continue

        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "core.config.validator" or alias.name.startswith(
                        "core.config.validator."
                    ):
                        violations.append(f"{py_file}:{node.lineno} imports {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "core.config.validator" or module.startswith("core.config.validator."):
                    violations.append(f"{py_file}:{node.lineno} imports from {module}")
                elif module == "core.config":
                    for alias in node.names:
                        if alias.name == "validator":
                            violations.append(
                                f"{py_file}:{node.lineno} imports validator from core.config"
                            )
                elif node.level > 0 and module == "config":
                    for alias in node.names:
                        if alias.name == "validator":
                            violations.append(
                                f"{py_file}:{node.lineno} imports validator from relative {'.' * node.level}{module}"
                            )

    assert not violations, "Runtime source must not import core.config.validator:\n" + "\n".join(
        violations
    )
