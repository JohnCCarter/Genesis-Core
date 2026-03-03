from __future__ import annotations

import pytest

from core.config.merge_policy import (
    ChampionMergeDecision,
    ChampionMergeReason,
    RuntimeMergeDecision,
    RuntimeMergeReason,
    resolve_champion_merge_decision,
    resolve_champion_merge_for_engine,
    resolve_champion_merge_for_evaluate,
    resolve_runtime_merge_decision,
)


@pytest.mark.parametrize(
    ("has_global_index", "skip_champion_merge", "expected_decision", "expected_reason"),
    [
        (
            True,
            False,
            ChampionMergeDecision.BYPASS_CHAMPION,
            ChampionMergeReason.EVALUATE_GLOBAL_INDEX,
        ),
        (
            False,
            True,
            ChampionMergeDecision.BYPASS_CHAMPION,
            ChampionMergeReason.ENGINE_META_SKIP,
        ),
        (
            False,
            False,
            ChampionMergeDecision.MERGE_CHAMPION,
            ChampionMergeReason.DEFAULT_MERGE,
        ),
    ],
)
def test_resolve_champion_merge_decision_matrix(
    has_global_index: bool,
    skip_champion_merge: bool,
    expected_decision: ChampionMergeDecision,
    expected_reason: ChampionMergeReason,
) -> None:
    resolution = resolve_champion_merge_decision(
        has_global_index=has_global_index,
        skip_champion_merge=skip_champion_merge,
    )

    assert resolution.decision is expected_decision
    assert resolution.reason is expected_reason
    assert resolution.should_merge is (expected_decision is ChampionMergeDecision.MERGE_CHAMPION)


def test_resolve_champion_merge_for_evaluate_uses_global_index_key_presence() -> None:
    resolution = resolve_champion_merge_for_evaluate({"_global_index": None})

    assert resolution.decision is ChampionMergeDecision.BYPASS_CHAMPION
    assert resolution.reason is ChampionMergeReason.EVALUATE_GLOBAL_INDEX


def test_resolve_champion_merge_for_engine_uses_skip_meta_truthiness() -> None:
    resolution = resolve_champion_merge_for_engine({"skip_champion_merge": 1})

    assert resolution.decision is ChampionMergeDecision.BYPASS_CHAMPION
    assert resolution.reason is ChampionMergeReason.ENGINE_META_SKIP


@pytest.mark.parametrize(
    ("has_merged_config", "expected_decision", "expected_reason"),
    [
        (
            True,
            RuntimeMergeDecision.USE_MERGED_CONFIG,
            RuntimeMergeReason.MERGED_CONFIG_PRESENT,
        ),
        (
            False,
            RuntimeMergeDecision.USE_RUNTIME_MERGE,
            RuntimeMergeReason.MERGED_CONFIG_ABSENT,
        ),
    ],
)
def test_resolve_runtime_merge_decision_matrix(
    has_merged_config: bool,
    expected_decision: RuntimeMergeDecision,
    expected_reason: RuntimeMergeReason,
) -> None:
    resolution = resolve_runtime_merge_decision(has_merged_config=has_merged_config)

    assert resolution.decision is expected_decision
    assert resolution.reason is expected_reason
    assert resolution.use_runtime_merge is (
        expected_decision is RuntimeMergeDecision.USE_RUNTIME_MERGE
    )
