from __future__ import annotations

from typing import Any

AUTHORITY_MODE_LEGACY = "legacy"
AUTHORITY_MODE_REGIME_MODULE = "regime_module"
ALLOWED_AUTHORITY_MODES = {AUTHORITY_MODE_LEGACY, AUTHORITY_MODE_REGIME_MODULE}

AUTHORITY_MODE_SOURCE_CANONICAL = "multi_timeframe.regime_intelligence.authority_mode"
AUTHORITY_MODE_SOURCE_ALIAS = "regime_unified.authority_mode"
AUTHORITY_MODE_SOURCE_DEFAULT = "default_legacy"
AUTHORITY_MODE_SOURCE_CANONICAL_INVALID_FALLBACK = "canonical_invalid_fallback_legacy"
AUTHORITY_MODE_SOURCE_ALIAS_INVALID_FALLBACK = "alias_invalid_fallback_legacy"

AUTHORITY_MODE_CANONICAL_PATH = (
    "multi_timeframe",
    "regime_intelligence",
    "authority_mode",
)
AUTHORITY_MODE_ALIAS_PATH = ("regime_unified", "authority_mode")


def normalize_authority_mode_strict(value: Any) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    return normalized if normalized in ALLOWED_AUTHORITY_MODES else None


def normalize_authority_mode_permissive(value: Any) -> str | None:
    normalized = str(value).strip().lower() if value is not None else AUTHORITY_MODE_LEGACY
    return normalized if normalized in ALLOWED_AUTHORITY_MODES else None


def _has_nested_key(data: dict[str, Any], path: tuple[str, ...]) -> bool:
    cur: Any = data
    for key in path[:-1]:
        if not isinstance(cur, dict) or key not in cur:
            return False
        cur = cur[key]
    return isinstance(cur, dict) and path[-1] in cur


def _get_nested_value(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    cur: Any = data
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _set_nested_value(data: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    cur: Any = data
    for key in path[:-1]:
        nxt = cur.get(key)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[key] = nxt
        cur = nxt
    cur[path[-1]] = value


def _delete_nested_key(data: dict[str, Any], path: tuple[str, ...]) -> None:
    cur: Any = data
    parents: list[tuple[dict[str, Any], str]] = []
    for key in path[:-1]:
        if not isinstance(cur, dict) or key not in cur:
            return
        parents.append((cur, key))
        cur = cur[key]
    if not isinstance(cur, dict) or path[-1] not in cur:
        return
    del cur[path[-1]]

    for parent, key in reversed(parents):
        child = parent.get(key)
        if isinstance(child, dict) and not child:
            del parent[key]
        else:
            break


def canonicalize_authority_mode_alias_strict(patch: dict[str, Any]) -> dict[str, Any]:
    """Normalize compatibility alias to canonical authority path (strict path).

    Deterministic precedence:
    - canonical key wins when both canonical and alias are present;
    - invalid canonical value is never rescued by alias.
    """

    normalized_patch = dict(patch or {})

    alias_root_present = "regime_unified" in normalized_patch
    alias_root = normalized_patch.get("regime_unified") if alias_root_present else None
    if alias_root_present:
        if not isinstance(alias_root, dict):
            raise ValueError("non_whitelisted_field:regime_unified")
        if set(alias_root.keys()) != {"authority_mode"}:
            raise ValueError("non_whitelisted_field:regime_unified")

    alias_present = alias_root_present and _has_nested_key(
        normalized_patch, AUTHORITY_MODE_ALIAS_PATH
    )

    canonical_present = _has_nested_key(normalized_patch, AUTHORITY_MODE_CANONICAL_PATH)

    if canonical_present:
        canonical_raw = _get_nested_value(normalized_patch, AUTHORITY_MODE_CANONICAL_PATH)
        canonical_mode = normalize_authority_mode_strict(canonical_raw)
        if canonical_mode is None:
            raise ValueError("invalid_value:regime_intelligence.authority_mode")
        _set_nested_value(normalized_patch, AUTHORITY_MODE_CANONICAL_PATH, canonical_mode)
    elif alias_present:
        alias_raw = _get_nested_value(normalized_patch, AUTHORITY_MODE_ALIAS_PATH)
        alias_mode = normalize_authority_mode_strict(alias_raw)
        if alias_mode is None:
            raise ValueError("invalid_value:regime_unified.authority_mode")
        _set_nested_value(normalized_patch, AUTHORITY_MODE_CANONICAL_PATH, alias_mode)

    if alias_present:
        _delete_nested_key(normalized_patch, AUTHORITY_MODE_ALIAS_PATH)

    return normalized_patch


def resolve_authority_mode_with_source_permissive(
    configs: dict[str, Any] | None,
) -> tuple[str, str]:
    """Resolve authority mode + source with deterministic precedence.

    Precedence contract:
    1) `multi_timeframe.regime_intelligence.authority_mode` (canonical)
    2) `regime_unified.authority_mode` (compatibility alias)
    3) default legacy fallback

    If canonical key is present but invalid, fallback is always legacy even when alias is valid.
    """

    cfg = dict(configs or {})

    mtf = cfg.get("multi_timeframe")
    regime_intelligence_cfg = mtf.get("regime_intelligence") if isinstance(mtf, dict) else None
    canonical_present = isinstance(regime_intelligence_cfg, dict) and (
        "authority_mode" in regime_intelligence_cfg
    )
    if canonical_present:
        canonical_mode = normalize_authority_mode_permissive(
            regime_intelligence_cfg.get("authority_mode")
        )
        if canonical_mode is not None:
            return canonical_mode, AUTHORITY_MODE_SOURCE_CANONICAL
        return AUTHORITY_MODE_LEGACY, AUTHORITY_MODE_SOURCE_CANONICAL_INVALID_FALLBACK

    alias_cfg = cfg.get("regime_unified")
    alias_present = isinstance(alias_cfg, dict) and ("authority_mode" in alias_cfg)
    if alias_present:
        alias_mode = normalize_authority_mode_permissive(alias_cfg.get("authority_mode"))
        if alias_mode is not None:
            return alias_mode, AUTHORITY_MODE_SOURCE_ALIAS
        return AUTHORITY_MODE_LEGACY, AUTHORITY_MODE_SOURCE_ALIAS_INVALID_FALLBACK

    return AUTHORITY_MODE_LEGACY, AUTHORITY_MODE_SOURCE_DEFAULT


def resolve_authority_mode_permissive(configs: dict[str, Any] | None) -> str:
    mode, _source = resolve_authority_mode_with_source_permissive(configs)
    return mode
