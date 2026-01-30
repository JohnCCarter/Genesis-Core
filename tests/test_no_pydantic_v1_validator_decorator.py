from __future__ import annotations

from pathlib import Path


def test_no_pydantic_v1_validator_decorator_in_src() -> None:
    """Guardrail: avoid reintroducing deprecated Pydantic v1 `@validator` in src.

    Pydantic v2 recommends `@field_validator` / `@model_validator` instead.
    """

    repo_root = Path(__file__).resolve().parents[1]
    src_root = repo_root / "src"

    forbidden_substrings = (
        "@validator(",
        "from pydantic import validator",
        "from pydantic import BaseModel, Field, validator",
    )

    offenders: list[str] = []
    for py_file in sorted(src_root.rglob("*.py")):
        text = py_file.read_text(encoding="utf-8", errors="replace")
        if any(s in text for s in forbidden_substrings):
            offenders.append(str(py_file.relative_to(repo_root)))

    assert not offenders, "Pydantic v1 @validator found in src: " + ", ".join(offenders)
