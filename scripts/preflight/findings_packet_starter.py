#!/usr/bin/env python3
"""Advisory packet starter built from matched research findings."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT_MARKER = "pyproject.toml"


def _find_repo_root(start: Path) -> Path:
    current = start if start.is_dir() else start.parent
    for candidate in [current, *current.parents]:
        if (candidate / REPO_ROOT_MARKER).is_file():
            return candidate
    raise RuntimeError("Could not locate repository root from script path")


ROOT = _find_repo_root(Path(__file__).resolve())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.preflight.findings_preflight_lookup import lookup_findings


STARTER_KIND_CHOICES = ("candidate", "analysis", "generic")


def _dedupe_preserve_order(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        normalized = value.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def _collect_reference_paths(match: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("bundle_path", "artifact_record_path"):
        value = match.get(key)
        if isinstance(value, str) and value:
            values.append(value)

    candidate_refs = match.get("candidate_refs") or []
    values.extend(str(value) for value in candidate_refs)

    evidence_refs = match.get("evidence_refs") or []
    for ref in evidence_refs:
        if isinstance(ref, dict):
            path = ref.get("path")
            if isinstance(path, str) and path:
                values.append(path)

    return _dedupe_preserve_order(values)


def _build_anchor_entry(match: dict[str, Any]) -> dict[str, Any]:
    return {
        "finding_id": match["finding_id"],
        "summary": match.get("summary"),
        "seam_class": match.get("seam_class"),
        "mechanism": match.get("mechanism"),
        "reference_paths": _collect_reference_paths(match),
    }


def build_packet_starter(
    matches: list[dict[str, Any]],
    *,
    title: str,
    starter_kind: str,
    filters: dict[str, str],
) -> dict[str, Any]:
    positive_anchors: list[dict[str, Any]] = []
    blocking_findings: list[dict[str, Any]] = []
    do_not_repeat: list[str] = []
    next_steps: list[str] = []
    reference_paths: list[str] = []

    for match in matches:
        if match.get("finding_outcome") == "positive":
            positive_anchors.append(_build_anchor_entry(match))
        elif match.get("finding_outcome") in {"negative", "direction_lock"}:
            blocking_entry = _build_anchor_entry(match)
            blocking_entry["finding_outcome"] = match.get("finding_outcome")
            blocking_findings.append(blocking_entry)

        do_not_repeat.extend(str(value) for value in match.get("do_not_repeat") or [])

        next_step = match.get("next_admissible_step")
        if isinstance(next_step, str) and next_step:
            next_steps.append(next_step)

        reference_paths.extend(_collect_reference_paths(match))

    return {
        "starter_title": title,
        "starter_kind": starter_kind,
        "advisory_only": True,
        "filters": filters,
        "matched_finding_ids": [str(match["finding_id"]) for match in matches],
        "match_count": len(matches),
        "positive_anchors": positive_anchors,
        "blocking_findings": blocking_findings,
        "do_not_repeat": _dedupe_preserve_order(do_not_repeat),
        "next_admissible_steps": _dedupe_preserve_order(next_steps),
        "reference_paths": _dedupe_preserve_order(reference_paths),
    }


def format_packet_starter_markdown(starter: dict[str, Any]) -> str:
    lines = [
        f"# {starter['starter_title']}",
        "",
        "> Advisory only. Generated from matched research findings for manual copy/paste.",
        "> It does not create governance, runtime, readiness, or promotion authority.",
        "",
        f"- starter_kind: `{starter['starter_kind']}`",
        f"- matched_findings: `{starter['match_count']}`",
        f"- matched_finding_ids: `{', '.join(starter['matched_finding_ids']) or 'none'}`",
    ]

    filters = starter.get("filters") or {}
    if filters:
        lines.append(f"- filters: `{json.dumps(filters, ensure_ascii=False, sort_keys=True)}`")

    reference_paths = starter.get("reference_paths") or []
    lines.extend(["", "## Reference paths"])
    if reference_paths:
        for path in reference_paths:
            lines.append(f"- `{path}`")
    else:
        lines.append("- None")

    lines.extend(["", "## Positive anchors to reuse"])
    positive_anchors = starter.get("positive_anchors") or []
    if positive_anchors:
        for anchor in positive_anchors:
            lines.append(
                f"- `{anchor['finding_id']}` — {anchor.get('summary') or 'No summary available.'}"
            )
            mechanism = anchor.get("mechanism")
            if mechanism:
                lines.append(f"  - mechanism: {mechanism}")
    else:
        lines.append("- None")

    lines.extend(["", "## Blocking findings and direction locks"])
    blocking_findings = starter.get("blocking_findings") or []
    if blocking_findings:
        for finding in blocking_findings:
            lines.append(
                f"- `{finding['finding_id']}` ({finding.get('finding_outcome')}) — "
                f"{finding.get('summary') or 'No summary available.'}"
            )
            mechanism = finding.get("mechanism")
            if mechanism:
                lines.append(f"  - mechanism: {mechanism}")
    else:
        lines.append("- None")

    lines.extend(["", "## Do not repeat"])
    repeated_hints = starter.get("do_not_repeat") or []
    if repeated_hints:
        for hint in repeated_hints:
            lines.append(f"- {hint}")
    else:
        lines.append("- None")

    lines.extend(["", "## Next admissible step hints"])
    next_steps = starter.get("next_admissible_steps") or []
    if next_steps:
        for step in next_steps:
            lines.append(f"- {step}")
    else:
        lines.append("- None")

    return "\n".join(lines)


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


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate advisory packet starter content from matched research findings."
    )
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="Repository root to inspect")
    parser.add_argument("--title", default="Research findings packet starter")
    parser.add_argument(
        "--starter-kind",
        choices=STARTER_KIND_CHOICES,
        default="generic",
        help="Advisory packet starter framing to emit",
    )
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
    parser.add_argument("--candidate-ref-contains", help="Substring filter across candidate refs")
    parser.add_argument("--timestamp-contains", help="Substring filter across key timestamps")
    parser.add_argument("--text-contains", help="Substring filter across advisory text fields")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
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

    starter = build_packet_starter(
        matches,
        title=args.title,
        starter_kind=args.starter_kind,
        filters=filters,
    )

    if args.json:
        print(json.dumps(starter, indent=2, ensure_ascii=False))
    else:
        print(format_packet_starter_markdown(starter))
    return 0


if __name__ == "__main__":
    sys.exit(main())
