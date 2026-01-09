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

    offenders: list[str] = []
    for rel_dir in ("src", "scripts", "tests"):
        base = repo_root / rel_dir
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            # Den här filen ska såklart inte flagga sig själv.
            if path.name == Path(__file__).name:
                continue

            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = path.read_text(encoding="utf-8", errors="ignore")

            if any(p.search(text) for p in patterns):
                offenders.append(str(path.relative_to(repo_root)))

    assert offenders == [], "Legacy-import hittad: \n" + "\n".join(offenders)
