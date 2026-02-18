from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

SUPPORTED_EXTENSIONS = {".py", ".ps1", ".sh"}


@dataclass(frozen=True)
class MovePlan:
    source_abs: Path
    source_rel: str
    target_abs: Path
    target_rel: str
    target_rel_from_source_parent: str


def _run_git(repo_root: Path, args: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _normalize_archive_subdir(value: str) -> str:
    normalized = value.replace("\\", "/").strip("/")
    if not normalized:
        return "deprecated"
    return normalized


def _resolve_source(repo_root: Path, source_arg: str) -> Path:
    raw = Path(source_arg)
    if raw.is_absolute():
        source_abs = raw.resolve()
    else:
        source_abs = (repo_root / raw).resolve()
    return source_abs


def _ensure_within_repo(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError as exc:
        raise ValueError(f"Path is outside repository: {path}") from exc


def _build_plan(
    *,
    repo_root: Path,
    source_arg: str,
    archive_subdir: str,
    archive_month: str,
) -> MovePlan:
    source_abs = _resolve_source(repo_root, source_arg)
    if not source_abs.exists() or not source_abs.is_file():
        raise FileNotFoundError(f"Source script does not exist: {source_abs}")

    source_rel = _ensure_within_repo(source_abs, repo_root)
    if not source_rel.startswith("scripts/"):
        raise ValueError("Source must be inside scripts/.")

    if source_rel.startswith("scripts/archive/"):
        raise ValueError("Source is already under scripts/archive/.")

    extension = source_abs.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported extension: "
            f"{extension or '<none>'}. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    archive_rel = Path("scripts") / "archive" / archive_month / archive_subdir / source_abs.name
    target_abs = (repo_root / archive_rel).resolve()
    target_rel = archive_rel.as_posix()

    if target_abs.exists():
        raise FileExistsError(f"Target already exists: {target_abs}")

    relative_to_parent = Path(os.path.relpath(target_abs, start=source_abs.parent)).as_posix()
    return MovePlan(
        source_abs=source_abs,
        source_rel=source_rel,
        target_abs=target_abs,
        target_rel=target_rel,
        target_rel_from_source_parent=relative_to_parent,
    )


def _python_wrapper(target_rel_from_source_parent: str, source_rel: str, target_rel: str) -> str:
    return (
        "from __future__ import annotations\n"
        "\n"
        "import runpy\n"
        "import sys\n"
        "from pathlib import Path\n"
        "\n"
        "\n"
        "def main() -> int:\n"
        f'    target = (Path(__file__).resolve().parent / "{target_rel_from_source_parent}").resolve()\n'
        "    print(\n"
        f'        "[DEPRECATED] {source_rel} moved to {target_rel}.",\n'
        "        file=sys.stderr,\n"
        "    )\n"
        "    argv = sys.argv[:]\n"
        "    sys.argv = [str(target), *argv[1:]]\n"
        '    runpy.run_path(str(target), run_name="__main__")\n'
        "    return 0\n"
        "\n"
        "\n"
        'if __name__ == "__main__":\n'
        "    raise SystemExit(main())\n"
    )


def _powershell_wrapper(
    target_rel_from_source_parent: str, source_rel: str, target_rel: str
) -> str:
    rel_windows = target_rel_from_source_parent.replace("/", "\\")
    return (
        f'Write-Warning "[DEPRECATED] {source_rel} moved to {target_rel}."\n'
        f"$target = Join-Path $PSScriptRoot '{rel_windows}'\n"
        "$resolvedTarget = (Resolve-Path $target).Path\n"
        "& $resolvedTarget @args\n"
        "exit $LASTEXITCODE\n"
    )


def _bash_wrapper(target_rel_from_source_parent: str, source_rel: str, target_rel: str) -> str:
    return (
        "#!/usr/bin/env bash\n"
        f'echo "[DEPRECATED] {source_rel} moved to {target_rel}." >&2\n'
        'SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"\n'
        f'TARGET="${{SCRIPT_DIR}}/{target_rel_from_source_parent}"\n'
        'exec bash "${TARGET}" "$@"\n'
    )


def _wrapper_content(plan: MovePlan) -> str:
    extension = plan.source_abs.suffix.lower()
    if extension == ".py":
        return _python_wrapper(
            plan.target_rel_from_source_parent,
            plan.source_rel,
            plan.target_rel,
        )
    if extension == ".ps1":
        return _powershell_wrapper(
            plan.target_rel_from_source_parent,
            plan.source_rel,
            plan.target_rel,
        )
    if extension == ".sh":
        return _bash_wrapper(
            plan.target_rel_from_source_parent,
            plan.source_rel,
            plan.target_rel,
        )
    raise ValueError(f"Unsupported source extension: {extension}")


def _apply_move(repo_root: Path, plan: MovePlan, *, dry_run: bool) -> int:
    print(f"[INFO] Source: {plan.source_rel}")
    print(f"[INFO] Target: {plan.target_rel}")
    print(f"[INFO] Dry-run: {dry_run}")

    wrapper = _wrapper_content(plan)

    if dry_run:
        print(f"[DRY-RUN] Would run: git mv {plan.source_rel} {plan.target_rel}")
        print("[DRY-RUN] Would write wrapper to original path with deprecation warning.")
        return 0

    plan.target_abs.parent.mkdir(parents=True, exist_ok=True)
    source_mode = plan.source_abs.stat().st_mode

    rc, _, err = _run_git(repo_root, ["mv", plan.source_rel, plan.target_rel])
    if rc != 0:
        raise RuntimeError(f"git mv failed: {err.strip()}")

    plan.source_abs.write_text(wrapper, encoding="utf-8")
    if plan.source_abs.suffix.lower() == ".sh":
        plan.source_abs.chmod(source_mode)

    print("[OK] Moved with git mv and created wrapper at original path.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Safely deprecate-move a script to scripts/archive/YYYY-MM/... and create a wrapper.",
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Path to source script (absolute or repo-relative).",
    )
    parser.add_argument(
        "--archive-subdir",
        required=True,
        help="Subdirectory under scripts/archive/YYYY-MM/ where script will be moved.",
    )
    parser.add_argument(
        "--archive-month",
        default=datetime.now(tz=UTC).strftime("%Y-%m"),
        help="Archive month folder name (default: current YYYY-MM).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without changing files.",
    )

    args = parser.parse_args(argv)

    repo_root = _repo_root()
    archive_subdir = _normalize_archive_subdir(args.archive_subdir)

    try:
        plan = _build_plan(
            repo_root=repo_root,
            source_arg=args.source,
            archive_subdir=archive_subdir,
            archive_month=args.archive_month,
        )
        return _apply_move(repo_root, plan, dry_run=args.dry_run)
    except (FileNotFoundError, FileExistsError, ValueError, RuntimeError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
