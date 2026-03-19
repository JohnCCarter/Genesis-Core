from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from core.research_ledger.enums import (
    ArtifactKind,
    ChampionStatus,
    GovernanceDecisionKind,
    LedgerEntityType,
    PromotionTargetKind,
)
from core.research_ledger.models import (
    ArtifactLink,
    ArtifactRecord,
    ChampionRecord,
    CodeVersionRef,
    DatasetRef,
    ExperimentRecord,
    GovernanceDecisionRecord,
    HypothesisRecord,
    IntelligenceRef,
    PromotionRecord,
    ProposalRecord,
)
from core.research_ledger.service import ResearchLedgerService
from core.research_ledger.storage import LedgerStorage
from core.research_ledger.validators import LedgerValidationError
from core.strategy.family_registry import StrategyFamilyValidationError


def _service(tmp_path: Path) -> ResearchLedgerService:
    return ResearchLedgerService(LedgerStorage(root=tmp_path / "artifacts" / "research_ledger"))


def _experiment_record(
    *,
    artifact_links: tuple[ArtifactLink, ...] = (),
    hypothesis_id: str = "HYP-2026-0001",
    proposal_id: str = "PROP-2026-0001",
) -> ExperimentRecord:
    return ExperimentRecord(
        entity_id="EXP-2026-0001",
        entity_type=LedgerEntityType.EXPERIMENT,
        created_at="2026-03-16T12:10:00+00:00",
        hypothesis_id=hypothesis_id,
        proposal_id=proposal_id,
        title="1h RI vs OFF",
        objective="Validate canonical Phase B on 1h.",
        command_packet_path="docs/governance/templates/command_packet.md",
        code_version=CodeVersionRef(commit_sha="abc123def456"),
        config_paths=("config/optimizer/1h/tBTCUSD_1h_risk_optuna_smoke.yaml",),
        dataset_refs=(DatasetRef(dataset_id="curated.tBTCUSD.1h", version="2026-03-16"),),
        artifact_links=artifact_links,
    )


def test_append_record_refreshes_indexes_and_lineage(tmp_path: Path) -> None:
    service = _service(tmp_path)

    hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0001",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="Ledger lineage",
        hypothesis="Append-only lineage should stay queryable.",
        intelligence_refs=(
            IntelligenceRef(
                module="regime_intelligence",
                ref_kind="artifact_metadata",
                label="ri-proof",
            ),
        ),
    )
    proposal = ProposalRecord(
        entity_id="PROP-2026-0001",
        entity_type=LedgerEntityType.PROPOSAL,
        created_at="2026-03-16T12:05:00+00:00",
        hypothesis_id=hypothesis.entity_id,
        title="Phase B proposal",
        summary="Run a deterministic 1h RI comparison.",
        command_packet_path="docs/governance/templates/command_packet.md",
    )
    experiment = replace(
        _experiment_record(
            hypothesis_id=hypothesis.entity_id,
            proposal_id=proposal.entity_id,
        ),
        metrics={"score": 0.1126, "profit_factor": 1.41},
    )
    artifact = ArtifactRecord(
        entity_id="ART-2026-0001",
        entity_type=LedgerEntityType.ARTIFACT,
        created_at="2026-03-16T12:15:00+00:00",
        experiment_id=experiment.entity_id,
        artifact_kind=ArtifactKind.RESULT_SUMMARY,
        path="results/hparam_search/run_20260316_123000/best_trial.json",
    )
    governance = GovernanceDecisionRecord(
        entity_id="GOV-2026-0001",
        entity_type=LedgerEntityType.GOVERNANCE_DECISION,
        created_at="2026-03-16T12:20:00+00:00",
        subject_type=LedgerEntityType.EXPERIMENT,
        subject_id=experiment.entity_id,
        decision=GovernanceDecisionKind.ACCEPTED,
        rationale="Experiment is traceable and passes gates.",
    )
    promotion = PromotionRecord(
        entity_id="PROMO-2026-0001",
        entity_type=LedgerEntityType.PROMOTION_RECORD,
        created_at="2026-03-16T12:25:00+00:00",
        subject_experiment_id=experiment.entity_id,
        governance_decision_id=governance.entity_id,
        target_kind=PromotionTargetKind.CHAMPION,
        target_ref="config/strategy/champions/tBTCUSD_1h.json",
        source_artifact_id=artifact.entity_id,
    )
    champion = ChampionRecord(
        entity_id="CHAMP-2026-0001",
        entity_type=LedgerEntityType.CHAMPION_RECORD,
        created_at="2026-03-16T12:30:00+00:00",
        symbol="tBTCUSD",
        timeframe="1h",
        promotion_record_id=promotion.entity_id,
        governance_decision_id=governance.entity_id,
        experiment_id=experiment.entity_id,
        artifact_id=artifact.entity_id,
        config_path="config/strategy/champions/tBTCUSD_1h.json",
        status=ChampionStatus.ACTIVE,
    )

    service.append_hypothesis(hypothesis)
    service.append_proposal(proposal)
    service.append_experiment(experiment)
    service.append_artifact(artifact)
    service.append_governance_decision(governance)
    service.append_promotion_record(promotion)
    service.append_champion_record(champion)

    lineage = service.queries.get_hypothesis_lineage(hypothesis.entity_id)
    assert lineage["hypothesis"]["entity_id"] == "HYP-2026-0001"
    assert [item["entity_id"] for item in lineage["proposals"]] == ["PROP-2026-0001"]
    assert [item["entity_id"] for item in lineage["experiments"]] == ["EXP-2026-0001"]
    assert [item["entity_id"] for item in lineage["artifacts"]] == ["ART-2026-0001"]
    assert [item["entity_id"] for item in lineage["promotion_records"]] == ["PROMO-2026-0001"]
    assert [item["entity_id"] for item in lineage["champion_records"]] == ["CHAMP-2026-0001"]

    hypothesis_index = service.storage.read_index("hypothesis")
    experiment_index = service.storage.read_index("experiment")
    champion_index = service.storage.read_index("champion")
    assert hypothesis_index["items"][0]["proposal_ids"] == ["PROP-2026-0001"]
    assert experiment_index["items"][0]["artifact_ids"] == ["ART-2026-0001"]
    assert champion_index["items"][0]["symbol"] == "tBTCUSD"


def test_append_record_rejects_duplicate_ids(tmp_path: Path) -> None:
    service = _service(tmp_path)
    hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0001",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="Duplicate",
        hypothesis="Duplicate IDs must fail.",
    )

    service.append_hypothesis(hypothesis)
    with pytest.raises(FileExistsError, match="HYP-2026-0001"):
        service.append_hypothesis(hypothesis)


def test_append_record_with_strategy_family_tags_metadata(tmp_path: Path) -> None:
    service = _service(tmp_path)
    hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0009",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-18T16:00:00+00:00",
        title="RI hypothesis",
        hypothesis="Family labels should persist in metadata.",
    )

    appended = service.append_record_with_strategy_family(hypothesis, strategy_family="ri")

    assert appended.metadata["strategy_family"] == "ri"
    assert appended.metadata["strategy_family_source"] == "family_registry_v1"


def test_append_record_with_strategy_family_rejects_config_family_mismatch(tmp_path: Path) -> None:
    service = _service(tmp_path)
    hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0010",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-18T16:05:00+00:00",
        title="Mismatch hypothesis",
        hypothesis="Explicit and config strategy_family must match.",
    )

    with pytest.raises(StrategyFamilyValidationError, match="strategy_family_config_mismatch"):
        service.append_record_with_strategy_family(
            hypothesis,
            config={"strategy_family": "legacy"},
            strategy_family="ri",
        )


def test_append_record_with_strategy_family_accepts_semantically_valid_declared_config(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0011",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-18T16:06:00+00:00",
        title="Valid RI hypothesis",
        hypothesis="Explicit family should accept semantically valid matching config.",
    )

    appended = service.append_record_with_strategy_family(
        hypothesis,
        config={
            "strategy_family": "ri",
            "thresholds": {
                "entry_conf_overall": 0.25,
                "regime_proba": {"balanced": 0.36},
                "signal_adaptation": {
                    "atr_period": 14,
                    "zones": {
                        "low": {"entry_conf_overall": 0.16, "regime_proba": 0.33},
                        "mid": {"entry_conf_overall": 0.40, "regime_proba": 0.51},
                        "high": {"entry_conf_overall": 0.32, "regime_proba": 0.57},
                    },
                },
            },
            "gates": {"hysteresis_steps": 3, "cooldown_bars": 2},
            "multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}},
        },
        strategy_family="ri",
    )

    assert appended.metadata["strategy_family"] == "ri"


def test_append_record_with_strategy_family_rejects_semantically_invalid_declared_config(
    tmp_path: Path,
) -> None:
    service = _service(tmp_path)
    hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0012",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-18T16:07:00+00:00",
        title="Invalid RI hypothesis",
        hypothesis="Explicit family should reject invalid declared RI configs.",
    )

    with pytest.raises(StrategyFamilyValidationError, match="ri_requires_canonical_gates"):
        service.append_record_with_strategy_family(
            hypothesis,
            config={
                "strategy_family": "ri",
                "thresholds": {
                    "entry_conf_overall": 0.25,
                    "regime_proba": {"balanced": 0.36},
                    "signal_adaptation": {
                        "atr_period": 14,
                        "zones": {
                            "low": {"entry_conf_overall": 0.16, "regime_proba": 0.33},
                            "mid": {"entry_conf_overall": 0.40, "regime_proba": 0.51},
                            "high": {"entry_conf_overall": 0.32, "regime_proba": 0.57},
                        },
                    },
                },
                "gates": {"hysteresis_steps": 2, "cooldown_bars": 0},
                "multi_timeframe": {"regime_intelligence": {"authority_mode": "regime_module"}},
            },
            strategy_family="ri",
        )


def test_allocate_id_is_storage_state_deterministic(tmp_path: Path) -> None:
    service = _service(tmp_path)

    assert service.allocate_id(LedgerEntityType.HYPOTHESIS, year=2026) == "HYP-2026-0001"
    service.append_hypothesis(
        HypothesisRecord(
            entity_id="HYP-2026-0001",
            entity_type=LedgerEntityType.HYPOTHESIS,
            created_at="2026-03-16T12:00:00+00:00",
            title="First",
            hypothesis="First",
        )
    )
    assert service.allocate_id(LedgerEntityType.HYPOTHESIS, year=2026) == "HYP-2026-0002"


def test_append_experiment_rejects_missing_hypothesis_reference(tmp_path: Path) -> None:
    service = _service(tmp_path)

    with pytest.raises(LedgerValidationError, match="missing hypothesis"):
        service.append_experiment(_experiment_record())


def test_append_experiment_rejects_missing_proposal_reference(tmp_path: Path) -> None:
    service = _service(tmp_path)
    hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0001",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="Hypothesis",
        hypothesis="Hypothesis",
    )

    service.append_hypothesis(hypothesis)

    with pytest.raises(LedgerValidationError, match="missing proposal"):
        service.append_experiment(_experiment_record(hypothesis_id=hypothesis.entity_id))


def test_append_experiment_rejects_mismatched_proposal_hypothesis(tmp_path: Path) -> None:
    service = _service(tmp_path)
    first_hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0001",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="First hypothesis",
        hypothesis="First hypothesis",
    )
    second_hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0002",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:01:00+00:00",
        title="Second hypothesis",
        hypothesis="Second hypothesis",
    )
    proposal = ProposalRecord(
        entity_id="PROP-2026-0001",
        entity_type=LedgerEntityType.PROPOSAL,
        created_at="2026-03-16T12:05:00+00:00",
        hypothesis_id=first_hypothesis.entity_id,
        title="Proposal",
        summary="Proposal",
        command_packet_path="docs/governance/templates/command_packet.md",
    )

    service.append_hypothesis(first_hypothesis)
    service.append_hypothesis(second_hypothesis)
    service.append_proposal(proposal)

    with pytest.raises(LedgerValidationError, match="must match the referenced proposal"):
        service.append_experiment(
            _experiment_record(
                hypothesis_id=second_hypothesis.entity_id,
                proposal_id=proposal.entity_id,
            )
        )


def test_append_experiment_rejects_missing_artifact_reference(tmp_path: Path) -> None:
    service = _service(tmp_path)
    hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0001",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="Hypothesis",
        hypothesis="Hypothesis",
    )
    proposal = ProposalRecord(
        entity_id="PROP-2026-0001",
        entity_type=LedgerEntityType.PROPOSAL,
        created_at="2026-03-16T12:05:00+00:00",
        hypothesis_id=hypothesis.entity_id,
        title="Proposal",
        summary="Proposal",
        command_packet_path="docs/governance/templates/command_packet.md",
    )

    service.append_hypothesis(hypothesis)
    service.append_proposal(proposal)

    with pytest.raises(LedgerValidationError, match="missing artifact"):
        service.append_experiment(
            _experiment_record(
                hypothesis_id=hypothesis.entity_id,
                proposal_id=proposal.entity_id,
                artifact_links=(ArtifactLink(artifact_id="ART-2026-0001"),),
            )
        )


def test_append_experiment_accepts_semantically_valid_traceable_record(tmp_path: Path) -> None:
    service = _service(tmp_path)
    hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0001",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="Hypothesis",
        hypothesis="Hypothesis",
    )
    proposal = ProposalRecord(
        entity_id="PROP-2026-0001",
        entity_type=LedgerEntityType.PROPOSAL,
        created_at="2026-03-16T12:05:00+00:00",
        hypothesis_id=hypothesis.entity_id,
        title="Proposal",
        summary="Proposal",
        command_packet_path="docs/governance/templates/command_packet.md",
    )

    service.append_hypothesis(hypothesis)
    service.append_proposal(proposal)
    experiment = service.append_experiment(
        _experiment_record(
            hypothesis_id=hypothesis.entity_id,
            proposal_id=proposal.entity_id,
        )
    )

    assert experiment.entity_id == "EXP-2026-0001"


def test_append_experiment_duplicate_id_wins_before_semantic_checks(tmp_path: Path) -> None:
    service = _service(tmp_path)
    hypothesis = HypothesisRecord(
        entity_id="HYP-2026-0001",
        entity_type=LedgerEntityType.HYPOTHESIS,
        created_at="2026-03-16T12:00:00+00:00",
        title="Hypothesis",
        hypothesis="Hypothesis",
    )
    proposal = ProposalRecord(
        entity_id="PROP-2026-0001",
        entity_type=LedgerEntityType.PROPOSAL,
        created_at="2026-03-16T12:05:00+00:00",
        hypothesis_id=hypothesis.entity_id,
        title="Proposal",
        summary="Proposal",
        command_packet_path="docs/governance/templates/command_packet.md",
    )
    valid_experiment = _experiment_record(
        hypothesis_id=hypothesis.entity_id,
        proposal_id=proposal.entity_id,
    )
    semantically_invalid_duplicate = replace(
        valid_experiment,
        hypothesis_id="HYP-2026-9999",
    )

    service.append_hypothesis(hypothesis)
    service.append_proposal(proposal)
    service.append_experiment(valid_experiment)

    with pytest.raises(FileExistsError, match=valid_experiment.entity_id):
        service.append_experiment(semantically_invalid_duplicate)
