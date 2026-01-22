from __future__ import annotations

import ast
from pathlib import Path


def test_no_src_core_imports_in_scripts() -> None:
    """Guardrail: scripts ska importera via core.* (inte src.core.*).

    Den korrekta src-layout-vägen är att ha `<repo>/src` på sys.path och sedan importera
    `core...`. Undantag: historiska script under `scripts/archive/**` (och varianter) som
    inte ska blockera aktiv utveckling.
    """

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    if not scripts_dir.exists():
        return

    excluded_second_level = {"archive", "_archive", "archive_local"}

    offenders: list[str] = []
    for path in scripts_dir.rglob("*.py"):
        rel_parts = path.relative_to(repo_root).parts
        if (
            len(rel_parts) >= 2
            and rel_parts[0] == "scripts"
            and rel_parts[1] in excluded_second_level
        ):
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="ignore")

        try:
            tree = ast.parse(text)
        except SyntaxError:
            # Denna guardrail ska inte blocka på enskilda scripts med parsing-problem.
            continue

        rel_path = str(path.relative_to(repo_root)).replace("\\", "/")

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module.startswith("src.core"):
                    offenders.append(f"{rel_path}:{node.lineno}: from {module} ...")
                    break

            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("src.core"):
                        offenders.append(f"{rel_path}:{node.lineno}: import {alias.name}")
                        break

    assert (
        offenders == []
    ), "Otillåtna imports i scripts (använd core.*, inte src.core.*):\n" + "\n".join(
        sorted(offenders)
    )
