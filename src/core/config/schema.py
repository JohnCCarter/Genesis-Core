from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class Thresholds(BaseModel):
    entry_conf_overall: float = Field(ge=0.0, le=1.0, default=0.7)
    regime_proba: dict[str, float] = Field(default_factory=lambda: {"balanced": 0.58})

    @field_validator("regime_proba")
    @classmethod
    def _validate_regime(cls, v: dict[str, float]) -> dict[str, float]:
        out: dict[str, float] = {}
        for k, val in (v or {}).items():
            out[str(k)] = float(val)
        return out


class Gates(BaseModel):
    hysteresis_steps: int = Field(default=2, ge=0)
    cooldown_bars: int = Field(default=0, ge=0)


class Risk(BaseModel):
    risk_map: list[tuple[float, float]] = Field(
        default_factory=lambda: [(0.6, 0.005), (0.7, 0.008), (0.8, 0.01), (0.9, 0.012)]
    )

    @field_validator("risk_map")
    @classmethod
    def _validate_risk_map(cls, v: Any) -> list[tuple[float, float]]:
        out: list[tuple[float, float]] = []
        for item in (v or []):
            thr, sz = (float(item[0]), float(item[1]))
            out.append((thr, sz))
        return out


class EV(BaseModel):
    R_default: float = Field(default=1.8)


class RuntimeConfig(BaseModel):
    thresholds: Thresholds = Field(default_factory=Thresholds)
    gates: Gates = Field(default_factory=Gates)
    risk: Risk = Field(default_factory=Risk)
    ev: EV = Field(default_factory=EV)

    def model_dump_canonical(self) -> dict[str, Any]:
        """Dump in a stable, hash-friendly form (tuples → lists)."""
        data = self.model_dump(mode="json")
        # Ensure risk_map is list[list]
        rm = data.get("risk", {}).get("risk_map")
        if isinstance(rm, list):
            data["risk"]["risk_map"] = [[float(a), float(b)] for a, b in rm]
        return data


class RuntimeSnapshot(BaseModel):
    version: int
    hash: str
    cfg: RuntimeConfig


