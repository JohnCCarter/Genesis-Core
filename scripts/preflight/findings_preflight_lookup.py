#!/usr/bin/env python3
"""Read-only preflight lookup over the research findings bank."""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Any


BLOCKING_FINDING_OUTCOMES = {"negative", "direction_lock"}
REPO_ROOT_MARKER = "pyproject.toml"
FINDINGS_INDEX_RELATIVE_PATH = (
    Path("artifacts") / "research_ledger" / "indexes" / "findings_index.json"
)
FINDINGS_BUNDLES_RELATIVE_DIR = Path("artifacts") / "bundles" / "findings"
FINDINGS_ARTIFACT_RECORDS_RELATIVE_DIR = Path("artifacts") / "research_ledger" / "artifacts"
FINDINGS_BUNDLE_SCHEMA_RELATIVE_PATH = (
    FINDINGS_BUNDLES_RELATIVE_DIR / "schema" / "research_findings_bundle_v1.schema.json"
)
FINDINGS_INDEX_NOTES = [
    "This index is a derived, rebuildable projection over finding bundles and ArtifactRecords.",
    "It is not a governance gate, runtime surface, readiness surface, or promotion surface.",
]


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


def _repo_relative_path(repo_root: Path, path: Path) -> str:
    return path.relative_to(repo_root).as_posix()


def _require_non_empty_string(payload: dict[str, Any], key: str, *, context: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise RuntimeError(f"{context} is missing required non-empty string field: {key}")
    return value


def _require_list(payload: dict[str, Any], key: str, *, context: str) -> list[Any]:
    value = payload.get(key)
    if not isinstance(value, list):
        raise RuntimeError(f"{context} is missing required list field: {key}")
    return value


def _findings_index_path(repo_root: Path) -> Path:
    return repo_root / FINDINGS_INDEX_RELATIVE_PATH


def _iter_finding_bundle_paths(repo_root: Path) -> list[Path]:
    bundles_root = repo_root / FINDINGS_BUNDLES_RELATIVE_DIR
    if not bundles_root.is_dir():
        raise RuntimeError(f"Findings bundles directory not found: {bundles_root}")

    bundle_paths = sorted(
        path
        for path in bundles_root.rglob("*.json")
        if "schema" not in path.relative_to(bundles_root).parts
    )
    if not bundle_paths:
        raise RuntimeError(f"No findings bundles found under {bundles_root}")
    return bundle_paths


def _load_finding_artifact_record(
    repo_root: Path,
    *,
    artifact_id: str,
    finding_id: str,
    finding_outcome: str,
    bundle_path: str,
) -> tuple[str, dict[str, Any]]:
    artifact_record_path = (
        repo_root / FINDINGS_ARTIFACT_RECORDS_RELATIVE_DIR / f"{artifact_id}.json"
    )
    artifact_record = _load_json_file(artifact_record_path)
    artifact_context = _repo_relative_path(repo_root, artifact_record_path)

    if artifact_record.get("entity_id") != artifact_id:
        raise RuntimeError(
            f"ArtifactRecord mismatch for {artifact_context}: expected entity_id={artifact_id!r}, "
            f"got {artifact_record.get('entity_id')!r}"
        )
    if artifact_record.get("artifact_kind") != "evidence_bundle":
        raise RuntimeError(
            f"ArtifactRecord {artifact_context} must use artifact_kind='evidence_bundle'"
        )
    if artifact_record.get("role") != "research_finding_bundle":
        raise RuntimeError(
            f"ArtifactRecord {artifact_context} must use role='research_finding_bundle'"
        )
    if artifact_record.get("format") != "json":
        raise RuntimeError(f"ArtifactRecord {artifact_context} must use format='json'")
    if artifact_record.get("path") != bundle_path:
        raise RuntimeError(
            f"ArtifactRecord path mismatch for {artifact_context}: expected {bundle_path!r}, "
            f"got {artifact_record.get('path')!r}"
        )

    metadata = artifact_record.get("metadata")
    if not isinstance(metadata, dict):
        raise RuntimeError(f"ArtifactRecord {artifact_context} must contain a metadata object")
    if metadata.get("finding_id") != finding_id:
        raise RuntimeError(
            f"ArtifactRecord metadata mismatch for {artifact_context}: expected finding_id="
            f"{finding_id!r}, got {metadata.get('finding_id')!r}"
        )
    if metadata.get("finding_outcome") != finding_outcome:
        raise RuntimeError(
            f"ArtifactRecord metadata mismatch for {artifact_context}: expected "
            f"finding_outcome={finding_outcome!r}, got {metadata.get('finding_outcome')!r}"
        )

    return artifact_context, artifact_record


def _validate_finding_artifact_record_coverage(
    repo_root: Path,
    *,
    expected_artifact_record_paths: set[str],
) -> None:
    artifact_records_root = repo_root / FINDINGS_ARTIFACT_RECORDS_RELATIVE_DIR
    if not artifact_records_root.is_dir():
        raise RuntimeError(f"Findings artifact-record directory not found: {artifact_records_root}")

    observed_paths: set[str] = set()
    findings_bundle_prefix = f"{FINDINGS_BUNDLES_RELATIVE_DIR.as_posix()}/"

    for artifact_record_path in sorted(artifact_records_root.glob("ART-*.json")):
        artifact_record = _load_json_file(artifact_record_path)
        bundle_path = artifact_record.get("path")
        if artifact_record.get("role") != "research_finding_bundle":
            continue
        if not isinstance(bundle_path, str) or not bundle_path.startswith(findings_bundle_prefix):
            continue
        observed_paths.add(_repo_relative_path(repo_root, artifact_record_path))

    unexpected_paths = sorted(observed_paths - expected_artifact_record_paths)
    missing_paths = sorted(expected_artifact_record_paths - observed_paths)
    if unexpected_paths or missing_paths:
        details: list[str] = []
        if unexpected_paths:
            details.append(f"unexpected ArtifactRecords: {unexpected_paths}")
        if missing_paths:
            details.append(f"missing ArtifactRecords: {missing_paths}")
        raise RuntimeError("Findings ArtifactRecord coverage mismatch: " + "; ".join(details))


def build_derived_findings_index(repo_root: Path) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    seen_finding_ids: set[str] = set()
    seen_artifact_ids: set[str] = set()
    expected_artifact_record_paths: set[str] = set()

    for bundle_path in _iter_finding_bundle_paths(repo_root):
        bundle = _load_json_file(bundle_path)
        bundle_context = _repo_relative_path(repo_root, bundle_path)

        finding_id = _require_non_empty_string(bundle, "finding_id", context=bundle_context)
        artifact_id = _require_non_empty_string(bundle, "artifact_id", context=bundle_context)
        finding_outcome = _require_non_empty_string(
            bundle, "finding_outcome", context=bundle_context
        )

        if finding_id in seen_finding_ids:
            raise RuntimeError(f"Duplicate finding_id across findings bundles: {finding_id}")
        if artifact_id in seen_artifact_ids:
            raise RuntimeError(f"Duplicate artifact_id across findings bundles: {artifact_id}")
        seen_finding_ids.add(finding_id)
        seen_artifact_ids.add(artifact_id)

        artifact_record_path, _artifact_record = _load_finding_artifact_record(
            repo_root,
            artifact_id=artifact_id,
            finding_id=finding_id,
            finding_outcome=finding_outcome,
            bundle_path=bundle_context,
        )
        expected_artifact_record_paths.add(artifact_record_path)

        items.append(
            {
                "finding_id": finding_id,
                "artifact_id": artifact_id,
                "finding_outcome": finding_outcome,
                "subject": _require_non_empty_string(bundle, "subject", context=bundle_context),
                "domain": _require_non_empty_string(bundle, "domain", context=bundle_context),
                "symbol": _require_non_empty_string(bundle, "symbol", context=bundle_context),
                "timeframe": _require_non_empty_string(bundle, "timeframe", context=bundle_context),
                "seam_class": _require_non_empty_string(
                    bundle, "seam_class", context=bundle_context
                ),
                "bundle_path": bundle_context,
                "artifact_record_path": artifact_record_path,
                "summary": _require_non_empty_string(bundle, "summary", context=bundle_context),
                "candidate_refs": _require_list(bundle, "candidate_refs", context=bundle_context),
                "key_timestamps": _require_list(bundle, "key_timestamps", context=bundle_context),
                "do_not_repeat": _require_list(bundle, "do_not_repeat", context=bundle_context),
            }
        )

    _validate_finding_artifact_record_coverage(
        repo_root,
        expected_artifact_record_paths=expected_artifact_record_paths,
    )
    items.sort(key=lambda item: item["finding_id"])

    return {
        "schema_version": "research_findings_index.v1",
        "entity_type": "finding",
        "authoritative_source": {
            "bundle_schema_path": FINDINGS_BUNDLE_SCHEMA_RELATIVE_PATH.as_posix(),
            "ledger_record_type": "artifact",
            "identity_authority": "artifact_record_and_bundle",
        },
        "rebuildable": True,
        "runtime_authority": "none",
        "notes": list(FINDINGS_INDEX_NOTES),
        "items": items,
    }


def _json_diff(expected: dict[str, Any], actual: dict[str, Any], *, max_lines: int = 40) -> str:
    expected_lines = json.dumps(expected, indent=2, ensure_ascii=False, sort_keys=True).splitlines()
    actual_lines = json.dumps(actual, indent=2, ensure_ascii=False, sort_keys=True).splitlines()
    diff_lines = list(
        difflib.unified_diff(
            expected_lines,
            actual_lines,
            fromfile="expected",
            tofile="actual",
            lineterm="",
        )
    )
    if len(diff_lines) > max_lines:
        diff_lines = [*diff_lines[:max_lines], "... diff truncated ..."]
    return "\n".join(diff_lines)


def validate_findings_index_projection(repo_root: Path) -> dict[str, Any]:
    index_path = _findings_index_path(repo_root)
    if not index_path.is_file():
        raise RuntimeError(f"findings_index.json is missing: {index_path}")

    expected_payload = build_derived_findings_index(repo_root)
    actual_payload = load_findings_index(repo_root)
    if actual_payload != expected_payload:
        diff = _json_diff(expected_payload, actual_payload)
        raise RuntimeError(
            "findings_index.json diverges from derived projection built from committed "
            f"findings-bank sources:\n{diff}"
        )

    return {
        "repo_root": str(repo_root),
        "index_path": str(index_path),
        "item_count": len(expected_payload["items"]),
        "artifact_record_count": len(expected_payload["items"]),
        "status": "ok",
    }


def load_findings_index(repo_root: Path) -> dict[str, Any]:
    index_path = _findings_index_path(repo_root)
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
    parser.add_argument(
        "--validate-index-projection",
        action="store_true",
        help=(
            "Derive the expected findings_index.json from committed findings bundles and "
            "ArtifactRecords, then fail if the local materialized index is missing or diverges."
        ),
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()

    if args.validate_index_projection:
        try:
            payload = validate_findings_index_projection(repo_root)
        except RuntimeError as exc:
            print(f"[FAIL] {exc}", file=sys.stderr)
            return 1

        if args.json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print(
                "[OK] findings_index.json matches derived projection from committed findings-bank "
                f"sources ({payload['item_count']} items)"
            )
        return 0

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
