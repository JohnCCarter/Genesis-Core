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


def _load_audit_entries(path: Path) -> tuple[list[dict[str, object]], list[str]]:
    """Load JSONL audit entries.

    We treat blank lines as separators.
    We also allow comment lines (starting with '#' or '//') so trailing notes
    don't become a CI footgun.
    """

    if not path.exists():
        return [], []

    entries: list[dict[str, object]] = []
    errors: list[str] = []

    for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        ln = raw.strip()
        if not ln:
            continue
        if ln.startswith("#") or ln.startswith("//"):
            continue
        try:
            obj = json.loads(ln)
        except json.JSONDecodeError as e:
            errors.append(f"invalid JSON in audit file at line {i}: {e}")
            continue
        if not isinstance(obj, dict):
            errors.append(f"audit entry at line {i} must be a JSON object")
            continue
        entries.append(obj)

    return entries, errors


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
    base_sha = _git("rev-parse", base_ref)
    entries, parse_errors = _load_audit_entries(_repo_root() / audit_path)
    if parse_errors:
        errors.extend(parse_errors)
        return errors
    if not entries:
        errors.append("audit file is empty but stable manifest changed")
        return errors

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

    def _normalize_commit_sha(sha: str) -> str | None:
        """Return full SHA if sha exists, else None."""

        try:
            return _git("rev-parse", sha)
        except subprocess.CalledProcessError:
            return None

    def _find_entry(*, predicate) -> dict[str, object] | None:
        for e in reversed(entries):
            # Prefer the most recent matching entry (files are append-only).
            if predicate(e):
                return e
        return None

    # If stable.json and the audit entry are introduced together in a *single* commit (common when a PR
    # is created as a squash-import), we cannot require the audit entry to reference the stable-changing
    # commit itself without becoming self-referential. In that case, require a break-glass override and
    # anchor commit_sha to base_ref instead.
    if len(stable_commits) == 1 and stable_commits[0] == head_sha:

        def _single_commit_ok(e: dict[str, object]) -> bool:
            commit_sha = e.get("commit_sha")
            if not isinstance(commit_sha, str) or not commit_sha:
                return False
            commit_sha_full = _normalize_commit_sha(commit_sha)
            if commit_sha_full != base_sha:
                return False
            return e.get("action") == "break_glass_override"

        entry = _find_entry(predicate=_single_commit_ok)
        if entry is None:
            errors.append(
                "single-commit stable-manifest change requires an audit entry with "
                f"action='break_glass_override' and commit_sha referencing base_ref ({base_sha})"
            )
            return errors

        approved_by = entry.get("approved_by")
        if (
            not isinstance(approved_by, list)
            or not approved_by
            or not all(isinstance(x, str) and x.strip() for x in approved_by)
        ):
            errors.append(
                "single-commit stable-manifest change requires non-empty approved_by list "
                "(explicit break-glass approval)"
            )
        return errors

    expected_sha = stable_commits[0]

    def _expected_sha_ok(e: dict[str, object]) -> bool:
        commit_sha = e.get("commit_sha")
        if not isinstance(commit_sha, str) or not commit_sha:
            return False
        commit_sha_full = _normalize_commit_sha(commit_sha)
        if commit_sha_full is None:
            return False
        if commit_sha_full != expected_sha:
            return False
        action = e.get("action")
        return action in {"stable_promotion", "break_glass_override"}

    entry = _find_entry(predicate=_expected_sha_ok)
    if entry is None:
        errors.append(
            "audit entry commit_sha must reference the latest stable-manifest change commit "
            f"({expected_sha})"
        )
        return errors

    commit_sha = entry.get("commit_sha")
    assert isinstance(commit_sha, str)
    commit_sha_full = _normalize_commit_sha(commit_sha)
    if commit_sha_full is None:
        errors.append(f"audit entry commit_sha does not exist as a commit: {commit_sha!r}")
        return errors

    if commit_sha_full == head_sha:
        errors.append(
            "audit entry commit_sha must NOT equal HEAD (self-referential). "
            "Set commit_sha to the earlier commit that modified registry/manifests/stable.json."
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
