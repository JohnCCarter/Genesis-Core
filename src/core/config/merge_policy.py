from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ChampionMergeDecision(StrEnum):
    """Decision for whether champion config should be merged."""

    MERGE_CHAMPION = "merge_champion"
    BYPASS_CHAMPION = "bypass_champion"


class ChampionMergeReason(StrEnum):
    """Reason code for champion merge decisions."""

    EVALUATE_GLOBAL_INDEX = "evaluate_global_index_present"
    ENGINE_META_SKIP = "engine_meta_skip_champion_merge"
    DEFAULT_MERGE = "default_merge_champion"


@dataclass(frozen=True)
class ChampionMergeResolution:
    """Pure decision result for champion merge behavior."""

    decision: ChampionMergeDecision
    reason: ChampionMergeReason

    @property
    def should_merge(self) -> bool:
        return self.decision is ChampionMergeDecision.MERGE_CHAMPION


class RuntimeMergeDecision(StrEnum):
    """Decision for runtime merge behavior in backtest runner."""

    USE_RUNTIME_MERGE = "use_runtime_merge"
    USE_MERGED_CONFIG = "use_merged_config"


class RuntimeMergeReason(StrEnum):
    """Reason code for runtime merge decisions."""

    MERGED_CONFIG_PRESENT = "merged_config_present"
    MERGED_CONFIG_ABSENT = "merged_config_absent"


@dataclass(frozen=True)
class RuntimeMergeResolution:
    """Pure decision result for runtime merge behavior."""

    decision: RuntimeMergeDecision
    reason: RuntimeMergeReason

    @property
    def use_runtime_merge(self) -> bool:
        return self.decision is RuntimeMergeDecision.USE_RUNTIME_MERGE


def resolve_champion_merge_decision(
    *,
    has_global_index: bool,
    skip_champion_merge: bool,
) -> ChampionMergeResolution:
    """Resolve champion merge decision from existing external trigger channels."""

    if has_global_index:
        return ChampionMergeResolution(
            decision=ChampionMergeDecision.BYPASS_CHAMPION,
            reason=ChampionMergeReason.EVALUATE_GLOBAL_INDEX,
        )
    if skip_champion_merge:
        return ChampionMergeResolution(
            decision=ChampionMergeDecision.BYPASS_CHAMPION,
            reason=ChampionMergeReason.ENGINE_META_SKIP,
        )
    return ChampionMergeResolution(
        decision=ChampionMergeDecision.MERGE_CHAMPION,
        reason=ChampionMergeReason.DEFAULT_MERGE,
    )


def resolve_champion_merge_for_evaluate(
    configs: Mapping[str, Any] | None,
) -> ChampionMergeResolution:
    """Evaluate path trigger: `_global_index` key presence."""

    has_global_index = isinstance(configs, Mapping) and "_global_index" in configs
    return resolve_champion_merge_decision(
        has_global_index=has_global_index,
        skip_champion_merge=False,
    )


def resolve_champion_merge_for_engine(meta: Mapping[str, Any] | None) -> ChampionMergeResolution:
    """Backtest engine trigger: `meta.skip_champion_merge` truthiness."""

    should_skip = bool(meta.get("skip_champion_merge")) if isinstance(meta, Mapping) else False
    return resolve_champion_merge_decision(
        has_global_index=False,
        skip_champion_merge=should_skip,
    )


def resolve_runtime_merge_decision(*, has_merged_config: bool) -> RuntimeMergeResolution:
    """Resolve runtime-vs-merged-config decision for run_backtest."""

    if has_merged_config:
        return RuntimeMergeResolution(
            decision=RuntimeMergeDecision.USE_MERGED_CONFIG,
            reason=RuntimeMergeReason.MERGED_CONFIG_PRESENT,
        )
    return RuntimeMergeResolution(
        decision=RuntimeMergeDecision.USE_RUNTIME_MERGE,
        reason=RuntimeMergeReason.MERGED_CONFIG_ABSENT,
    )
