"""Validate the skills/compacts registry.

This is a lightweight CI gate for Alternative A (repo SSOT).

Usage:
  python scripts/validate_registry.py
  python scripts/validate_registry.py --ci-diff-base origin/main

CI rule (optional): if stable manifest changed vs base, require an audit entry in
`registry/audit/break_glass.jsonl` for the current commit.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from core.governance.registry import validate_registry


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=_repo_root(),
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def _last_nonempty_line(path: Path) -> str | None:
    if not path.exists():
        return None
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return lines[-1] if lines else None


def _validate_audit_for_head(*, base_ref: str) -> list[str]:
    """Enforce break-glass audit when stable manifest changes."""

    errors: list[str] = []

    changed = {
        p.strip()
        for p in _git("diff", "--name-only", f"{base_ref}...HEAD").splitlines()
        if p.strip()
    }

    stable_manifest = "registry/manifests/stable.json"
    audit_path = "registry/audit/break_glass.jsonl"

    if stable_manifest not in changed:
        return errors

    if audit_path not in changed:
        errors.append(
            "stable manifest changed but no audit update found: "
            "expected registry/audit/break_glass.jsonl to change in same PR"
        )
        return errors

    head_sha = _git("rev-parse", "HEAD")
    last = _last_nonempty_line(_repo_root() / audit_path)
    if last is None:
        errors.append("audit file is empty but stable manifest changed")
        return errors

    try:
        entry = json.loads(last)
    except json.JSONDecodeError as e:
        errors.append(f"invalid JSON in last audit entry: {e}")
        return errors

    if not isinstance(entry, dict):
        errors.append("last audit entry must be a JSON object")
        return errors

    if entry.get("commit_sha") != head_sha:
        errors.append(
            f"last audit entry commit_sha must match HEAD ({head_sha}); got {entry.get('commit_sha')!r}"
        )

    action = entry.get("action")
    if action not in {"stable_promotion", "break_glass_override"}:
        errors.append(
            f"audit entry action must be stable_promotion|break_glass_override; got {action!r}"
        )

    items = entry.get("items")
    if not isinstance(items, list) or not items:
        errors.append("audit entry must include non-empty items list")

    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ci-diff-base",
        default=None,
        help="If set, enforce audit rule when stable manifest changes vs this git ref.",
    )
    args = parser.parse_args(argv)

    repo_root = _repo_root()
    result = validate_registry(repo_root)
    errors = list(result.errors)

    if args.ci_diff_base:
        try:
            errors.extend(_validate_audit_for_head(base_ref=args.ci_diff_base))
        except subprocess.CalledProcessError as e:
            errors.append(f"git diff/audit check failed: {e}")

    if errors:
        print("[REGISTRY] Validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("[REGISTRY] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
