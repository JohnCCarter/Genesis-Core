#!/usr/bin/env python3
"""Read-only preflight lookup over the research findings bank."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


BLOCKING_FINDING_OUTCOMES = {"negative", "direction_lock"}
REPO_ROOT_MARKER = "pyproject.toml"


def _find_repo_root(start: Path) -> Path:
    current = start if start.is_dir() else start.parent
    for candidate in [current, *current.parents]:
        if (candidate / REPO_ROOT_MARKER).is_file():
            return candidate
    raise RuntimeError("Could not locate repository root from script path")


ROOT = _find_repo_root(Path(__file__).resolve())


def _load_json_file(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"JSON file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid JSON in {path}: {exc}") from exc

    if not isinstance(payload, dict):
        raise RuntimeError(f"Expected JSON object in {path}")
    return payload


def load_findings_index(repo_root: Path) -> dict[str, Any]:
    index_path = repo_root / "artifacts" / "research_ledger" / "indexes" / "findings_index.json"
    payload = _load_json_file(index_path)
    items = payload.get("items")
    if not isinstance(items, list):
        raise RuntimeError(f"findings_index.json must contain an 'items' list: {index_path}")
    return payload


def load_finding_bundle(repo_root: Path, item: dict[str, Any]) -> dict[str, Any]:
    bundle_path_value = item.get("bundle_path")
    if not isinstance(bundle_path_value, str) or not bundle_path_value:
        finding_id = item.get("finding_id", "<unknown>")
        raise RuntimeError(f"Finding {finding_id} is missing bundle_path")

    bundle_path = repo_root / bundle_path_value
    bundle = _load_json_file(bundle_path)

    for key in ("finding_id", "artifact_id", "finding_outcome"):
        if bundle.get(key) != item.get(key):
            raise RuntimeError(
                f"Bundle mismatch for {bundle_path}: expected {key}={item.get(key)!r}, "
                f"got {bundle.get(key)!r}"
            )
    return bundle


def _normalized(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def _matches_exact_field(item: dict[str, Any], key: str, expected: str | None) -> bool:
    if expected is None:
        return True
    return _normalized(item.get(key)) == _normalized(expected)


def _contains_value(values: list[str], needle: str | None) -> bool:
    if needle is None:
        return True
    lowered = _normalized(needle)
    return any(lowered in _normalized(value) for value in values)


def _collect_text_haystack(item: dict[str, Any], bundle: dict[str, Any]) -> list[str]:
    haystack: list[str] = []

    for key in (
        "finding_id",
        "artifact_id",
        "subject",
        "domain",
        "symbol",
        "timeframe",
        "seam_class",
        "summary",
        "mechanism",
        "next_admissible_step",
    ):
        for source in (item, bundle):
            value = source.get(key)
            if isinstance(value, str) and value:
                haystack.append(value)

    for key in ("candidate_refs", "key_timestamps", "do_not_repeat"):
        for source in (item, bundle):
            values = source.get(key)
            if isinstance(values, list):
                haystack.extend(str(value) for value in values)

    evidence_refs = bundle.get("evidence_refs")
    if isinstance(evidence_refs, list):
        for ref in evidence_refs:
            if isinstance(ref, dict):
                for subkey in ("path", "role"):
                    value = ref.get(subkey)
                    if isinstance(value, str) and value:
                        haystack.append(value)

    return haystack


def enrich_finding(item: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    return {
        "finding_id": item["finding_id"],
        "artifact_id": item["artifact_id"],
        "finding_outcome": item["finding_outcome"],
        "subject": item.get("subject"),
        "domain": item.get("domain"),
        "symbol": item.get("symbol"),
        "timeframe": item.get("timeframe"),
        "seam_class": item.get("seam_class"),
        "summary": item.get("summary") or bundle.get("summary"),
        "bundle_path": item.get("bundle_path"),
        "artifact_record_path": item.get("artifact_record_path"),
        "candidate_refs": bundle.get("candidate_refs") or item.get("candidate_refs") or [],
        "key_timestamps": bundle.get("key_timestamps") or item.get("key_timestamps") or [],
        "do_not_repeat": bundle.get("do_not_repeat") or item.get("do_not_repeat") or [],
        "mechanism": bundle.get("mechanism"),
        "next_admissible_step": bundle.get("next_admissible_step"),
        "evidence_refs": bundle.get("evidence_refs") or [],
        "runtime_authority": bundle.get("runtime_authority"),
        "blocking_match": item.get("finding_outcome") in BLOCKING_FINDING_OUTCOMES,
    }


def lookup_findings(
    repo_root: Path,
    *,
    domain: str | None = None,
    subject: str | None = None,
    symbol: str | None = None,
    timeframe: str | None = None,
    seam_class: str | None = None,
    finding_outcome: str | None = None,
    candidate_ref_contains: str | None = None,
    timestamp_contains: str | None = None,
    text_contains: str | None = None,
) -> list[dict[str, Any]]:
    index_payload = load_findings_index(repo_root)
    matches: list[dict[str, Any]] = []

    for raw_item in index_payload["items"]:
        if not isinstance(raw_item, dict):
            raise RuntimeError("Each findings index item must be a JSON object")

        item = dict(raw_item)
        if not all(
            _matches_exact_field(item, key, expected)
            for key, expected in (
                ("domain", domain),
                ("subject", subject),
                ("symbol", symbol),
                ("timeframe", timeframe),
                ("seam_class", seam_class),
                ("finding_outcome", finding_outcome),
            )
        ):
            continue

        bundle = load_finding_bundle(repo_root, item)

        candidate_refs = [
            str(value) for value in bundle.get("candidate_refs") or item.get("candidate_refs") or []
        ]
        key_timestamps = [
            str(value) for value in bundle.get("key_timestamps") or item.get("key_timestamps") or []
        ]

        if not _contains_value(candidate_refs, candidate_ref_contains):
            continue
        if not _contains_value(key_timestamps, timestamp_contains):
            continue
        if not _contains_value(_collect_text_haystack(item, bundle), text_contains):
            continue

        matches.append(enrich_finding(item, bundle))

    return matches


def find_blocking_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        match
        for match in matches
        if _normalized(match.get("finding_outcome")) in BLOCKING_FINDING_OUTCOMES
    ]


def _group_by_outcome(matches: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for match in matches:
        outcome = str(match.get("finding_outcome", "unknown"))
        grouped.setdefault(outcome, []).append(match)
    return grouped


def _format_filters(args: argparse.Namespace) -> dict[str, str]:
    filters: dict[str, str] = {}
    for name in (
        "domain",
        "subject",
        "symbol",
        "timeframe",
        "seam_class",
        "finding_outcome",
        "candidate_ref_contains",
        "timestamp_contains",
        "text_contains",
    ):
        value = getattr(args, name)
        if value is not None:
            filters[name] = value
    return filters


def format_lookup_report(
    matches: list[dict[str, Any]],
    *,
    repo_root: Path,
    filters: dict[str, str],
) -> str:
    lines = [
        "RESEARCH FINDINGS PREFLIGHT LOOKUP",
        f"repo_root: {repo_root}",
        f"filters: {filters or {'none': 'all'}}",
        f"matches: {len(matches)}",
        f"blocking_matches: {len(find_blocking_matches(matches))}",
    ]

    if not matches:
        lines.append("status: no findings matched the provided filters")
        return "\n".join(lines)

    for outcome, grouped_matches in sorted(_group_by_outcome(matches).items()):
        lines.append("")
        lines.append(f"[{outcome}] {len(grouped_matches)} match(es)")
        for match in grouped_matches:
            lines.append(
                "- "
                f"{match['finding_id']} | {match.get('subject')} | {match.get('symbol')} "
                f"{match.get('timeframe')} | seam={match.get('seam_class')}"
            )
            lines.append(f"  summary: {match.get('summary')}")
            mechanism = match.get("mechanism")
            if mechanism:
                lines.append(f"  mechanism: {mechanism}")
            next_step = match.get("next_admissible_step")
            if next_step:
                lines.append(f"  next_admissible_step: {next_step}")

            do_not_repeat = match.get("do_not_repeat") or []
            if do_not_repeat:
                lines.append("  do_not_repeat:")
                for entry in do_not_repeat:
                    lines.append(f"    - {entry}")

            candidate_refs = match.get("candidate_refs") or []
            if candidate_refs:
                lines.append("  candidate_refs:")
                for ref in candidate_refs:
                    lines.append(f"    - {ref}")

    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Look up existing research findings before authoring a new slice."
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--domain", help="Exact domain filter")
    parser.add_argument("--subject", help="Exact subject filter")
    parser.add_argument("--symbol", help="Exact symbol filter")
    parser.add_argument("--timeframe", help="Exact timeframe filter")
    parser.add_argument("--seam-class", dest="seam_class", help="Exact seam class filter")
    parser.add_argument(
        "--finding-outcome",
        choices=("positive", "negative", "direction_lock"),
        help="Exact finding outcome filter",
    )
    parser.add_argument(
        "--candidate-ref-contains",
        help="Substring filter across candidate_refs",
    )
    parser.add_argument(
        "--timestamp-contains",
        help="Substring filter across key_timestamps",
    )
    parser.add_argument(
        "--text-contains",
        help="Substring filter across finding summary, mechanism, do_not_repeat, and refs",
    )
    parser.add_argument(
        "--fail-on-blocking-match",
        action="store_true",
        help=(
            "Exit non-zero only when the filtered result set contains a structured finding_outcome "
            "of negative or direction_lock. Research convenience only; not governance authority."
        ),
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    filters = _format_filters(args)

    try:
        matches = lookup_findings(
            repo_root,
            domain=args.domain,
            subject=args.subject,
            symbol=args.symbol,
            timeframe=args.timeframe,
            seam_class=args.seam_class,
            finding_outcome=args.finding_outcome,
            candidate_ref_contains=args.candidate_ref_contains,
            timestamp_contains=args.timestamp_contains,
            text_contains=args.text_contains,
        )
    except RuntimeError as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1

    blocking_matches = find_blocking_matches(matches)
    payload = {
        "repo_root": str(repo_root),
        "filters": filters,
        "count": len(matches),
        "blocking_count": len(blocking_matches),
        "items": matches,
    }

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(format_lookup_report(matches, repo_root=repo_root, filters=filters))

    if args.fail_on_blocking_match and blocking_matches:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
