"""Validate the skills/compacts registry.

This is a lightweight CI gate for Alternative A (repo SSOT).

Usage:
  python scripts/validate_registry.py
    python scripts/validate_registry.py --ci-diff-base origin/master

CI rule (optional): if stable manifest changed vs base, require an audit entry in
`registry/audit/break_glass.jsonl` that references the commit which changed the stable manifest.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _ensure_import_path() -> None:
    """Ensure repo modules are importable when running this script directly.

    CI typically installs the package (pip -e .), but local usage may not.
    """

    root = _repo_root()
    src = root / "src"

    for p in (root, src):
        sp = str(p)
        if sp not in sys.path:
            sys.path.insert(0, sp)


_ensure_import_path()

from core.governance.registry import validate_registry  # noqa: E402


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


def _validate_audit_for_stable_change(*, base_ref: str) -> list[str]:
    """Enforce break-glass audit when stable manifest changes.

    NOTE: We intentionally do NOT require audit.commit_sha == HEAD.
    Doing so is self-referential (the commit hash depends on the file contents).
    Instead, we require audit.commit_sha to point to the latest commit in the PR range
    that modified `registry/manifests/stable.json`, and require it to be different from HEAD.
    """

    errors: list[str] = []

    # Prefer triple-dot (merge-base) diff when possible. If the branch and base_ref have
    # no common history (or merge-base cannot be computed), fall back to two-dot diff.
    try:
        diff_range = f"{base_ref}...HEAD"
        changed_out = _git("diff", "--name-only", diff_range)
    except subprocess.CalledProcessError:
        diff_range = f"{base_ref}..HEAD"
        changed_out = _git("diff", "--name-only", diff_range)

    changed = {p.strip() for p in changed_out.splitlines() if p.strip()}

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

    commit_sha = entry.get("commit_sha")
    if not isinstance(commit_sha, str) or not commit_sha:
        errors.append("audit entry must include commit_sha")
        return errors

    # Allow short SHA in audit entry by normalizing to full SHA.
    try:
        commit_sha_full = _git("rev-parse", commit_sha)
    except subprocess.CalledProcessError:
        errors.append(f"audit entry commit_sha does not exist as a commit: {commit_sha!r}")
        return errors

    if commit_sha_full == head_sha:
        errors.append(
            "audit entry commit_sha must NOT equal HEAD (self-referential). "
            "Set commit_sha to the earlier commit that modified registry/manifests/stable.json."
        )

    # Determine the latest commit in the PR range that modified the stable manifest.
    # Use two-dot (base..HEAD) so we only consider commits introduced by this PR/branch.
    stable_commits = [
        ln.strip()
        for ln in _git("rev-list", f"{base_ref}..HEAD", "--", stable_manifest).splitlines()
        if ln.strip()
    ]
    if not stable_commits:
        errors.append(
            "stable manifest appears changed, but no commits were found in the range that modify it; "
            "is base_ref correct?"
        )
        return errors

    expected_sha = stable_commits[0]
    # rev-list returns newest-first, so the first entry is the latest change.
    if commit_sha_full != expected_sha:
        errors.append(
            f"audit entry commit_sha must reference the latest stable-manifest change commit ({expected_sha}); "
            f"got {commit_sha!r}"
        )

    # Sanity: referenced commit must exist.
    try:
        _git("cat-file", "-e", f"{commit_sha_full}^{{commit}}")
    except subprocess.CalledProcessError:
        errors.append(f"audit entry commit_sha does not exist as a commit: {commit_sha!r}")

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
            errors.extend(_validate_audit_for_stable_change(base_ref=args.ci_diff_base))
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
