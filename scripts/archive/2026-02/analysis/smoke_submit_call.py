import asyncio
import json
import sys
from pathlib import Path


def _find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "pyproject.toml").exists() and (candidate / "src").exists():
            return candidate
    raise RuntimeError("Could not locate repository root from script path")


ROOT = _find_repo_root(Path(__file__).resolve())
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import core.server as srv  # noqa: E402


class DummyResp:
    def __init__(self, payload: dict):
        self._payload = payload

    def json(self):
        return {"status": "stubbed", "echo": self._payload}


class DummyClient:
    async def signed_request(self, method: str, endpoint: str, body: dict):
        return DummyResp(body)


async def run() -> int:
    srv.get_exchange_client = lambda: DummyClient()  # type: ignore[assignment]
    out = await srv.paper_submit(
        {"symbol": "tTESTETH:TESTUSD", "side": "LONG", "size": 0.0005, "type": "MARKET"}
    )
    print(json.dumps(out, ensure_ascii=False))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    rc = asyncio.get_event_loop().run_until_complete(run())
    raise SystemExit(rc)
