from __future__ import annotations

import json
from pathlib import Path


def test_repo_model_registry_avoids_unsafe_1M_filenames() -> None:
    """Guardrail: repo registry.json must not reference *_1M.json on Windows/macOS.

    Rationale:
    - On case-insensitive filesystems, "_1M.json" can alias to "_1m.json".
    - Repo convention is to use "*_1mo.json" for monthly model filenames.

    Note:
    - This test validates the *tracked* registry under config/models/registry.json.
    - Separate tests simulate legacy/unsafe registry entries to verify warning behavior.
    """

    repo_root = Path(__file__).resolve().parents[1]
    registry_path = repo_root / "config" / "models" / "registry.json"
    data = json.loads(registry_path.read_text(encoding="utf-8"))

    unsafe: list[str] = []
    for key, meta in (data or {}).items():
        if not isinstance(meta, dict):
            continue
        champ = meta.get("champion")
        if isinstance(champ, str) and "_1M.json" in champ:
            unsafe.append(f"{key} -> {champ}")

    assert (
        not unsafe
    ), "Unsafe monthly model paths found in config/models/registry.json: " + ", ".join(unsafe)
