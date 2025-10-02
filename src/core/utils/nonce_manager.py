from __future__ import annotations

import json
import time
from pathlib import Path
from threading import Lock


# Lagra nonces lokalt per API‑nyckel för strikt växande sekvens (mikrosekunder)
NONCE_FILE = Path(__file__).parent / ".nonce_tracker.json"
_lock = Lock()


def get_nonce(key_id: str) -> str:
    """Returnerar en strikt ökande nonce per API‑nyckel i mikrosekunder.

    Persistens används för att undvika backstep efter omstart.
    """
    now = int(time.time() * 1_000_000)
    with _lock:
        try:
            if NONCE_FILE.exists():
                try:
                    content = NONCE_FILE.read_text(encoding="utf-8").strip()
                    data = json.loads(content) if content else {}
                except Exception:
                    data = {}
            else:
                data = {}

            last_nonce = int(data.get(key_id, 0) or 0)
            new_nonce = max(now, last_nonce + 1)
            data[key_id] = new_nonce

            NONCE_FILE.parent.mkdir(parents=True, exist_ok=True)
            try:
                NONCE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except (OSError, PermissionError, json.JSONDecodeError) as io_err:
                # Fallback: logga lätt och returnera ändå nytt värde
                # (undvik hårt fail i hot path)
                print(f"nonce_manager: write failed: {io_err}")

            return str(new_nonce)
        except Exception:
            # Fallback vid I/O-problem: returnera current time
            return str(now)


def bump_nonce(key_id: str, min_increment_micro: int = 1_000_000) -> str:
    """Bumpar noncen rejält för angiven key_id (≥ min_increment_micro).

    Används vid t.ex. Bitfinex 10114 ("nonce too small").
    """
    now = int(time.time() * 1_000_000)
    with _lock:
        try:
            data = {}
            if NONCE_FILE.exists():
                try:
                    content = NONCE_FILE.read_text(encoding="utf-8").strip()
                    data = json.loads(content) if content else {}
                except Exception:
                    data = {}

            last_nonce = int(data.get(key_id, 0) or 0)
            target = max(
                last_nonce + int(min_increment_micro), now + int(min_increment_micro)
            )
            data[key_id] = target

            NONCE_FILE.parent.mkdir(parents=True, exist_ok=True)
            try:
                NONCE_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
            except (OSError, PermissionError, json.JSONDecodeError) as io_err:
                print(f"nonce_manager: bump write failed: {io_err}")

            return str(target)
        except Exception:
            return str(now + int(min_increment_micro))
