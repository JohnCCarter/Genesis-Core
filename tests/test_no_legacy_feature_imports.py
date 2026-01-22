from __future__ import annotations

import re
from pathlib import Path


def test_no_imports_of_core_strategy_features_module() -> None:
    """Guardrail: features_asof är SSOT.

    Vi tillåter att legacy-modulen (`core.strategy.features`) finns kvar för referens,
    men ingen kod ska importera den (annars riskerar vi olika feature-set i olika flöden).
    """

    repo_root = Path(__file__).resolve().parents[1]
    patterns = [
        re.compile(r"^\s*from\s+core\.strategy\.features\s+import\s+", re.MULTILINE),
        re.compile(r"^\s*import\s+core\.strategy\.features\b", re.MULTILINE),
    ]

    # Explicit allow-list: this test imports the legacy module intentionally to enforce delegation.
    allow_list = {
        "tests/test_dead_code_tripwires.py",
    }

    offenders: list[str] = []
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

            if any(p.search(text) for p in patterns):
                offenders.append(rel_path)

    assert offenders == [], "Legacy-import hittad: \n" + "\n".join(offenders)
