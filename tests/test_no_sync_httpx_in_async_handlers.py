from __future__ import annotations

import ast
from pathlib import Path

_SYNC_HTTPX_METHODS: frozenset[str] = frozenset(
    {
        "get",
        "post",
        "put",
        "delete",
        "head",
        "options",
        "patch",
        "request",
    }
)


def _find_sync_httpx_calls_in_async_functions(source: str) -> list[tuple[str, int]]:
    tree = ast.parse(source)
    hits: list[tuple[str, int]] = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.AsyncFunctionDef):
            continue
        for sub in ast.walk(node):
            if not isinstance(sub, ast.Call):
                continue
            func = sub.func
            if not isinstance(func, ast.Attribute):
                continue
            if func.attr not in _SYNC_HTTPX_METHODS:
                continue
            if not isinstance(func.value, ast.Name):
                continue
            if func.value.id != "httpx":
                continue
            hits.append((func.attr, getattr(sub, "lineno", -1)))

    return hits


def test_no_sync_httpx_calls_in_async_handlers() -> None:
    path = Path(__file__).resolve().parents[1] / "src" / "core" / "server.py"
    src = path.read_text(encoding="utf-8")

    hits = _find_sync_httpx_calls_in_async_functions(src)
    assert hits == [], f"Found sync httpx.* calls inside async functions: {hits}"
