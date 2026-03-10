from __future__ import annotations

import hashlib
import json
import string
from pathlib import Path

from core.config.authority import ConfigAuthority


def _canon_json(data: dict) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def test_hash_contract_is_sha256_of_canonical_json(tmp_path: Path) -> None:
    auth = ConfigAuthority(tmp_path / "runtime.json")
    cfg, h, _ver = auth.get()

    canon = _canon_json(cfg.model_dump_canonical())
    expected = hashlib.sha256(canon.encode("utf-8")).hexdigest()

    assert h == expected
    assert len(h) == 64
    assert all(ch in string.hexdigits for ch in h)


def test_hash_is_order_independent_for_dict_keys(tmp_path: Path) -> None:
    auth = ConfigAuthority(tmp_path / "runtime.json")

    cfg1 = {"b": 2, "a": 1}
    cfg2 = {"a": 1, "b": 2}

    h1 = auth._hash_cfg(cfg1)
    h2 = auth._hash_cfg(cfg2)

    assert h1 == h2


def test_hash_changes_when_content_changes(tmp_path: Path) -> None:
    auth = ConfigAuthority(tmp_path / "runtime.json")

    cfg1 = {"a": 1, "b": 2}
    cfg2 = {"a": 1, "b": 3}

    assert auth._hash_cfg(cfg1) != auth._hash_cfg(cfg2)
