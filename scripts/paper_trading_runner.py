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
import signal
import sys
import time
from dataclasses import dataclass
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


# --- State Management ---


@dataclass
class RunnerState:
    """Persistent runner state for idempotency."""

    last_processed_candle_ts: int | None = None  # Unix timestamp (ms)
    total_evaluations: int = 0
    total_orders_submitted: int = 0
    last_heartbeat: str | None = None

    def to_dict(self) -> dict:
        return {
            "last_processed_candle_ts": self.last_processed_candle_ts,
            "total_evaluations": self.total_evaluations,
            "total_orders_submitted": self.total_orders_submitted,
            "last_heartbeat": self.last_heartbeat,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RunnerState":
        return cls(
            last_processed_candle_ts=data.get("last_processed_candle_ts"),
            total_evaluations=data.get("total_evaluations", 0),
            total_orders_submitted=data.get("total_orders_submitted", 0),
            last_heartbeat=data.get("last_heartbeat"),
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

        # If now > latest_ts + duration, latest is closed
        if now_ms > latest_ts + candle_duration_ms:
            closed_candle_ts = latest_ts
        else:
            # Latest is still forming, use previous
            closed_candle_ts = int(previous[0])

        return {
            "ts": closed_candle_ts,
            "open": float(latest[1]),
            "close": float(latest[2]),
            "high": float(latest[3]),
            "low": float(latest[4]),
            "volume": float(latest[5]),
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
    config: RunnerConfig, client: httpx.Client, logger: logging.Logger
) -> dict | None:
    """POST to /strategy/evaluate and return response."""
    try:
        url = f"{config.api_base}/strategy/evaluate"
        payload = {"policy": {"symbol": config.symbol, "timeframe": config.timeframe}}
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
        # Extract size from evaluation response
        size_pct = eval_response.get("result", {}).get("size_pct", 0.0)
        confidence = eval_response.get("result", {}).get("confidence", {}).get("overall", 0.0)

        payload = {
            "symbol": config.symbol,
            "side": action.lower(),  # "buy" or "sell"
            "size_pct": size_pct,
            "confidence": confidence,
        }

        resp = client.post(url, json=payload, timeout=10.0)
        resp.raise_for_status()
        return resp.json()
    except httpx.HTTPError as e:
        logger.error(f"HTTP error submitting order: {e}")
        return None
    except Exception as e:
        logger.error(f"Error submitting order: {e}")
        return None


# --- Main Loop ---


def run_loop(config: RunnerConfig, logger: logging.Logger, state: RunnerState) -> None:
    """Main polling loop."""
    logger.info("=" * 80)
    logger.info("Paper Trading Runner Started")
    logger.info(f"Symbol: {config.symbol}, Timeframe: {config.timeframe}")
    logger.info(f"Poll interval: {config.poll_interval}s")
    logger.info(f"Mode: {'DRY-RUN (no orders)' if config.dry_run else 'LIVE PAPER TRADING'}")
    logger.info(f"State file: {config.state_file}")
    logger.info("=" * 80)

    # Setup HTTP client
    client = httpx.Client()

    # Verify champion on startup
    logger.info("Verifying champion loading...")
    eval_resp = evaluate_strategy(config, client, logger)
    if not eval_resp:
        logger.error("Failed to evaluate strategy on startup. Exiting.")
        sys.exit(1)

    if not verify_champion_loaded(eval_resp, logger):
        logger.error("Champion verification failed. Exiting.")
        sys.exit(1)

    logger.info("Champion verified successfully.")

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
            logger.info(f"NEW CANDLE CLOSE: ts={candle_ts}, close={candle['close']:.2f}")

            # Evaluate strategy
            eval_resp = evaluate_strategy(config, client, logger)
            if not eval_resp:
                logger.error("Evaluation failed. Skipping this candle.")
                time.sleep(config.poll_interval)
                continue

            # Verify champion
            if not verify_champion_loaded(eval_resp, logger):
                logger.error("Champion verification failed. Exiting.")
                sys.exit(1)

            state.total_evaluations += 1

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
                        logger.error("Order submission failed.")
                else:
                    logger.info(f"DRY-RUN: Would submit {action} order (skipped)")
            else:
                logger.info("Action=NONE. No order.")

            # Mark candle as processed
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
        default=Path("logs/paper_trading"),
        help="Log directory (default: logs/paper_trading)",
    )
    parser.add_argument(
        "--state-file",
        type=Path,
        default=Path("logs/paper_trading/runner_state.json"),
        help="State file for idempotency (default: logs/paper_trading/runner_state.json)",
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

    # Load state
    state = load_state(config.state_file, logger)

    # Run loop
    run_loop(config, logger, state)


if __name__ == "__main__":
    main()
