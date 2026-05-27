"""Materialize the Phase-1 runtime-only Genesis-Core-V2 seed.

Why this exists
---------------
The current repository now has a bounded V2 plan that says the first seed should be
runtime-only, not runtime+API. This script turns that plan into a repeatable local
materialization step by copying the runtime kernel and its local dependency closure
into a sibling `Genesis-Core-V2` folder while explicitly excluding legacy and
service-shell surfaces.

What this script does
---------------------
- starts from the approved Phase-1 runtime roots
- resolves local `core.*` and `config.*` imports transitively via AST
- copies only the required local files into a destination tree
- generates a narrow README, pyproject, .gitignore, and seed manifest
- writes V2-specific guardrails instead of blindly copying current API/legacy tests

What this script does not do
----------------------------
- it does not change the current Genesis-Core runtime
- it does not push or publish a new repository
- it does not copy current branch state/artifacts as future V2 defaults
- it does not include `src/core/server.py`, `src/core/api/**`,
  `src/core/strategy/features.py`, or `src/core/config/validator.py`
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PHASE_ONE_ROOTS = [
    "src/core/pipeline.py",
    "src/core/backtest/engine.py",
    "src/core/backtest/engine_precompute.py",
    "src/core/strategy/evaluate.py",
    "src/core/strategy/features_asof.py",
    "src/core/strategy/decision.py",
    "src/core/strategy/model_registry.py",
    "src/core/strategy/champion_loader.py",
    "src/core/intelligence/regime/authority.py",
    "src/core/strategy/regime.py",
    "config/__init__.py",
    "config/timeframe_configs.py",
    "tests/governance/test_no_legacy_feature_imports.py",
]

EXCLUDED_MODULE_PREFIXES = (
    "core.api",
    "core.server",
    "core.strategy.features",
    "core.config.validator",
)

EXCLUDED_RELATIVE_PATHS = {
    "src/core/server.py",
    "src/core/strategy/features.py",
    "src/core/config/validator.py",
}

EXCLUDED_PATH_PREFIXES = (
    "src/core/api/",
    "results/",
    "docs/analysis/edge_topology/",
)

GENERATED_FILES = {
    "README.md",
    "pyproject.toml",
    ".gitignore",
    "src/core/utils/diffing/__init__.py",
    "tests/governance/test_v2_seed_boundaries.py",
    "seed_manifest.json",
}

PYPROJECT_RUNTIME_DEPS = [
    "python-dotenv>=1,<2",
    "jsonschema>=4.20,<5",
    "numpy>=1.26,<2",
    "pandas>=2.0,<3",
    "PyYAML>=6.0,<7",
    "tqdm>=4.65,<5",
    "pydantic>=2.7,<3",
    "pyarrow>=14,<16",
]

PYPROJECT_DEV_DEPS = [
    "pytest>=8",
    "black>=24.10",
    "ruff>=0.6",
]


@dataclass(frozen=True)
class SourceFile:
    relative_path: str
    absolute_path: Path
    generated: bool = False


class SeedGenerationError(RuntimeError):
    """Raised when the runtime-only seed cannot be generated safely."""


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_destination(repo_root: Path) -> Path:
    return repo_root.parent / "Genesis-Core-V2"


def _module_name_for_path(relative_path: str) -> str | None:
    normalized = relative_path.replace("\\", "/")
    if normalized.startswith("src/") and normalized.endswith(".py"):
        body = normalized[len("src/") : -len(".py")]
        if body.endswith("/__init__"):
            body = body[: -len("/__init__")]
        return body.replace("/", ".")
    if normalized.startswith("config/") and normalized.endswith(".py"):
        body = normalized[: -len(".py")]
        if body.endswith("/__init__"):
            body = body[: -len("/__init__")]
        return body.replace("/", ".")
    if normalized.startswith("tests/") and normalized.endswith(".py"):
        body = normalized[: -len(".py")]
        if body.endswith("/__init__"):
            body = body[: -len("/__init__")]
        return body.replace("/", ".")
    return None


def _path_for_module(repo_root: Path, module_name: str) -> Path | None:
    if module_name.startswith("core.") or module_name == "core":
        base = repo_root / "src" / Path(module_name.replace(".", "/"))
    elif module_name.startswith("config.") or module_name == "config":
        base = repo_root / Path(module_name.replace(".", "/"))
    elif module_name.startswith("tests.") or module_name == "tests":
        base = repo_root / Path(module_name.replace(".", "/"))
    else:
        return None

    file_candidate = base.with_suffix(".py")
    if file_candidate.exists():
        return file_candidate

    init_candidate = base / "__init__.py"
    if init_candidate.exists():
        return init_candidate

    return None


def _is_excluded_relative_path(relative_path: str) -> bool:
    normalized = relative_path.replace("\\", "/")
    if normalized in EXCLUDED_RELATIVE_PATHS:
        return True
    return any(normalized.startswith(prefix) for prefix in EXCLUDED_PATH_PREFIXES)


def _is_excluded_module(module_name: str) -> bool:
    return any(
        module_name == prefix or module_name.startswith(f"{prefix}.")
        for prefix in EXCLUDED_MODULE_PREFIXES
    )


def _package_init_paths(repo_root: Path, source_relative: str) -> list[Path]:
    normalized = source_relative.replace("\\", "/")
    candidate_roots: list[Path] = []
    if normalized.startswith("src/"):
        relative_dir = Path(normalized).parent
        current = repo_root / relative_dir
        src_root = repo_root / "src"
        while current != src_root.parent:
            init_path = current / "__init__.py"
            if init_path.exists():
                candidate_roots.append(init_path)
            if current == src_root:
                break
            current = current.parent
        return candidate_roots

    current = (repo_root / normalized).parent
    while current != repo_root.parent:
        init_path = current / "__init__.py"
        if init_path.exists():
            candidate_roots.append(init_path)
        if current == repo_root:
            break
        current = current.parent
    return candidate_roots


def _relative_import_module(
    current_module: str,
    node: ast.ImportFrom,
    *,
    is_package: bool,
) -> str | None:
    level = int(getattr(node, "level", 0) or 0)
    module = node.module or ""
    if level == 0:
        return module or None

    current_parts = current_module.split(".")
    package_parts = current_parts if is_package else current_parts[:-1]
    trim = level - 1
    if trim > len(package_parts):
        return None

    if trim == 0:
        base_parts = package_parts
    else:
        base_parts = package_parts[:-trim]
    if module:
        base_parts.extend(module.split("."))
    return ".".join(part for part in base_parts if part)


def _collect_local_import_targets(relative_path: str, text: str) -> tuple[set[str], list[str]]:
    module_name = _module_name_for_path(relative_path)
    if module_name is None:
        return set(), []

    normalized_path = relative_path.replace("\\", "/")
    is_package = normalized_path.endswith("/__init__.py")
    tree = ast.parse(text, filename=relative_path)
    targets: set[str] = set()
    blocked: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported = alias.name
                if imported.startswith(("core", "config", "tests")):
                    if _is_excluded_module(imported):
                        blocked.append(f"{relative_path}:{node.lineno} import {imported}")
                    else:
                        targets.add(imported)
        elif isinstance(node, ast.ImportFrom):
            base_module = _relative_import_module(module_name, node, is_package=is_package)
            if not base_module:
                continue
            if not base_module.startswith(("core", "config", "tests")):
                continue
            if _is_excluded_module(base_module):
                blocked.append(f"{relative_path}:{node.lineno} from {base_module}")
                continue
            targets.add(base_module)

            for alias in node.names:
                if alias.name == "*":
                    continue
                child_module = f"{base_module}.{alias.name}"
                if _is_excluded_module(child_module):
                    blocked.append(f"{relative_path}:{node.lineno} from {child_module}")
                    continue
                targets.add(child_module)

    return targets, blocked


def _git_short_head(repo_root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception:
        return None
    value = result.stdout.strip()
    return value or None


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_source_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _build_closure(repo_root: Path) -> tuple[list[SourceFile], list[str]]:
    queue: list[str] = list(PHASE_ONE_ROOTS)
    seen_paths: set[str] = set()
    files: dict[str, SourceFile] = {}
    blocked_imports: list[str] = []

    while queue:
        relative_path = queue.pop(0).replace("\\", "/")
        if relative_path in seen_paths:
            continue
        seen_paths.add(relative_path)

        if _is_excluded_relative_path(relative_path):
            blocked_imports.append(f"requested excluded path: {relative_path}")
            continue

        absolute_path = repo_root / relative_path
        if not absolute_path.exists():
            raise SeedGenerationError(f"Missing required Phase-1 source: {relative_path}")

        files[relative_path] = SourceFile(relative_path=relative_path, absolute_path=absolute_path)

        if absolute_path.suffix != ".py":
            continue

        text = _load_source_text(absolute_path)
        targets, blocked = _collect_local_import_targets(relative_path, text)
        blocked_imports.extend(blocked)

        for module_name in sorted(targets):
            resolved = _path_for_module(repo_root, module_name)
            if resolved is None:
                continue
            candidate_relative = str(resolved.relative_to(repo_root)).replace("\\", "/")
            if _is_excluded_relative_path(candidate_relative):
                blocked_imports.append(
                    f"{relative_path} depends on excluded path {candidate_relative}"
                )
                continue
            if candidate_relative not in seen_paths:
                queue.append(candidate_relative)

        for init_path in _package_init_paths(repo_root, relative_path):
            init_relative = str(init_path.relative_to(repo_root)).replace("\\", "/")
            if _is_excluded_relative_path(init_relative):
                continue
            if init_relative not in seen_paths and init_relative not in queue:
                queue.append(init_relative)

    deduped_blocked = sorted(set(blocked_imports))
    ordered_files = [files[key] for key in sorted(files)]
    return ordered_files, deduped_blocked


def _v2_boundary_test_content() -> str:
    return """from __future__ import annotations

import ast
from pathlib import Path


_EXCLUDED_FILES = [
    "src/core/server.py",
    "src/core/strategy/features.py",
    "src/core/config/validator.py",
]

_EXCLUDED_PREFIXES = [
    "src/core/api",
]

_EXCLUDED_MODULE_PREFIXES = [
    "core.server",
    "core.api",
    "core.strategy.features",
    "core.config.validator",
]


def _is_excluded_module(module: str) -> bool:
    return any(
        module == prefix or module.startswith(f"{prefix}.")
        for prefix in _EXCLUDED_MODULE_PREFIXES
    )


def test_phase_one_seed_excludes_service_and_legacy_surfaces() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _EXCLUDED_FILES:
        assert not (repo_root / relative_path).exists(), relative_path

    for prefix in _EXCLUDED_PREFIXES:
        assert not (repo_root / prefix).exists(), prefix


def test_runtime_source_has_no_service_or_legacy_imports() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    src_root = repo_root / "src"
    assert src_root.exists()

    violations: list[str] = []
    for path in src_root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        rel_path = path.relative_to(repo_root).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported = alias.name
                    if _is_excluded_module(imported):
                        violations.append(f"{rel_path}:{node.lineno} import {imported}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if _is_excluded_module(module):
                    violations.append(f"{rel_path}:{node.lineno} from {module}")

    assert not violations, "Excluded import found:\\n" + "\\n".join(violations)
"""


def _runtime_diffing_init_content() -> str:
    return '''"""Runtime-only exports for diffing utilities."""

from __future__ import annotations

from .canonical import canonicalize_config, fingerprint_config
from .feature_cache import IndicatorCache, make_indicator_fingerprint

__all__ = [
    "canonicalize_config",
    "fingerprint_config",
    "IndicatorCache",
    "make_indicator_fingerprint",
]
'''


def _readme_content(source_head: str | None) -> str:
    source_line = (
        f"Source Genesis-Core HEAD: `{source_head}`"
        if source_head
        else "Source Genesis-Core HEAD: `unknown`"
    )
    return f"""# Genesis-Core-V2

Runtime-only Phase-1 seed generated from the current `Genesis-Core` repository.

{source_line}

## What is included

- runtime kernel roots (`pipeline`, `backtest`, `strategy`, `regime`)
- local dependency closure required by those roots
- narrow config bootstrap (`config/__init__.py`, `config/timeframe_configs.py`)
- runtime-only governance guardrails

## What is intentionally excluded

- `src/core/server.py`
- `src/core/api/**`
- `src/core/strategy/features.py`
- `src/core/config/validator.py`
- branch-local research corpora and historical explanation surfaces

## Notes

This seed is intentionally narrower than the source repository.
It is a local starting point, not a claim that all later bootstrap, model, champion,
or API/service decisions are already resolved.
"""


def _pyproject_content() -> str:
    runtime_deps = ",\n".join(f'  "{dep}"' for dep in PYPROJECT_RUNTIME_DEPS)
    dev_deps = ",\n".join(f'  "{dep}"' for dep in PYPROJECT_DEV_DEPS)
    return f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "genesis-core-v2"
version = "0.1.0"
description = "Runtime-only seed extracted from Genesis-Core"
requires-python = ">=3.11"
dependencies = [
{runtime_deps}
]

[project.optional-dependencies]
dev = [
{dev_deps}
]

[tool.setuptools]
package-dir = {{"" = "src"}}

[tool.setuptools.packages.find]
where = ["src"]
include = ["core*"]

[tool.pytest.ini_options]
addopts = "-q"
pythonpath = ["src"]
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.black]
line-length = 100
target-version = ['py311']
"""


def _gitignore_content() -> str:
    return """.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
*.pyc
*.pyo
*.egg-info/
cache/
logs/
results/
data/
.env
.nonce_tracker.json
"""


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _prepare_destination(destination: Path, *, clean: bool) -> None:
    if destination.exists() and any(destination.iterdir()):
        if not clean:
            raise SeedGenerationError(
                f"Destination already exists and is not empty: {destination}. "
                "Use --clean to replace it."
            )
        shutil.rmtree(destination)

    destination.mkdir(parents=True, exist_ok=True)


def _copy_sources(destination: Path, source_files: list[SourceFile], repo_root: Path) -> list[str]:
    copied: list[str] = []
    for source_file in source_files:
        relative_path = source_file.relative_path
        if relative_path == "src/core/utils/diffing/__init__.py":
            continue
        destination_path = destination / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file.absolute_path, destination_path)
        copied.append(relative_path)
    return copied


def _write_generated_files(destination: Path, *, source_head: str | None) -> list[str]:
    generated_paths: list[str] = []

    generated_map = {
        "README.md": _readme_content(source_head),
        "pyproject.toml": _pyproject_content(),
        ".gitignore": _gitignore_content(),
        "src/core/utils/diffing/__init__.py": _runtime_diffing_init_content(),
        "tests/governance/test_v2_seed_boundaries.py": _v2_boundary_test_content(),
    }

    for relative_path, content in generated_map.items():
        _write_text(destination / relative_path, content)
        generated_paths.append(relative_path)

    return generated_paths


def _manifest_payload(
    *,
    repo_root: Path,
    destination: Path,
    copied_paths: list[str],
    generated_paths: list[str],
    blocked_imports: list[str],
    source_head: str | None,
) -> dict[str, Any]:
    all_paths = sorted(copied_paths + generated_paths)
    output_hashes = {
        relative_path: _sha256_file(destination / relative_path)
        for relative_path in all_paths
        if (destination / relative_path).is_file()
    }

    return {
        "status": "genesis_core_v2_runtime_seed_local_materialization",
        "mode": "RESEARCH",
        "source_repo": str(repo_root),
        "destination_repo": str(destination),
        "source_head": source_head,
        "phase": "runtime_only_seed",
        "authorizing": False,
        "entry_roots": list(PHASE_ONE_ROOTS),
        "excluded_modules": list(EXCLUDED_MODULE_PREFIXES),
        "excluded_relative_paths": sorted(EXCLUDED_RELATIVE_PATHS),
        "excluded_path_prefixes": list(EXCLUDED_PATH_PREFIXES),
        "copied_files": sorted(copied_paths),
        "generated_files": sorted(generated_paths),
        "blocked_imports": blocked_imports,
        "output_hashes": output_hashes,
        "notes": [
            "Runtime-only seed generated locally.",
            "API/service shell intentionally excluded.",
            "Legacy compatibility surfaces intentionally excluded.",
            "Current branch stateful artifacts were not blindly carried over.",
        ],
    }


def _write_manifest(destination: Path, payload: dict[str, Any]) -> None:
    manifest_path = destination / "seed_manifest.json"
    _write_text(
        manifest_path,
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
    )


def generate_seed(destination: Path, *, clean: bool, dry_run: bool) -> dict[str, Any]:
    repo_root = _repo_root()
    source_files, blocked_imports = _build_closure(repo_root)

    if blocked_imports:
        raise SeedGenerationError(
            "Blocked excluded dependency detected during seed generation:\n"
            + "\n".join(blocked_imports)
        )

    source_head = _git_short_head(repo_root)
    copied_paths = [source.relative_path for source in source_files]
    generated_paths = [path for path in sorted(GENERATED_FILES) if path != "seed_manifest.json"]

    payload = _manifest_payload(
        repo_root=repo_root,
        destination=destination,
        copied_paths=copied_paths,
        generated_paths=generated_paths + ["seed_manifest.json"],
        blocked_imports=blocked_imports,
        source_head=source_head,
    )

    if dry_run:
        return payload

    _prepare_destination(destination, clean=clean)
    _copy_sources(destination, source_files, repo_root)
    _write_generated_files(destination, source_head=source_head)
    _write_manifest(destination, payload)
    return payload


def main() -> int:
    repo_root = _repo_root()
    parser = argparse.ArgumentParser(
        description="Materialize the Phase-1 Genesis-Core-V2 runtime seed"
    )
    parser.add_argument(
        "--dest",
        default=str(_default_destination(repo_root)),
        help="Destination directory for the generated Genesis-Core-V2 seed",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove the destination first if it already exists and is not empty",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned seed manifest without writing files",
    )
    args = parser.parse_args()

    destination = Path(args.dest).resolve()
    payload = generate_seed(destination, clean=bool(args.clean), dry_run=bool(args.dry_run))
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
