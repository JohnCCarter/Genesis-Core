#!/usr/bin/env python3
"""Validate the #2 precompute-cache selector policy.

Usage:
    python scripts/validate/validate_precompute_cache_selector_policy.py
    python scripts/validate/validate_precompute_cache_selector_policy.py --ci-diff-base origin/master

When the tracked precompute-cache contract surface in
`src/core/backtest/engine.py` is touched, this script runs the focused pytest
selector bundle that anchors the current #2 cache-contract behavior. Otherwise
it exits successfully without invoking pytest.
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

TARGET_FILE = Path("src/core/backtest/engine.py")
TARGET_FUNCTIONS = {
    "_precompute_cache_key_material",
    "_build_precompute_cache_metadata",
    "_validate_metadata_bearing_precompute_cache",
    "_precompute_cache_key",
}
TARGET_ASSIGNMENTS = {"PRECOMPUTE_SCHEMA_VERSION"}
TARGET_CALL_LABEL = "load_data.prepare_precomputed_features"
TARGET_SELECTORS: tuple[str, ...] = (
    "tests/backtest/test_precompute_cache_key_versioning.py::test_precompute_cache_key_changes_when_schema_version_changes",
    "tests/backtest/test_backtest_engine.py::test_engine_precompute_cache_metadata_payload_loads_when_valid",
    "tests/backtest/test_backtest_engine.py::test_engine_precompute_cache_metadata_payload_recomputes_on_dense_length_mismatch",
    "tests/backtest/test_backtest_engine.py::test_engine_precompute_cache_metadata_payload_recomputes_on_material_mismatch",
    "tests/backtest/test_backtest_engine.py::test_engine_precompute_cache_metadata_payload_recomputes_on_swing_pair_misalignment",
)
_DIFF_HUNK_RE = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? \+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@"
)


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from script path")


def _git(*args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=_repo_root(),
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def _relative_git_path(path: Path) -> str:
    return path.as_posix()


def _diff_name_only(*, base_ref: str | None) -> set[str]:
    changed: set[str] = set()
    if base_ref:
        try:
            changed.update(
                p.strip()
                for p in _git("diff", "--name-only", f"{base_ref}...HEAD").splitlines()
                if p.strip()
            )
        except subprocess.CalledProcessError:
            changed.update(
                p.strip()
                for p in _git("diff", "--name-only", f"{base_ref}..HEAD").splitlines()
                if p.strip()
            )
    changed.update(p.strip() for p in _git("diff", "--name-only", "HEAD").splitlines() if p.strip())
    return changed


def _diff_batches(
    *, base_ref: str | None, rel_path: str
) -> list[tuple[str | None, str | None, str]]:
    batches: list[tuple[str | None, str | None, str]] = []

    if base_ref:
        try:
            diff_text = _git("diff", "--unified=0", f"{base_ref}...HEAD", "--", rel_path)
        except subprocess.CalledProcessError:
            diff_text = _git("diff", "--unified=0", f"{base_ref}..HEAD", "--", rel_path)
        if diff_text:
            batches.append((base_ref, "HEAD", diff_text))

    worktree_diff = _git("diff", "--unified=0", "HEAD", "--", rel_path)
    if worktree_diff:
        batches.append(("HEAD", None, worktree_diff))

    if not batches and base_ref is None:
        head_diff = _git("diff", "--unified=0", "HEAD", "--", rel_path)
        if head_diff:
            batches.append(("HEAD", None, head_diff))

    return batches


def _read_worktree_text(rel_path: str) -> str | None:
    path = _repo_root() / Path(rel_path)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def _read_revision_text(revision: str, rel_path: str) -> str | None:
    try:
        return _git("show", f"{revision}:{rel_path}")
    except subprocess.CalledProcessError:
        return None


def _parse_hunk_ranges(diff_text: str) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    old_ranges: list[tuple[int, int]] = []
    new_ranges: list[tuple[int, int]] = []

    for line in diff_text.splitlines():
        match = _DIFF_HUNK_RE.match(line)
        if match is None:
            continue

        old_start = int(match.group("old_start"))
        old_count = int(match.group("old_count") or "1")
        new_start = int(match.group("new_start"))
        new_count = int(match.group("new_count") or "1")

        if old_count > 0:
            old_ranges.append((old_start, old_start + old_count - 1))
        if new_count > 0:
            new_ranges.append((new_start, new_start + new_count - 1))

    return old_ranges, new_ranges


def _span_intersects(span: tuple[int, int], ranges: list[tuple[int, int]]) -> bool:
    start, end = span
    for range_start, range_end in ranges:
        if start <= range_end and range_start <= end:
            return True
    return False


def _collect_target_spans(source: str) -> dict[str, tuple[int, int]]:
    tree = ast.parse(source)
    spans: dict[str, tuple[int, int]] = {}

    class _Visitor(ast.NodeVisitor):
        def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in TARGET_ASSIGNMENTS:
                    spans[target.id] = (node.lineno, getattr(node, "end_lineno", node.lineno))
            self.generic_visit(node)

        def visit_AnnAssign(self, node: ast.AnnAssign) -> None:  # noqa: N802
            target = node.target
            if isinstance(target, ast.Name) and target.id in TARGET_ASSIGNMENTS:
                spans[target.id] = (node.lineno, getattr(node, "end_lineno", node.lineno))
            self.generic_visit(node)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
            if node.name in TARGET_FUNCTIONS:
                spans[node.name] = (node.lineno, getattr(node, "end_lineno", node.lineno))
            if node.name == "load_data":
                for child in ast.walk(node):
                    if not isinstance(child, ast.Call):
                        continue
                    func = child.func
                    func_name = None
                    if isinstance(func, ast.Name):
                        func_name = func.id
                    elif isinstance(func, ast.Attribute):
                        func_name = func.attr
                    if func_name == "prepare_precomputed_features":
                        spans[TARGET_CALL_LABEL] = (
                            child.lineno,
                            getattr(child, "end_lineno", child.lineno),
                        )
            self.generic_visit(node)

    _Visitor().visit(tree)
    return spans


def _touched_labels_for_source(
    *,
    source: str | None,
    ranges: list[tuple[int, int]],
    label: str,
) -> set[str]:
    if source is None or not ranges:
        return set()

    try:
        spans = _collect_target_spans(source)
    except SyntaxError as exc:  # pragma: no cover - exercised through validate_selector_policy
        raise RuntimeError(f"Could not parse {label}: {exc}") from exc

    return {name for name, span in spans.items() if _span_intersects(span, ranges)}


def _detect_touched_targets(*, base_ref: str | None) -> list[str]:
    rel_path = _relative_git_path(TARGET_FILE)
    touched: set[str] = set()

    for old_ref, new_ref, diff_text in _diff_batches(base_ref=base_ref, rel_path=rel_path):
        old_ranges, new_ranges = _parse_hunk_ranges(diff_text)
        if old_ranges:
            old_source = _read_revision_text(old_ref, rel_path) if old_ref is not None else None
            touched.update(
                _touched_labels_for_source(
                    source=old_source, ranges=old_ranges, label=f"{old_ref}:{rel_path}"
                )
            )
        if new_ranges:
            if new_ref is None:
                new_source = _read_worktree_text(rel_path)
                source_label = rel_path
            else:
                new_source = _read_revision_text(new_ref, rel_path)
                source_label = f"{new_ref}:{rel_path}"
            touched.update(
                _touched_labels_for_source(source=new_source, ranges=new_ranges, label=source_label)
            )

    return sorted(touched)


def _run_pytest_selectors(selectors: tuple[str, ...]) -> int:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", *selectors],
        cwd=_repo_root(),
        check=False,
    )
    return int(proc.returncode)


def validate_selector_policy(
    *,
    base_ref: str | None = None,
    run_pytest_fn: Callable[[tuple[str, ...]], int] | None = None,
) -> int:
    rel_path = _relative_git_path(TARGET_FILE)
    changed_files = _diff_name_only(base_ref=base_ref)

    if rel_path not in changed_files:
        print("[PRECOMPUTE_SELECTOR_POLICY] OK: tracked engine surface untouched")
        return 0

    touched_targets = _detect_touched_targets(base_ref=base_ref)
    if not touched_targets:
        print(
            "[PRECOMPUTE_SELECTOR_POLICY] OK: engine.py changed outside tracked "
            "precompute-cache contract surface"
        )
        return 0

    print(
        "[PRECOMPUTE_SELECTOR_POLICY] Triggered by tracked surface: " + ", ".join(touched_targets)
    )

    runner = run_pytest_fn or _run_pytest_selectors
    exit_code = int(runner(TARGET_SELECTORS))
    if exit_code == 0:
        print("[PRECOMPUTE_SELECTOR_POLICY] OK")
    else:
        print(f"[PRECOMPUTE_SELECTOR_POLICY] FAILED: pytest exit_code={exit_code}")
    return exit_code


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ci-diff-base",
        default=None,
        help="If set, compare the tracked surface against this git ref before dispatching selectors.",
    )
    args = parser.parse_args(argv)
    return validate_selector_policy(base_ref=args.ci_diff_base)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
