from __future__ import annotations

from fastapi import APIRouter

from core.observability.metrics import get_dashboard

TEST_SPOT_WHITELIST: set[str] = {
    "tTESTBTC:TESTUSD",
    "tTESTBTC:TESTUSDT",
    "tTESTETH:TESTUSD",
    "tTESTSOL:TESTUSD",
    "tTESTADA:TESTUSD",
    "tTESTALGO:TESTUSD",
    "tTESTAPT:TESTUSD",
    "tTESTAVAX:TESTUSD",
    "tTESTDOGE:TESTUSD",
    "tTESTDOT:TESTUSD",
    "tTESTEOS:TESTUSD",
    "tTESTFIL:TESTUSD",
    "tTESTLTC:TESTUSD",
    "tTESTNEAR:TESTUSD",
    "tTESTXAUT:TESTUSD",
    "tTESTXTZ:TESTUSD",
}

router = APIRouter()


@router.get("/paper/whitelist")
def paper_whitelist() -> dict:
    """Returnera whitelist av tillåtna TEST-spotpar för UI-val."""
    return {"symbols": sorted(TEST_SPOT_WHITELIST)}


@router.get("/observability/dashboard")
def observability_dashboard() -> dict:
    return get_dashboard()
