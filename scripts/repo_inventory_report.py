from __future__ import annotations

from collections import Counter
from pathlib import Path

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
}

TOP_LEVEL_FOCUS = [
    "docs",
    "scripts",
    "results",
    "archive",
    "tmp",
    "src",
    "tests",
    "config",
]

ROOT_CATEGORIES = {
    "Kategori A (kärnrepo)": [
        ".gitattributes",
        ".gitignore",
        ".pre-commit-config.yaml",
        ".secrets.baseline",
        "AGENTS.md",
        "bandit.yaml",
        "CHANGELOG.md",
        "CLAUDE.md",
        "conftest.py",
        "dev.overrides.example.json",
        "pyproject.toml",
        "README.md",
    ],
    "Kategori B (miljö/operativt lokalt)": [
        ".env",
        ".env.example",
    ],
    "Kategori C (artefakter/scratch-kandidater)": [
        "burnin_summary.json",
        "candles.json",
        "DEV_MARKER.txt",
        "optimizer_phase7b.db",
        "optuna_search.db",
    ],
}

CANDIDATE_PATTERNS = {
    "scripts/archive/**": "scripts/archive/**/*",
    "scripts/debug_*.py": "scripts/debug_*.py",
    "scripts/diagnose_*.py": "scripts/diagnose_*.py",
    "scripts/test_*.py": "scripts/test_*.py",
    "docs/daily_summaries/*.md": "docs/daily_summaries/*.md",
    "results/backtests/*": "results/backtests/*",
    "results/hparam_search/**": "results/hparam_search/**/*",
}


def _iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        files.append(path)
    return files


def _count_top_level(files: list[Path], root: Path) -> dict[str, int]:
    counts = Counter()
    for file_path in files:
        rel = file_path.relative_to(root)
        top = rel.parts[0] if rel.parts else "."
        counts[top] += 1
    return {key: counts.get(key, 0) for key in sorted(counts.keys())}


def _focus_counts(top_counts: dict[str, int]) -> dict[str, int]:
    return {name: top_counts.get(name, 0) for name in TOP_LEVEL_FOCUS}


def _root_category_status(root: Path) -> dict[str, list[tuple[str, bool]]]:
    result: dict[str, list[tuple[str, bool]]] = {}
    for category, names in ROOT_CATEGORIES.items():
        result[category] = [(name, (root / name).exists()) for name in names]
    return result


def _candidate_counts(root: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for label, pattern in CANDIDATE_PATTERNS.items():
        matched = [
            p
            for p in root.glob(pattern)
            if p.is_file() and not any(part in EXCLUDE_DIRS for part in p.parts)
        ]
        counts[label] = len(matched)
    return counts


def _render_report(root: Path) -> str:
    files = _iter_files(root)
    top_counts = _count_top_level(files, root)
    focus_counts = _focus_counts(top_counts)
    root_status = _root_category_status(root)
    candidate_counts = _candidate_counts(root)

    lines: list[str] = []
    lines.append("# Repo Inventory Report (P1, 2026-02-14)")
    lines.append("")
    lines.append("## Syfte")
    lines.append("")
    lines.append(
        "Icke-destruktiv inventering av repo-strukturen inför fortsatt cleanup. "
        "Denna rapport ändrar eller tar inte bort filer."
    )
    lines.append("")
    lines.append("## Översikt")
    lines.append("")
    lines.append(f"- Totalt inventerade filer (exkl. tekniska cache-kataloger): **{len(files)}**")
    lines.append("")
    lines.append("## Top-level filantal")
    lines.append("")
    lines.append("| Katalog | Antal filer |")
    lines.append("| --- | ---: |")
    for name, count in sorted(top_counts.items()):
        lines.append(f"| `{name}` | {count} |")

    lines.append("")
    lines.append("## Fokuskataloger för cleanup")
    lines.append("")
    lines.append("| Katalog | Antal filer |")
    lines.append("| --- | ---: |")
    for name in TOP_LEVEL_FOCUS:
        lines.append(f"| `{name}` | {focus_counts.get(name, 0)} |")

    lines.append("")
    lines.append("## Root-artefakter (status)")
    lines.append("")
    for category, entries in root_status.items():
        lines.append(f"### {category}")
        lines.append("")
        lines.append("| Fil | Finns |")
        lines.append("| --- | --- |")
        for filename, exists in entries:
            marker = "Ja" if exists else "Nej"
            lines.append(f"| `{filename}` | {marker} |")
        lines.append("")

    lines.append("## Kandidatmönster (föreslagen uppföljning)")
    lines.append("")
    lines.append("| Mönster | Matchade filer |")
    lines.append("| --- | ---: |")
    for label, count in sorted(candidate_counts.items()):
        lines.append(f"| `{label}` | {count} |")

    lines.append("")
    lines.append("## Notering")
    lines.append("")
    lines.append(
        "Rensning/flytt/radering är fortsatt **föreslagen** och kräver separat "
        "kontrakt i senare etapp (P2/P3)."
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    output = repo_root / "docs" / "ops" / "REPO_INVENTORY_REPORT_2026-02-14.md"
    output.write_text(_render_report(repo_root), encoding="utf-8")
    print(f"[OK] Inventory report written to: {output}")


if __name__ == "__main__":
    main()
