from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _parse_kv_tokens(line: str) -> dict[str, str]:
    tokens = line.strip().split()
    out: dict[str, str] = {}
    for tok in tokens:
        if "=" not in tok:
            continue
        key, value = tok.split("=", 1)
        # Ta bort eventuella avslutande skiljetecken
        out[key.strip()] = value.strip().rstrip(",;)")
    return out


def parse_burnin_log(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    result: dict[str, Any] = {}
    for line in lines:
        if ("BURN-IN start" in line) or ("duration_s=" in line and "symbols=" in line):
            kv = _parse_kv_tokens(line)
            start: dict[str, Any] = {}
            if "duration_s" in kv:
                start["duration_s"] = int(kv["duration_s"])  # type: ignore[arg-type]
            if "symbols" in kv:
                start["symbols"] = kv["symbols"].split(",")
            if "rest_enabled" in kv:
                start["rest_enabled"] = kv["rest_enabled"].lower() == "true"
            if start:
                result["start"] = start
        elif ("BURN-IN end" in line) or ("ws_req=" in line and "ws_ok=" in line):
            kv = _parse_kv_tokens(line)
            end: dict[str, Any] = {}
            for key in ("ws_req", "ws_ok", "ws_err", "ws_to", "rest_req", "rest_ok"):
                if key in kv:
                    end[key] = int(kv[key])  # type: ignore[arg-type]
            if end:
                result["end"] = end
    # Fallback: regex över hela texten om line-by-line missade
    if "start" not in result:
        import re as _re

        m = _re.search(
            r"BURN-IN start.*?duration_s\s*=\s*(\d+).*?symbols\s*=\s*([^\s]+)",
            text,
            _re.IGNORECASE | _re.DOTALL,
        )
        if m:
            result["start"] = {
                "duration_s": int(m.group(1)),
                "symbols": m.group(2).split(","),
            }
    if "end" not in result:
        import re as _re

        m = _re.search(
            r"BURN-IN end.*?ws_req\s*=\s*(\d+).*?ws_ok\s*=\s*(\d+).*?ws_err\s*=\s*(\d+).*?ws_to\s*=\s*(\d+).*?rest_req\s*=\s*(\d+).*?rest_ok\s*=\s*(\d+)",
            text,
            _re.IGNORECASE | _re.DOTALL,
        )
        if m:
            result["end"] = {
                "ws_req": int(m.group(1)),
                "ws_ok": int(m.group(2)),
                "ws_err": int(m.group(3)),
                "ws_to": int(m.group(4)),
                "rest_req": int(m.group(5)),
                "rest_ok": int(m.group(6)),
            }
    # härledda nyckeltal om end finns
    if "end" in result:
        e = result["end"]
        req = max(1, int(e.get("ws_req", 0)))
        e["ws_success_rate"] = e.get("ws_ok", 0) / req
        e["ws_error_rate"] = e.get("ws_err", 0) / req
        e["ws_timeout_rate"] = e.get("ws_to", 0) / req
    return result


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    log_path = root / "burnin.log"
    out_path = root / "burnin_summary.json"
    data = parse_burnin_log(log_path)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
