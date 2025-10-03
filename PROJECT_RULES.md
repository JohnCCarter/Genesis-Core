# Genesis-Core Project Rules

## Master Rules
- **Pause on Uncertainty**: Always verify with codebase_search + grep. No assumptions.
- **Planning Mode**: Always lay out steps before acting.
- **Tools Usage**: Use codebase_search and grep when uncertainty exists.
- **Persistence**: Continue until the task is complete.
- **Workflow**: Work step-by-step, systematically and methodically.
- **Reflection**: Stop at milestones, reflect on root cause vs symptom.
- **Context**: Communicate when context is insufficient.
- **Language**: Always respond in Swedish, unless otherwise specified.

## Code Standards

### Python Version & Style
- Target Python 3.11+
- Use modern type hints: `dict` not `Dict`, `list` not `List`, `X | None` not `Optional[X]`
- Line length: 100 characters
- Follow black formatting
- Follow ruff linting rules (E, W, F, I, B, C4, UP)

### Project Structure
```
Genesis-Core/
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
└── scripts/            # Utility scripts
```

### API & Exchange Rules
- **Paper Trading Only**: Always use TEST symbols (tTESTBTC:TESTUSD, etc.)
- **Whitelist Enforcement**: Only allow specific TEST-spot pairs
- **API Keys**: Load from .env file (BITFINEX_API_KEY, BITFINEX_API_SECRET)
- **Nonce Management**: Use centralized nonce_manager with file tracking
- **JSON Serialization**: Always use `json.dumps(body, separators=(",", ":"))` for signing

### Strategy Pipeline
1. **Feature Extraction** (P1): EMA delta percentage + RSI from candles
2. **Probability Model** (P2): predict_proba with calibration
3. **Confidence Calculation** (P3): Confidence scores based on probabilities
4. **Regime Classification** (P3): HTF regime detection (trend/range/balanced)
5. **Decision Making** (P3): Final trading decision with risk management
6. **E2E Pipeline** (P4): Complete evaluation flow with observability

### FastAPI Endpoints
- `/ui` - Trading dashboard interface
- `/strategy/evaluate` - Run complete strategy pipeline
- `/public/candles` - Fetch public market data
- `/auth/check` - Verify API authentication
- `/dev/overrides` - Development configuration overrides
- `/paper/submit` - Submit paper trading orders (TEST symbols only)
- `/debug/auth` - Debug authentication issues
- `/health` - Service health check
- `/metrics` - Prometheus metrics
- `/config/validate` - Validate configuration
- `/config/diff` - Compare configurations

## Development Workflow

### Before Making Changes
1. Read existing code with `read_file`
2. Search for related code with `codebase_search`
3. Verify patterns with `grep`
4. Create TODO list with `todo_write` for complex tasks

### When Making Changes
1. **Never output code blocks** - use edit tools instead
2. **Prefer editing existing files** over creating new ones
3. **Never create documentation files** unless explicitly requested
4. **Add all necessary imports** for code to run immediately
5. **Fix linter errors** if introduced (max 3 attempts)
6. **Backup files** if you are not sure about the changes

### Testing & Validation
1. Run tests before committing: `python -m pytest`
2. Check formatting: `python -m black --check src`
3. Check linting: `python -m ruff check src`
4. Security scan: `python -m bandit -r src`
5. Verify no secrets: `detect-secrets scan`

### Git Workflow
1. **Never commit sensitive files**: .env, .nonce_tracker.json, dev.overrides.local.json
2. **Use descriptive commit messages** with prefixes:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `security:` for security improvements
   - `sync:` for tool/config synchronization
   - `refactor:` for code restructuring
3. **Always update .gitignore** before adding sensitive configuration

## Security Rules

### Sensitive Data
- **Never expose API keys** in code or commits
- **Use environment variables** for all secrets
- **Redact sensitive data** in logs using logging_redaction
- **Force TEST symbols** for all paper trading operations

### Pre-commit Hooks
- black (code formatting)
- ruff (linting with fixes)
- bandit (security scanning)
- detect-secrets (prevent secret commits)
- check-added-large-files (prevent large files)
- check-merge-conflict (prevent conflict markers)
- check-yaml/json (validate configs)

## Error Handling

### Common Issues & Solutions
1. **"invalid key" error**: Check JSON serialization consistency between signing and request body
2. **"Ingen giltig order"**: Verify model exists for symbol/timeframe, check risk configuration
3. **Nonce errors**: Use bump_nonce() for retry, ensure proper nonce tracking
4. **WebSocket timeouts**: Implement exponential backoff with reconnection logic

### Debugging Steps
1. Check `/debug/auth` endpoint for authentication issues
2. Verify `/auth/check` returns success
3. Review `/metrics` for system state
4. Check logs with proper redaction

## Configuration Management

### Model Registry
- Models stored in `config/models/{symbol}_{timeframe}.json`
- Registry tracks all available models in `config/models/registry.json`
- Each model includes: weights, calibration, schema, version

### Risk Management
- Position sizing based on confidence and risk map
- Stop-loss and take-profit thresholds
- Maximum position limits
- Paper trading enforcement

### Development Overrides
- Local overrides in `dev.overrides.local.json` (gitignored)
- Example template in `dev.overrides.example.json`
- Override any configuration without modifying defaults

## Code Quality Standards

### Functions Should Be
- **Pure when possible**: No side effects, deterministic
- **Well-typed**: Complete type hints for all parameters and returns
- **Documented**: Clear docstrings explaining purpose and usage
- **Tested**: Unit tests for business logic, integration tests for IO

### Avoid
- Global state except for singletons (metrics, settings)
- Mutable default arguments
- Broad exception catching without logging
- Hardcoded values - use configuration
- Direct file IO in business logic

## Response Format

### When Reporting Progress
- Use Swedish language
- Structure with clear headings
- List completed items with ✅
- Show current status
- Explain next steps if any

### When Encountering Issues
- Explain the problem clearly
- Show relevant error messages
- Propose solution options
- Ask for clarification if needed

## Project-Specific Context

### Current State (as of October 2025)
- P1-P3 features complete: feature extraction, probability model, confidence/regime/decision
- P4 E2E pipeline with observability implemented
- All major endpoints functional
- Paper trading restricted to TEST symbols
- Comprehensive test coverage
- Security hardening completed (no .env in git history)

### Technology Stack
- Python 3.11+
- FastAPI for REST API
- httpx for HTTP client
- websockets for real-time data
- pydantic for validation
- pytest for testing
- black/ruff for code quality
- bandit/detect-secrets for security

### Integration Points
- Bitfinex REST API v2 for trading
- Bitfinex WebSocket API for real-time data
- Prometheus metrics format
- JSON configuration with schema validation

## Remember
- **Quality over speed**: Take time to do things right
- **Security first**: Never compromise on security
- **Test everything**: Untested code is broken code
- **Document decisions**: Explain why, not just what
- **Stay systematic**: Follow the workflow consistently
