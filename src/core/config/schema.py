from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class SignalAdaptationZone(BaseModel):
    entry_conf_overall: float
    regime_proba: dict[str, float]
    pct: float | None = None

    @field_validator("regime_proba")
    @classmethod
    def _validate_regime(cls, v: dict[str, float]) -> dict[str, float]:
        out: dict[str, float] = {}
        for k, val in (v or {}).items():
            out[str(k)] = float(val)
        return out


class SignalAdaptationConfig(BaseModel):
    atr_period: int = Field(default=14, ge=1, le=200)
    zones: dict[str, SignalAdaptationZone]


class Thresholds(BaseModel):
    entry_conf_overall: float = Field(ge=0.0, le=1.0, default=0.7)
    regime_proba: dict[str, float] = Field(default_factory=lambda: {"balanced": 0.58})
    signal_adaptation: SignalAdaptationConfig | None = None
    min_edge: float | None = Field(default=None)

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
        for item in v or []:
            thr, sz = (float(item[0]), float(item[1]))
            out.append((thr, sz))
        return out


class EV(BaseModel):
    R_default: float = Field(default=1.8)


class ExitLogic(BaseModel):
    """Exit configuration for backtest and live trading."""

    enabled: bool = Field(default=True, description="Enable exit logic")
    max_hold_bars: int = Field(default=20, ge=1, description="Max bars to hold position")
    stop_loss_pct: float = Field(default=0.02, ge=0.0, le=1.0, description="Stop loss %")
    take_profit_pct: float = Field(default=0.05, ge=0.0, le=1.0, description="Take profit %")
    exit_conf_threshold: float = Field(
        default=0.45, ge=0.0, le=1.0, description="Close if confidence drops below"
    )
    regime_aware_exits: bool = Field(
        default=True, description="Close on regime change (e.g., SHORT in BULL)"
    )
    trailing_stop_enabled: bool = Field(default=False, description="Enable trailing stop-loss")
    trailing_stop_pct: float = Field(
        default=0.015, ge=0.0, le=1.0, description="Trailing stop distance %"
    )


class LTFOverrideAdaptiveConfig(BaseModel):
    enabled: bool = Field(default=False)
    window: int = Field(default=120, ge=5, le=2000)
    percentile: float = Field(default=0.85, ge=0.0, le=1.0)
    min_history: int = Field(default=30, ge=1, le=2000)
    min_floor: float | None = Field(default=None)
    max_ceiling: float | None = Field(default=None)
    fallback_threshold: float | None = Field(default=None)
    regime_multipliers: dict[str, float] = Field(default_factory=dict)


class MultiTimeframeConfig(BaseModel):
    use_htf_block: bool = Field(default=True)
    allow_ltf_override: bool = Field(default=False)
    ltf_override_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    ltf_override_adaptive: LTFOverrideAdaptiveConfig = Field(
        default_factory=LTFOverrideAdaptiveConfig
    )


class FibOverrideConfidence(BaseModel):
    enabled: bool = Field(default=False)
    min: float | None = Field(default=None)
    max: float | None = Field(default=None)


class FibEntryConfig(BaseModel):
    enabled: bool = Field(default=False)
    tolerance_atr: float = Field(default=0.5, ge=0.0)
    targets: list[float] | None = None
    long_target_levels: list[float] | None = None
    short_target_levels: list[float] | None = None
    long_max_level: float | None = None
    long_min_level: float | None = None
    short_min_level: float | None = None
    short_max_level: float | None = None
    missing_policy: str | None = None
    override_confidence: FibOverrideConfidence | None = None

    @field_validator("targets", "long_target_levels", "short_target_levels", mode="before")
    @classmethod
    def _coerce_float_list(cls, v: Any) -> list[float] | None:
        if v is None:
            return None
        if isinstance(v, list | tuple):
            out: list[float] = []
            for item in v:
                try:
                    out.append(float(item))
                except (TypeError, ValueError):
                    continue
            return out
        return v


class FibExitConfig(BaseModel):
    enabled: bool = Field(default=False)
    fib_threshold_atr: float | None = Field(default=None, ge=0.0)
    trail_atr_multiplier: float | None = Field(default=None, ge=0.0)


class FibConfig(BaseModel):
    entry: FibEntryConfig | None = None
    exit: FibExitConfig | None = None


class HTFExitConfig(BaseModel):
    enable_partials: bool = Field(default=True)
    enable_trailing: bool = Field(default=True)
    enable_structure_breaks: bool = Field(default=True)
    partial_1_pct: float = Field(default=0.4, ge=0.0, le=1.0)
    partial_2_pct: float = Field(default=0.3, ge=0.0, le=1.0)
    fib_threshold_atr: float = Field(default=0.3, ge=0.0)
    trail_atr_multiplier: float = Field(default=1.3, ge=0.0)
    swing_update_strategy: str = Field(default="fixed")


class RuntimeConfig(BaseModel):
    thresholds: Thresholds = Field(default_factory=Thresholds)
    gates: Gates = Field(default_factory=Gates)
    risk: Risk = Field(default_factory=Risk)
    ev: EV = Field(default_factory=EV)
    exit: ExitLogic = Field(default_factory=ExitLogic)
    multi_timeframe: MultiTimeframeConfig = Field(default_factory=MultiTimeframeConfig)
    warmup_bars: int | None = Field(default=None, ge=0)
    htf_exit_config: HTFExitConfig | None = None
    htf_fib: FibConfig | None = None
    ltf_fib: FibConfig | None = None

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
