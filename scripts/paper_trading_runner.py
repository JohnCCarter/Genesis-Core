#!/usr/bin/env python3
"""
Paper Trading Runner - Autotrade Loop for Genesis-Core Phase 3

Polls Bitfinex public candles, detects candle-close, evaluates strategy,
and submits paper orders based on signals.

Usage:
    python scripts/paper_trading_runner.py --dry-run                    # Safe mode (no orders)
    python scripts/paper_trading_runner.py --live-paper                 # Live paper trading

Features:
    - Idempotent candle processing (persistent state on disk)
    - Fail-closed on state corruption
    - Exactly 1 evaluation per candle-close
    - Exactly 1 order per signal (if --live-paper)
    - Heartbeat logging
    - Graceful shutdown (SIGTERM/SIGINT)

Safety:
    - Default: --dry-run (logs orders but doesn't submit)
    - Champion verification on startup (abort if baseline fallback)
    - Rate limiting (max 1 request per poll-interval)
    - Restart-safe (state persisted to disk)
"""

import argparse
import json
import logging
import os
import signal
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, UTC
from pathlib import Path

import httpx

# --- Configuration ---


@dataclass
class RunnerConfig:
    """Runner configuration."""

    host: str
    port: int
    symbol: str
    timeframe: str
    poll_interval: int
    dry_run: bool
    live_paper: bool
    log_dir: Path
    state_file: Path

    @property
    def api_base(self) -> str:
        return f"http://{self.host}:{self.port}"


def _safe_resolve(path: Path) -> Path:
    """Resolve path for guardrail checks without requiring path existence."""
    try:
        return path.expanduser().resolve()
    except Exception:
        return (Path.cwd() / path).resolve()


def _is_subpath(path: Path, root: Path) -> bool:
    """Return True if path is under root."""
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_live_paper_guardrails(config: RunnerConfig) -> list[str]:
    """Validate live-paper guardrails for mode and output path separation."""
    if not config.live_paper:
        return []

    issues: list[str] = []
    execution_mode = os.environ.get("GENESIS_EXECUTION_MODE", "").strip().lower()
    if execution_mode != "paper_live":
        issues.append("Live paper kräver GENESIS_EXECUTION_MODE=paper_live (fail-fast mode-gate).")

    results_root = _safe_resolve(Path("results"))
    paper_live_root = _safe_resolve(Path("results/paper_live"))
    forbidden_roots = [
        _safe_resolve(Path("results/hparam_search")),
        _safe_resolve(Path("results/backtests")),
    ]

    path_targets = {
        "log_dir": config.log_dir,
        "state_file_parent": config.state_file.parent,
    }

    for name, raw_path in path_targets.items():
        resolved = _safe_resolve(raw_path)

        for forbidden in forbidden_roots:
            if _is_subpath(resolved, forbidden):
                issues.append(
                    f"{name}={raw_path} är otillåten i live-paper (forbidden root: {forbidden})."
                )

        if _is_subpath(resolved, results_root) and not _is_subpath(resolved, paper_live_root):
            issues.append(
                f"{name}={raw_path} måste ligga under results/paper_live/** vid live-paper."
            )

    return issues


def enforce_live_paper_guardrails(
    config: RunnerConfig, logger: logging.Logger | None = None
) -> None:
    """Enforce live-paper guardrails; exits fail-closed on violations."""
    issues = validate_live_paper_guardrails(config)
    if not issues:
        return

    for issue in issues:
        msg = f"FATAL guardrail violation: {issue}"
        if logger is not None:
            logger.error(msg)
        else:
            print(msg, file=sys.stderr)
    raise SystemExit(1)


# --- State Management ---


@dataclass
class RunnerState:
    """Persistent runner state for idempotency."""

    last_processed_candle_ts: int | None = None  # Unix timestamp (ms)
    total_evaluations: int = 0
    total_orders_submitted: int = 0
    last_heartbeat: str | None = None
    pipeline_state: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "last_processed_candle_ts": self.last_processed_candle_ts,
            "total_evaluations": self.total_evaluations,
            "total_orders_submitted": self.total_orders_submitted,
            "last_heartbeat": self.last_heartbeat,
            "pipeline_state": self.pipeline_state,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RunnerState":
        return cls(
            last_processed_candle_ts=data.get("last_processed_candle_ts"),
            total_evaluations=data.get("total_evaluations", 0),
            total_orders_submitted=data.get("total_orders_submitted", 0),
            last_heartbeat=data.get("last_heartbeat"),
            pipeline_state=data.get("pipeline_state") or {},
        )


def load_state(state_file: Path, logger: logging.Logger) -> RunnerState:
    """Load state from disk. Fail-closed if corrupt."""
    if not state_file.exists():
        logger.info(f"State file not found: {state_file}. Starting fresh.")
        return RunnerState()

    try:
        with open(state_file) as f:
            data = json.load(f)
        state = RunnerState.from_dict(data)
        logger.info(
            f"Loaded state: last_candle_ts={state.last_processed_candle_ts}, "
            f"evaluations={state.total_evaluations}, orders={state.total_orders_submitted}"
        )
        return state
    except Exception as e:
        logger.error(f"FATAL: State file corrupt: {state_file}. Error: {e}")
        logger.error("Fail-closed: Cannot proceed with corrupt state.")
        sys.exit(1)


def save_state(state: RunnerState, state_file: Path, logger: logging.Logger) -> None:
    """Save state to disk atomically."""
    try:
        tmp_file = state_file.with_suffix(".tmp")
        with open(tmp_file, "w") as f:
            json.dump(state.to_dict(), f, indent=2)
        tmp_file.replace(state_file)
        logger.debug(f"State saved: {state_file}")
    except Exception as e:
        logger.error(f"Failed to save state: {e}")


# --- Candle Polling ---


def fetch_latest_candle(
    symbol: str, timeframe: str, client: httpx.Client, logger: logging.Logger
) -> dict | None:
    """Fetch latest closed candle from Bitfinex public API."""
    try:
        # Bitfinex candles endpoint: /v2/candles/trade:{timeframe}:{symbol}/hist
        url = f"https://api-pub.bitfinex.com/v2/candles/trade:{timeframe}:{symbol}/hist"
        params = {"limit": 2, "sort": -1}  # Last 2 candles, descending
        resp = client.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        candles = resp.json()

        if not isinstance(candles, list) or len(candles) < 2:
            logger.warning(f"Unexpected candles response: {candles}")
            return None

        # candles[0] = latest (may be forming)
        # candles[1] = previous closed candle
        latest = candles[0]
        previous = candles[1]

        # Check if latest candle is closed (compare timestamps)
        # A candle is closed if current time > candle_close_time
        now_ms = int(time.time() * 1000)
        latest_ts = int(latest[0])
        candle_duration_ms = _timeframe_to_ms(timeframe)
        latest_close_ms = latest_ts + candle_duration_ms

        # Determine which candle is closed (use consistent ts + OHLCV from same candle)
        if now_ms > latest_close_ms:
            # Latest is closed - use latest candle data
            selected_candle = latest
            source = "latest"
        else:
            # Latest is still forming - use previous closed candle
            selected_candle = previous
            source = "previous"

        closed_candle_ts = int(selected_candle[0])

        # Audit logging for determinism verification
        logger.debug(
            f"Candle selection: source={source}, ts={closed_candle_ts}, "
            f"now_ms={now_ms}, latest_ts={latest_ts}, latest_close_ms={latest_close_ms}"
        )

        return {
            "ts": closed_candle_ts,
            "open": float(selected_candle[1]),
            "close": float(selected_candle[2]),
            "high": float(selected_candle[3]),
            "low": float(selected_candle[4]),
            "volume": float(selected_candle[5]),
            "_source": source,  # Audit metadata
        }

    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching candles: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching candles: {e}")
        return None


def _timeframe_to_ms(timeframe: str) -> int:
    """Convert timeframe string to milliseconds."""
    mapping = {
        "1m": 60 * 1000,
        "5m": 5 * 60 * 1000,
        "15m": 15 * 60 * 1000,
        "1h": 60 * 60 * 1000,
        "4h": 4 * 60 * 60 * 1000,
        "1D": 24 * 60 * 60 * 1000,
    }
    return mapping.get(timeframe, 60 * 60 * 1000)  # Default 1h


# --- Strategy Evaluation ---


def evaluate_strategy(
    config: RunnerConfig,
    candle_ts_ms: int,
    state_in: dict,
    client: httpx.Client,
    logger: logging.Logger,
) -> dict | None:
    """POST to /strategy/evaluate and return response.

    IMPORTANT: We always include a real candles window so the server does not
    evaluate against its built-in dummy candles payload.
    """
    try:
        url = f"{config.api_base}/strategy/evaluate"
        end_ms = int(candle_ts_ms) + _timeframe_to_ms(config.timeframe) - 1
        candles = fetch_candles_window(
            symbol=config.symbol,
            timeframe=config.timeframe,
            end_ms=end_ms,
            client=client,
            logger=logger,
        )
        if not candles:
            return None

        payload = {
            "policy": {"symbol": config.symbol, "timeframe": config.timeframe},
            "candles": candles,
            "state": state_in or {},
        }
        resp = client.post(url, json=payload, timeout=30.0)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as e:
        logger.error(f"HTTP error evaluating strategy: {e}")
        return None
    except Exception as e:
        logger.error(f"Error evaluating strategy: {e}")
        return None


def verify_champion_loaded(eval_response: dict, logger: logging.Logger) -> bool:
    """Verify champion is loaded (not baseline fallback)."""
    champion_source = eval_response.get("meta", {}).get("champion", {}).get("source", "")
    if "champions" in champion_source:
        return True
    else:
        logger.error(f"Champion NOT loaded! Source: {champion_source}")
        logger.error("Baseline fallback detected. ABORTING.")
        return False


# --- Paper Order Submission ---


def submit_paper_order(
    config: RunnerConfig,
    action: str,
    eval_response: dict,
    client: httpx.Client,
    logger: logging.Logger,
) -> dict | None:
    """POST to /paper/submit and return response."""
    try:
        url = f"{config.api_base}/paper/submit"
        # Strategy returns size under meta.decision.size (base units, used by backtest engine)
        raw_size = (eval_response.get("meta", {}) or {}).get("decision", {}).get("size", 0.0)
        try:
            size = float(raw_size) if raw_size is not None else 0.0
        except (TypeError, ValueError):
            size = 0.0

        test_symbol = map_policy_symbol_to_test_symbol(config.symbol)

        payload = {
            "symbol": test_symbol,
            "side": str(action).upper(),  # LONG|SHORT
            "size": size,
            "type": "MARKET",
        }

        resp = client.post(url, json=payload, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, dict) or not data.get("ok"):
            logger.error(f"paper_submit returned ok=false: {data}")
            return None
        return data
    except httpx.HTTPError as e:
        logger.error(f"HTTP error submitting order: {e}")
        return None
    except Exception as e:
        logger.error(f"Error submitting order: {e}")
        return None


def fetch_candles_window(
    symbol: str,
    timeframe: str,
    end_ms: int,
    client: httpx.Client,
    logger: logging.Logger,
    limit: int = 120,
) -> dict | None:
    """Fetch a candles window from Bitfinex public API and normalize to {open,high,low,close,volume} arrays."""
    try:
        # IMPORTANT:
        # Bitfinex returns candles sorted by `sort`.
        # - sort=1  (ascending) + limit=N yields the *oldest* N candles in the range.
        # - sort=-1 (descending) + limit=N yields the *newest* N candles in the range.
        # We want the most recent window ending at `end_ms`, in chronological order.
        sort = -1
        url = f"https://api-pub.bitfinex.com/v2/candles/trade:{timeframe}:{symbol}/hist"
        params = {"limit": int(limit), "sort": int(sort), "end": int(end_ms)}
        resp = client.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()

        # Ensure we build arrays in chronological order (oldest -> newest).
        if sort == -1 and isinstance(data, list):
            data = list(reversed(data))

        if not isinstance(data, list) or not data:
            logger.error(f"Unexpected candles window response: {data}")
            return None

        opens: list[float] = []
        highs: list[float] = []
        lows: list[float] = []
        closes: list[float] = []
        volumes: list[float] = []

        for row in data:
            # Bitfinex format: [MTS, OPEN, CLOSE, HIGH, LOW, VOLUME]
            if isinstance(row, list) and len(row) >= 6:
                opens.append(float(row[1]))
                closes.append(float(row[2]))
                highs.append(float(row[3]))
                lows.append(float(row[4]))
                volumes.append(float(row[5]))

        if len(opens) < 2:
            logger.error(
                f"Insufficient candles window length={len(opens)} for {symbol} {timeframe}"
            )
            return None

        return {
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
        }
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching candles window: {e}")
        return None
    except Exception as e:
        logger.error(f"Error fetching candles window: {e}")
        return None


def map_policy_symbol_to_test_symbol(policy_symbol: str) -> str:
    """Map a real/policy Bitfinex symbol (e.g. tBTCUSD) to a TEST spot symbol (e.g. tTESTBTC:TESTUSD).

    This allows the runner to use real market data while ensuring paper orders are forced to TEST symbols.
    """
    s = (policy_symbol or "").strip()
    if not s:
        return "tTESTBTC:TESTUSD"

    u = s.upper()
    # Already a TEST symbol
    if ":TEST" in u:
        # Accept either full Bitfinex form 'tTEST...' or bare 'TEST...'.
        if u.startswith(("TTEST", "FTEST")):
            u = u[1:]
        return ("t" + u) if not u.startswith("T") else ("t" + u)

    # Strip leading 't'/'f'
    if u.startswith(("T", "F")):
        u = u[1:]

    # Handle colon form (e.g. DOGE:USD)
    if ":" in u:
        base, quote = u.split(":", 1)
    else:
        # Heuristic for common quotes
        if u.endswith("USDT"):
            base, quote = u[:-4], "USDT"
        elif u.endswith("USD"):
            base, quote = u[:-3], "USD"
        else:
            base, quote = u, "USD"

    base = base.replace("TEST", "")
    quote = quote.replace("TEST", "")
    if not base:
        base = "BTC"
    if quote not in ("USD", "USDT"):
        quote = "USD"
    return f"tTEST{base}:TEST{quote}"


def _maybe_reset_pipeline_state(
    pipeline_state: dict,
    *,
    live_close: float,
    logger: logging.Logger,
    rel_threshold: float = 0.50,
) -> dict:
    """Defensive state migration guard.

    If we resume from a persisted `pipeline_state` that is incompatible with the live inputs
    (e.g. historical bugs such as wrong candle window ordering), the persisted `last_close`
    can be wildly different from the live candle close.

    In that case we reset the pipeline state to avoid propagating incompatible hysteresis/
    cooldown state.
    """
    if not isinstance(pipeline_state, dict) or not pipeline_state:
        return pipeline_state if isinstance(pipeline_state, dict) else {}

    prev_close = pipeline_state.get("last_close")
    if prev_close is None:
        return pipeline_state

    try:
        prev_close_f = float(prev_close)
        live_close_f = float(live_close)
    except (TypeError, ValueError):
        return pipeline_state

    if prev_close_f <= 0 or live_close_f <= 0:
        return pipeline_state

    rel = abs(prev_close_f - live_close_f) / live_close_f
    if rel <= rel_threshold:
        return pipeline_state

    logger.warning(
        "Resetting pipeline_state due to last_close mismatch: "
        f"state_last_close={prev_close_f:.4f}, live_close={live_close_f:.4f}"
    )
    return {}


# --- Main Loop ---


def run_loop(config: RunnerConfig, logger: logging.Logger, state: RunnerState) -> None:
    """Main polling loop."""
    enforce_live_paper_guardrails(config, logger)

    logger.info("=" * 80)
    logger.info("Paper Trading Runner Started")
    logger.info(f"Symbol: {config.symbol}, Timeframe: {config.timeframe}")
    logger.info(f"Poll interval: {config.poll_interval}s")
    logger.info(f"Mode: {'DRY-RUN (no orders)' if config.dry_run else 'LIVE PAPER TRADING'}")
    logger.info(f"State file: {config.state_file}")
    logger.info("=" * 80)

    # Setup HTTP client
    client = httpx.Client()

    # Verify champion on startup (use a real candles window)
    logger.info("Verifying champion loading...")
    startup_candle = fetch_latest_candle(config.symbol, config.timeframe, client, logger)
    if not startup_candle:
        logger.error("Failed to fetch candle on startup. Exiting.")
        sys.exit(1)

    state.pipeline_state = _maybe_reset_pipeline_state(
        state.pipeline_state,
        live_close=float(startup_candle.get("close")),
        logger=logger,
    )

    eval_resp = evaluate_strategy(
        config, startup_candle["ts"], state.pipeline_state, client, logger
    )
    if not eval_resp:
        logger.error("Failed to evaluate strategy on startup. Exiting.")
        sys.exit(1)

    if not verify_champion_loaded(eval_resp, logger):
        logger.error("Champion verification failed. Exiting.")
        sys.exit(1)

    logger.info("Champion verified successfully.")

    # Persist pipeline state after startup evaluation
    try:
        out_state = ((eval_resp.get("meta") or {}).get("decision") or {}).get("state_out") or {}
        if isinstance(out_state, dict):
            state.pipeline_state = out_state
    except Exception:
        pass

    # Main loop
    heartbeat_counter = 0
    try:
        while True:
            heartbeat_counter += 1
            if heartbeat_counter % 10 == 0:  # Heartbeat every 10 polls
                logger.info(
                    f"Heartbeat: evaluations={state.total_evaluations}, "
                    f"orders={state.total_orders_submitted}, "
                    f"last_candle_ts={state.last_processed_candle_ts}"
                )
                state.last_heartbeat = datetime.now(UTC).isoformat()
                save_state(state, config.state_file, logger)

            # Fetch latest candle
            candle = fetch_latest_candle(config.symbol, config.timeframe, client, logger)
            if not candle:
                logger.warning("Failed to fetch candle. Retrying...")
                time.sleep(config.poll_interval)
                continue

            candle_ts = candle["ts"]

            # Check if this candle has already been processed (idempotency)
            if (
                state.last_processed_candle_ts is not None
                and candle_ts <= state.last_processed_candle_ts
            ):
                # Already processed, skip
                logger.debug(f"Candle {candle_ts} already processed. Skipping.")
                time.sleep(config.poll_interval)
                continue

            # New candle detected!
            candle_source = candle.get("_source", "unknown")
            logger.info(
                f"NEW CANDLE CLOSE: ts={candle_ts}, close={candle['close']:.2f}, source={candle_source}"
            )

            # Evaluate strategy
            eval_resp = evaluate_strategy(config, candle_ts, state.pipeline_state, client, logger)
            if not eval_resp:
                logger.error("Evaluation failed. Skipping this candle.")
                time.sleep(config.poll_interval)
                continue

            # Verify champion
            if not verify_champion_loaded(eval_resp, logger):
                logger.error("Champion verification failed. Exiting.")
                sys.exit(1)

            state.total_evaluations += 1

            # Update pipeline state (cooldown/hysteresis etc.)
            try:
                out_state = ((eval_resp.get("meta") or {}).get("decision") or {}).get(
                    "state_out"
                ) or {}
                if isinstance(out_state, dict):
                    state.pipeline_state = out_state
            except Exception:
                pass

            # Extract action
            action = eval_resp.get("result", {}).get("action", "NONE")
            confidence = eval_resp.get("result", {}).get("confidence", {}).get("overall", 0.0)
            signal = eval_resp.get("result", {}).get("signal")

            logger.info(
                f"EVALUATION: action={action}, signal={signal}, confidence={confidence:.3f}"
            )

            # Submit order if action != NONE and live-paper mode
            if action != "NONE":
                if config.live_paper:
                    logger.info(f"Submitting {action} order...")
                    order_resp = submit_paper_order(config, action, eval_resp, client, logger)
                    if order_resp:
                        logger.info(f"ORDER SUBMITTED: {order_resp}")
                        state.total_orders_submitted += 1
                    else:
                        # CRITICAL: Order submission failed in uncertain state
                        logger.error(
                            f"FATAL: Order submission failed for candle {candle_ts}. "
                            f"Fail-closed: Cannot proceed with uncertain order state. "
                            f"Manual intervention required."
                        )
                        save_state(state, config.state_file, logger)  # Persist current state
                        sys.exit(1)  # Fail-closed
                else:
                    logger.info(f"DRY-RUN: Would submit {action} order (skipped)")
            else:
                logger.info("Action=NONE. No order.")

            # Mark candle as processed (only reached if order succeeded, dry-run, or NONE)
            state.last_processed_candle_ts = candle_ts
            save_state(state, config.state_file, logger)

            # Sleep until next poll
            time.sleep(config.poll_interval)

    except KeyboardInterrupt:
        logger.info("Shutdown signal received (Ctrl+C). Exiting gracefully...")
    except Exception as e:
        logger.exception(f"Unexpected error in main loop: {e}")
    finally:
        client.close()
        save_state(state, config.state_file, logger)
        logger.info("Runner stopped.")


# --- CLI ---


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Paper Trading Runner for Genesis-Core Phase 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--host", default="localhost", help="API server host (default: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="API server port (default: 8000)")
    parser.add_argument("--symbol", default="tBTCUSD", help="Trading symbol (default: tBTCUSD)")
    parser.add_argument("--timeframe", default="1h", help="Candle timeframe (default: 1h)")
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=10,
        help="Polling interval in seconds (default: 10)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Dry-run mode: log orders but don't submit (default: true if --live-paper not set)",
    )
    parser.add_argument(
        "--live-paper",
        action="store_true",
        default=False,
        help="Live paper trading: submit real orders (default: false)",
    )
    parser.add_argument(
        "--log-dir",
        type=Path,
        default=Path("results/paper_live/logs"),
        help="Log directory (default: results/paper_live/logs)",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=Path("results/paper_live/runner_state.json"),
        help=("State file for idempotency " "(default: results/paper_live/runner_state.json)"),
    )

    args = parser.parse_args()

    # If neither dry-run nor live-paper is set, default to dry-run
    if not args.dry_run and not args.live_paper:
        args.dry_run = True

    # Mutual exclusivity
    if args.dry_run and args.live_paper:
        parser.error("Cannot set both --dry-run and --live-paper. Choose one.")

    return args


def setup_logging(log_dir: Path) -> logging.Logger:
    """Setup logging to file and console."""
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"runner_{datetime.now().strftime('%Y%m%d')}.log"

    # Create logger
    logger = logging.getLogger("paper_trading_runner")
    logger.setLevel(logging.DEBUG)

    # File handler
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def handle_shutdown(signum, frame, logger: logging.Logger):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}. Shutting down...")
    sys.exit(0)


def main():
    """Main entry point."""
    args = parse_args()

    # Setup logging
    logger = setup_logging(args.log_dir)

    # Register signal handlers
    signal.signal(signal.SIGINT, lambda s, f: handle_shutdown(s, f, logger))
    signal.signal(signal.SIGTERM, lambda s, f: handle_shutdown(s, f, logger))

    # Create config
    config = RunnerConfig(
        host=args.host,
        port=args.port,
        symbol=args.symbol,
        timeframe=args.timeframe,
        poll_interval=args.poll_interval,
        dry_run=args.dry_run,
        live_paper=args.live_paper,
        log_dir=args.log_dir,
        state_file=args.state_file,
    )

    # Enforce mode/path guardrails before initializing runtime resources.
    enforce_live_paper_guardrails(config, logger=None)

    # Load state
    state = load_state(config.state_file, logger)

    # Run loop
    run_loop(config, logger, state)


if __name__ == "__main__":
    main()
