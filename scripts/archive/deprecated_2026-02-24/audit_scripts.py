from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

TEXT_EXTENSIONS = {
    ".py",
    ".ps1",
    ".sh",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".env",
    ".csv",
    ".xml",
    ".html",
    ".js",
    ".ts",
}

SCRIPT_EXTENSIONS = {".py", ".ps1", ".sh"}

SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    "data",
    "results",
}


@dataclass(frozen=True)
class ScriptAuditRow:
    path: str
    ext: str
    line_count: int
    size_bytes: int
    last_modified_utc: str
    last_modified_source: str
    days_since_modified: int | None
    internal_ref_mentions: int
    internal_ref_files: int
    risk_flags: str
    candidate_score: int


def _run_git(repo_root: Path, args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout


def _tracked_files(repo_root: Path) -> list[Path]:
    rc, out = _run_git(repo_root, ["ls-files"])
    if rc != 0:
        return []
    rel_paths = [line.strip() for line in out.splitlines() if line.strip()]
    return [repo_root / rel for rel in rel_paths]


def _iter_script_files(base_dir: Path) -> list[Path]:
    scripts: list[Path] = []
    if not base_dir.exists():
        return scripts

    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        root_path = Path(root)
        for file_name in files:
            file_path = root_path / file_name
            if file_path.suffix.lower() in SCRIPT_EXTENSIONS:
                scripts.append(file_path)

    return scripts


def _collect_script_files(repo_root: Path, script_dirs: list[str]) -> list[Path]:
    collected: set[Path] = set()
    for script_dir in script_dirs:
        target = (repo_root / script_dir).resolve()
        for script_path in _iter_script_files(target):
            collected.add(script_path.resolve())
    return sorted(collected)


def _is_archive_path(rel_path: str) -> bool:
    return rel_path.startswith("scripts/archive/")


def _is_skipped_by_prefix(rel_path: str) -> bool:
    parts = rel_path.split("/")
    return any(part in SKIP_DIRS for part in parts)


def _is_text_file(path: Path) -> bool:
    suffix = path.suffix.lower()
    if suffix in TEXT_EXTENSIONS:
        return True
    return path.name in {"README", "README.md", "AGENTS.md", "CLAUDE.md"}


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _line_count(path: Path) -> int:
    text = _read_text(path)
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)


def _last_modified_from_git(repo_root: Path, rel_path: str) -> tuple[datetime | None, str]:
    rc, out = _run_git(repo_root, ["log", "-1", "--format=%ct", "--", rel_path])
    if rc != 0:
        return None, "none"

    value = out.strip()
    if not value:
        return None, "none"

    try:
        ts = int(value)
    except ValueError:
        return None, "none"

    return datetime.fromtimestamp(ts, tz=UTC), "git"


def _last_modified_fallback(path: Path) -> tuple[datetime, str]:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=UTC), "filesystem"


def _find_rg() -> str | None:
    return shutil.which("rg")


def _rg_reference_counts(
    repo_root: Path,
    script_rel: str,
    script_name: str,
) -> tuple[int, int]:
    pattern = rf"{re.escape(script_rel)}|{re.escape(script_name)}"
    globs = [
        "!scripts/archive/**",
        "!data/**",
        "!results/**",
        "!.venv/**",
        "!node_modules/**",
        "!dist/**",
        "!build/**",
        "!**/__pycache__/**",
        "!.git/**",
        f"!{script_rel}",
    ]

    cmd: list[str] = [
        "rg",
        "--no-heading",
        "--line-number",
        "--with-filename",
        "--only-matching",
        "--color",
        "never",
    ]
    for glob in globs:
        cmd.extend(["--glob", glob])
    cmd.extend([pattern, "."])

    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )

    if proc.returncode not in {0, 1}:
        return 0, 0
    if proc.returncode == 1 or not proc.stdout.strip():
        return 0, 0

    files: set[str] = set()
    mentions = 0
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        mentions += 1
        parts = line.split(":", 2)
        if parts:
            rel = parts[0].replace("\\", "/")
            if rel and rel != script_rel:
                files.add(rel)

    return mentions, len(files)


def _python_reference_counts(
    repo_root: Path,
    script_rel: str,
    script_name: str,
    searchable_files: list[Path],
) -> tuple[int, int]:
    pattern = re.compile(rf"{re.escape(script_rel)}|{re.escape(script_name)}")
    mentions = 0
    files = 0

    for path in searchable_files:
        rel = path.relative_to(repo_root).as_posix()
        if rel == script_rel or _is_archive_path(rel):
            continue

        content = _read_text(path)
        if not content:
            continue

        hits = sum(1 for _ in pattern.finditer(content))
        if hits > 0:
            mentions += hits
            files += 1

    return mentions, files


def _searchable_files(repo_root: Path) -> list[Path]:
    tracked = _tracked_files(repo_root)
    if tracked:
        candidates = tracked
    else:
        candidates = [path for path in repo_root.rglob("*") if path.is_file()]

    out: list[Path] = []
    for path in candidates:
        try:
            rel = path.relative_to(repo_root).as_posix()
        except ValueError:
            continue

        if _is_skipped_by_prefix(rel):
            continue
        if _is_archive_path(rel):
            continue
        if not _is_text_file(path):
            continue
        out.append(path)

    return out


def _risk_flags(
    *,
    rel_path: str,
    line_count: int,
    size_bytes: int,
    ref_mentions: int,
    duplicate_name: bool,
    days_since_modified: int | None,
) -> list[str]:
    flags: list[str] = []

    if ref_mentions == 0:
        flags.append("NO_REFS")
    if line_count == 0 or size_bytes == 0:
        flags.append("EMPTY_FILE")
    if duplicate_name:
        flags.append("DUPLICATE_BASENAME")
    if re.search(r"(?:^|[_\-.])v\d+(?:$|[_\-.])", Path(rel_path).stem, flags=re.IGNORECASE):
        flags.append("VERSION_SUFFIX")
    if _is_archive_path(rel_path):
        flags.append("IN_ARCHIVE")
    if size_bytes > 0 and size_bytes < 1024:
        flags.append("VERY_SMALL")
    if days_since_modified is not None and days_since_modified > 365:
        flags.append("STALE_AGE")

    return flags


def _candidate_score(
    *,
    rel_path: str,
    ref_mentions: int,
    line_count: int,
    size_bytes: int,
    duplicate_name: bool,
    version_suffix: bool,
    days_since_modified: int | None,
) -> int:
    score = 0

    if ref_mentions == 0:
        score += 5
    if line_count == 0 or size_bytes == 0:
        score += 4
    if duplicate_name:
        score += 2
    if version_suffix:
        score += 1
    if size_bytes > 0 and size_bytes < 2048:
        score += 1

    if days_since_modified is not None:
        if days_since_modified > 365:
            score += 2
        elif days_since_modified > 180:
            score += 1

    if _is_archive_path(rel_path):
        score -= 4

    return score


def _build_rows(repo_root: Path, script_paths: list[Path]) -> list[ScriptAuditRow]:
    now = datetime.now(tz=UTC)
    basename_counts = Counter(path.name for path in script_paths)
    rg_path = _find_rg()
    searchable = _searchable_files(repo_root) if rg_path is None else []

    rows: list[ScriptAuditRow] = []
    for script_path in script_paths:
        rel = script_path.relative_to(repo_root).as_posix()
        ext = script_path.suffix.lower()
        size_bytes = script_path.stat().st_size
        line_count = _line_count(script_path)

        last_modified, source = _last_modified_from_git(repo_root, rel)
        if last_modified is None:
            last_modified, source = _last_modified_fallback(script_path)

        days_since = max((now - last_modified).days, 0)

        if rg_path is not None:
            mentions, ref_files = _rg_reference_counts(repo_root, rel, script_path.name)
        else:
            mentions, ref_files = _python_reference_counts(
                repo_root,
                rel,
                script_path.name,
                searchable,
            )

        duplicate_name = basename_counts[script_path.name] > 1
        version_suffix = bool(
            re.search(r"(?:^|[_\-.])v\d+(?:$|[_\-.])", script_path.stem, flags=re.IGNORECASE)
        )
        flags = _risk_flags(
            rel_path=rel,
            line_count=line_count,
            size_bytes=size_bytes,
            ref_mentions=mentions,
            duplicate_name=duplicate_name,
            days_since_modified=days_since,
        )

        score = _candidate_score(
            rel_path=rel,
            ref_mentions=mentions,
            line_count=line_count,
            size_bytes=size_bytes,
            duplicate_name=duplicate_name,
            version_suffix=version_suffix,
            days_since_modified=days_since,
        )

        rows.append(
            ScriptAuditRow(
                path=rel,
                ext=ext,
                line_count=line_count,
                size_bytes=size_bytes,
                last_modified_utc=last_modified.isoformat(),
                last_modified_source=source,
                days_since_modified=days_since,
                internal_ref_mentions=mentions,
                internal_ref_files=ref_files,
                risk_flags=",".join(flags) if flags else "-",
                candidate_score=score,
            )
        )

    rows.sort(
        key=lambda row: (
            -row.candidate_score,
            row.internal_ref_mentions,
            row.size_bytes,
            -(row.days_since_modified or 0),
            row.path,
        )
    )
    return rows


def _write_csv(rows: list[ScriptAuditRow], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "path",
                "ext",
                "line_count",
                "size_bytes",
                "last_modified_utc",
                "last_modified_source",
                "days_since_modified",
                "internal_ref_mentions",
                "internal_ref_files",
                "risk_flags",
                "candidate_score",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row.path,
                    row.ext,
                    row.line_count,
                    row.size_bytes,
                    row.last_modified_utc,
                    row.last_modified_source,
                    row.days_since_modified,
                    row.internal_ref_mentions,
                    row.internal_ref_files,
                    row.risk_flags,
                    row.candidate_score,
                ]
            )


def _write_markdown(
    rows: list[ScriptAuditRow], output_path: Path, root: Path, dirs: list[str]
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Scripts Audit Report",
        "",
        f"- Generated at: `{datetime.now(tz=UTC).isoformat()}`",
        f"- Root: `{root}`",
        f"- Script directories: `{', '.join(dirs)}`",
        "- Reference search: `ripgrep` when available, Python fallback otherwise",
        "- Dead zone excluded from reference counting: `scripts/archive/**`",
        "",
        "| path | ext | lines | bytes | last modified (UTC) | refs | risk flags | score |",
        "| --- | --- | ---: | ---: | --- | ---: | --- | ---: |",
    ]

    for row in rows:
        lines.append(
            f"| `{row.path}` | `{row.ext}` | {row.line_count} | {row.size_bytes} | "
            f"`{row.last_modified_utc}` | {row.internal_ref_mentions} | "
            f"`{row.risk_flags}` | {row.candidate_score} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Högre score = högre sannolikhet att filen är städkandidat.",
            "- Rapporten är beslutsstöd, inte automatisk radering.",
            "- Inga hårda borttagningar ska göras utan separat deprecate-flytt med wrapper.",
            "",
        ]
    )

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit all scripts and rank likely cleanup candidates.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root path (default: current directory).",
    )
    parser.add_argument(
        "--scripts-dir",
        action="append",
        default=[],
        help="Script directory relative to root. Repeatable. Default: scripts",
    )
    parser.add_argument(
        "--out",
        default="reports/scripts_audit.csv",
        help="CSV output path relative to root.",
    )
    parser.add_argument(
        "--out-md",
        default="reports/scripts_audit.md",
        help="Markdown output path relative to root.",
    )

    args = parser.parse_args(argv)
    repo_root = Path(args.root).resolve()
    script_dirs = args.scripts_dir or ["scripts"]
    script_paths = _collect_script_files(repo_root, script_dirs)

    rows = _build_rows(repo_root, script_paths)

    output_csv = (repo_root / args.out).resolve()
    output_md = (repo_root / args.out_md).resolve()
    _write_csv(rows, output_csv)
    _write_markdown(rows, output_md, repo_root, script_dirs)

    print(f"[OK] Audited {len(rows)} script files")
    print(f"[OK] CSV report: {output_csv}")
    print(f"[OK] Markdown report: {output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
