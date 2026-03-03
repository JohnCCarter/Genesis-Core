from __future__ import annotations

import copy
import sys
from typing import Any

import pytest

from core.utils.dict_merge import deep_merge_dicts


def _nested_level(depth: int, leaf: dict[str, Any]) -> dict[str, Any]:
    node: dict[str, Any] = dict(leaf)
    for i in reversed(range(depth)):
        node = {f"k{i}": node}
    return node


def test_deep_merge_is_stack_safe_no_recursionerror() -> None:
    depth = sys.getrecursionlimit() + 200
    base = {"root": _nested_level(depth, {"shared": {"a": 1}, "base_only": True})}
    override = {"root": _nested_level(depth, {"shared": {"b": 2}, "override_only": True})}

    try:
        merged = deep_merge_dicts(base, override)
    except RecursionError as exc:  # pragma: no cover - explicit contract assertion
        pytest.fail(f"deep_merge_dicts raised RecursionError at depth={depth}: {exc}")

    leaf = merged["root"]
    for i in range(depth):
        leaf = leaf[f"k{i}"]

    assert leaf == {
        "shared": {"a": 1, "b": 2},
        "base_only": True,
        "override_only": True,
    }


def test_deep_merge_matches_existing_behavior_for_shallow_cases() -> None:
    base = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "nested": {"keep": True, "replace_me": 1},
        },
        "risk": {"risk_map": {"ranging": 1.0}},
        "list_value": [1, 2],
        "scalar": "base",
    }
    override = {
        "thresholds": {
            "nested": {"replace_me": 99, "new_leaf": "x"},
            "new_top": 7,
        },
        "risk": {"risk_map": {"bull": 1.3}},
        "list_value": [9],
        "scalar": {"replaced": True},
        "added": "yes",
    }

    base_before = copy.deepcopy(base)
    override_before = copy.deepcopy(override)

    expected = {
        "thresholds": {
            "entry_conf_overall": 0.6,
            "nested": {"keep": True, "replace_me": 99, "new_leaf": "x"},
            "new_top": 7,
        },
        "risk": {"risk_map": {"ranging": 1.0, "bull": 1.3}},
        "list_value": [9],
        "scalar": {"replaced": True},
        "added": "yes",
    }

    merged = deep_merge_dicts(base, override)

    assert merged == expected
    assert base == base_before
    assert override == override_before
