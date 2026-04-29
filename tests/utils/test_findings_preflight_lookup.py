from __future__ import annotations

import json
from pathlib import Path

from scripts.preflight.findings_preflight_lookup import (
    _find_repo_root as find_preflight_lookup_repo_root,
)
from scripts.preflight.findings_preflight_lookup import (
    build_derived_findings_index,
    find_blocking_matches,
    format_lookup_report,
    load_findings_index,
    lookup_findings,
    main,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _artifact_record_payload(
    *,
    artifact_id: str,
    finding_id: str,
    finding_outcome: str,
    created_at: str,
    bundle_path: str,
) -> dict:
    return {
        "entity_id": artifact_id,
        "entity_type": "artifact",
        "created_at": created_at,
        "schema_version": "research_ledger.v1",
        "metadata": {
            "strategy_family": "ri",
            "strategy_family_source": "family_registry_v1",
            "classification_role": "descriptive_only",
            "runtime_authority": "none",
            "lane": "findings-preflight-lookup-test",
            "finding_id": finding_id,
            "finding_outcome": finding_outcome,
        },
        "experiment_id": None,
        "artifact_kind": "evidence_bundle",
        "path": bundle_path,
        "role": "research_finding_bundle",
        "format": "json",
        "checksum_sha256": f"checksum-{artifact_id}",
        "size_bytes": 123,
        "intelligence_refs": [],
    }


def _seed_findings_repo(tmp_path: Path) -> Path:
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)
    (repo_root / "pyproject.toml").write_text(
        '[project]\nname = "findings-preflight-lookup-test"\nversion = "0.0.0"\n',
        encoding="utf-8",
    )

    positive_bundle_path = (
        repo_root
        / "artifacts"
        / "bundles"
        / "findings"
        / "ri_policy_router"
        / "FIND-2026-0100_positive.json"
    )
    negative_bundle_path = (
        repo_root
        / "artifacts"
        / "bundles"
        / "findings"
        / "ri_policy_router"
        / "FIND-2026-0101_negative.json"
    )
    lock_bundle_path = (
        repo_root
        / "artifacts"
        / "bundles"
        / "findings"
        / "ri_policy_router"
        / "FIND-2026-0102_direction_lock.json"
    )

    _write_json(
        positive_bundle_path,
        {
            "finding_id": "FIND-2026-0100",
            "artifact_id": "ART-2026-0100",
            "finding_outcome": "positive",
            "subject": "ri_policy_router",
            "domain": "ri_policy_router",
            "symbol": "tBTCUSD",
            "timeframe": "3h",
            "summary": "Positive seam proof; text mentions negative only as a historical contrast.",
            "mechanism": "Bounded continuation-local guard reaches the target row.",
            "seam_class": "weak_pre_aged_release_target_reachability",
            "candidate_refs": ["docs/governance/example_positive_packet.md"],
            "key_timestamps": ["2023-12-22T15:00:00+00:00"],
            "do_not_repeat": ["Do not reopen reachability work without citing this proof."],
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
            "finding_id": "FIND-2026-0101",
            "artifact_id": "ART-2026-0101",
            "finding_outcome": "negative",
            "subject": "ri_policy_router",
            "domain": "ri_policy_router",
            "symbol": "tBTCUSD",
            "timeframe": "3h",
            "summary": "Candidate worsens the fail window through broader churn.",
            "mechanism": "Blocking one row shifts replacement entries two bars later.",
            "seam_class": "cooldown_displacement_loop",
            "candidate_refs": ["docs/governance/example_negative_packet.md"],
            "key_timestamps": ["2023-12-24T21:00:00+00:00"],
            "do_not_repeat": ["Do not advance this candidate unchanged."],
            "next_admissible_step": "Keep the next packet explicit about cooldown displacement.",
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
            "finding_id": "FIND-2026-0102",
            "artifact_id": "ART-2026-0102",
            "finding_outcome": "direction_lock",
            "subject": "ri_policy_router",
            "domain": "ri_policy_router",
            "symbol": "tBTCUSD",
            "timeframe": "3h",
            "summary": "Seam A and seam B must stay split.",
            "mechanism": "The two rows represent different continuation states.",
            "seam_class": "continuation_split_direction_lock",
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
        repo_root / "artifacts" / "research_ledger" / "artifacts" / "ART-2026-0100.json",
        _artifact_record_payload(
            artifact_id="ART-2026-0100",
            finding_id="FIND-2026-0100",
            finding_outcome="positive",
            created_at="2026-04-24T09:30:00+00:00",
            bundle_path=positive_bundle_path.relative_to(repo_root).as_posix(),
        ),
    )
    _write_json(
        repo_root / "artifacts" / "research_ledger" / "artifacts" / "ART-2026-0101.json",
        _artifact_record_payload(
            artifact_id="ART-2026-0101",
            finding_id="FIND-2026-0101",
            finding_outcome="negative",
            created_at="2026-04-24T09:31:00+00:00",
            bundle_path=negative_bundle_path.relative_to(repo_root).as_posix(),
        ),
    )
    _write_json(
        repo_root / "artifacts" / "research_ledger" / "artifacts" / "ART-2026-0102.json",
        _artifact_record_payload(
            artifact_id="ART-2026-0102",
            finding_id="FIND-2026-0102",
            finding_outcome="direction_lock",
            created_at="2026-04-24T09:32:00+00:00",
            bundle_path=lock_bundle_path.relative_to(repo_root).as_posix(),
        ),
    )

    _write_json(
        repo_root / "artifacts" / "research_ledger" / "indexes" / "findings_index.json",
        {
            "schema_version": "research_findings_index.v1",
            "entity_type": "finding",
            "authoritative_source": {
                "bundle_schema_path": "artifacts/bundles/findings/schema/research_findings_bundle_v1.schema.json",
                "ledger_record_type": "artifact",
                "identity_authority": "artifact_record_and_bundle",
            },
            "rebuildable": True,
            "runtime_authority": "none",
            "notes": [
                "This index is a derived, rebuildable projection over finding bundles and ArtifactRecords.",
                "It is not a governance gate, runtime surface, readiness surface, or promotion surface.",
            ],
            "items": [
                {
                    "finding_id": "FIND-2026-0100",
                    "artifact_id": "ART-2026-0100",
                    "finding_outcome": "positive",
                    "subject": "ri_policy_router",
                    "domain": "ri_policy_router",
                    "symbol": "tBTCUSD",
                    "timeframe": "3h",
                    "seam_class": "weak_pre_aged_release_target_reachability",
                    "bundle_path": positive_bundle_path.relative_to(repo_root).as_posix(),
                    "artifact_record_path": "artifacts/research_ledger/artifacts/ART-2026-0100.json",
                    "summary": "Positive seam proof; text mentions negative only as a historical contrast.",
                    "candidate_refs": ["docs/governance/example_positive_packet.md"],
                    "key_timestamps": ["2023-12-22T15:00:00+00:00"],
                    "do_not_repeat": ["Do not reopen reachability work without citing this proof."],
                },
                {
                    "finding_id": "FIND-2026-0101",
                    "artifact_id": "ART-2026-0101",
                    "finding_outcome": "negative",
                    "subject": "ri_policy_router",
                    "domain": "ri_policy_router",
                    "symbol": "tBTCUSD",
                    "timeframe": "3h",
                    "seam_class": "cooldown_displacement_loop",
                    "bundle_path": negative_bundle_path.relative_to(repo_root).as_posix(),
                    "artifact_record_path": "artifacts/research_ledger/artifacts/ART-2026-0101.json",
                    "summary": "Candidate worsens the fail window through broader churn.",
                    "candidate_refs": ["docs/governance/example_negative_packet.md"],
                    "key_timestamps": ["2023-12-24T21:00:00+00:00"],
                    "do_not_repeat": ["Do not advance this candidate unchanged."],
                },
                {
                    "finding_id": "FIND-2026-0102",
                    "artifact_id": "ART-2026-0102",
                    "finding_outcome": "direction_lock",
                    "subject": "ri_policy_router",
                    "domain": "ri_policy_router",
                    "symbol": "tBTCUSD",
                    "timeframe": "3h",
                    "seam_class": "continuation_split_direction_lock",
                    "bundle_path": lock_bundle_path.relative_to(repo_root).as_posix(),
                    "artifact_record_path": "artifacts/research_ledger/artifacts/ART-2026-0102.json",
                    "summary": "Seam A and seam B must stay split.",
                    "candidate_refs": ["docs/governance/example_direction_lock_packet.md"],
                    "key_timestamps": ["2023-12-22T15:00:00+00:00", "2023-12-24T21:00:00+00:00"],
                    "do_not_repeat": ["Do not bundle both seams into one candidate."],
                },
            ],
        },
    )

    return repo_root


def test_find_repo_root_uses_repo_marker_without_generated_findings_index(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    script_path = repo_root / "scripts" / "preflight" / "dummy.py"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text("# dummy\n", encoding="utf-8")
    (repo_root / "pyproject.toml").write_text(
        '[project]\nname = "findings-preflight-lookup-test"\nversion = "0.0.0"\n',
        encoding="utf-8",
    )

    assert find_preflight_lookup_repo_root(script_path) == repo_root


def test_load_findings_index_reads_items(tmp_path: Path) -> None:
    repo_root = _seed_findings_repo(tmp_path)

    payload = load_findings_index(repo_root)

    assert payload["schema_version"] == "research_findings_index.v1"
    assert len(payload["items"]) == 3


def test_lookup_findings_filters_exact_fields_and_enriches_bundle_data(tmp_path: Path) -> None:
    repo_root = _seed_findings_repo(tmp_path)

    matches = lookup_findings(
        repo_root,
        domain="ri_policy_router",
        seam_class="cooldown_displacement_loop",
    )

    assert len(matches) == 1
    match = matches[0]
    assert match["finding_id"] == "FIND-2026-0101"
    assert match["mechanism"] == "Blocking one row shifts replacement entries two bars later."
    assert match["next_admissible_step"] == (
        "Keep the next packet explicit about cooldown displacement."
    )
    assert match["blocking_match"] is True


def test_lookup_findings_supports_text_and_candidate_ref_filters(tmp_path: Path) -> None:
    repo_root = _seed_findings_repo(tmp_path)

    matches = lookup_findings(
        repo_root,
        candidate_ref_contains="example_positive_packet",
        text_contains="historical contrast",
    )

    assert [match["finding_id"] for match in matches] == ["FIND-2026-0100"]


def test_find_blocking_matches_uses_exact_structured_outcome_not_text(tmp_path: Path) -> None:
    repo_root = _seed_findings_repo(tmp_path)

    matches = lookup_findings(repo_root, text_contains="historical contrast")
    blocking = find_blocking_matches(matches)

    assert [match["finding_id"] for match in matches] == ["FIND-2026-0100"]
    assert blocking == []


def test_main_returns_zero_by_default_even_when_blocking_matches_exist(
    tmp_path: Path,
    capsys,
) -> None:
    repo_root = _seed_findings_repo(tmp_path)

    exit_code = main(["--repo-root", str(repo_root), "--domain", "ri_policy_router"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "blocking_matches: 2" in captured.out


def test_main_returns_non_zero_only_for_structured_blocking_matches(
    tmp_path: Path,
    capsys,
) -> None:
    repo_root = _seed_findings_repo(tmp_path)

    positive_exit = main(
        [
            "--repo-root",
            str(repo_root),
            "--text-contains",
            "historical contrast",
            "--fail-on-blocking-match",
        ]
    )
    blocking_exit = main(
        [
            "--repo-root",
            str(repo_root),
            "--seam-class",
            "cooldown_displacement_loop",
            "--fail-on-blocking-match",
        ]
    )
    _ = capsys.readouterr()

    assert positive_exit == 0
    assert blocking_exit == 2


def test_format_lookup_report_includes_next_step_and_do_not_repeat(tmp_path: Path) -> None:
    repo_root = _seed_findings_repo(tmp_path)
    matches = lookup_findings(repo_root, finding_outcome="direction_lock")

    report = format_lookup_report(
        matches,
        repo_root=repo_root,
        filters={"finding_outcome": "direction_lock"},
    )

    assert "Choose one seam before writing a new packet." in report
    assert "Do not bundle both seams into one candidate." in report


def test_build_derived_findings_index_matches_seeded_index(tmp_path: Path) -> None:
    repo_root = _seed_findings_repo(tmp_path)

    expected = load_findings_index(repo_root)
    derived = build_derived_findings_index(repo_root)

    assert derived == expected


def test_main_validate_index_projection_reports_success(tmp_path: Path, capsys) -> None:
    repo_root = _seed_findings_repo(tmp_path)

    exit_code = main(["--repo-root", str(repo_root), "--validate-index-projection"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "matches derived projection" in captured.out


def test_main_validate_index_projection_fails_on_divergence(tmp_path: Path, capsys) -> None:
    repo_root = _seed_findings_repo(tmp_path)
    index_path = repo_root / "artifacts" / "research_ledger" / "indexes" / "findings_index.json"
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    payload["items"][0]["summary"] = "Drifted summary"
    index_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    exit_code = main(["--repo-root", str(repo_root), "--validate-index-projection"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "diverges from derived projection" in captured.err


def test_main_validate_index_projection_fails_when_index_missing(tmp_path: Path, capsys) -> None:
    repo_root = _seed_findings_repo(tmp_path)
    index_path = repo_root / "artifacts" / "research_ledger" / "indexes" / "findings_index.json"
    index_path.unlink()

    exit_code = main(["--repo-root", str(repo_root), "--validate-index-projection"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "findings_index.json is missing" in captured.err
