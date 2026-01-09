from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class RuntimeSection(BaseModel):
    model_config = ConfigDict(extra="allow")


class SignalAdaptationZone(RuntimeSection):
    entry_conf_overall: float
    # Backwards compatible: older Optuna/backtest configs used a scalar (e.g. 0.45) here.
    # The decision logic supports both scalar and per-regime dict thresholds.
    regime_proba: dict[str, float] | float
    pct: float | None = None

    @field_validator("regime_proba", mode="before")
    @classmethod
    def _validate_regime(cls, v: Any) -> dict[str, float] | float:
        if v is None:
            return {}
        if isinstance(v, float | int):
            return float(v)
        if isinstance(v, dict):
            out: dict[str, float] = {}
            for k, val in (v or {}).items():
                out[str(k)] = float(val)
            return out
        raise TypeError("regime_proba must be a dict[str, float] or a float")


class SignalAdaptationConfig(RuntimeSection):
    atr_period: int = Field(default=14, ge=1, le=200)
    zones: dict[str, SignalAdaptationZone]


class Thresholds(RuntimeSection):
    entry_conf_overall: float = Field(ge=0.0, le=1.0, default=0.7)
    # Backwards compatible: some configs use a scalar proba threshold.
    regime_proba: dict[str, float] | float = Field(default_factory=lambda: {"balanced": 0.58})
    signal_adaptation: SignalAdaptationConfig | None = None
    min_edge: float | None = Field(default=None)

    @field_validator("regime_proba", mode="before")
    @classmethod
    def _validate_regime(cls, v: Any) -> dict[str, float] | float:
        if v is None:
            return {"balanced": 0.58}
        if isinstance(v, float | int):
            return float(v)
        if isinstance(v, dict):
            out: dict[str, float] = {}
            for k, val in (v or {}).items():
                out[str(k)] = float(val)
            return out
        raise TypeError("regime_proba must be a dict[str, float] or a float")


class Gates(RuntimeSection):
    hysteresis_steps: int = Field(default=2, ge=0)
    cooldown_bars: int = Field(default=0, ge=0)


class Risk(RuntimeSection):
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


class EV(RuntimeSection):
    R_default: float = Field(default=1.8)


class ExitLogic(RuntimeSection):
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


class LTFOverrideAdaptiveConfig(RuntimeSection):
    enabled: bool = Field(default=False)
    window: int = Field(default=120, ge=5, le=2000)
    percentile: float = Field(default=0.85, ge=0.0, le=1.0)
    min_history: int = Field(default=30, ge=1, le=2000)
    min_floor: float | None = Field(default=None)
    max_ceiling: float | None = Field(default=None)
    fallback_threshold: float | None = Field(default=None)
    regime_multipliers: dict[str, float] = Field(default_factory=dict)


class HTFSelectorRule(RuntimeSection):
    timeframe: str | None = None
    multiplier: float | None = Field(default=None, gt=0)


class HTFSelectorConfig(RuntimeSection):
    mode: str = Field(default="fixed")
    default_timeframe: str | None = None
    default_multiplier: float | None = Field(default=None, gt=0)
    fallback_timeframe: str | None = None
    per_timeframe: dict[str, HTFSelectorRule] = Field(default_factory=dict)


class MultiTimeframeConfig(RuntimeSection):
    use_htf_block: bool = Field(default=True)
    allow_ltf_override: bool = Field(default=False)
    ltf_override_threshold: float = Field(default=0.85, ge=0.0, le=1.0)
    ltf_override_adaptive: LTFOverrideAdaptiveConfig = Field(
        default_factory=LTFOverrideAdaptiveConfig
    )
    htf_selector: HTFSelectorConfig = Field(default_factory=HTFSelectorConfig)


class FeaturePercentileRange(RuntimeSection):
    low: float
    high: float

    @model_validator(mode="before")
    @classmethod
    def _from_sequence(cls, value: Any) -> dict[str, float] | Any:
        if isinstance(value, list | tuple) and len(value) == 2:
            return {"low": value[0], "high": value[1]}
        return value

    @field_validator("low", "high")
    @classmethod
    def _coerce(cls, v: Any) -> float:
        return float(v)


class FeaturesConfig(RuntimeSection):
    percentiles: dict[str, FeaturePercentileRange] = Field(default_factory=dict)
    versions: dict[str, Any] = Field(default_factory=dict)


class FibOverrideConfidence(RuntimeSection):
    enabled: bool = Field(default=False)
    min: float | None = Field(default=None)
    max: float | None = Field(default=None)


class FibEntryConfig(RuntimeSection):
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


class FibExitConfig(RuntimeSection):
    enabled: bool = Field(default=False)
    fib_threshold_atr: float | None = Field(default=None, ge=0.0)
    trail_atr_multiplier: float | None = Field(default=None, ge=0.0)


class FibConfig(RuntimeSection):
    entry: FibEntryConfig | None = None
    exit: FibExitConfig | None = None


class HTFExitConfig(RuntimeSection):
    enable_partials: bool = Field(default=True)
    enable_trailing: bool = Field(default=True)
    enable_structure_breaks: bool = Field(default=True)
    partial_1_pct: float = Field(default=0.4, ge=0.0, le=1.0)
    partial_2_pct: float = Field(default=0.3, ge=0.0, le=1.0)
    fib_threshold_atr: float = Field(default=0.3, ge=0.0)
    trail_atr_multiplier: float = Field(default=1.3, ge=0.0)
    swing_update_strategy: str = Field(default="fixed")


class RuntimeConfig(RuntimeSection):
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
    features: FeaturesConfig | None = None

    def model_dump_canonical(self) -> dict[str, Any]:
        """Dump in a stable, hash-friendly form (tuples → lists)."""
        data = self.model_dump(mode="json")
        # Ensure risk_map is list[list]
        rm = data.get("risk", {}).get("risk_map")
        if isinstance(rm, list):
            data["risk"]["risk_map"] = [[float(a), float(b)] for a, b in rm]
        feats_cfg = data.get("features")
        if isinstance(feats_cfg, dict):
            pct = feats_cfg.get("percentiles")
            if isinstance(pct, dict):
                feats_cfg["percentiles"] = {
                    key: [
                        float((rng or {}).get("low", 0.0)),
                        float((rng or {}).get("high", 0.0)),
                    ]
                    for key, rng in pct.items()
                    if isinstance(rng, dict)
                }
        return data


class RuntimeSnapshot(BaseModel):
    version: int
    hash: str
    cfg: RuntimeConfig
