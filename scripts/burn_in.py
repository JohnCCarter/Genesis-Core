from __future__ import annotations

import asyncio
import contextlib
import json
import sys
from pathlib import Path
from typing import Any

# Ensure local 'src' is on sys.path when running as a script
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from core.config.settings import get_settings
from core.io.bitfinex.ws_public import one_message_ticker
from core.io.bitfinex.read_helpers import get_wallets, get_positions
from core.io.bitfinex.ws_reconnect import WSReconnectClient
from core.observability.metrics import metrics


async def burn_in(
    duration_seconds: int = 300, *, symbols: list[str] | None = None
) -> dict[str, Any]:
    s = get_settings()
    # Startlogg
    try:
        from core.utils.logging_redaction import get_logger  # lazy import

        _log = get_logger(__name__)
        _log.info(
            "BURN-IN start duration_s=%s symbols=%s rest_enabled=%s",
            duration_seconds,
            ",".join(symbols or ["tBTCUSD"]),
            bool((s.BITFINEX_API_KEY or "").strip() and (s.BITFINEX_API_SECRET or "").strip()),
        )
    except Exception:
        _log = None

    async def ws_loop() -> None:
        client = WSReconnectClient(enable_auth=False)
        # Kör enkel ticker-subscribe/cykel med ack/error/timeout-observation
        end = asyncio.get_running_loop().time() + duration_seconds
        while asyncio.get_running_loop().time() < end:
            syms = symbols or ["tBTCUSD"]
            for sym in syms:
                res = await one_message_ticker(symbol=sym, timeout=5.0)
                await asyncio.sleep(0.5 if res.get("ok") else 0.25)

    async def rest_loop() -> None:
        # Kör endast om nycklar finns
        if not ((s.BITFINEX_API_KEY or "").strip() and (s.BITFINEX_API_SECRET or "").strip()):
            return
        end = asyncio.get_running_loop().time() + duration_seconds
        while asyncio.get_running_loop().time() < end:
            try:
                await get_wallets()
                await get_positions()
            except Exception:
                # metrics i underliggande lager fångar counters
                pass
            await asyncio.sleep(30.0)

    ws_task = asyncio.create_task(ws_loop())
    rest_task = asyncio.create_task(rest_loop())

    try:
        await asyncio.wait({ws_task, rest_task}, timeout=duration_seconds)
    finally:
        for t in (ws_task, rest_task):
            if not t.done():
                t.cancel()
                with contextlib.suppress(asyncio.CancelledError, Exception):
                    await t

    # Sammanställ kort rapport
    c = metrics.counters
    report = {
        "ws_public": {
            "request": c.get("ws_public_request", 0),
            "success": c.get("ws_public_success", 0),
            "error": c.get("ws_public_error", 0),
            "timeout": c.get("ws_public_timeout", 0),
            "maintenance": c.get("ws_public_maintenance", 0),
        },
        "rest_auth": {
            "request": c.get("rest_auth_request", 0),
            "success": c.get("rest_auth_success", 0),
            "error": c.get("rest_auth_error", 0),
            "retry": c.get("rest_auth_retry_triggered", 0),
        },
        "duration_s": duration_seconds,
    }
    # Härledda nyckeltal
    req = max(1, report["ws_public"]["request"])  # skydda mot div0
    report["ws_public"]["success_rate"] = report["ws_public"]["success"] / req
    report["ws_public"]["timeout_rate"] = report["ws_public"]["timeout"] / req
    report["ws_public"]["error_rate"] = report["ws_public"]["error"] / req
    # Slutlogg
    try:
        if _log:
            _log.info(
                "BURN-IN end ws_req=%s ws_ok=%s ws_err=%s ws_to=%s rest_req=%s rest_ok=%s",
                report["ws_public"]["request"],
                report["ws_public"]["success"],
                report["ws_public"]["error"],
                report["ws_public"]["timeout"],
                report["rest_auth"]["request"],
                report["rest_auth"]["success"],
            )
    except Exception:
        pass
    return report


async def main(argv: list[str]) -> int:
    duration = 120
    if len(argv) >= 2:
        try:
            duration = int(argv[1])
        except Exception:
            pass
    # CLI: valfri kommaseparerad lista på symboler som tredje argument
    sym_list: list[str] | None = None
    if len(argv) >= 3 and isinstance(argv[2], str) and argv[2].strip():
        sym_list = [s.strip() for s in argv[2].split(",") if s.strip()]
    rep = await burn_in(duration, symbols=sym_list)

    # Valfri skrivning till fil: fjärde argument (path) eller ENV BURNIN_SUMMARY
    out_path = None
    if len(argv) >= 4 and argv[3].strip():
        out_path = argv[3].strip()
    else:
        import os as _os

        out_path = _os.environ.get("BURNIN_SUMMARY")

    text = json.dumps(rep, indent=2)
    if out_path:
        try:
            from pathlib import Path as _P

            _P(out_path).write_text(text, encoding="utf-8")
            print(text)
            return 0
        except Exception:
            # Faller tillbaka till stdout
            pass
    print(text)
    return 0


if __name__ == "__main__":
    try:
        asyncio.run(main(sys.argv))
    except KeyboardInterrupt:
        pass
