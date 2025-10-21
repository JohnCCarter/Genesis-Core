"""Optimizer utilities (runner, scoring, champion management)."""

from .champion import ChampionCandidate, ChampionManager, ChampionRecord

__all__ = [
    "ChampionCandidate",
    "ChampionManager",
    "ChampionRecord",
]
