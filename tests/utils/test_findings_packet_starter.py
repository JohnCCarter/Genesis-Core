from __future__ import annotations

import json
from pathlib import Path

from scripts.preflight.findings_packet_starter import (
    build_packet_starter,
    format_packet_starter_markdown,
    main,
)
from scripts.preflight.findings_preflight_lookup import lookup_findings


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _seed_findings_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"

    positive_bundle_path = (
        repo_root
        / "artifacts"
        / "bundles"
        / "findings"
        / "ri_policy_router"
        / "FIND-2026-0200_positive.json"
    )
    negative_bundle_path = (
        repo_root
        / "artifacts"
        / "bundles"
        / "findings"
        / "ri_policy_router"
        / "FIND-2026-0201_negative.json"
    )
    lock_bundle_path = (
        repo_root
        / "artifacts"
        / "bundles"
        / "findings"
        / "ri_policy_router"
        / "FIND-2026-0202_direction_lock.json"
    )

    _write_json(
        positive_bundle_path,
        {
            "finding_id": "FIND-2026-0200",
            "artifact_id": "ART-2026-0200",
            "finding_outcome": "positive",
            "summary": "Positive seam proof ready to cite.",
            "mechanism": "Bounded guard reaches the target row.",
            "candidate_refs": ["docs/governance/example_positive_packet.md"],
            "key_timestamps": ["2023-12-22T15:00:00+00:00"],
            "do_not_repeat": ["Do not reopen seam reachability work."],
            "next_admissible_step": "Use the reachable seam as input to a narrower candidate.",
            "runtime_authority": "none",
            "evidence_refs": [
                {
                    "path": "docs/governance/example_positive_evidence.md",
                    "role": "supporting_evidence",
                }
            ],
        },
    )
    _write_json(
        negative_bundle_path,
        {
            "finding_id": "FIND-2026-0201",
            "artifact_id": "ART-2026-0201",
            "finding_outcome": "negative",
            "summary": "Candidate worsens the fail window through broader churn.",
            "mechanism": "Blocking one row shifts replacement entries two bars later.",
            "candidate_refs": ["docs/governance/example_negative_packet.md"],
            "key_timestamps": ["2023-12-24T21:00:00+00:00"],
            "do_not_repeat": [
                "Do not bundle both seams into one candidate.",
                "Do not advance this candidate unchanged.",
            ],
            "next_admissible_step": "Choose one seam before writing a new packet.",
            "runtime_authority": "none",
            "evidence_refs": [
                {
                    "path": "docs/governance/example_negative_evidence.md",
                    "role": "mechanism_diagnosis",
                }
            ],
        },
    )
    _write_json(
        lock_bundle_path,
        {
            "finding_id": "FIND-2026-0202",
            "artifact_id": "ART-2026-0202",
            "finding_outcome": "direction_lock",
            "summary": "Seam A and seam B must stay split.",
            "mechanism": "The two rows represent different continuation states.",
            "candidate_refs": ["docs/governance/example_direction_lock_packet.md"],
            "key_timestamps": ["2023-12-22T15:00:00+00:00", "2023-12-24T21:00:00+00:00"],
            "do_not_repeat": ["Do not bundle both seams into one candidate."],
            "next_admissible_step": "Choose one seam before writing a new packet.",
            "runtime_authority": "none",
            "evidence_refs": [
                {
                    "path": "docs/governance/example_direction_lock_evidence.md",
                    "role": "direction_lock",
                }
            ],
        },
    )

    _write_json(
        repo_root / "artifacts" / "research_ledger" / "indexes" / "findings_index.json",
        {
            "schema_version": "research_findings_index.v1",
            "entity_type": "finding",
            "items": [
                {
                    "finding_id": "FIND-2026-0200",
                    "artifact_id": "ART-2026-0200",
                    "finding_outcome": "positive",
                    "subject": "ri_policy_router",
                    "domain": "ri_policy_router",
                    "symbol": "tBTCUSD",
                    "timeframe": "3h",
                    "seam_class": "weak_pre_aged_release_target_reachability",
                    "bundle_path": positive_bundle_path.relative_to(repo_root).as_posix(),
                    "artifact_record_path": "artifacts/research_ledger/artifacts/ART-2026-0200.json",
                    "summary": "Positive seam proof ready to cite.",
                    "candidate_refs": ["docs/governance/example_positive_packet.md"],
                    "key_timestamps": ["2023-12-22T15:00:00+00:00"],
                    "do_not_repeat": ["Do not reopen seam reachability work."],
                },
                {
                    "finding_id": "FIND-2026-0201",
                    "artifact_id": "ART-2026-0201",
                    "finding_outcome": "negative",
                    "subject": "ri_policy_router",
                    "domain": "ri_policy_router",
                    "symbol": "tBTCUSD",
                    "timeframe": "3h",
                    "seam_class": "cooldown_displacement_loop",
                    "bundle_path": negative_bundle_path.relative_to(repo_root).as_posix(),
                    "artifact_record_path": "artifacts/research_ledger/artifacts/ART-2026-0201.json",
                    "summary": "Candidate worsens the fail window through broader churn.",
                    "candidate_refs": ["docs/governance/example_negative_packet.md"],
                    "key_timestamps": ["2023-12-24T21:00:00+00:00"],
                    "do_not_repeat": [
                        "Do not bundle both seams into one candidate.",
                        "Do not advance this candidate unchanged.",
                    ],
                },
                {
                    "finding_id": "FIND-2026-0202",
                    "artifact_id": "ART-2026-0202",
                    "finding_outcome": "direction_lock",
                    "subject": "ri_policy_router",
                    "domain": "ri_policy_router",
                    "symbol": "tBTCUSD",
                    "timeframe": "3h",
                    "seam_class": "continuation_split_direction_lock",
                    "bundle_path": lock_bundle_path.relative_to(repo_root).as_posix(),
                    "artifact_record_path": "artifacts/research_ledger/artifacts/ART-2026-0202.json",
                    "summary": "Seam A and seam B must stay split.",
                    "candidate_refs": ["docs/governance/example_direction_lock_packet.md"],
                    "key_timestamps": ["2023-12-22T15:00:00+00:00", "2023-12-24T21:00:00+00:00"],
                    "do_not_repeat": ["Do not bundle both seams into one candidate."],
                },
            ],
        },
    )

    return repo_root


def test_build_packet_starter_deduplicates_hints_in_first_seen_order(tmp_path: Path) -> None:
    repo_root = _seed_findings_repo(tmp_path)
    matches = lookup_findings(repo_root, domain="ri_policy_router")

    starter = build_packet_starter(
        matches,
        title="RI packet starter",
        starter_kind="candidate",
        filters={"domain": "ri_policy_router"},
    )

    assert starter["matched_finding_ids"] == [
        "FIND-2026-0200",
        "FIND-2026-0201",
        "FIND-2026-0202",
    ]
    assert [anchor["finding_id"] for anchor in starter["positive_anchors"]] == ["FIND-2026-0200"]
    assert [finding["finding_id"] for finding in starter["blocking_findings"]] == [
        "FIND-2026-0201",
        "FIND-2026-0202",
    ]
    assert starter["do_not_repeat"] == [
        "Do not reopen seam reachability work.",
        "Do not bundle both seams into one candidate.",
        "Do not advance this candidate unchanged.",
    ]
    assert starter["next_admissible_steps"] == [
        "Use the reachable seam as input to a narrower candidate.",
        "Choose one seam before writing a new packet.",
    ]


def test_format_packet_starter_markdown_includes_advisory_header_and_reference_paths(
    tmp_path: Path,
) -> None:
    repo_root = _seed_findings_repo(tmp_path)
    matches = lookup_findings(repo_root, domain="ri_policy_router")
    starter = build_packet_starter(
        matches,
        title="RI packet starter",
        starter_kind="analysis",
        filters={"domain": "ri_policy_router"},
    )

    markdown = format_packet_starter_markdown(starter)

    assert "> Advisory only." in markdown
    assert "It does not create governance, runtime, readiness, or promotion authority." in markdown
    assert "## Reference paths" in markdown
    assert "docs/governance/example_negative_packet.md" in markdown


def test_main_json_output_omits_authority_like_keys_and_preserves_order(
    tmp_path: Path,
    capsys,
) -> None:
    repo_root = _seed_findings_repo(tmp_path)

    exit_code = main(
        [
            "--repo-root",
            str(repo_root),
            "--domain",
            "ri_policy_router",
            "--title",
            "RI packet starter",
            "--starter-kind",
            "candidate",
            "--json",
        ]
    )
    captured = capsys.readouterr()

    payload = json.loads(captured.out)

    assert exit_code == 0
    for forbidden_key in ("verdict", "ready_for_review", "promotion", "family_rule"):
        assert forbidden_key not in payload
    assert payload["next_admissible_steps"] == [
        "Use the reachable seam as input to a narrower candidate.",
        "Choose one seam before writing a new packet.",
    ]


def test_main_does_not_create_files_or_directories(tmp_path: Path, capsys) -> None:
    repo_root = _seed_findings_repo(tmp_path)
    before_paths = sorted(str(path.relative_to(repo_root)) for path in repo_root.rglob("*"))

    exit_code = main(
        [
            "--repo-root",
            str(repo_root),
            "--domain",
            "ri_policy_router",
            "--title",
            "No-write starter",
        ]
    )
    _ = capsys.readouterr()
    after_paths = sorted(str(path.relative_to(repo_root)) for path in repo_root.rglob("*"))

    assert exit_code == 0
    assert before_paths == after_paths
