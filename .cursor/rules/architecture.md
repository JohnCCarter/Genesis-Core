# Genesis-Core Architecture & Reference

This document contains architectural details, system design, and reference material for the Genesis-Core trading system.

## Project Structure

```
Genesis-Core/
├── .cursor/            # Editor rules for this repo (Cursor)
├── .github/
│   ├── agents/         # Repo-local chat agents (bounded roles)
│   └── skills/         # Skill definitions used by repo governance
├── registry/           # Repo governance registry (manifests/schemas/compacts/audit)
├── docs/               # Documentation, runbooks, and reference material
├── data/               # Market data (raw/curated/metadata)
├── results/            # Backtests, evaluations, and optimizer artifacts
├── reports/            # Benchmarks, profiling outputs, and audits
├── mcp_server/         # MCP server (local/remote ops integration)
├── src/core/           # Main application code
│   ├── config/         # Configuration and validation
│   ├── indicators/     # Technical indicators (EMA, RSI, ADX, ATR)
│   ├── io/bitfinex/    # Exchange integration
│   ├── observability/  # Metrics and monitoring
│   ├── risk/           # Risk management
│   ├── strategy/       # Trading strategy modules
│   └── utils/          # Utilities (nonce, logging, backoff)
├── tests/              # Test files
├── config/             # Configuration files
│   ├── models/         # Model configurations and registry
│   └── strategy/       # Strategy defaults
├── scripts/            # Utility scripts
├── tools/              # Helper tooling and misc utilities
├── cache/              # Precomputed caches (may be large)
├── logs/               # Local logs
└── tmp/                # Local scratch space
```

## Strategy Pipeline

1. **Feature Extraction** (P1): EMA delta percentage + RSI from candles
2. **Probability Model** (P2): predict_proba with calibration
3. **Confidence Calculation** (P3): Confidence scores based on probabilities
4. **Regime Classification** (P3): HTF regime detection (trend/range/balanced)
5. **Decision Making** (P3): Final trading decision with risk management
6. **E2E Pipeline** (P4): Complete evaluation flow with observability

## Configuration Management

### Model Registry

- Models stored in `config/models/{symbol}_{timeframe}.json`
- Registry tracks all available models in `config/models/registry.json`
- Each model includes: weights, calibration, schema, version

Note: This model registry is separate from the repo governance registry under top-level `registry/`.

### Risk Management

- Position sizing based on confidence and risk map
- Stop-loss and take-profit thresholds
- Maximum position limits
- Paper trading enforcement

### Development Overrides

- Local overrides in `dev.overrides.local.json` (gitignored)
- Example template in `dev.overrides.example.json`
- Override any configuration without modifying defaults

## System Integration

### Bitfinex Integration

- **REST API v2**: For trading operations.
- **WebSocket API**: For real-time data streaming.
- **Nonce Management**: Centralized `nonce_manager` with file tracking.
- **Serialization**: `json.dumps(body, separators=(",", ":"))` for signing.

### Observability

- **Prometheus Metrics**: Exposes system state and pipeline performance.
- **Logging**: Redacted logging for security.

## FastAPI Endpoints Reference

- `/ui` - Trading dashboard interface
- `/strategy/evaluate` - Run complete strategy pipeline
- `/public/candles` - Fetch public market data
- `/auth/check` - Verify API authentication
- `/paper/submit` - Submit paper trading orders (TEST symbols only)
- `/debug/auth` - Debug authentication issues
- `/health` - Service health check
- `/metrics` - Prometheus metrics
- `/account/wallets` - Exchange wallets (proxy)
- `/account/positions` - Active positions (proxy, TEST)
- `/account/orders` - Open orders (proxy, TEST)
- `/config/runtime` - Get SSOT config
- `/config/runtime/validate` - Validate SSOT config
- `/config/runtime/propose` - Propose SSOT changes (Bearer)

## Troubleshooting Guide

### Common Issues

1. **"invalid key" error**: Check JSON serialization consistency between signing and request body.
2. **"Ingen giltig order"**: Verify model exists for symbol/timeframe, check risk configuration.
3. **Nonce errors**: Use `bump_nonce()` for retry, ensure proper nonce tracking.
4. **WebSocket timeouts**: Implement exponential backoff with reconnection logic.

### Debugging Steps

1. Check `/debug/auth` endpoint for authentication issues.
2. Verify `/auth/check` returns success.
3. Review `/metrics` for system state.
4. Check logs with proper redaction.
