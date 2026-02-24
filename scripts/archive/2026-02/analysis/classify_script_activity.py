from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections.abc import Iterable
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
}

HISTORICAL_DOC_PREFIXES = (
    "docs/ops/",
    "docs/audits/",
    "docs/archive/",
    "docs/history/",
)


@dataclass(frozen=True)
class ScriptEvidence:
    path: str
    status: str
    score: int
    days_since_last_commit: int | None
    deprecated_marker: bool
    refs_runtime: int
    refs_workflows: int
    refs_tests: int
    refs_docs_active: int
    refs_docs_historical: int
    refs_scripts_active: int
    refs_scripts_archive: int
    refs_other: int
    notes: list[str]


def _run_git(repo_root: Path, args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        return ""
    return proc.stdout


def _tracked_files(repo_root: Path) -> list[Path]:
    out = _run_git(repo_root, ["ls-files"])
    rel_paths = [line.strip() for line in out.splitlines() if line.strip()]
    return [repo_root / rel for rel in rel_paths]


def _script_files(repo_root: Path, include_archive: bool) -> list[Path]:
    scripts = []
    for path in _tracked_files(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        if not rel.startswith("scripts/") or not rel.endswith(".py"):
            continue
        if not include_archive and rel.startswith("scripts/archive/"):
            continue
        scripts.append(path)
    return sorted(scripts)


def _reference_group(rel_path: str) -> str:
    if rel_path.startswith(".github/workflows/"):
        return "workflows"
    if rel_path.startswith(("src/", "mcp_server/", "config/")):
        return "runtime"
    if rel_path.startswith("tests/"):
        return "tests"
    if rel_path.startswith("docs/"):
        if rel_path.startswith(HISTORICAL_DOC_PREFIXES):
            return "docs_historical"
        return "docs_active"
    if rel_path.startswith("scripts/"):
        if rel_path.startswith("scripts/archive/"):
            return "scripts_archive"
        return "scripts_active"
    if rel_path in {"README.md", "AGENTS.md", "CLAUDE-LOCAL.md"}:
        return "docs_active"
    return "other"


def _is_text_candidate(path: Path) -> bool:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return True
    return path.name in {"README", "README.md", "AGENTS.md", "CLAUDE-LOCAL.md"}


def _load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _days_since_last_commit(repo_root: Path, script_rel: str, now_utc: datetime) -> int | None:
    out = _run_git(repo_root, ["log", "-1", "--format=%ct", "--", script_rel]).strip()
    if not out:
        return None
    try:
        ts = int(out)
    except ValueError:
        return None
    dt = datetime.fromtimestamp(ts, tz=UTC)
    return max((now_utc - dt).days, 0)


def _score_status(
    *,
    script_rel: str,
    groups: dict[str, set[str]],
    days_since_last_commit: int | None,
    deprecated_marker: bool,
) -> tuple[int, str, list[str]]:
    notes: list[str] = []
    score = 0

    refs_runtime = len(groups["runtime"])
    refs_workflows = len(groups["workflows"])
    refs_tests = len(groups["tests"])
    refs_docs_active = len(groups["docs_active"])
    refs_docs_historical = len(groups["docs_historical"])
    refs_scripts_active = len(groups["scripts_active"])
    refs_scripts_archive = len(groups["scripts_archive"])
    refs_other = len(groups["other"])

    if refs_runtime > 0:
        score += 8
        notes.append("runtime-referenser hittade")
    if refs_workflows > 0:
        score += 6
        notes.append("workflow-referenser hittade")
    if refs_tests > 0:
        score += 4
        notes.append("test-referenser hittade")
    if refs_scripts_active > 0:
        score += 3
        notes.append("refereras av aktiva scripts")
    if refs_docs_active > 0:
        score += 2
        notes.append("refereras i aktiva docs")
    if refs_other > 0:
        score += 1

    if script_rel.startswith("scripts/archive/"):
        score -= 3
        notes.append("ligger i scripts/archive")
    else:
        score += 1

    if deprecated_marker:
        score -= 4
        notes.append("deprecated-markör i filinnehåll")

    if days_since_last_commit is not None:
        if days_since_last_commit <= 90:
            score += 2
            notes.append("nyligen ändrad (<90 dagar)")
        elif days_since_last_commit <= 180:
            score += 1
        elif days_since_last_commit > 365:
            score -= 2
            notes.append("gammal ändringshistorik (>365 dagar)")

    strong_refs = (
        refs_runtime + refs_workflows + refs_tests + refs_docs_active + refs_scripts_active
    )
    total_refs = (
        refs_runtime
        + refs_workflows
        + refs_tests
        + refs_docs_active
        + refs_docs_historical
        + refs_scripts_active
        + refs_scripts_archive
        + refs_other
    )

    if strong_refs == 0 and refs_docs_historical > 0:
        score -= 2
        notes.append("refereras främst i historiska/governance-dokument")
    if total_refs == 0:
        score -= 3
        notes.append("inga externa referenser hittade")

    if score >= 8:
        status = "ACTIVE"
    elif score >= 3:
        status = "REVIEW"
    else:
        status = "STALE"

    return score, status, notes


def _collect_script_evidence(
    repo_root: Path,
    scripts: list[Path],
) -> list[ScriptEvidence]:
    scripts_by_rel = {script.relative_to(repo_root).as_posix(): script for script in scripts}
    rel_keys = list(scripts_by_rel.keys())

    reference_hits: dict[str, dict[str, set[str]]] = {rel: defaultdict(set) for rel in rel_keys}

    tracked_text_files = [
        path for path in _tracked_files(repo_root) if _is_text_candidate(path) and path.exists()
    ]

    for source_path in tracked_text_files:
        source_rel = source_path.relative_to(repo_root).as_posix()
        content = _load_text(source_path)
        if not content:
            continue

        for script_rel, script_path in scripts_by_rel.items():
            if source_path == script_path:
                continue

            basename = script_path.name
            if script_rel in content or basename in content:
                group = _reference_group(source_rel)
                reference_hits[script_rel][group].add(source_rel)

    now_utc = datetime.now(tz=UTC)
    evidences: list[ScriptEvidence] = []

    for script_rel in rel_keys:
        script_path = scripts_by_rel[script_rel]
        groups = reference_hits[script_rel]
        script_text = _load_text(script_path)
        deprecated_marker = bool(re.search(r"\bdeprecated\b", script_text, flags=re.IGNORECASE))

        days_since = _days_since_last_commit(repo_root, script_rel, now_utc)
        score, status, notes = _score_status(
            script_rel=script_rel,
            groups=groups,
            days_since_last_commit=days_since,
            deprecated_marker=deprecated_marker,
        )

        evidences.append(
            ScriptEvidence(
                path=script_rel,
                status=status,
                score=score,
                days_since_last_commit=days_since,
                deprecated_marker=deprecated_marker,
                refs_runtime=len(groups["runtime"]),
                refs_workflows=len(groups["workflows"]),
                refs_tests=len(groups["tests"]),
                refs_docs_active=len(groups["docs_active"]),
                refs_docs_historical=len(groups["docs_historical"]),
                refs_scripts_active=len(groups["scripts_active"]),
                refs_scripts_archive=len(groups["scripts_archive"]),
                refs_other=len(groups["other"]),
                notes=notes,
            )
        )

    evidences.sort(key=lambda item: (-item.score, item.path))
    return evidences


def _to_json_payload(evidences: Iterable[ScriptEvidence], include_archive: bool) -> dict:
    evidence_list = list(evidences)
    counts = Counter(item.status for item in evidence_list)
    return {
        "generated_at_utc": datetime.now(tz=UTC).isoformat(),
        "classifier_version": "c7-v1",
        "include_archive": include_archive,
        "thresholds": {
            "ACTIVE": "score >= 8",
            "REVIEW": "3 <= score < 8",
            "STALE": "score < 3",
        },
        "summary": {
            "total_scripts": len(evidence_list),
            "active": counts.get("ACTIVE", 0),
            "review": counts.get("REVIEW", 0),
            "stale": counts.get("STALE", 0),
        },
        "scripts": [
            {
                "path": item.path,
                "status": item.status,
                "score": item.score,
                "days_since_last_commit": item.days_since_last_commit,
                "deprecated_marker": item.deprecated_marker,
                "refs": {
                    "runtime": item.refs_runtime,
                    "workflows": item.refs_workflows,
                    "tests": item.refs_tests,
                    "docs_active": item.refs_docs_active,
                    "docs_historical": item.refs_docs_historical,
                    "scripts_active": item.refs_scripts_active,
                    "scripts_archive": item.refs_scripts_archive,
                    "other": item.refs_other,
                },
                "notes": item.notes,
            }
            for item in evidence_list
        ],
    }


def _to_markdown(payload: dict, limit: int | None = None) -> str:
    scripts = payload["scripts"]
    if limit is not None:
        scripts = scripts[:limit]

    lines = [
        "# Script Activity Evidence Report",
        "",
        f"- Generated at: `{payload['generated_at_utc']}`",
        f"- Classifier version: `{payload['classifier_version']}`",
        f"- include_archive: `{payload['include_archive']}`",
        "",
        "## Summary",
        "",
        f"- Total scripts: **{payload['summary']['total_scripts']}**",
        f"- ACTIVE: **{payload['summary']['active']}**",
        f"- REVIEW: **{payload['summary']['review']}**",
        f"- STALE: **{payload['summary']['stale']}**",
        "",
        "## Top scripts",
        "",
        "| Script | Status | Score | Last commit (days) | Runtime refs | Tests refs | Docs active refs | Docs historical refs |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for item in scripts:
        days = item["days_since_last_commit"]
        days_txt = str(days) if days is not None else "n/a"
        lines.append(
            "| `{path}` | `{status}` | {score} | {days} | {runtime} | {tests} | {docs_active} | {docs_hist} |".format(
                path=item["path"],
                status=item["status"],
                score=item["score"],
                days=days_txt,
                runtime=item["refs"]["runtime"],
                tests=item["refs"]["tests"],
                docs_active=item["refs"]["docs_active"],
                docs_hist=item["refs"]["docs_historical"],
            )
        )

    lines.append("")
    lines.append("## Note")
    lines.append("")
    lines.append(
        "Klassificeringen är evidensbaserad prioritering för cleanup-beslut, inte automatisk radering/flytt. "
        "Verifiera alltid med tranche-kontrakt + Opus review."
    )

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Evidence-driven classifier for script activity (ACTIVE/REVIEW/STALE)."
    )
    parser.add_argument(
        "--include-archive",
        action="store_true",
        help="Include scripts under scripts/archive/** in the classification set.",
    )
    parser.add_argument(
        "--output-json",
        default="reports/script_activity_latest.json",
        help="Output path for JSON report.",
    )
    parser.add_argument(
        "--output-md",
        default="reports/script_activity_latest.md",
        help="Output path for Markdown report.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Optional max rows in markdown table (0 = all).",
    )

    args = parser.parse_args()

    here = Path(__file__).resolve()
    repo_root = None
    for candidate in [here, *here.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            repo_root = candidate
            break
    if repo_root is None:
        raise RuntimeError("Could not locate repository root from script path")

    scripts = _script_files(repo_root, include_archive=args.include_archive)
    evidences = _collect_script_evidence(repo_root, scripts)

    payload = _to_json_payload(evidences, include_archive=args.include_archive)

    output_json = repo_root / args.output_json
    output_md = repo_root / args.output_md
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.parent.mkdir(parents=True, exist_ok=True)

    output_json.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    md_limit = args.limit if args.limit > 0 else None
    output_md.write_text(_to_markdown(payload, limit=md_limit), encoding="utf-8")

    summary = payload["summary"]
    print(
        "[OK] Classified {total} scripts: ACTIVE={active}, REVIEW={review}, STALE={stale}".format(
            total=summary["total_scripts"],
            active=summary["active"],
            review=summary["review"],
            stale=summary["stale"],
        )
    )
    print(f"[OK] JSON: {output_json}")
    print(f"[OK] Markdown: {output_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
