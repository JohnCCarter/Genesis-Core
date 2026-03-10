from __future__ import annotations

import ast
from pathlib import Path


def _iter_repo_python_asts(repo_root: Path, *, allow_list: set[str]):
    for rel_dir in ("src", "scripts", "tests"):
        base = repo_root / rel_dir
        if not base.exists():
            continue

        for path in base.rglob("*.py"):
            # Den här filen ska såklart inte flagga sig själv.
            if path.name == Path(__file__).name:
                continue

            rel_path = str(path.relative_to(repo_root)).replace("\\", "/")
            if rel_path in allow_list:
                continue

            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = path.read_text(encoding="utf-8", errors="ignore")

            try:
                tree = ast.parse(text, filename=rel_path)
            except SyntaxError:
                continue

            yield rel_path, tree


def test_no_imports_of_core_strategy_features_module() -> None:
    """Guardrail: features_asof är SSOT.

    Vi tillåter att legacy-modulen (`core.strategy.features`) finns kvar för referens,
    men ingen kod ska importera den (annars riskerar vi olika feature-set i olika flöden).
    """

    repo_root = Path(__file__).resolve().parents[2]

    # Explicit allow-list: this test imports the legacy module intentionally to enforce delegation.
    allow_list = {
        "tests/governance/test_dead_code_tripwires.py",
    }

    offenders: list[str] = []
    for rel_path, tree in _iter_repo_python_asts(repo_root, allow_list=allow_list):
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported = alias.name
                    if imported == "core.strategy.features" or imported.startswith(
                        "core.strategy.features."
                    ):
                        offenders.append(f"{rel_path}:{node.lineno} import {imported}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "core.strategy.features" or module.startswith(
                    "core.strategy.features."
                ):
                    offenders.append(f"{rel_path}:{node.lineno} from {module}")

    assert offenders == [], "Legacy-import hittad:\n" + "\n".join(offenders)


def test_no_imports_of_deprecated_features_asof_extract_features_wrapper() -> None:
    """Guardrail: undvik deprecated wrapper i intern kod.

    `core.strategy.features_asof.extract_features` är kvar för bakåtkompatibilitet,
    men all intern kod ska använda `extract_features_live` eller `extract_features_backtest`.
    """

    repo_root = Path(__file__).resolve().parents[2]

    # Explicit allow-list:
    # - `core.strategy.features` är en deprecated modul som avsiktligt delegerar till wrappern.
    # - `tests/utils/test_features.py` täcker wrapperns bakåtkompat (och ska inte blockas av guardrailen).
    allow_list = {
        "src/core/strategy/features.py",
        "tests/utils/test_features.py",
    }

    offenders: list[str] = []
    for rel_path, tree in _iter_repo_python_asts(repo_root, allow_list=allow_list):
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue
            if node.module != "core.strategy.features_asof":
                continue
            if any(alias.name == "extract_features" for alias in node.names):
                offenders.append(rel_path)
                break

    assert (
        offenders == []
    ), "Deprecated-import hittad (features_asof.extract_features):\n" + "\n".join(offenders)
