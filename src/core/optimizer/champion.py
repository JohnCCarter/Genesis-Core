"""Champion-hantering för optimeringskörningar."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

JsonDict = dict[str, Any]


@dataclass(slots=True)
class ChampionCandidate:
    parameters: JsonDict
    score: float
    metrics: JsonDict
    constraints_ok: bool
    constraints: JsonDict
    hard_failures: list[str]
    trial_id: str
    results_path: str
    merged_config: JsonDict | None = None  # Full merged config for reproducibility


@dataclass(slots=True)
class ChampionRecord:
    created_at: str
    run_id: str
    git_commit: str
    snapshot_id: str
    symbol: str
    timeframe: str
    score: float
    metrics: JsonDict
    parameters: JsonDict
    constraints: JsonDict
    metadata: JsonDict
    merged_config: JsonDict | None = None  # Full merged config for reproducibility
    runtime_version: int | None = None  # Runtime version used during optimization

    def to_json(self) -> str:
        payload = {
            "created_at": self.created_at,
            "run_id": self.run_id,
            "git_commit": self.git_commit,
            "snapshot_id": self.snapshot_id,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "score": self.score,
            "metrics": self.metrics,
            "parameters": self.parameters,
            "constraints": self.constraints,
            "metadata": self.metadata,
        }
        if self.merged_config is not None:
            payload["merged_config"] = self.merged_config
        if self.runtime_version is not None:
            payload["runtime_version"] = self.runtime_version
        return json.dumps(payload, indent=2)


class ChampionManager:
    """Ansvarar för att läsa/skapa champion-filer med backup."""

    def __init__(self, champions_dir: Path | None = None) -> None:
        # Default ska peka på repo-roten, inte under src/.
        # Vi försöker hitta pyproject.toml uppåt i trädet för robusthet.
        resolved = Path(__file__).resolve()
        repo_root: Path | None = None
        for parent in resolved.parents:
            if (parent / "pyproject.toml").exists():
                repo_root = parent
                break
        if repo_root is None:
            # Fallback: .../src/core/optimizer/champion.py -> repo root är normalt parents[3]
            repo_root = resolved.parents[3]

        self.champions_dir = champions_dir or (repo_root / "config" / "strategy" / "champions")
        self.champions_dir.mkdir(parents=True, exist_ok=True)

    def _champion_path(self, symbol: str, timeframe: str) -> Path:
        fname = f"{symbol}_{timeframe}.json"
        return self.champions_dir / fname

    def _backup_path(self, symbol: str, timeframe: str, timestamp: str) -> Path:
        fname = f"{symbol}_{timeframe}_{timestamp}.json"
        backup_dir = self.champions_dir / "backup"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return backup_dir / fname

    def load_current(self, symbol: str, timeframe: str) -> ChampionRecord | None:
        path = self._champion_path(symbol, timeframe)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return None
            return ChampionRecord(
                created_at=str(data.get("created_at", "")),
                run_id=str(data.get("run_id", "")),
                git_commit=str(data.get("git_commit", "")),
                snapshot_id=str(data.get("snapshot_id", "")),
                symbol=str(data.get("symbol", symbol)),
                timeframe=str(data.get("timeframe", timeframe)),
                score=float(data.get("score", 0.0)),
                metrics=dict(data.get("metrics") or {}),
                parameters=dict(data.get("parameters") or {}),
                constraints=dict(data.get("constraints") or {}),
                metadata=dict(data.get("metadata") or {}),
            )
        except Exception:
            return None

    def should_replace(self, current: ChampionRecord | None, candidate: ChampionCandidate) -> bool:
        if not candidate.constraints_ok or candidate.hard_failures:
            return False
        if current is None:
            return True
        return candidate.score > current.score

    def write_champion(
        self,
        *,
        symbol: str,
        timeframe: str,
        candidate: ChampionCandidate,
        run_id: str,
        git_commit: str,
        snapshot_id: str,
        run_meta: dict[str, Any] | None = None,
        runtime_version: int | None = None,
    ) -> ChampionRecord:
        path = self._champion_path(symbol, timeframe)
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        if path.exists():
            backup_path = self._backup_path(symbol, timeframe, timestamp)
            backup_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
        record = ChampionRecord(
            created_at=datetime.now(UTC).isoformat(),
            run_id=run_id,
            git_commit=git_commit,
            snapshot_id=snapshot_id,
            symbol=symbol,
            timeframe=timeframe,
            score=candidate.score,
            metrics=candidate.metrics,
            parameters=candidate.parameters,
            constraints={
                "hard_failures": candidate.hard_failures,
                "raw": candidate.constraints,
            },
            metadata={
                "trial_id": candidate.trial_id,
                "results_path": candidate.results_path,
                "run_meta": run_meta or {},
            },
            merged_config=candidate.merged_config,
            runtime_version=runtime_version,
        )
        path.write_text(record.to_json(), encoding="utf-8")
        return record
