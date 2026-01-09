from __future__ import annotations

from enum import Enum

from core.utils.logging_redaction import get_logger

_LOGGER = get_logger(__name__)


class SymbolMode(str, Enum):
    REALISTIC = "realistic"
    SYNTHETIC = "synthetic"


DEFAULT_MAP: dict[str, dict[str, str]] = {
    # base: BTCUSD → map to Bitfinex symbols
    "BTCUSD": {"realistic": "tBTCUSD", "synthetic": "tTESTBTC:TESTUSD"},
    "ETHUSD": {"realistic": "tETHUSD", "synthetic": "tTESTETH:TESTUSD"},
    "SOLUSD": {"realistic": "tSOLUSD", "synthetic": "tTESTSOL:TESTUSD"},
    "ADAUSD": {"realistic": "tADAUSD", "synthetic": "tTESTADA:TESTUSD"},
    "ALGOUSD": {"realistic": "tALGUSD", "synthetic": "tTESTALGO:TESTUSD"},
    "APTUSD": {"realistic": "tAPTUSD", "synthetic": "tTESTAPT:TESTUSD"},
    "AVAXUSD": {"realistic": "tAVAXUSD", "synthetic": "tTESTAVAX:TESTUSD"},
    "DOGEUSD": {"realistic": "tDOGE:USD", "synthetic": "tTESTDOGE:TESTUSD"},
    "DOTUSD": {"realistic": "tDOTUSD", "synthetic": "tTESTDOT:TESTUSD"},
    "EOSUSD": {"realistic": "tEOSUSD", "synthetic": "tTESTEOS:TESTUSD"},
    "FILUSD": {"realistic": "tFILUSD", "synthetic": "tTESTFIL:TESTUSD"},
    "LTCUSD": {"realistic": "tLTCUSD", "synthetic": "tTESTLTC:TESTUSD"},
    "NEARUSD": {"realistic": "tNEARUSD", "synthetic": "tTESTNEAR:TESTUSD"},
    "XAUTUSD": {"realistic": "tXAUT:USD", "synthetic": "tTESTXAUT:TESTUSD"},
    "XTZUSD": {"realistic": "tXTZUSD", "synthetic": "tTESTXTZ:TESTUSD"},
}


class SymbolMapper:
    def __init__(self, mode: SymbolMode, mapping: dict[str, dict[str, str]] | None = None) -> None:
        self.mode = mode
        self.mapping = dict(mapping or DEFAULT_MAP)

    @staticmethod
    def normalize(symbol: str) -> str:
        """Normalisera användarinmatning till basformatet 'BASEUSD', t.ex. 'BTCUSD'.

        - Accepterar 'BTCUSD', 'BTC:USD', 'tBTCUSD'
        - För TEST-symboler som 'tTESTBTC:TESTUSD' → 'BTCUSD'
        """
        s = (symbol or "").strip().upper()
        if not s:
            return ""
        # TEST-form: tTEST<COIN>:TESTUSD
        if s.startswith("TTEST") or s.startswith("FTES"):  # unlikely, guard
            # fall back to generic stripping below
            pass
        if s.startswith("TTEST"):
            # Already stripped 't', so skip; but real pattern starts with 'TTEST' only if 't' removed.
            pass
        # Strip leading 't' or 'f'
        if s.startswith("T") or s.startswith("F"):
            s_ = s[1:]
        else:
            s_ = s
        # Handle colon form 'BTC:USD' or 'TESTBTC:TESTUSD'
        if ":" in s_:
            left, right = s_.split(":", 1)
            # For TEST pairs like TESTBTC:TESTUSD → extract coin from left with optional TEST prefix
            left = left.replace("TEST", "")
            right = right.replace("TEST", "")
            base = f"{left}{right}"
        else:
            # tBTCUSD → BTCUSD, BTCUSD → BTCUSD
            base = s_.replace("TEST", "")
        return base

    def resolve(self, human: str) -> str:
        """Returnera Bitfinex-symbol baserat på aktuell mode.

        Exempel: resolve("BTCUSD") → "tBTCUSD" (realistic) eller "tTESTBTC:TESTUSD" (synthetic)
        """
        base = self.normalize(human)
        if not base:
            return human
        entry = self.mapping.get(base)
        if not entry:
            _LOGGER.warning("SymbolMapper: no mapping for base=%s; passthrough", base)
            return human
        out = entry.get(self.mode.value)
        return out or human

    def force(self, symbol: str) -> str:
        """Bypassar mappning och returnerar symbolen som den är. Loggar WARN.
        Avsedd för redan-formatterade Bitfinex-symboler.
        """
        _LOGGER.warning("SymbolMapper.force passthrough: %s", symbol)
        return symbol
