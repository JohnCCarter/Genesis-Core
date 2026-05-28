"""Materialize the runtime-first Genesis-Core-V2 seed with admitted API shell.

Why this exists
---------------
The current repository now has a bounded V2 plan that starts runtime-first and admits
additional surfaces in controlled slices. This script turns the currently admitted
seed boundary into a repeatable local materialization step by copying the runtime
kernel, the API/service shell, and their local dependency closure into a sibling
`Genesis-Core-V2` folder while explicitly excluding legacy-only and freeze-sensitive
authority/state surfaces.

What this script does
---------------------
- starts from the approved runtime roots plus the admitted API/service shell
- resolves local `core.*` and `config.*` imports transitively via AST
- copies only the required local files into a destination tree
- generates a narrow README, pyproject, .gitignore, and seed manifest
- writes V2-specific guardrails instead of blindly copying current stateful surfaces

What this script does not do
----------------------------
- it does not change the current Genesis-Core runtime
- it does not push or publish a new repository
- it does not copy current branch state/artifacts as future V2 defaults
- it does not include `src/core/strategy/features.py`
- it does not copy runtime state, champion authority payloads, or `data/**`
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
    "src/core/backtest/engine.py",
    "src/core/backtest/engine_precompute.py",
    "src/core/server.py",
    "mcp_server/server.py",
    "src/core/strategy/evaluate.py",
    "src/core/strategy/features_asof.py",
    "src/core/strategy/decision.py",
    "src/core/strategy/model_registry.py",
    "src/core/strategy/champion_loader.py",
    "src/core/intelligence/regime/authority.py",
    "src/core/strategy/regime.py",
    "config/__init__.py",
    "config/timeframe_configs.py",
    "src/core/config/legacy_schema_v1.json",
    "tests/integration/test_config_endpoints.py",
    "tests/governance/test_no_legacy_feature_imports.py",
]

EXCLUDED_MODULE_PREFIXES = (
    "core.api.account",
    "core.api.info",
    "core.api.paper",
    "core.api.public",
    "core.api.ui",
    "core.io",
    "core.optimizer",
    "core.pipeline",
    "core.strategy.features",
    "core.utils.diffing.optuna_guard",
    "core.utils.diffing.results_diff",
    "core.utils.diffing.trial_cache",
    "core.utils.optuna_helpers",
)

EXCLUDED_RELATIVE_PATHS = {
    "config/mcp_settings.remote_git.json",
    "config/mcp_settings.remote_safe.json",
    "mcp_server/remote_server.py",
    "src/core/api/account.py",
    "src/core/api/info.py",
    "src/core/api/paper.py",
    "src/core/api/public.py",
    "src/core/api/ui.py",
    "src/core/pipeline.py",
    "src/core/strategy/features.py",
    "src/core/utils/optuna_helpers.py",
}

EXCLUDED_PATH_PREFIXES = (
    "src/core/io/",
    "src/core/optimizer/",
    "results/",
    "docs/analysis/edge_topology/",
)

VERIFY_BEFORE_INCLUDE_PATHS = (
    "config/runtime.json",
    "config/runtime.seed.json",
    "config/strategy/champions/**",
    "data/**",
)

EXPLICIT_STATEFUL_ADMISSIONS = (
    "config/backtest_defaults.yaml",
    "config/models/**",
)

CHAMPIONLESS_FALLBACK_CONTRACT = {
    "phase_one_champion_policy": "exclude_config_strategy_champions",
    "fallback_loader": "core.strategy.champion_loader.ChampionLoader",
    "runtime_fallback_source": "config/timeframe_configs.py",
    "runtime_behavior": "fallback_to_timeframe_configs_when_champion_missing_or_invalid",
}

GENERATED_FILES = {
    ".vscode/extensions.json",
    ".vscode/launch.json",
    ".vscode/mcp.json",
    ".vscode/settings.json",
    ".vscode/tasks.json",
    ".github/copilot-instructions.md",
    ".pre-commit-config.yaml",
    "README.md",
    "AGENTS.md",
    "pyproject.toml",
    ".gitignore",
    ".env",
    ".env.example",
    "config/backtest_defaults.yaml",
    "config/mcp_settings.json",
    "docs/SKELETON_SCOPE.md",
    "registry/fixtures/champions/tBTCUSD_1h.json",
    "registry/fixtures/model_registry/config/models/registry.json",
    "registry/fixtures/model_registry/config/models/tBTCUSD_1h.json",
    "registry/fixtures/runtime_fixture_smoke_minimal.json",
    "scripts/api/api_shell.py",
    "scripts/mcp/mcp_stdio.py",
    "scripts/smoke/champion_smoke.py",
    "scripts/smoke/evaluate_champion_smoke.py",
    "scripts/smoke/backtest_smoke.py",
    "scripts/smoke/fixture_smoke.py",
    "scripts/smoke/model_smoke.py",
    "scripts/smoke/smoke_suite.py",
    "scripts/validate/pytest_suite.py",
    "src/core/bootstrap/__init__.py",
    "src/core/bootstrap/backtest_smoke.py",
    "src/core/bootstrap/champion_smoke.py",
    "src/core/bootstrap/evaluate_champion_smoke.py",
    "src/core/bootstrap/fixture_smoke.py",
    "src/core/bootstrap/model_smoke.py",
    "src/core/bootstrap/smoke_suite.py",
    "src/core/server.py",
    "src/core/utils/diffing/__init__.py",
    "src/genesis_core_v2_cli/__init__.py",
    "src/genesis_core_v2_cli/console_scripts.py",
    "tests/governance/test_pyproject_console_scripts.py",
    "tests/runtime/test_installed_console_scripts.py",
    "tests/runtime/test_backtest_bootstrap_smoke.py",
    "tests/runtime/test_champion_smoke.py",
    "tests/runtime/test_evaluate_champion_smoke.py",
    "tests/governance/test_v2_seed_boundaries.py",
    "tests/runtime/test_backtest_engine_fixture_smoke.py",
    "tests/runtime/test_local_api_shell_script.py",
    "tests/runtime/test_local_mcp_script.py",
    "tests/runtime/test_local_mcp_setup.py",
    "tests/runtime/test_local_pytest_script.py",
    "tests/runtime/test_local_smoke_scripts.py",
    "tests/runtime/test_local_vscode_launch.py",
    "tests/runtime/test_local_vscode_settings.py",
    "tests/runtime/test_local_vscode_tasks.py",
    "tests/runtime/test_model_smoke.py",
    "tests/runtime/test_evaluate_pipeline_smoke.py",
    "tests/runtime/test_runtime_fixture_smoke.py",
    "tests/runtime/test_smoke_suite.py",
    "seed_manifest.json",
}

PYPROJECT_RUNTIME_DEPS = [
    "fastapi>=0.116,<0.117",
    "uvicorn>=0.24,<0.25",
    "pydantic>=2.7,<3",
    "pydantic-settings>=2,<3",
    "python-dotenv>=1,<2",
    "jsonschema>=4.20,<5",
    "numpy>=1.26,<2",
    "pandas>=2.0,<3",
    "PyYAML>=6.0,<7",
    "tqdm>=4.65,<5",
    "pyarrow>=14,<16",
]

GENERATED_SOURCE_OVERRIDES = {
    "src/core/server.py",
    "src/core/utils/diffing/__init__.py",
}

PYPROJECT_DEV_DEPS = [
    "pytest>=8",
    "black>=24.10",
    "ruff>=0.6",
    "pre-commit>=3.0",
]

PYPROJECT_MCP_DEPS = [
    "mcp>=0.9,<1",
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
    if normalized.startswith("mcp_server/") and normalized.endswith(".py"):
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
    elif module_name.startswith("mcp_server.") or module_name == "mcp_server":
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
                if imported.startswith(("core", "config", "tests", "mcp_server")):
                    if _is_excluded_module(imported):
                        blocked.append(f"{relative_path}:{node.lineno} import {imported}")
                    else:
                        targets.add(imported)
        elif isinstance(node, ast.ImportFrom):
            base_module = _relative_import_module(module_name, node, is_package=is_package)
            if not base_module:
                continue
            if not base_module.startswith(("core", "config", "tests", "mcp_server")):
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


def _source_config_model_paths(repo_root: Path) -> list[str]:
    models_dir = repo_root / "config" / "models"
    if not models_dir.exists():
        return []

    return sorted(
        str(path.relative_to(repo_root)).replace("\\", "/")
        for path in models_dir.glob("*.json")
        if path.is_file()
    )


def _copy_source_config_models(destination: Path, repo_root: Path) -> list[str]:
    copied: list[str] = []
    for relative_path in _source_config_model_paths(repo_root):
        source_path = repo_root / relative_path
        destination_path = destination / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination_path)
        copied.append(relative_path)
    return copied


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

        text = _closure_scan_text(relative_path, absolute_path)
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
import json
from pathlib import Path


_ADMITTED_FILES = [
    "src/core/server.py",
    "src/core/api/config.py",
    "src/core/api/models.py",
    "src/core/api/status.py",
    "src/core/api/strategy.py",
    "src/core/config/validator.py",
    "src/core/config/legacy_schema_v1.json",
    "tests/integration/test_config_endpoints.py",
]


_WORKFLOW_FILES = [
    ".github/copilot-instructions.md",
    "AGENTS.md",
    "docs/SKELETON_SCOPE.md",
]


_TASK_FILES = [
    ".vscode/tasks.json",
    "tests/runtime/test_local_vscode_tasks.py",
]


_SETTINGS_FILES = [
    ".vscode/settings.json",
    "tests/runtime/test_local_vscode_settings.py",
]


_ENV_TEMPLATE_FILES = [
    ".env.example",
    "tests/runtime/test_local_env_template.py",
]


_PRECOMMIT_FILES = [
    ".pre-commit-config.yaml",
    "tests/runtime/test_local_precommit_config.py",
]


_EXTENSIONS_FILES = [
    ".vscode/extensions.json",
    "tests/runtime/test_local_vscode_extensions.py",
]


_API_SCRIPT_FILES = [
    "scripts/api/api_shell.py",
    "tests/runtime/test_local_api_shell_script.py",
]


_MCP_SCRIPT_FILES = [
    "scripts/mcp/mcp_stdio.py",
    "tests/runtime/test_local_mcp_script.py",
]


_PYTEST_SCRIPT_FILES = [
    "scripts/validate/pytest_suite.py",
    "tests/runtime/test_local_pytest_script.py",
]


_SCRIPT_FILES = [
    "scripts/smoke/backtest_smoke.py",
    "scripts/smoke/champion_smoke.py",
    "scripts/smoke/evaluate_champion_smoke.py",
    "scripts/smoke/fixture_smoke.py",
    "scripts/smoke/model_smoke.py",
    "scripts/smoke/smoke_suite.py",
    "tests/runtime/test_local_smoke_scripts.py",
]


_CONSOLE_SCRIPT_FILES = [
    "pyproject.toml",
    "src/genesis_core_v2_cli/console_scripts.py",
    "tests/governance/test_pyproject_console_scripts.py",
    "tests/runtime/test_installed_console_scripts.py",
]


_INSTALL_VERIFICATION_FILES = [
    "seed_manifest.json",
    "tests/runtime/test_installed_console_scripts.py",
]


_WORKSPACE_VERIFICATION_FILES = [
    "seed_manifest.json",
    ".vscode/tasks.json",
    ".vscode/launch.json",
    ".vscode/settings.json",
    ".vscode/extensions.json",
    "tests/runtime/test_local_vscode_tasks.py",
    "tests/runtime/test_local_vscode_launch.py",
    "tests/runtime/test_local_vscode_settings.py",
    "tests/runtime/test_local_vscode_extensions.py",
]


_BOOTSTRAP_VERIFICATION_FILES = [
    "seed_manifest.json",
    ".env.example",
    ".pre-commit-config.yaml",
    "tests/runtime/test_local_env_template.py",
    "tests/runtime/test_local_precommit_config.py",
]


_MCP_VERIFICATION_FILES = [
    "seed_manifest.json",
    ".vscode/mcp.json",
    "config/mcp_settings.json",
    "scripts/mcp/mcp_stdio.py",
    "tests/runtime/test_local_mcp_setup.py",
    "tests/runtime/test_local_mcp_script.py",
]


_MODULE_LOOP_FILES = [
    "src/core/server.py",
    "mcp_server/server.py",
    "scripts/validate/pytest_suite.py",
    "src/core/bootstrap/model_smoke.py",
    "src/core/bootstrap/smoke_suite.py",
    "tests/runtime/test_installed_console_scripts.py",
]


_LAUNCH_FILES = [
    ".vscode/launch.json",
    "tests/runtime/test_local_vscode_launch.py",
]


_MCP_FILES = [
    ".vscode/mcp.json",
    "config/mcp_settings.json",
    "mcp_server/__init__.py",
    "mcp_server/config.py",
    "mcp_server/resources.py",
    "mcp_server/server.py",
    "mcp_server/tools.py",
    "mcp_server/utils.py",
    "tests/runtime/test_local_mcp_setup.py",
]


_EXCLUDED_FILES = [
    "config/mcp_settings.remote_git.json",
    "config/mcp_settings.remote_safe.json",
    "mcp_server/remote_server.py",
    "src/core/api/account.py",
    "src/core/api/info.py",
    "src/core/api/paper.py",
    "src/core/api/public.py",
    "src/core/api/ui.py",
    "src/core/pipeline.py",
    "src/core/strategy/features.py",
    "src/core/utils/diffing/optuna_guard.py",
    "src/core/utils/diffing/results_diff.py",
    "src/core/utils/diffing/trial_cache.py",
    "src/core/utils/optuna_helpers.py",
    "config/runtime.json",
    "config/runtime.seed.json",
]

_EXCLUDED_PREFIXES = [
    "src/core/io",
    "src/core/optimizer",
    "data",
]

_EXCLUDED_JSON_PAYLOAD_DIRS = [
    "config/strategy/champions",
]

_EXCLUDED_MODULE_PREFIXES = [
    "core.api.account",
    "core.api.info",
    "core.api.paper",
    "core.api.public",
    "core.api.ui",
    "core.io",
    "core.optimizer",
    "core.pipeline",
    "core.strategy.features",
    "core.utils.diffing.optuna_guard",
    "core.utils.diffing.results_diff",
    "core.utils.diffing.trial_cache",
    "core.utils.optuna_helpers",
]


def _is_excluded_module(module: str) -> bool:
    return any(
        module == prefix or module.startswith(f"{prefix}.")
        for prefix in _EXCLUDED_MODULE_PREFIXES
    )


def test_seed_contains_admitted_local_api_shell_slice() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _ADMITTED_FILES:
        assert (repo_root / relative_path).exists(), relative_path


def test_seed_contains_skeleton_workflow_guidance() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _WORKFLOW_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    agents_text = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    instructions_text = (repo_root / ".github" / "copilot-instructions.md").read_text(
        encoding="utf-8"
    )
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert "Prioritize V2 skeleton completeness before content migration." in agents_text
    assert "Prefer generator-driven changes in `Genesis-Core` over manual drift in this repo." in instructions_text
    assert "Track A — skeleton completeness" in scope_text
    assert "Track B — authority migration" in scope_text


def test_seed_contains_local_mcp_shell() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _MCP_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")
    assert "local MCP stdio shell" in scope_text
    assert "remote MCP surfaces remain deferred" in scope_text


def test_seed_contains_local_mcp_script() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _MCP_SCRIPT_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert "Non-installed local MCP launcher:" in readme
    assert "scripts/mcp/mcp_stdio.py" in readme
    assert "scripts/mcp/mcp_stdio.py" in scope_text


def test_seed_contains_local_vscode_task_loop() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _TASK_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert "Local VS Code tasks:" in readme
    assert "genesis-v2: api shell" in readme
    assert "genesis-v2: mcp stdio" in readme
    assert "genesis-v2: pytest" in readme
    assert "genesis-v2: mcp stdio" in scope_text
    assert ".vscode/tasks.json" in scope_text


def test_seed_contains_local_vscode_settings() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _SETTINGS_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert ".vscode/settings.json" in readme
    assert "Python analysis/test settings" in readme
    assert ".vscode/settings.json" in scope_text


def test_seed_contains_local_env_template() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _ENV_TEMPLATE_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert ".env.example" in readme
    assert "tracked env bootstrap template" in readme
    assert ".env.example" in scope_text


def test_seed_contains_local_precommit_workflow() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _PRECOMMIT_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert ".pre-commit-config.yaml" in readme
    assert "Local pre-commit workflow" in readme
    assert ".pre-commit-config.yaml" in scope_text


def test_seed_contains_local_vscode_extensions() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _EXTENSIONS_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert ".vscode/extensions.json" in readme
    assert "Suggested VS Code extensions" in readme
    assert ".vscode/extensions.json" in scope_text


def test_seed_contains_local_api_shell_script() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _API_SCRIPT_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert "Non-installed local API launcher:" in readme
    assert "scripts/api/api_shell.py" in readme
    assert "scripts/api/api_shell.py" in scope_text


def test_seed_contains_local_pytest_script() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _PYTEST_SCRIPT_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert "Non-installed local pytest launcher:" in readme
    assert "scripts/validate/pytest_suite.py" in readme
    assert "scripts/validate/pytest_suite.py" in scope_text


def test_seed_contains_local_smoke_scripts() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _SCRIPT_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert "Non-installed local smoke scripts:" in readme
    assert "scripts/smoke/evaluate_champion_smoke.py" in readme
    assert "scripts/smoke/model_smoke.py" in readme
    assert "scripts/smoke/smoke_suite.py" in readme
    assert "scripts/smoke/model_smoke.py" in scope_text
    assert "scripts/smoke/*.py" in scope_text


def test_seed_contains_installed_console_script_loop() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _CONSOLE_SCRIPT_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert "Console scripts after editable install:" in readme
    assert "genesis-v2-api-shell" in readme
    assert "genesis-v2-model-smoke" in readme
    assert "genesis-v2-api-shell" in scope_text
    assert "genesis-v2-model-smoke" in scope_text
    assert 'python -m pip install -e ".[dev,mcp]"' in scope_text
    assert "tests/runtime/test_installed_console_scripts.py" in scope_text


def test_seed_contains_install_verification_manifest() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _INSTALL_VERIFICATION_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    manifest = json.loads((repo_root / "seed_manifest.json").read_text(encoding="utf-8"))
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert manifest["install_verification"] == {
        "editable_install_command": 'python -m pip install -e ".[dev,mcp]"',
        "installed_console_script_test_command": "pytest tests/runtime/test_installed_console_scripts.py -q",
        "installed_console_script_test_file": "tests/runtime/test_installed_console_scripts.py",
        "optional_mcp_install_command": 'python -m pip install -e ".[mcp]"',
    }
    assert manifest["install_verification"]["editable_install_command"] in readme
    assert manifest["install_verification"]["editable_install_command"] in scope_text
    assert manifest["install_verification"]["installed_console_script_test_command"] in readme
    assert manifest["install_verification"]["installed_console_script_test_command"] in scope_text


def test_seed_contains_workspace_verification_manifest() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _WORKSPACE_VERIFICATION_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    manifest = json.loads((repo_root / "seed_manifest.json").read_text(encoding="utf-8"))

    assert manifest["workspace_verification"] == {
        "extensions": {
            "runtime_test_file": "tests/runtime/test_local_vscode_extensions.py",
            "workspace_file": ".vscode/extensions.json",
        },
        "launch": {
            "runtime_test_file": "tests/runtime/test_local_vscode_launch.py",
            "workspace_file": ".vscode/launch.json",
        },
        "settings": {
            "runtime_test_file": "tests/runtime/test_local_vscode_settings.py",
            "workspace_file": ".vscode/settings.json",
        },
        "tasks": {
            "runtime_test_file": "tests/runtime/test_local_vscode_tasks.py",
            "workspace_file": ".vscode/tasks.json",
        },
    }


def test_seed_contains_bootstrap_verification_manifest() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _BOOTSTRAP_VERIFICATION_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    manifest = json.loads((repo_root / "seed_manifest.json").read_text(encoding="utf-8"))

    assert manifest["bootstrap_verification"] == {
        "env_template": {
            "runtime_test_file": "tests/runtime/test_local_env_template.py",
            "tracked_file": ".env.example",
        },
        "precommit": {
            "runtime_test_file": "tests/runtime/test_local_precommit_config.py",
            "tracked_file": ".pre-commit-config.yaml",
        },
    }


def test_seed_contains_mcp_verification_manifest() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _MCP_VERIFICATION_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    manifest = json.loads((repo_root / "seed_manifest.json").read_text(encoding="utf-8"))

    assert manifest["mcp_verification"] == {
        "workspace_registration": {
            "workspace_file": ".vscode/mcp.json",
            "config_file": "config/mcp_settings.json",
            "runtime_test_file": "tests/runtime/test_local_mcp_setup.py",
        },
        "local_launcher": {
            "tracked_file": "scripts/mcp/mcp_stdio.py",
            "runtime_test_file": "tests/runtime/test_local_mcp_script.py",
        },
    }


def test_seed_contains_editable_install_module_loop() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _MODULE_LOOP_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert "python -m uvicorn core.server:app --app-dir src --reload" in readme
    assert "python -m mcp_server.server" in readme
    assert "python -m pytest -q" in readme
    assert "python -m core.bootstrap.model_smoke" in readme
    assert "python -m core.bootstrap.smoke_suite" in readme
    assert "python -m uvicorn core.server:app --app-dir src --reload" in scope_text
    assert "python -m mcp_server.server" in scope_text
    assert "python -m pytest -q" in scope_text
    assert "python -m core.bootstrap.model_smoke" in scope_text
    assert "python -m core.bootstrap.smoke_suite" in scope_text


def test_seed_contains_local_vscode_launch_loop() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _LAUNCH_FILES:
        assert (repo_root / relative_path).exists(), relative_path

    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    scope_text = (repo_root / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert "Local VS Code debug profiles:" in readme
    assert "genesis-v2: mcp stdio" in readme
    assert "genesis-v2: smoke suite" in readme
    assert "genesis-v2: mcp stdio" in scope_text
    assert ".vscode/launch.json" in scope_text


def test_seed_excludes_legacy_and_stateful_surfaces() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_path in _EXCLUDED_FILES:
        assert not (repo_root / relative_path).exists(), relative_path

    for prefix in _EXCLUDED_PREFIXES:
        assert not (repo_root / prefix).exists(), prefix


def test_phase_one_seed_has_no_excluded_json_payloads() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    for relative_dir in _EXCLUDED_JSON_PAYLOAD_DIRS:
        candidate_dir = repo_root / relative_dir
        if not candidate_dir.exists():
            continue
        leaked = sorted(path.relative_to(repo_root).as_posix() for path in candidate_dir.rglob("*.json"))
        assert not leaked, relative_dir + "\\n" + "\\n".join(leaked)


def test_runtime_source_has_no_excluded_imports() -> None:
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


def _pyproject_console_scripts_test_content() -> str:
    return """from __future__ import annotations

import tomllib
from pathlib import Path


def test_pyproject_declares_local_tooling_console_scripts() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    payload = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))

    assert payload["project"]["scripts"] == {
        "genesis-v2-api-shell": "genesis_core_v2_cli.console_scripts:api_shell_main",
        "genesis-v2-mcp-stdio": "genesis_core_v2_cli.console_scripts:mcp_stdio_main",
        "genesis-v2-pytest": "genesis_core_v2_cli.console_scripts:pytest_suite_main",
        "genesis-v2-champion-smoke": "genesis_core_v2_cli.console_scripts:champion_smoke_main",
        "genesis-v2-evaluate-champion-smoke": "genesis_core_v2_cli.console_scripts:evaluate_champion_smoke_main",
        "genesis-v2-fixture-smoke": "genesis_core_v2_cli.console_scripts:fixture_smoke_main",
        "genesis-v2-backtest-smoke": "genesis_core_v2_cli.console_scripts:backtest_smoke_main",
        "genesis-v2-model-smoke": "genesis_core_v2_cli.console_scripts:model_smoke_main",
        "genesis-v2-smoke-suite": "genesis_core_v2_cli.console_scripts:smoke_suite_main",
    }


def test_pyproject_declares_narrow_local_tooling_defaults() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    payload = tomllib.loads((repo_root / "pyproject.toml").read_text(encoding="utf-8"))

    assert payload["tool"]["pytest"]["ini_options"]["norecursedirs"] == [
        "cache",
        "data",
        "logs",
        "results",
        ".venv",
    ]
    assert payload["tool"]["ruff"]["extend-exclude"] == [
        ".venv/",
        "cache/",
        "data/",
        "logs/",
        "results/",
    ]
    assert payload["tool"]["ruff"]["lint"]["select"] == ["E", "W", "F", "I", "B", "C4", "UP"]
    assert payload["tool"]["ruff"]["lint"]["ignore"] == ["E501", "B008", "C901"]
    assert payload["tool"]["black"]["extend-exclude"] == "(^cache/|^data/|^logs/|^results/)"
"""


def _backtest_defaults_content() -> str:
    content = _load_source_text(_repo_root() / "config" / "backtest_defaults.yaml")
    return content if content.endswith("\n") else f"{content}\n"


def _env_placeholder_lines() -> list[str]:
    return [
        "BEARER_TOKEN=change-me",
        "SYMBOL_MODE=realistic",
        "LOG_LEVEL=INFO",
    ]


def _env_placeholder_content() -> str:
    placeholder_lines = "\n".join(_env_placeholder_lines())
    return (
        "# Placeholder environment values for the generated Genesis-Core-V2 seed\n"
        "# Replace before using protected local config-write endpoints.\n"
        f"{placeholder_lines}\n"
    )


def _env_example_content() -> str:
    return "# Copy this file to .env for local use.\n" + _env_placeholder_content()


def _precommit_config_content() -> str:
    return (
        "repos:\n"
        "  - repo: https://github.com/psf/black\n"
        "    rev: 24.10.0\n"
        "    hooks:\n"
        "      - id: black\n"
        "        language_version: python3.11\n"
        "        files: \\.py$\n"
        "\n"
        "  - repo: https://github.com/astral-sh/ruff-pre-commit\n"
        "    rev: v0.6.9\n"
        "    hooks:\n"
        "      - id: ruff\n"
        "        language_version: python3.11\n"
        "        files: \\.py$\n"
        "\n"
        "  - repo: https://github.com/pre-commit/pre-commit-hooks\n"
        "    rev: v4.6.0\n"
        "    hooks:\n"
        "      - id: check-added-large-files\n"
        "        args: [--maxkb=1000]\n"
        "      - id: check-merge-conflict\n"
        "      - id: check-yaml\n"
        "      - id: end-of-file-fixer\n"
        "      - id: trailing-whitespace\n"
        "      - id: check-json\n"
    )


def _v2_mcp_settings_payload() -> dict[str, Any]:
    return {
        "server_name": "genesis-core-v2",
        "version": "0.1.0",
        "features": {
            "code_execution": False,
            "file_operations": True,
            "git_integration": True,
        },
        "log_file": "logs/mcp_server.log",
        "log_level": "INFO",
        "security": {
            "allowed_paths": [
                ".github",
                ".vscode",
                "AGENTS.md",
                "README.md",
                "config",
                "docs",
                "mcp_server",
                "pyproject.toml",
                "registry",
                "scripts",
                "seed_manifest.json",
                "src",
                "tests",
            ],
            "blocked_patterns": [
                ".git",
                "__pycache__",
                "*.pyc",
                "node_modules",
                ".env",
                "config/runtime.json",
                "config/runtime.seed.json",
                ".nonce_tracker.json",
                "dev.overrides.local.json",
            ],
            "execution_timeout_seconds": 15,
            "max_file_size_mb": 5,
        },
    }


def _v2_vscode_mcp_payload() -> dict[str, Any]:
    return {
        "servers": {
            "genesis-core-v2": {
                "command": "python",
                "args": ["scripts/mcp/mcp_stdio.py"],
                "env": {
                    "GENESIS_MCP_CONFIG_PATH": "config/mcp_settings.json",
                },
            }
        }
    }


def _v2_vscode_launch_payload() -> dict[str, Any]:
    return {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "genesis-v2: api shell",
                "type": "debugpy",
                "request": "launch",
                "program": "${workspaceFolder}/scripts/api/api_shell.py",
                "args": ["--reload"],
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "console": "integratedTerminal",
            },
            {
                "name": "genesis-v2: mcp stdio",
                "type": "debugpy",
                "request": "launch",
                "program": "${workspaceFolder}/scripts/mcp/mcp_stdio.py",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "console": "integratedTerminal",
            },
            {
                "name": "genesis-v2: smoke suite",
                "type": "debugpy",
                "request": "launch",
                "program": "${workspaceFolder}/scripts/smoke/smoke_suite.py",
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "console": "integratedTerminal",
            },
            {
                "name": "genesis-v2: pytest",
                "type": "debugpy",
                "request": "launch",
                "program": "${workspaceFolder}/scripts/validate/pytest_suite.py",
                "args": ["-q"],
                "cwd": "${workspaceFolder}",
                "env": {"PYTHONPATH": "${workspaceFolder}/src"},
                "console": "integratedTerminal",
                "purpose": ["debug-test"],
            },
        ],
    }


def _v2_vscode_settings_payload() -> dict[str, Any]:
    return {
        "python.analysis.extraPaths": ["${workspaceFolder}/src"],
        "python.envFile": "${workspaceFolder}/.env",
        "python.testing.cwd": "${workspaceFolder}",
        "python.testing.pytestArgs": ["-q"],
        "python.testing.pytestEnabled": True,
        "python.testing.unittestEnabled": False,
    }


def _v2_vscode_extensions_payload() -> dict[str, Any]:
    return {
        "recommendations": [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "charliermarsh.ruff",
        ],
        "unwantedRecommendations": [],
    }


def _v2_vscode_tasks_payload() -> dict[str, Any]:
    return {
        "version": "2.0.0",
        "options": {
            "cwd": "${workspaceFolder}",
            "env": {"PYTHONPATH": "${workspaceFolder}/src"},
        },
        "tasks": [
            {
                "label": "genesis-v2: api shell",
                "type": "shell",
                "command": "python",
                "args": ["scripts/api/api_shell.py", "--reload"],
                "isBackground": True,
                "problemMatcher": [],
                "presentation": {"panel": "dedicated", "reveal": "always"},
            },
            {
                "label": "genesis-v2: mcp stdio",
                "type": "shell",
                "command": "python",
                "args": ["scripts/mcp/mcp_stdio.py"],
                "isBackground": True,
                "problemMatcher": [],
                "presentation": {"panel": "dedicated", "reveal": "always"},
            },
            {
                "label": "genesis-v2: smoke suite",
                "type": "shell",
                "command": "python",
                "args": ["scripts/smoke/smoke_suite.py"],
                "presentation": {"panel": "shared", "reveal": "always"},
            },
            {
                "label": "genesis-v2: pytest",
                "type": "shell",
                "command": "python",
                "args": ["scripts/validate/pytest_suite.py", "-q"],
                "group": {"kind": "test", "isDefault": True},
                "presentation": {"panel": "shared", "reveal": "always"},
            },
        ],
    }


def _v2_agents_content() -> str:
    return """# AGENTS.md — Genesis-Core-V2 Skeleton Contract

## Purpose

`Genesis-Core-V2` is a generated, local-only skeleton repository.
`Genesis-Core` remains the source of truth until a slice is explicitly admitted and verified.

## Working rule

Prioritize V2 skeleton completeness before content migration.

## Track A — skeleton completeness

Use this track for:

- repo structure and generated workflow files
- local MCP stdio shell and safe editor hookup
- repo-local MCP launcher under `scripts/mcp/`
- repo-local API launcher under `scripts/api/`
- repo-local pytest launcher under `scripts/validate/`
- repo-local smoke scripts under `scripts/smoke/`
- local VS Code tasks, debug profiles, settings, and extension recommendations
- local-only API shell
- fixture-backed smoke tests
- README/docs that explain the current admitted boundary
- local developer and agent workflow guidance

## Track B — authority migration

Defer these to separate verified slices:

- strategy authority expansion
- config semantics and runtime authority
- backtest authority, comparison, readiness, and promotion surfaces
- remote MCP exposure and remote Git workflow surfaces
- exchange, paper, UI, and other private/live-adjacent edges
- freeze-sensitive surfaces

## Change workflow

1. Change the generator in `Genesis-Core`.
2. Regenerate `Genesis-Core-V2`.
3. Run the focused generator regressions in `Genesis-Core`.
4. Run `pytest -q` in `Genesis-Core-V2`.
5. Commit only green, scoped slices.

## Default

If a surface is not explicitly admitted into the seed, treat it as deferred.
"""


def _v2_copilot_instructions_content() -> str:
    return """# Copilot Instructions — Genesis-Core-V2

This repository is a skeleton-first, local-only V2 seed.
Read `AGENTS.md` and `docs/SKELETON_SCOPE.md` before widening scope.

## Default behavior

- Prefer the smallest admissible slice.
- Prioritize V2 skeleton completeness before content migration.
- Keep `Genesis-Core` as the source of truth for authority-bearing behavior until a slice is admitted.
- Prefer generator-driven changes in `Genesis-Core` over manual drift in this repo.
- Keep the local-only API shell runnable and tested.
- Keep the local MCP stdio shell local-first and safe by default.
- Prefer generated local `scripts/mcp/mcp_stdio.py` or `.vscode/mcp.json` for non-installed MCP startup.
- Prefer generated local `scripts/api/api_shell.py` or editor task/debug profiles for non-installed API startup.
- Prefer generated local `scripts/validate/pytest_suite.py` or editor task/debug profiles for non-installed pytest loops.
- Prefer generated local `scripts/smoke/*.py` wrappers or `python -m core.bootstrap...` commands for non-installed smoke loops.
- Prefer the generated local VS Code tasks, debug profiles, settings, and extension recommendations for repeatable API/smoke/test loops when working interactively.
- Prefer fixture-backed smoke tests before moving wider runtime content.

## Out of scope by default

- exchange, paper, UI, and private runtime edges
- remote MCP server and remote MCP config surfaces
- runtime state and champion authority payloads
- freeze-sensitive and governance-sensitive authority surfaces
- unverified content migration for its own sake
"""


def _v2_skeleton_scope_content() -> str:
    return """# Genesis-Core-V2 Skeleton Scope

## Current target

`Genesis-Core-V2` is intentionally a thin, runnable shell:

- minimal repo structure
- local-only API
- local MCP stdio shell
- generated workflow guidance for agent-driven work
- fixture-backed smoke tests
- no exchange, no UI, and no private runtime edges

`Genesis-Core` remains the source of truth until each slice is proven.

## Track A — skeleton completeness

Included in the current priority lane:

- README and local workflow docs
- `AGENTS.md`, `.github/copilot-instructions.md`, and `.pre-commit-config.yaml`
- `.vscode/mcp.json`, `.vscode/tasks.json`, `.vscode/launch.json`, `.vscode/settings.json`, and `.vscode/extensions.json` for local editor workflow
- tracked local env bootstrap template (`.env.example`) plus ignored local placeholder `.env`
- narrow local pytest/ruff/black defaults in `pyproject.toml`
- repo-local MCP launcher (`scripts/mcp/mcp_stdio.py`) for non-installed stdio startup
- repo-local API launcher (`scripts/api/api_shell.py`) for non-installed startup
- repo-local pytest launcher (`scripts/validate/pytest_suite.py`) for non-installed test execution
- repo-local smoke scripts (`scripts/smoke/*.py`) for non-installed execution
- `config/mcp_settings.json` and `mcp_server/**` for local MCP use
- local-only API shell (`config`, `status`, `models`, `strategy`)
- fixture-backed smoke tests and console scripts
- explicitly admitted non-sensitive config/model artifacts already carried into the seed

## Track B — authority migration

Deferred to separate verified slices:

- strategy authority expansion
- config semantics and runtime authority
- backtest authority plus comparison/readiness surfaces
- remote MCP surfaces remain deferred (`mcp_server/remote_server.py`, remote-safe/git configs)
- exchange, paper, UI, and other private/live-adjacent edges
- freeze-sensitive surfaces

## Verification loop

- In `Genesis-Core`: `python -m pytest tests/utils/test_open_v2_runtime_seed.py -q`
- Regenerate the seed: `python scripts/extract/open_v2_runtime_seed.py --clean`
- In `Genesis-Core-V2`: `python -m pytest -q`
- Local task loop: `genesis-v2: api shell`, `genesis-v2: mcp stdio`, `genesis-v2: smoke suite`, `genesis-v2: pytest`
- Local debug loop: `genesis-v2: api shell`, `genesis-v2: mcp stdio`, `genesis-v2: smoke suite`, `genesis-v2: pytest`
- Local editor settings: `python.analysis.extraPaths`, `python.testing.*`, `python.envFile`
- Local editor recommendations: `ms-python.python`, `ms-python.vscode-pylance`, `charliermarsh.ruff`
- Local pre-commit workflow: `pre-commit install`, then `pre-commit run --all-files`
- Local QA defaults: `pytest` recursion guards plus narrow `ruff`/`black` excludes in `pyproject.toml`
- Non-installed local MCP launcher: `python scripts/mcp/mcp_stdio.py`, optional config probe via `python scripts/mcp/mcp_stdio.py --print-config`
- Non-installed local API launcher: `python scripts/api/api_shell.py`, optional reload via `python scripts/api/api_shell.py --reload`
- Non-installed local pytest launcher: `python scripts/validate/pytest_suite.py`, optional focused run via `python scripts/validate/pytest_suite.py tests/runtime/test_local_api_shell_script.py -q`
- Non-installed local smoke scripts: `python scripts/smoke/fixture_smoke.py`, `python scripts/smoke/backtest_smoke.py`, `python scripts/smoke/champion_smoke.py`, `python scripts/smoke/evaluate_champion_smoke.py`, `python scripts/smoke/model_smoke.py`, `python scripts/smoke/smoke_suite.py`
- Installable local console scripts: `genesis-v2-api-shell`, `genesis-v2-mcp-stdio`, `genesis-v2-pytest`, `genesis-v2-champion-smoke`, `genesis-v2-evaluate-champion-smoke`, `genesis-v2-fixture-smoke`, `genesis-v2-backtest-smoke`, `genesis-v2-model-smoke`, `genesis-v2-smoke-suite`
- Installable console-script verification: `python -m pip install -e ".[dev,mcp]"`, then `pytest tests/runtime/test_installed_console_scripts.py -q`
- Editable-install module loop: `python -m uvicorn core.server:app --app-dir src --reload`, `python -m mcp_server.server`, `python -m pytest -q`
- Editable-install smoke module loop: `python -m core.bootstrap.model_smoke`, `python -m core.bootstrap.champion_smoke`, `python -m core.bootstrap.evaluate_champion_smoke`, `python -m core.bootstrap.fixture_smoke`, `python -m core.bootstrap.backtest_smoke`, `python -m core.bootstrap.smoke_suite`
- Optional local MCP install: `python -m pip install -e ".[mcp]"`
"""


def _runtime_local_mcp_setup_test_content() -> str:
    return """from __future__ import annotations

import json
from pathlib import Path

from mcp_server.config import load_config
from mcp_server.server import TOOLS


def test_local_mcp_files_encode_safe_skeleton_defaults() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    vscode_payload = json.loads((repo_root / ".vscode" / "mcp.json").read_text(encoding="utf-8"))
    settings_payload = json.loads(
        (repo_root / "config" / "mcp_settings.json").read_text(encoding="utf-8")
    )

    server = vscode_payload["servers"]["genesis-core-v2"]
    assert server["args"] == ["scripts/mcp/mcp_stdio.py"]
    assert server["env"]["GENESIS_MCP_CONFIG_PATH"] == "config/mcp_settings.json"

    assert settings_payload["server_name"] == "genesis-core-v2"
    assert settings_payload["features"] == {
        "code_execution": False,
        "file_operations": True,
        "git_integration": True,
    }
    assert ".vscode" in settings_payload["security"]["allowed_paths"]
    assert "mcp_server" in settings_payload["security"]["allowed_paths"]
    assert ".env" in settings_payload["security"]["blocked_patterns"]
    assert "config/runtime.json" in settings_payload["security"]["blocked_patterns"]


def test_local_mcp_server_loads_generated_v2_settings() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    config = load_config(repo_root / "config" / "mcp_settings.json")
    tool_names = {tool.name for tool in TOOLS}

    assert config.server_name == "genesis-core-v2"
    assert config.features.file_operations is True
    assert config.features.code_execution is False
    assert config.features.git_integration is True
    assert {
        "read_file",
        "write_file",
        "list_directory",
        "get_project_structure",
        "search_code",
        "get_git_status",
    }.issubset(tool_names)
"""


def _runtime_local_vscode_tasks_test_content() -> str:
    return """from __future__ import annotations

import json
from pathlib import Path


EXPECTED_TASK_ARGS = {
    "genesis-v2: api shell": ["scripts/api/api_shell.py", "--reload"],
    "genesis-v2: mcp stdio": ["scripts/mcp/mcp_stdio.py"],
    "genesis-v2: smoke suite": ["scripts/smoke/smoke_suite.py"],
    "genesis-v2: pytest": ["scripts/validate/pytest_suite.py", "-q"],
}


def test_local_vscode_tasks_encode_repeatable_skeleton_loop() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    payload = json.loads((repo_root / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
    tasks = {task["label"]: task for task in payload["tasks"]}

    assert payload["version"] == "2.0.0"
    assert payload["options"] == {
        "cwd": "${workspaceFolder}",
        "env": {"PYTHONPATH": "${workspaceFolder}/src"},
    }
    assert set(EXPECTED_TASK_ARGS).issubset(tasks)

    for label, expected_args in EXPECTED_TASK_ARGS.items():
        assert tasks[label]["command"] == "python"
        assert tasks[label]["args"] == expected_args

    assert tasks["genesis-v2: api shell"]["isBackground"] is True
    assert tasks["genesis-v2: mcp stdio"]["isBackground"] is True
    assert tasks["genesis-v2: pytest"]["group"] == {"kind": "test", "isDefault": True}
"""


def _runtime_local_vscode_launch_test_content() -> str:
    return """from __future__ import annotations

import json
from pathlib import Path


EXPECTED_LAUNCH_PROGRAMS = {
    "genesis-v2: api shell": "${workspaceFolder}/scripts/api/api_shell.py",
    "genesis-v2: mcp stdio": "${workspaceFolder}/scripts/mcp/mcp_stdio.py",
    "genesis-v2: smoke suite": "${workspaceFolder}/scripts/smoke/smoke_suite.py",
    "genesis-v2: pytest": "${workspaceFolder}/scripts/validate/pytest_suite.py",
}


def test_local_vscode_launch_profiles_encode_repeatable_debug_loop() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    payload = json.loads((repo_root / ".vscode" / "launch.json").read_text(encoding="utf-8"))
    configs = {config["name"]: config for config in payload["configurations"]}

    assert payload["version"] == "0.2.0"
    assert set(EXPECTED_LAUNCH_PROGRAMS).issubset(configs)

    for name, expected_program in EXPECTED_LAUNCH_PROGRAMS.items():
        assert configs[name]["type"] == "debugpy"
        assert configs[name]["request"] == "launch"
        assert configs[name]["program"] == expected_program
        assert configs[name]["cwd"] == "${workspaceFolder}"
        assert configs[name]["env"] == {"PYTHONPATH": "${workspaceFolder}/src"}
        assert configs[name]["console"] == "integratedTerminal"

    assert configs["genesis-v2: api shell"]["args"] == ["--reload"]
    assert configs["genesis-v2: mcp stdio"].get("args", []) == []
    assert configs["genesis-v2: smoke suite"].get("args", []) == []
    assert configs["genesis-v2: pytest"]["args"] == ["-q"]
    assert configs["genesis-v2: pytest"]["purpose"] == ["debug-test"]
"""


def _runtime_local_vscode_settings_test_content() -> str:
    return """from __future__ import annotations

import json
from pathlib import Path


def test_local_vscode_settings_align_python_analysis_and_test_discovery() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    payload = json.loads((repo_root / ".vscode" / "settings.json").read_text(encoding="utf-8"))

    assert payload["python.analysis.extraPaths"] == ["${workspaceFolder}/src"]
    assert payload["python.envFile"] == "${workspaceFolder}/.env"
    assert payload["python.testing.cwd"] == "${workspaceFolder}"
    assert payload["python.testing.pytestArgs"] == ["-q"]
    assert payload["python.testing.pytestEnabled"] is True
    assert payload["python.testing.unittestEnabled"] is False
"""


def _runtime_local_vscode_extensions_test_content() -> str:
    return """from __future__ import annotations

import json
from pathlib import Path


def test_local_vscode_extensions_recommend_python_workflow_stack() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    payload = json.loads((repo_root / ".vscode" / "extensions.json").read_text(encoding="utf-8"))

    assert payload["recommendations"] == [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
    ]
    assert payload["unwantedRecommendations"] == []
"""


def _runtime_local_env_template_test_content() -> str:
    return """from __future__ import annotations

from pathlib import Path


def test_local_env_example_tracks_the_narrow_placeholder_values() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    env_text = (repo_root / ".env").read_text(encoding="utf-8")
    template_text = (repo_root / ".env.example").read_text(encoding="utf-8")

    assert "# Copy this file to .env for local use." in template_text
    for expected_line in [
        "BEARER_TOKEN=change-me",
        "SYMBOL_MODE=realistic",
        "LOG_LEVEL=INFO",
    ]:
        assert expected_line in env_text
        assert expected_line in template_text
"""


def _runtime_local_precommit_config_test_content() -> str:
    return """from __future__ import annotations

from pathlib import Path

import yaml


def test_local_precommit_config_encodes_narrow_dev_hooks() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    payload = yaml.safe_load((repo_root / ".pre-commit-config.yaml").read_text(encoding="utf-8"))

    hook_ids = [
        hook["id"]
        for repo in payload["repos"]
        for hook in repo.get("hooks", [])
    ]
    assert hook_ids == [
        "black",
        "ruff",
        "check-added-large-files",
        "check-merge-conflict",
        "check-yaml",
        "end-of-file-fixer",
        "trailing-whitespace",
        "check-json",
    ]
"""


def _runtime_local_smoke_script_content(module_name: str) -> str:
    return f"""from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / \"src\"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from {module_name} import main as _target_main


def main() -> int:
    return _target_main()


if __name__ == \"__main__\":
    raise SystemExit(main())
"""


def _runtime_local_smoke_scripts_test_content() -> str:
    return """from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    ("relative_path", "expected_pairs"),
    [
        ("scripts/smoke/fixture_smoke.py", {"action": "NONE"}),
        ("scripts/smoke/backtest_smoke.py", {"trade_count": 1, "deterministic": True}),
        ("scripts/smoke/champion_smoke.py", {"version": "seed_champion_fixture_v1"}),
        (
            "scripts/smoke/evaluate_champion_smoke.py",
            {"action": "NONE", "champion_source": "registry/fixtures/champions/tBTCUSD_1h.json"},
        ),
        ("scripts/smoke/model_smoke.py", {"schema": ["ema_50"]}),
        ("scripts/smoke/smoke_suite.py", {"suite": "runtime_smoke_suite_v1"}),
    ],
)
def test_local_smoke_scripts_execute_without_editable_install(
    relative_path: str,
    expected_pairs: dict[str, object],
) -> None:
    repo_root = Path(__file__).resolve().parents[2]

    completed = subprocess.run(
        [sys.executable, str(repo_root / relative_path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)

    for key, expected_value in expected_pairs.items():
        assert payload.get(key) == expected_value
"""


def _runtime_local_api_shell_script_content() -> str:
    return """from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import uvicorn

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

import core.server as server_mod


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local Genesis-Core-V2 API shell")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--print-config", action="store_true")
    return parser


def build_runtime_config(*, host: str, port: int, reload: bool) -> dict[str, Any]:
    return {
        "app": "core.server:app",
        "app_dir": str(SRC_ROOT),
        "host": host,
        "port": port,
        "reload": reload,
        "module_file": str(Path(server_mod.__file__).resolve()),
        "route_count": len(server_mod.app.routes),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = build_runtime_config(host=str(args.host), port=int(args.port), reload=bool(args.reload))
    if args.print_config:
        print(json.dumps(config, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    uvicorn.run(
        config["app"],
        app_dir=config["app_dir"],
        host=config["host"],
        port=config["port"],
        reload=config["reload"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _runtime_local_api_shell_script_test_content() -> str:
    return """from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_local_api_shell_script_prints_runtime_config() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    completed = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "api" / "api_shell.py"), "--print-config"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["app"] == "core.server:app"
    assert payload["host"] == "127.0.0.1"
    assert payload["port"] == 8000
    assert payload["reload"] is False
    assert payload["module_file"].replace("\\\\", "/").endswith("/src/core/server.py")
    assert payload["route_count"] >= 4
"""


def _runtime_local_mcp_script_content() -> str:
    return """from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "mcp_settings.json"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

os.environ["GENESIS_MCP_CONFIG_PATH"] = str(DEFAULT_CONFIG_PATH)

import mcp_server.server as server_mod


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local Genesis-Core-V2 MCP stdio shell")
    parser.add_argument("--print-config", action="store_true")
    return parser


def build_runtime_config() -> dict[str, Any]:
    return {
        "config_env": os.environ.get("GENESIS_MCP_CONFIG_PATH", ""),
        "config_path": str(DEFAULT_CONFIG_PATH),
        "feature_flags": {
            "file_operations": server_mod.config.features.file_operations,
            "code_execution": server_mod.config.features.code_execution,
            "git_integration": server_mod.config.features.git_integration,
        },
        "log_level": server_mod.config.log_level,
        "module_file": str(Path(server_mod.__file__).resolve()),
        "server_name": server_mod.config.server_name,
        "tool_count": len(server_mod.TOOLS),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = build_runtime_config()
    if args.print_config:
        print(json.dumps(config, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    asyncio.run(server_mod.main())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _runtime_local_mcp_script_test_content() -> str:
    return """from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_local_mcp_script_prints_runtime_config() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    completed = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "mcp" / "mcp_stdio.py"), "--print-config"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["server_name"] == "genesis-core-v2"
    assert payload["log_level"] == "INFO"
    assert payload["feature_flags"] == {
        "file_operations": True,
        "code_execution": False,
        "git_integration": True,
    }
    assert payload["config_env"].replace("\\\\", "/").endswith("/config/mcp_settings.json")
    assert payload["config_path"].replace("\\\\", "/").endswith("/config/mcp_settings.json")
    assert payload["module_file"].replace("\\\\", "/").endswith("/mcp_server/server.py")
    assert payload["tool_count"] >= 6
"""


def _runtime_local_pytest_script_content() -> str:
    return """from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
DEFAULT_PYTEST_ARGS = ["-q"]


def _prefer_local_src() -> None:
    normalized_src = str(SRC_ROOT)
    if normalized_src not in sys.path:
        sys.path.insert(0, normalized_src)

    existing = [entry for entry in os.environ.get("PYTHONPATH", "").split(os.pathsep) if entry]
    if normalized_src not in existing:
        os.environ["PYTHONPATH"] = os.pathsep.join([normalized_src, *existing]) if existing else normalized_src


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local Genesis-Core-V2 pytest suite")
    parser.add_argument("--print-config", action="store_true")
    return parser


def build_runtime_config(pytest_args: list[str] | None = None) -> dict[str, Any]:
    return {
        "cwd": str(REPO_ROOT),
        "src_root": str(SRC_ROOT),
        "pythonpath": os.environ.get("PYTHONPATH", ""),
        "pytest_args": list(pytest_args or DEFAULT_PYTEST_ARGS),
    }


def main(argv: list[str] | None = None) -> int:
    _prefer_local_src()
    parsed_args, pytest_args = build_parser().parse_known_args(argv)
    config = build_runtime_config(pytest_args or DEFAULT_PYTEST_ARGS)
    if parsed_args.print_config:
        print(json.dumps(config, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    return int(pytest.main(config["pytest_args"]))


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _runtime_local_pytest_script_test_content() -> str:
    return """from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def test_local_pytest_script_prints_runtime_config() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    completed = subprocess.run(
        [sys.executable, str(repo_root / "scripts" / "validate" / "pytest_suite.py"), "--print-config"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["cwd"].replace("\\\\", "/").endswith("/Genesis-Core-V2")
    assert payload["src_root"].replace("\\\\", "/").endswith("/Genesis-Core-V2/src")
    assert payload["pytest_args"] == ["-q"]
    assert payload["pythonpath"].split(os.pathsep)[0].replace("\\\\", "/").endswith(
        "/Genesis-Core-V2/src"
    )


def test_local_pytest_script_runs_focused_runtime_test() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    completed = subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts" / "validate" / "pytest_suite.py"),
            "tests/runtime/test_local_api_shell_script.py",
            "-q",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    combined_output = completed.stdout + completed.stderr

    assert combined_output.strip()
"""


def _local_api_server_content() -> str:
    return """from contextlib import asynccontextmanager

from fastapi import FastAPI

from core.api.config import router as config_router
from core.api.models import reload_models, router as models_router
from core.api.status import _AUTH, debug_auth, health, router as status_router
from core.api.strategy import router as strategy_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"Lifespan event handler for startup only in the local-only V2 API shell.\"\"\"
    try:
        _, h, v = _AUTH.get()
        print(f\"CONFIG_VERSION={v} CONFIG_HASH={h[:12]}\")
    except Exception as e:
        print(f\"CONFIG_READ_FAILED: {e}\")

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(config_router)
app.include_router(status_router)
app.include_router(models_router)
app.include_router(strategy_router)

__all__ = [
    \"app\",
    \"debug_auth\",
    \"health\",
    \"models_router\",
    \"reload_models\",
    \"status_router\",
    \"strategy_router\",
]
"""


def _genesis_core_v2_cli_init_content() -> str:
    return '''"""Console-script helpers for the runtime-only V2 seed."""

from __future__ import annotations

__all__: list[str] = []
'''


def _genesis_core_v2_cli_console_scripts_content() -> str:
    return """from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

LOCAL_REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_SRC_ROOT = LOCAL_REPO_ROOT / "src"
DEFAULT_MCP_CONFIG_PATH = LOCAL_REPO_ROOT / "config" / "mcp_settings.json"
DEFAULT_PYTEST_ARGS = ["-q"]


def _prefer_local_paths() -> None:
    normalized_local_src = str(LOCAL_SRC_ROOT.resolve())
    normalized_local_repo = str(LOCAL_REPO_ROOT.resolve())
    filtered: list[str] = []
    for entry in sys.path:
        try:
            normalized_entry = str(Path(entry).resolve())
        except Exception:
            normalized_entry = entry
        if normalized_entry in {normalized_local_src, normalized_local_repo}:
            continue
        filtered.append(entry)
    sys.path[:] = [str(LOCAL_SRC_ROOT), str(LOCAL_REPO_ROOT), *filtered]


def _prefer_local_pythonpath() -> None:
    normalized_src = str(LOCAL_SRC_ROOT)
    existing = [entry for entry in os.environ.get("PYTHONPATH", "").split(os.pathsep) if entry]
    if normalized_src not in existing:
        os.environ["PYTHONPATH"] = os.pathsep.join([normalized_src, *existing]) if existing else normalized_src


def _load_api_server_module():
    import core.server as server_mod

    return server_mod


def _load_mcp_server_module():
    os.environ["GENESIS_MCP_CONFIG_PATH"] = str(DEFAULT_MCP_CONFIG_PATH)

    import mcp_server.server as server_mod

    return server_mod


def _build_api_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local Genesis-Core-V2 API shell")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument("--print-config", action="store_true")
    return parser


def _build_api_runtime_config(args: argparse.Namespace) -> dict[str, Any]:
    server_mod = _load_api_server_module()
    app = getattr(server_mod, "app")
    routes = getattr(app, "routes", [])
    return {
        "app": "core.server:app",
        "app_dir": str(LOCAL_SRC_ROOT),
        "host": args.host,
        "port": args.port,
        "reload": bool(args.reload),
        "module_file": str(Path(server_mod.__file__).resolve()),
        "route_count": len(routes),
    }


def api_shell_main(argv: list[str] | None = None) -> int:
    args = _build_api_parser().parse_args(argv)
    config = _build_api_runtime_config(args)
    if args.print_config:
        print(json.dumps(config, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    import uvicorn

    uvicorn.run(
        config["app"],
        app_dir=config["app_dir"],
        host=config["host"],
        port=config["port"],
        reload=config["reload"],
    )
    return 0


def _build_mcp_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local Genesis-Core-V2 MCP stdio shell")
    parser.add_argument("--print-config", action="store_true")
    return parser


def _build_mcp_runtime_config(server_mod) -> dict[str, Any]:
    return {
        "config_env": os.environ.get("GENESIS_MCP_CONFIG_PATH", ""),
        "config_path": str(DEFAULT_MCP_CONFIG_PATH),
        "feature_flags": {
            "file_operations": server_mod.config.features.file_operations,
            "code_execution": server_mod.config.features.code_execution,
            "git_integration": server_mod.config.features.git_integration,
        },
        "log_level": server_mod.config.log_level,
        "module_file": str(Path(server_mod.__file__).resolve()),
        "server_name": server_mod.config.server_name,
        "tool_count": len(server_mod.TOOLS),
    }


def mcp_stdio_main(argv: list[str] | None = None) -> int:
    args = _build_mcp_parser().parse_args(argv)
    try:
        server_mod = _load_mcp_server_module()
    except ModuleNotFoundError as exc:
        missing_name = getattr(exc, "name", "mcp")
        raise SystemExit(
            f'genesis-v2-mcp-stdio requires the [{missing_name}] dependency; install with `python -m pip install -e ".[mcp]"`.'
        ) from exc

    config = _build_mcp_runtime_config(server_mod)
    if args.print_config:
        print(json.dumps(config, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    asyncio.run(server_mod.main())
    return 0


def _build_pytest_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the local Genesis-Core-V2 pytest suite")
    parser.add_argument("--print-config", action="store_true")
    return parser


def _build_pytest_runtime_config(pytest_args: list[str] | None = None) -> dict[str, Any]:
    return {
        "cwd": str(LOCAL_REPO_ROOT),
        "src_root": str(LOCAL_SRC_ROOT),
        "pythonpath": os.environ.get("PYTHONPATH", ""),
        "pytest_args": list(pytest_args or DEFAULT_PYTEST_ARGS),
    }


def pytest_suite_main(argv: list[str] | None = None) -> int:
    _prefer_local_pythonpath()
    parsed_args, pytest_args = _build_pytest_parser().parse_known_args(argv)
    config = _build_pytest_runtime_config(pytest_args or DEFAULT_PYTEST_ARGS)
    if parsed_args.print_config:
        print(json.dumps(config, indent=2, ensure_ascii=False, sort_keys=True))
        return 0

    os.chdir(LOCAL_REPO_ROOT)

    try:
        import pytest
    except ModuleNotFoundError as exc:
        raise SystemExit(
            'genesis-v2-pytest requires pytest; install with `python -m pip install -e ".[dev]"`.'
        ) from exc

    return int(pytest.main(config["pytest_args"]))


_prefer_local_paths()

from core.bootstrap.backtest_smoke import main as backtest_smoke_main
from core.bootstrap.champion_smoke import main as champion_smoke_main
from core.bootstrap.evaluate_champion_smoke import main as evaluate_champion_smoke_main
from core.bootstrap.fixture_smoke import main as fixture_smoke_main
from core.bootstrap.model_smoke import main as model_smoke_main
from core.bootstrap.smoke_suite import main as smoke_suite_main

__all__ = [
    "api_shell_main",
    "mcp_stdio_main",
    "pytest_suite_main",
    "champion_smoke_main",
    "evaluate_champion_smoke_main",
    "fixture_smoke_main",
    "backtest_smoke_main",
    "model_smoke_main",
    "smoke_suite_main",
]
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


def _closure_scan_text(relative_path: str, absolute_path: Path) -> str:
    normalized = relative_path.replace("\\", "/")
    if normalized == "src/core/server.py":
        return _local_api_server_content()
    if normalized == "src/core/utils/diffing/__init__.py":
        return _runtime_diffing_init_content()
    return _load_source_text(absolute_path)


def _runtime_pipeline_smoke_test_content() -> str:
    return """from __future__ import annotations

from types import SimpleNamespace


def _synthetic_candles(n: int = 80) -> dict[str, list[float]]:
    close = [100.0 + (i * 0.5) for i in range(n)]
    open_ = [close[0]] + close[:-1]
    high = [max(o, c) + 0.5 for o, c in zip(open_, close, strict=False)]
    low = [min(o, c) - 0.5 for o, c in zip(open_, close, strict=False)]
    volume = [100.0] * n
    timestamp = [float(i * 3600) for i in range(n)]
    return {
        "timestamp": timestamp,
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    }


def test_runtime_seed_evaluate_pipeline_smoke(monkeypatch) -> None:
    monkeypatch.setenv("GENESIS_DISABLE_METRICS", "1")

    from core.strategy import evaluate as evaluate_mod

    dummy_champion = SimpleNamespace(config={}, source="seed_dummy")
    monkeypatch.setattr(
        evaluate_mod.champion_loader,
        "load_cached",
        lambda *_args, **_kwargs: dummy_champion,
    )
    monkeypatch.setattr(
        evaluate_mod,
        "predict_proba_for",
        lambda *_args, **_kwargs: (
            {"buy": 0.55, "sell": 0.45},
            {"schema": [], "versions": {}},
        ),
    )
    monkeypatch.setattr(
        evaluate_mod,
        "compute_confidence",
        lambda *_args, **_kwargs: (
            {"buy": 0.55, "sell": 0.45, "overall": 0.55},
            {"versions": {}},
        ),
    )
    monkeypatch.setattr(
        evaluate_mod,
        "decide",
        lambda *_args, **_kwargs: (
            "NONE",
            {"versions": {}, "reasons": [], "state_out": {}, "size": 0.0},
        ),
    )

    candles = _synthetic_candles()
    configs = {
        "_global_index": len(candles["close"]) - 1,
        "thresholds": {
            "entry_conf_overall": 0.5,
            "regime_proba": {"balanced": 0.55},
        },
        "gates": {"hysteresis_steps": 2, "cooldown_bars": 0},
        "risk": {"risk_map": [[0.5, 0.01], [0.6, 0.02]]},
        "ev": {"R_default": 1.5},
        "precomputed_features": {"ema_50": list(candles["close"])},
    }

    result, meta = evaluate_mod.evaluate_pipeline(
        candles,
        policy={"symbol": "tBTCUSD", "timeframe": "1h"},
        configs=configs,
        state={},
    )

    assert result["action"] == "NONE"
    assert isinstance(result.get("features"), dict)
    assert result.get("regime") in {"bull", "bear", "ranging", "balanced"}
    assert meta.get("decision", {}).get("size") == 0.0
    assert meta.get("champion", {}).get("source") == "explicit_backtest_config"
"""


def _runtime_fixture_payload() -> dict[str, Any]:
    bar_count = 120
    close = [100.0 + (i * 0.25) for i in range(bar_count)]
    open_ = [close[0]] + close[:-1]
    high = [max(o, c) + 0.5 for o, c in zip(open_, close, strict=False)]
    low = [min(o, c) - 0.5 for o, c in zip(open_, close, strict=False)]
    volume = [100.0 + float(i % 5) for i in range(bar_count)]
    timestamp = [float(i * 3600) for i in range(bar_count)]

    return {
        "name": "runtime_fixture_smoke_minimal",
        "policy": {"symbol": "tBTCUSD", "timeframe": "1h"},
        "configs": {
            "thresholds": {
                "entry_conf_overall": 0.7,
                "regime_proba": {"balanced": 0.55},
            },
            "gates": {"hysteresis_steps": 2, "cooldown_bars": 0},
            "risk": {"risk_map": [[0.6, 0.005], [0.7, 0.01]]},
            "ev": {"R_default": 1.5},
        },
        "candles": {
            "timestamp": timestamp,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        },
    }


def _runtime_champion_fixture_payload() -> dict[str, Any]:
    config = dict(_runtime_fixture_payload()["configs"])
    config["meta"] = {"note": "seed_fixture_champion"}
    config["exit"] = {"enabled": False}
    return {
        "created_at": "seed_champion_fixture_v1",
        "symbol": "tBTCUSD",
        "timeframe": "1h",
        "metadata": {
            "note": "Synthetic local champion fixture for the runtime-only V2 seed.",
        },
        "merged_config": config,
    }


def _runtime_model_fixture_payload() -> dict[str, Any]:
    return {
        "version": "seed_model_fixture_v1",
        "calibration_version": "seed_model_fixture_v1",
        "schema": ["ema_50"],
        "buy": {
            "w": [0.0],
            "b": 0.2,
            "calib": {"a": 1.0, "b": 0.0},
        },
        "sell": {
            "w": [0.0],
            "b": -0.2,
            "calib": {"a": 1.0, "b": 0.0},
        },
        "calibration_by_regime": {
            "buy": {"balanced": {"a": 1.0, "b": 0.1}},
            "sell": {"balanced": {"a": 1.0, "b": -0.1}},
        },
    }


def _runtime_model_registry_fixture_payload() -> dict[str, Any]:
    return {
        "tBTCUSD:1h": {
            "champion": "config/models/tBTCUSD_1h.json",
        }
    }


def _runtime_bootstrap_init_content() -> str:
    return '''"""Bootstrap helpers for the runtime-only V2 seed."""

from __future__ import annotations

__all__: list[str] = []
'''


def _runtime_bootstrap_module_content() -> str:
    return """from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.strategy.confidence import compute_confidence
from core.strategy.decision import decide
from core.strategy.features_asof import extract_features_backtest
from core.strategy.model_registry import ModelRegistry
from core.strategy.prob_model import predict_proba_for
from core.strategy.regime import detect_regime_from_candles

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FIXTURE_PATH = REPO_ROOT / "registry" / "fixtures" / "runtime_fixture_smoke_minimal.json"
FIXTURE_MODEL_ROOT = REPO_ROOT / "registry" / "fixtures" / "model_registry"


def load_fixture(path: Path | None = None) -> dict[str, Any]:
    fixture_path = Path(path) if path is not None else DEFAULT_FIXTURE_PATH
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Runtime fixture payload must be a JSON object")
    return payload


def run_fixture_smoke(path: Path | None = None) -> dict[str, Any]:
    fixture_path = Path(path) if path is not None else DEFAULT_FIXTURE_PATH
    payload = load_fixture(fixture_path)
    candles = dict(payload.get("candles") or {})
    policy = dict(payload.get("policy") or {})
    configs = dict(payload.get("configs") or {})

    timeframe = str(policy.get("timeframe") or "1h")
    symbol = str(policy.get("symbol") or "tBTCUSD")
    asof_bar = len(candles.get("close") or []) - 1
    if asof_bar < 0:
        raise ValueError("Runtime fixture must contain at least one close bar")

    features, features_meta = extract_features_backtest(
        candles,
        asof_bar,
        config=configs,
        timeframe=timeframe,
        symbol=symbol,
    )
    regime = detect_regime_from_candles(candles, config=configs)
    previous_registry = getattr(predict_proba_for, "_registry", None)
    predict_proba_for._registry = ModelRegistry(root=FIXTURE_MODEL_ROOT)
    try:
        probas, proba_meta = predict_proba_for(
            symbol,
            timeframe,
            features,
            regime=regime,
        )
    finally:
        if previous_registry is None:
            delattr(predict_proba_for, "_registry")
        else:
            predict_proba_for._registry = previous_registry
    confidence, confidence_meta = compute_confidence(probas, config=configs.get("quality"))
    action, decision_meta = decide(
        policy,
        probas=probas,
        confidence=confidence,
        regime=regime,
        state={},
        risk_ctx=configs.get("risk"),
        cfg=configs,
    )

    return {
        "fixture_path": str(fixture_path.resolve()),
        "bar_count": len(candles.get("close") or []),
        "features_count": len(features),
        "feature_reasons": list(features_meta.get("reasons", [])),
        "regime": regime,
        "probas": probas,
        "confidence": confidence,
        "action": action,
        "decision_reasons": list(decision_meta.get("reasons", [])),
        "versions": {
            "prob_model": proba_meta.get("versions", {}).get("prob_model_version"),
            "calibration": proba_meta.get("versions", {}).get("calibration_version"),
            "confidence": confidence_meta.get("versions", {}).get("confidence"),
            "decision": decision_meta.get("versions", {}).get("decision"),
        },
    }


def main() -> int:
    print(json.dumps(run_fixture_smoke(), indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _runtime_bootstrap_test_content() -> str:
    return """from __future__ import annotations

from core.bootstrap.fixture_smoke import DEFAULT_FIXTURE_PATH, load_fixture, run_fixture_smoke


def test_runtime_fixture_file_exists_with_expected_shape() -> None:
    payload = load_fixture()

    assert DEFAULT_FIXTURE_PATH.exists()
    assert payload["policy"] == {"symbol": "tBTCUSD", "timeframe": "1h"}
    assert payload["name"] == "runtime_fixture_smoke_minimal"
    assert len(payload["candles"]["close"]) == 120


def test_runtime_fixture_smoke_runs_end_to_end() -> None:
    result = run_fixture_smoke()

    assert result["bar_count"] == 120
    assert result["features_count"] > 0
    assert result["regime"] in {"bull", "bear", "ranging", "balanced"}
    assert result["probas"]["buy"] > result["probas"]["sell"]
    assert result["confidence"]["overall"] < 0.7
    assert result["action"] == "NONE"
    assert result["versions"] == {
        "prob_model": "seed_model_fixture_v1",
        "calibration": "seed_model_fixture_v1",
        "confidence": "v1",
        "decision": "v1",
    }
"""


def _runtime_backtest_bootstrap_module_content() -> str:
    return """from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pandas as pd

from core.backtest.engine import BacktestEngine
from core.bootstrap.fixture_smoke import DEFAULT_FIXTURE_PATH, load_fixture


class _DummyChampionCfg:
    def __init__(self) -> None:
        self.config: dict = {}
        self.source = "seed_dummy"
        self.version = "0"
        self.checksum = "seed_dummy"
        self.loaded_at = "now"


class _QuietProgress:
    def update(self, *_args, **_kwargs) -> None:
        return None

    def close(self) -> None:
        return None


def _quiet_tqdm(*_args, **_kwargs) -> _QuietProgress:
    return _QuietProgress()


def _fake_evaluate_pipeline(*, candles, policy, configs, state):
    _ = (candles, policy, configs)
    already_entered = bool((state or {}).get("entered"))
    if already_entered:
        result = {"action": "NONE", "confidence": 0.5, "regime": "BALANCED"}
        meta = {
            "decision": {"size": 0.0, "reasons": [], "state_out": {"entered": True}},
            "features": {},
        }
        return result, meta

    result = {"action": "LONG", "confidence": {"overall": 0.6}, "regime": {"name": "BALANCED"}}
    meta = {
        "decision": {
            "size": 0.01,
            "reasons": ["FIXTURE_ENTRY"],
            "state_out": {"entered": True},
        },
        "features": {},
    }
    return result, meta


def _fixture_frame(payload: dict[str, Any]) -> pd.DataFrame:
    candles = payload["candles"]
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(candles["timestamp"], unit="s"),
            "open": candles["open"],
            "high": candles["high"],
            "low": candles["low"],
            "close": candles["close"],
            "volume": candles["volume"],
        }
    )


def run_backtest_fixture_smoke(path: Path | None = None) -> dict[str, Any]:
    fixture_path = Path(path) if path is not None else DEFAULT_FIXTURE_PATH
    payload = load_fixture(fixture_path)
    policy = dict(payload["policy"])
    configs = dict(payload["configs"])
    configs["exit"] = {"enabled": False}

    engine = BacktestEngine(
        symbol=str(policy["symbol"]),
        timeframe=str(policy["timeframe"]),
        warmup_bars=0,
        fast_window=False,
    )
    engine.candles_df = _fixture_frame(payload)

    with patch.object(
        engine.champion_loader,
        "load_cached",
        return_value=_DummyChampionCfg(),
    ), patch(
        "core.backtest.engine.evaluate_pipeline",
        new=_fake_evaluate_pipeline,
    ), patch(
        "core.backtest.engine_results.shutil.which",
        return_value=None,
    ), patch(
        "core.backtest.engine.tqdm",
        new=_quiet_tqdm,
    ):
        first = engine.run(configs=configs)
        second = engine.run(configs=configs)

    if first.get("error") is not None or second.get("error") is not None:
        raise RuntimeError(
            "Backtest fixture smoke failed: "
            f"first={first.get('error')} second={second.get('error')}"
        )

    first_trades = first.get("trades") or []
    second_trades = second.get("trades") or []
    first_summary = first.get("summary") or {}
    second_summary = second.get("summary") or {}
    first_metrics = first.get("metrics") or {}
    second_metrics = second.get("metrics") or {}

    deterministic = (
        first_trades == second_trades
        and first_summary == second_summary
        and first_metrics == second_metrics
    )
    if not deterministic:
        raise AssertionError("Backtest fixture smoke must be deterministic across two runs")

    return {
        "fixture_path": str(fixture_path.resolve()),
        "bar_count": len(engine.candles_df),
        "trade_count": len(first_trades),
        "entry_reasons": list(first_trades[0].get("entry_reasons") or []) if first_trades else [],
        "deterministic": deterministic,
        "git_hash": (first.get("backtest_info") or {}).get("git_hash"),
        "final_capital": first_summary.get("final_capital"),
        "total_return_pct": first_summary.get("total_return"),
    }


def main() -> int:
    print(json.dumps(run_backtest_fixture_smoke(), indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _runtime_champion_smoke_module_content() -> str:
    return """from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.strategy.champion_loader import ChampionLoader

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CHAMPION_FIXTURE_PATH = (
    REPO_ROOT / "registry" / "fixtures" / "champions" / "tBTCUSD_1h.json"
)


def load_champion_fixture(path: Path | None = None) -> dict[str, Any]:
    fixture_path = Path(path) if path is not None else DEFAULT_CHAMPION_FIXTURE_PATH
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("Champion fixture payload must be a JSON object")
    return payload


def run_champion_smoke(path: Path | None = None) -> dict[str, Any]:
    fixture_path = Path(path) if path is not None else DEFAULT_CHAMPION_FIXTURE_PATH
    payload = load_champion_fixture(fixture_path)
    loader = ChampionLoader(champions_dir=fixture_path.parent)

    first = loader.load("tBTCUSD", "1h")
    second = loader.load_cached("tBTCUSD", "1h")
    normalized_source = str(first.source).replace("\\\\", "/")

    return {
        "fixture_path": str(fixture_path.resolve()),
        "source": normalized_source,
        "version": first.version,
        "checksum": first.checksum,
        "cache_reused": first.checksum == second.checksum,
        "threshold_entry_conf_overall": (first.config.get("thresholds") or {}).get(
            "entry_conf_overall"
        ),
        "risk_map_rows": len((first.config.get("risk") or {}).get("risk_map") or []),
    }


def main() -> int:
    print(json.dumps(run_champion_smoke(), indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _runtime_evaluate_champion_smoke_module_content() -> str:
    return """from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from core.bootstrap.champion_smoke import DEFAULT_CHAMPION_FIXTURE_PATH
from core.bootstrap.fixture_smoke import load_fixture
from core.strategy.champion_loader import ChampionLoader
from core.strategy.model_registry import ModelRegistry
from core.strategy.prob_model import predict_proba_for
from core.strategy import evaluate as evaluate_mod

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_MODEL_ROOT = REPO_ROOT / "registry" / "fixtures" / "model_registry"


def run_evaluate_champion_smoke(path: Path | None = None) -> dict[str, object]:
    fixture_path = Path(path) if path is not None else DEFAULT_CHAMPION_FIXTURE_PATH
    runtime_fixture = load_fixture()
    candles = dict(runtime_fixture.get("candles") or {})
    policy = dict(runtime_fixture.get("policy") or {})
    configs = {
        "precomputed_features": {"ema_50": list(candles.get("close") or [])},
    }
    captured: dict[str, object] = {}

    def _fake_extract_features_live(candles, *, config, timeframe, symbol):
        _ = candles
        captured["config"] = config
        captured["timeframe"] = timeframe
        captured["symbol"] = symbol
        return {"ema_50": 1.0}, {"reasons": [], "htf_fibonacci": {}, "ltf_fibonacci": {}}

    previous_registry = getattr(predict_proba_for, "_registry", None)
    predict_proba_for._registry = ModelRegistry(root=FIXTURE_MODEL_ROOT)
    try:
        with patch.object(
            evaluate_mod,
            "champion_loader",
            ChampionLoader(champions_dir=fixture_path.parent),
        ), patch.object(
            evaluate_mod,
            "extract_features_live",
            new=_fake_extract_features_live,
        ), patch.object(
            evaluate_mod,
            "_detect_authoritative_regime",
            lambda *_args, **_kwargs: "balanced",
        ), patch.object(
            evaluate_mod,
            "_detect_shadow_regime_from_regime_module",
            lambda *_args, **_kwargs: "balanced",
        ), patch.object(
            evaluate_mod,
            "compute_confidence",
            lambda *_args, **_kwargs: (
                {"buy": 0.55, "sell": 0.45, "overall": 0.55},
                {"versions": {"confidence": "v1"}},
            ),
        ), patch.object(
            evaluate_mod,
            "compute_htf_regime",
            lambda *_args, **_kwargs: "balanced",
        ), patch.object(
            evaluate_mod,
            "decide",
            lambda *_args, **_kwargs: (
                "NONE",
                {"versions": {"decision": "v1"}, "reasons": [], "state_out": {}, "size": 0.0},
            ),
        ):
            result, meta = evaluate_mod.evaluate_pipeline(
                candles,
                policy=policy,
                configs=configs,
                state={},
            )
    finally:
        if previous_registry is None:
            delattr(predict_proba_for, "_registry")
        else:
            predict_proba_for._registry = previous_registry

    effective_config = dict(captured.get("config") or {})
    normalized_source = str(meta.get("champion", {}).get("source") or "").replace("\\\\", "/")
    proba_versions = dict((meta.get("proba") or {}).get("versions") or {})

    return {
        "fixture_path": str(fixture_path.resolve()),
        "symbol": captured.get("symbol"),
        "timeframe": captured.get("timeframe"),
        "action": result.get("action"),
        "buy_proba": (result.get("probas") or {}).get("buy"),
        "sell_proba": (result.get("probas") or {}).get("sell"),
        "champion_source": normalized_source,
        "prob_model_version": proba_versions.get("prob_model_version"),
        "calibration_version": proba_versions.get("calibration_version"),
        "regime_aware_calibration": proba_versions.get("regime_aware_calibration"),
        "model_schema": list((meta.get("proba") or {}).get("schema") or []),
        "threshold_entry_conf_overall": (effective_config.get("thresholds") or {}).get(
            "entry_conf_overall"
        ),
        "risk_map_rows": len((effective_config.get("risk") or {}).get("risk_map") or []),
        "meta_note": (effective_config.get("meta") or {}).get("note"),
        "precomputed_feature_keys": sorted((effective_config.get("precomputed_features") or {}).keys()),
    }


def main() -> int:
    print(json.dumps(run_evaluate_champion_smoke(), indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _runtime_model_smoke_module_content() -> str:
    return """from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.strategy.model_registry import ModelRegistry
from core.strategy.prob_model import predict_proba_for

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_MODEL_ROOT = REPO_ROOT / "registry" / "fixtures" / "model_registry"
DEFAULT_MODEL_REGISTRY_PATH = FIXTURE_MODEL_ROOT / "config" / "models" / "registry.json"
DEFAULT_MODEL_FIXTURE_PATH = FIXTURE_MODEL_ROOT / "config" / "models" / "tBTCUSD_1h.json"


def run_model_smoke() -> dict[str, Any]:
    registry = ModelRegistry(root=FIXTURE_MODEL_ROOT)
    model_meta = registry.get_meta("tBTCUSD", "1h") or {}
    schema = list(model_meta.get("schema") or [])
    if not schema:
        raise AssertionError("Expected local V2 model fixture to expose a non-empty schema")

    features = {schema[0]: 1.0}
    previous_registry = getattr(predict_proba_for, "_registry", None)
    predict_proba_for._registry = registry
    try:
        probas, meta = predict_proba_for("tBTCUSD", "1h", features, regime="balanced")
    finally:
        if previous_registry is None:
            delattr(predict_proba_for, "_registry")
        else:
            predict_proba_for._registry = previous_registry

    return {
        "registry_path": str(DEFAULT_MODEL_REGISTRY_PATH.resolve()),
        "model_path": str(DEFAULT_MODEL_FIXTURE_PATH.resolve()),
        "schema": schema,
        "probas": probas,
        "versions": dict(meta.get("versions") or {}),
        "calibration_used": dict(meta.get("calibration_used") or {}),
    }


def main() -> int:
    print(json.dumps(run_model_smoke(), indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _runtime_smoke_suite_module_content() -> str:
    return """from __future__ import annotations

import json
from typing import Any

from core.bootstrap.backtest_smoke import run_backtest_fixture_smoke
from core.bootstrap.champion_smoke import run_champion_smoke
from core.bootstrap.evaluate_champion_smoke import run_evaluate_champion_smoke
from core.bootstrap.fixture_smoke import run_fixture_smoke
from core.bootstrap.model_smoke import run_model_smoke


def run_smoke_suite() -> dict[str, Any]:
    fixture = run_fixture_smoke()
    champion = run_champion_smoke()
    evaluate_champion = run_evaluate_champion_smoke()
    model = run_model_smoke()
    backtest = run_backtest_fixture_smoke()
    return {
        "suite": "runtime_smoke_suite_v1",
        "checks": {
            "fixture_smoke": "passed",
            "champion_smoke": "passed",
            "evaluate_champion_smoke": "passed",
            "model_smoke": "passed",
            "backtest_smoke": "passed",
        },
        "fixture_smoke": fixture,
        "champion_smoke": champion,
        "evaluate_champion_smoke": evaluate_champion,
        "model_smoke": model,
        "backtest_smoke": backtest,
    }


def main() -> int:
    print(json.dumps(run_smoke_suite(), indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
"""


def _runtime_backtest_bootstrap_test_content() -> str:
    return """from __future__ import annotations

from core.bootstrap.backtest_smoke import run_backtest_fixture_smoke


def test_runtime_backtest_fixture_bootstrap_smoke_runs_end_to_end() -> None:
    result = run_backtest_fixture_smoke()

    assert result["bar_count"] == 120
    assert result["trade_count"] == 1
    assert result["entry_reasons"] == ["FIXTURE_ENTRY"]
    assert result["deterministic"] is True
    assert result["git_hash"] == "unknown"
    assert result["final_capital"] is not None
"""


def _runtime_champion_smoke_test_content() -> str:
    return """from __future__ import annotations

from core.bootstrap.champion_smoke import run_champion_smoke


def test_runtime_champion_smoke_loads_local_fixture() -> None:
    result = run_champion_smoke()

    assert result["source"] == "registry/fixtures/champions/tBTCUSD_1h.json"
    assert result["version"] == "seed_champion_fixture_v1"
    assert result["cache_reused"] is True
    assert result["threshold_entry_conf_overall"] == 0.7
    assert result["risk_map_rows"] == 2
"""


def _runtime_evaluate_champion_smoke_test_content() -> str:
    return """from __future__ import annotations

from core.bootstrap.evaluate_champion_smoke import run_evaluate_champion_smoke


def test_runtime_evaluate_champion_smoke_uses_local_champion_fixture() -> None:
    result = run_evaluate_champion_smoke()

    assert result["symbol"] == "tBTCUSD"
    assert result["timeframe"] == "1h"
    assert result["action"] == "NONE"
    assert result["buy_proba"] > result["sell_proba"]
    assert result["champion_source"] == "registry/fixtures/champions/tBTCUSD_1h.json"
    assert result["prob_model_version"] == "seed_model_fixture_v1"
    assert result["calibration_version"] == "seed_model_fixture_v1"
    assert result["regime_aware_calibration"] is True
    assert result["model_schema"] == ["ema_50"]
    assert result["threshold_entry_conf_overall"] == 0.7
    assert result["risk_map_rows"] == 2
    assert result["meta_note"] == "seed_fixture_champion"
    assert result["precomputed_feature_keys"] == ["ema_50"]
"""


def _runtime_model_smoke_test_content() -> str:
    return """from __future__ import annotations

from core.bootstrap.model_smoke import run_model_smoke


def test_runtime_model_smoke_uses_local_registry_and_model_fixture() -> None:
    result = run_model_smoke()

    assert result["schema"] == ["ema_50"]
    assert result["probas"]["buy"] > result["probas"]["sell"]
    assert abs(result["probas"]["hold"]) < 1e-12
    assert result["versions"] == {
        "prob_model_version": "seed_model_fixture_v1",
        "calibration_version": "seed_model_fixture_v1",
        "regime_aware_calibration": True,
    }
    assert result["calibration_used"]["regime"] == "balanced"
    assert result["calibration_used"]["buy_calib"] == {"a": 1.0, "b": 0.1}
    assert result["calibration_used"]["sell_calib"] == {"a": 1.0, "b": -0.1}
"""


def _runtime_smoke_suite_test_content() -> str:
    return """from __future__ import annotations

from core.bootstrap.smoke_suite import run_smoke_suite


def test_runtime_smoke_suite_runs_all_smokes() -> None:
    result = run_smoke_suite()

    assert result["suite"] == "runtime_smoke_suite_v1"
    assert result["checks"] == {
        "fixture_smoke": "passed",
        "champion_smoke": "passed",
        "evaluate_champion_smoke": "passed",
        "model_smoke": "passed",
        "backtest_smoke": "passed",
    }
    assert result["fixture_smoke"]["action"] == "NONE"
    assert result["champion_smoke"]["threshold_entry_conf_overall"] == 0.7
    assert result["evaluate_champion_smoke"]["champion_source"] == "registry/fixtures/champions/tBTCUSD_1h.json"
    assert result["evaluate_champion_smoke"]["prob_model_version"] == "seed_model_fixture_v1"
    assert result["model_smoke"]["versions"]["prob_model_version"] == "seed_model_fixture_v1"
    assert result["backtest_smoke"]["deterministic"] is True
    assert result["backtest_smoke"]["trade_count"] == 1
"""


def _runtime_installed_console_scripts_test_content() -> str:
    return """from __future__ import annotations

import importlib.metadata as importlib_metadata
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


EXPECTED_ENTRYPOINTS = {
    "genesis-v2-api-shell": "genesis_core_v2_cli.console_scripts:api_shell_main",
    "genesis-v2-mcp-stdio": "genesis_core_v2_cli.console_scripts:mcp_stdio_main",
    "genesis-v2-pytest": "genesis_core_v2_cli.console_scripts:pytest_suite_main",
    "genesis-v2-champion-smoke": "genesis_core_v2_cli.console_scripts:champion_smoke_main",
    "genesis-v2-evaluate-champion-smoke": "genesis_core_v2_cli.console_scripts:evaluate_champion_smoke_main",
    "genesis-v2-fixture-smoke": "genesis_core_v2_cli.console_scripts:fixture_smoke_main",
    "genesis-v2-backtest-smoke": "genesis_core_v2_cli.console_scripts:backtest_smoke_main",
    "genesis-v2-model-smoke": "genesis_core_v2_cli.console_scripts:model_smoke_main",
    "genesis-v2-smoke-suite": "genesis_core_v2_cli.console_scripts:smoke_suite_main",
}


def _require_installed_distribution() -> None:
    try:
        importlib_metadata.distribution("genesis-core-v2")
    except importlib_metadata.PackageNotFoundError:
        pytest.skip("Editable install required for console script verification")


def _require_module(module_name: str, install_hint: str) -> None:
    if importlib.util.find_spec(module_name) is None:
        pytest.skip(f"Console script verification requires {install_hint}")


def test_installed_distribution_registers_expected_console_scripts() -> None:
    _require_installed_distribution()

    entry_points = {
        entry_point.name: f"{entry_point.module}:{entry_point.attr}"
        for entry_point in importlib_metadata.entry_points(group="console_scripts")
        if entry_point.name in EXPECTED_ENTRYPOINTS
    }

    assert entry_points == EXPECTED_ENTRYPOINTS


def _run_installed_entrypoint(command: str, command_args: list[str]) -> subprocess.CompletedProcess[str]:
    repo_root = Path(__file__).resolve().parents[2]
    code = '''
import importlib.metadata as importlib_metadata
import sys

entry_points = {
    entry_point.name: entry_point
    for entry_point in importlib_metadata.entry_points(group='console_scripts')
}
entry_point = entry_points[sys.argv[1]]
callable_obj = entry_point.load()
sys.argv = [sys.argv[1], *sys.argv[2:]]
raise SystemExit(callable_obj())
'''
    return subprocess.run(
        [sys.executable, "-c", code, command, *command_args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )


@pytest.mark.parametrize(
    ("command", "command_args", "required_module", "install_hint", "expected_pairs"),
    [
        (
            "genesis-v2-api-shell",
            ["--print-config"],
            None,
            None,
            {
                "app": "core.server:app",
                "host": "127.0.0.1",
                "port": 8000,
                "reload": False,
            },
        ),
        (
            "genesis-v2-mcp-stdio",
            ["--print-config"],
            "mcp",
            'the optional `[mcp]` extra (`python -m pip install -e ".[mcp]")',
            {
                "server_name": "genesis-core-v2",
                "log_level": "INFO",
            },
        ),
        (
            "genesis-v2-pytest",
            ["--print-config"],
            "pytest",
            'the local test dependencies (`python -m pip install -e ".[dev]")',
            {
                "pytest_args": ["-q"],
            },
        ),
        (
            "genesis-v2-champion-smoke",
            [],
            None,
            None,
            {"version": "seed_champion_fixture_v1"},
        ),
        (
            "genesis-v2-evaluate-champion-smoke",
            [],
            None,
            None,
            {"action": "NONE", "champion_source": "registry/fixtures/champions/tBTCUSD_1h.json"},
        ),
        ("genesis-v2-fixture-smoke", [], None, None, {"action": "NONE"}),
        (
            "genesis-v2-backtest-smoke",
            [],
            None,
            None,
            {"trade_count": 1, "deterministic": True},
        ),
        (
            "genesis-v2-model-smoke",
            [],
            None,
            None,
            {"schema": ["ema_50"]},
        ),
        (
            "genesis-v2-smoke-suite",
            [],
            None,
            None,
            {"suite": "runtime_smoke_suite_v1"},
        ),
    ],
)
def test_installed_console_scripts_execute(
    command: str,
    command_args: list[str],
    required_module: str | None,
    install_hint: str | None,
    expected_pairs: dict[str, object],
) -> None:
    _require_installed_distribution()
    if required_module is not None and install_hint is not None:
        _require_module(required_module, install_hint)

    completed = _run_installed_entrypoint(command, command_args)
    payload = json.loads(completed.stdout)

    for key, expected_value in expected_pairs.items():
        assert payload.get(key) == expected_value
"""


def _runtime_backtest_engine_smoke_test_content() -> str:
    return """from __future__ import annotations

import pandas as pd

from core.backtest.engine import BacktestEngine
from core.bootstrap.fixture_smoke import load_fixture


class _DummyChampionCfg:
    def __init__(self) -> None:
        self.config: dict = {}
        self.source = "seed_dummy"
        self.version = "0"
        self.checksum = "seed_dummy"
        self.loaded_at = "now"


def _fixture_frame() -> pd.DataFrame:
    payload = load_fixture()
    candles = payload["candles"]
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(candles["timestamp"], unit="s"),
            "open": candles["open"],
            "high": candles["high"],
            "low": candles["low"],
            "close": candles["close"],
            "volume": candles["volume"],
        }
    )


def test_backtest_engine_fixture_smoke_is_deterministic(monkeypatch) -> None:
    monkeypatch.setenv("GENESIS_DISABLE_METRICS", "1")
    monkeypatch.setattr("core.backtest.engine_results.shutil.which", lambda *_args, **_kwargs: None)

    class _QuietProgress:
        def update(self, *_args, **_kwargs) -> None:
            return None

        def close(self) -> None:
            return None

    monkeypatch.setattr("core.backtest.engine.tqdm", lambda *_args, **_kwargs: _QuietProgress())

    def _fake_evaluate_pipeline(*, candles, policy, configs, state):
        _ = (candles, policy, configs)
        already_entered = bool((state or {}).get("entered"))
        if already_entered:
            result = {"action": "NONE", "confidence": 0.5, "regime": "BALANCED"}
            meta = {
                "decision": {"size": 0.0, "reasons": [], "state_out": {"entered": True}},
                "features": {},
            }
            return result, meta

        result = {"action": "LONG", "confidence": {"overall": 0.6}, "regime": {"name": "BALANCED"}}
        meta = {
            "decision": {
                "size": 0.01,
                "reasons": ["FIXTURE_ENTRY"],
                "state_out": {"entered": True},
            },
            "features": {},
        }
        return result, meta

    monkeypatch.setattr("core.backtest.engine.evaluate_pipeline", _fake_evaluate_pipeline)

    payload = load_fixture()
    policy = dict(payload["policy"])
    configs = dict(payload["configs"])
    configs["exit"] = {"enabled": False}

    engine = BacktestEngine(
        symbol=str(policy["symbol"]),
        timeframe=str(policy["timeframe"]),
        warmup_bars=0,
        fast_window=False,
    )
    engine.champion_loader.load_cached = lambda *_args, **_kwargs: _DummyChampionCfg()
    engine.candles_df = _fixture_frame()

    first = engine.run(configs=configs)
    second = engine.run(configs=configs)

    first_trades = first.get("trades") or []
    second_trades = second.get("trades") or []

    assert first.get("error") is None
    assert second.get("error") is None
    assert len(first_trades) == 1
    assert first_trades == second_trades
    assert first_trades[0].get("entry_reasons") == ["FIXTURE_ENTRY"]
    assert (first.get("summary") or {}) == (second.get("summary") or {})
    assert (first.get("metrics") or {}) == (second.get("metrics") or {})
"""


def _readme_content(source_head: str | None) -> str:
    source_line = (
        f"Source Genesis-Core HEAD: `{source_head}`"
        if source_head
        else "Source Genesis-Core HEAD: `unknown`"
    )
    return f"""# Genesis-Core-V2

Runtime-first seed with admitted local-only API shell generated from the current
`Genesis-Core` repository.

{source_line}

## What is included

- runtime kernel roots (`backtest`, `strategy`, `regime`)
- local dependency closure required by those roots
- admitted local-only API shell (`src/core/server.py`,
  `src/core/api/{{config,models,status,strategy}}.py`)
- source-backed config validation seam (`src/core/config/validator.py`,
  `src/core/config/legacy_schema_v1.json`)
- source-backed config endpoint integration smoke (`tests/integration/test_config_endpoints.py`)
- narrow config bootstrap (`config/__init__.py`, `config/timeframe_configs.py`,
    `config/backtest_defaults.yaml`)
- local MCP stdio shell (`mcp_server/*.py`, `.vscode/mcp.json`, `config/mcp_settings.json`)
- local VS Code task/debug loop (`.vscode/tasks.json`, `.vscode/launch.json`)
- local VS Code Python analysis/test settings (`.vscode/settings.json`)
- local VS Code extension recommendations (`.vscode/extensions.json`)
- tracked env bootstrap template (`.env.example`)
- local pre-commit hook config (`.pre-commit-config.yaml`)
- narrow local QA defaults in `pyproject.toml`
- repo-local MCP launcher (`scripts/mcp/mcp_stdio.py`)
- repo-local API launcher (`scripts/api/api_shell.py`)
- repo-local pytest launcher (`scripts/validate/pytest_suite.py`)
- repo-local smoke scripts (`scripts/smoke/{{backtest_smoke,champion_smoke,evaluate_champion_smoke,fixture_smoke,model_smoke,smoke_suite}}.py`)
- runtime-only governance guardrails
- admitted source model payloads under `config/models/**`
- deterministic fixture model-registry/prob-model smoke
    (`registry/fixtures/model_registry/config/models/{{registry.json,tBTCUSD_1h.json}}`,
    `core.bootstrap.model_smoke`)
- local champion fixture/bootstrap smoke (`registry/fixtures/champions/tBTCUSD_1h.json`,
  `core.bootstrap.champion_smoke`)
- live evaluate smoke backed by the local champion fixture (`core.bootstrap.evaluate_champion_smoke`)
- fixture-driven bootstrap smoke (`registry/fixtures/runtime_fixture_smoke_minimal.json`,
  `core.bootstrap.fixture_smoke`)
- fixture-driven backtest bootstrap smoke (`core.bootstrap.backtest_smoke`)
- combined runtime smoke suite (`core.bootstrap.smoke_suite`)
- fixture-driven backtest engine smoke (`tests/runtime/test_backtest_engine_fixture_smoke.py`)
- installable console scripts for local API/MCP/pytest and smoke entrypoints

## What is intentionally excluded

- `src/core/api/{{account,info,paper,public,ui}}.py`
- `src/core/io/**`
- `src/core/pipeline.py`
- `src/core/optimizer/**`
- `src/core/strategy/features.py`
- `src/core/utils/optuna_helpers.py`
- `src/core/utils/diffing/{{optuna_guard,results_diff,trial_cache}}.py`
- `config/runtime.json`
- `config/runtime.seed.json`
- `config/strategy/champions/**`
- `mcp_server/remote_server.py`
- `config/mcp_settings.remote_safe.json`
- `config/mcp_settings.remote_git.json`
- `data/**`
- branch-local research corpora and historical explanation surfaces

## Notes

This seed is intentionally narrower than the source repository.
It is a local starting point, not a claim that all later bootstrap, model, champion,
or wider state-authority decisions are already resolved.
Source `config/models/**` payloads are copied into the seed, while deterministic smoke
paths use fixture-backed model registry payloads under `registry/fixtures/model_registry/**`.
Phase 1 intentionally excludes `config/strategy/champions/**`; runtime falls back to
`config/timeframe_configs.py` through `ChampionLoader` when champion payloads are absent.
The admitted API shell is local-only (`config/status/models/strategy`); exchange-facing,
paper, public-data, and UI surfaces remain excluded for a later slice.
Runtime state and champion authority payloads remain excluded; generated `.env` contains only
local-shell placeholders. Tracked `.env.example` mirrors the same narrow values for copy-forward bootstrap.
Unneeded Optuna/optimizer closure is intentionally pruned from the seed until and unless a later
explicit slice admits those higher-sensitivity surfaces.
Local MCP support is admitted for stdio-only workspace usage; remote MCP entrypoints and remote
allowlist variants remain deferred.
Repo-local MCP launcher is generated so the local stdio shell can start without depending on
editor-specific config wiring first.
Repo-local API launcher is generated so the local API shell can start without depending on
editor-specific tasks or an editable install first.
Repo-local pytest launcher is generated so the seed can run its test loop without depending on
editor-specific tasks or an editable install first.
Repo-local smoke scripts are generated so the seed can run its core smoke loops without relying on
editor-specific tasks or an editable install first.

## Skeleton workflow

- `AGENTS.md` defines the skeleton-first repo contract.
- `.github/copilot-instructions.md` keeps local agent work aligned with generator-driven slices.
- `docs/SKELETON_SCOPE.md` records Track A vs Track B and the verification loop.
- `.vscode/mcp.json` wires VS Code to the local `scripts/mcp/mcp_stdio.py` wrapper using `config/mcp_settings.json`.
- `.vscode/tasks.json` and `.vscode/launch.json` route local API/MCP/smoke/test loops through the repo-local wrappers while keeping `PYTHONPATH=${{workspaceFolder}}/src` available.
- `.vscode/settings.json` aligns Python analysis/test discovery with the `src/` layout and local `.env` placeholder.
- `.vscode/extensions.json` recommends the Python/Pylance/Ruff stack for local skeleton work.
- `.env.example` keeps the narrow local placeholder values tracked even though `.env` stays ignored.
- `.pre-commit-config.yaml` keeps a narrow local formatting/lint/sanity hook loop tracked in the seed.
- `pyproject.toml` carries narrow local pytest/ruff/black defaults for the generated V2 workspace.
- `scripts/mcp/mcp_stdio.py` wraps the local MCP stdio shell with repo-root bootstrap and the generated config path.
- `scripts/api/api_shell.py` wraps the local API shell with `src/` bootstrapping for non-installed startup.
- `scripts/validate/pytest_suite.py` wraps `pytest` with local `src/` bootstrapping for non-installed test execution.
- `scripts/smoke/*.py` wraps the admitted core smoke modules with local `src/` bootstrapping so the seed is runnable before install.

After editable install, local module commands:

Local API shell: `python -m uvicorn core.server:app --app-dir src --reload`
Local MCP stdio shell: `python -m mcp_server.server`
Local pytest suite: `python -m pytest -q`

Local model smoke: `python -m core.bootstrap.model_smoke`
Local champion smoke: `python -m core.bootstrap.champion_smoke`
Local champion-backed evaluate smoke: `python -m core.bootstrap.evaluate_champion_smoke`
Local bootstrap smoke: `python -m core.bootstrap.fixture_smoke`
Local backtest bootstrap smoke: `python -m core.bootstrap.backtest_smoke`
Local runtime smoke suite: `python -m core.bootstrap.smoke_suite`

Non-installed local MCP launcher:
`python scripts/mcp/mcp_stdio.py`
`python scripts/mcp/mcp_stdio.py --print-config`

Non-installed local API launcher:
`python scripts/api/api_shell.py`
`python scripts/api/api_shell.py --reload`

Non-installed local pytest launcher:
`python scripts/validate/pytest_suite.py`
`python scripts/validate/pytest_suite.py tests/runtime/test_local_api_shell_script.py -q`

Non-installed local smoke scripts:
`python scripts/smoke/fixture_smoke.py`
`python scripts/smoke/backtest_smoke.py`
`python scripts/smoke/champion_smoke.py`
`python scripts/smoke/evaluate_champion_smoke.py`
`python scripts/smoke/model_smoke.py`
`python scripts/smoke/smoke_suite.py`

Local VS Code tasks:
`genesis-v2: api shell`, `genesis-v2: mcp stdio`, `genesis-v2: smoke suite`, `genesis-v2: pytest`

Local VS Code debug profiles:
`genesis-v2: api shell`, `genesis-v2: mcp stdio`, `genesis-v2: smoke suite`, `genesis-v2: pytest`

Suggested VS Code extensions:
`ms-python.python`, `ms-python.vscode-pylance`, `charliermarsh.ruff`

Python analysis/test settings:
`.vscode/settings.json`

Console scripts after editable install:
`genesis-v2-api-shell`, `genesis-v2-mcp-stdio`, `genesis-v2-pytest`
`genesis-v2-champion-smoke`, `genesis-v2-evaluate-champion-smoke`
`genesis-v2-fixture-smoke`, `genesis-v2-backtest-smoke`, `genesis-v2-smoke-suite`
`genesis-v2-model-smoke`

Suggested install verification:
`python -m pip install -e \".[dev,mcp]\"`
then run `pytest tests/runtime/test_installed_console_scripts.py -q`

Local pre-commit workflow:
`pre-commit install`
then run `pre-commit run --all-files`

Optional local MCP install:
`python -m pip install -e \".[mcp]\"`
then connect the `genesis-core-v2` server from `.vscode/mcp.json`
"""


def _pyproject_content() -> str:
    runtime_deps = ",\n".join(f'  "{dep}"' for dep in PYPROJECT_RUNTIME_DEPS)
    dev_deps = ",\n".join(f'  "{dep}"' for dep in PYPROJECT_DEV_DEPS)
    mcp_deps = ",\n".join(f'  "{dep}"' for dep in PYPROJECT_MCP_DEPS)
    return f"""[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "genesis-core-v2"
version = "0.1.0"
description = "Runtime-first seed with admitted local-only API shell extracted from Genesis-Core"
requires-python = ">=3.11"
dependencies = [
{runtime_deps}
]

[project.scripts]
genesis-v2-api-shell = "genesis_core_v2_cli.console_scripts:api_shell_main"
genesis-v2-mcp-stdio = "genesis_core_v2_cli.console_scripts:mcp_stdio_main"
genesis-v2-pytest = "genesis_core_v2_cli.console_scripts:pytest_suite_main"
genesis-v2-champion-smoke = "genesis_core_v2_cli.console_scripts:champion_smoke_main"
genesis-v2-evaluate-champion-smoke = "genesis_core_v2_cli.console_scripts:evaluate_champion_smoke_main"
genesis-v2-fixture-smoke = "genesis_core_v2_cli.console_scripts:fixture_smoke_main"
genesis-v2-backtest-smoke = "genesis_core_v2_cli.console_scripts:backtest_smoke_main"
genesis-v2-model-smoke = "genesis_core_v2_cli.console_scripts:model_smoke_main"
genesis-v2-smoke-suite = "genesis_core_v2_cli.console_scripts:smoke_suite_main"

[project.optional-dependencies]
dev = [
{dev_deps}
]
mcp = [
{mcp_deps}
]

[tool.setuptools]
package-dir = {{"" = "src"}}

[tool.setuptools.packages.find]
where = ["src"]
include = ["core*", "genesis_core_v2_cli*"]

[tool.pytest.ini_options]
addopts = "-q"
pythonpath = ["src"]
testpaths = ["tests"]
norecursedirs = ["cache", "data", "logs", "results", ".venv"]

[tool.ruff]
line-length = 100
target-version = "py311"
extend-exclude = [
    ".venv/",
    "cache/",
    "data/",
    "logs/",
    "results/"
]

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "C4", "UP"]
ignore = ["E501", "B008", "C901"]

[tool.black]
line-length = 100
target-version = ['py311']
extend-exclude = '(^cache/|^data/|^logs/|^results/)'
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


def _clear_destination_contents(destination: Path) -> None:
    for child in destination.iterdir():
        if child.name == ".git":
            continue
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink(missing_ok=True)


def _prepare_destination(destination: Path, *, clean: bool) -> None:
    if destination.exists() and any(destination.iterdir()):
        if not clean:
            raise SeedGenerationError(
                f"Destination already exists and is not empty: {destination}. "
                "Use --clean to replace it."
            )
        if (destination / ".git").exists():
            _clear_destination_contents(destination)
        else:
            shutil.rmtree(destination)

    destination.mkdir(parents=True, exist_ok=True)


def _copy_sources(destination: Path, source_files: list[SourceFile], repo_root: Path) -> list[str]:
    copied: list[str] = []
    for source_file in source_files:
        relative_path = source_file.relative_path
        if relative_path in GENERATED_SOURCE_OVERRIDES:
            continue
        destination_path = destination / relative_path
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file.absolute_path, destination_path)
        copied.append(relative_path)
    return copied


def _write_generated_files(destination: Path, *, source_head: str | None) -> list[str]:
    generated_paths: list[str] = []

    generated_map = {
        ".github/copilot-instructions.md": _v2_copilot_instructions_content(),
        ".pre-commit-config.yaml": _precommit_config_content(),
        ".vscode/extensions.json": json.dumps(
            _v2_vscode_extensions_payload(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        ".vscode/launch.json": json.dumps(
            _v2_vscode_launch_payload(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        ".vscode/mcp.json": json.dumps(
            _v2_vscode_mcp_payload(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        ".vscode/settings.json": json.dumps(
            _v2_vscode_settings_payload(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        ".vscode/tasks.json": json.dumps(
            _v2_vscode_tasks_payload(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        "README.md": _readme_content(source_head),
        "AGENTS.md": _v2_agents_content(),
        "pyproject.toml": _pyproject_content(),
        ".gitignore": _gitignore_content(),
        ".env": _env_placeholder_content(),
        ".env.example": _env_example_content(),
        "config/backtest_defaults.yaml": _backtest_defaults_content(),
        "config/mcp_settings.json": json.dumps(
            _v2_mcp_settings_payload(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        "docs/SKELETON_SCOPE.md": _v2_skeleton_scope_content(),
        "registry/fixtures/champions/tBTCUSD_1h.json": json.dumps(
            _runtime_champion_fixture_payload(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        "registry/fixtures/model_registry/config/models/registry.json": json.dumps(
            _runtime_model_registry_fixture_payload(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        "registry/fixtures/model_registry/config/models/tBTCUSD_1h.json": json.dumps(
            _runtime_model_fixture_payload(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        "registry/fixtures/runtime_fixture_smoke_minimal.json": json.dumps(
            _runtime_fixture_payload(),
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        "scripts/api/api_shell.py": _runtime_local_api_shell_script_content(),
        "scripts/mcp/mcp_stdio.py": _runtime_local_mcp_script_content(),
        "scripts/smoke/backtest_smoke.py": _runtime_local_smoke_script_content(
            "core.bootstrap.backtest_smoke"
        ),
        "scripts/smoke/champion_smoke.py": _runtime_local_smoke_script_content(
            "core.bootstrap.champion_smoke"
        ),
        "scripts/smoke/evaluate_champion_smoke.py": _runtime_local_smoke_script_content(
            "core.bootstrap.evaluate_champion_smoke"
        ),
        "scripts/smoke/fixture_smoke.py": _runtime_local_smoke_script_content(
            "core.bootstrap.fixture_smoke"
        ),
        "scripts/smoke/model_smoke.py": _runtime_local_smoke_script_content(
            "core.bootstrap.model_smoke"
        ),
        "scripts/smoke/smoke_suite.py": _runtime_local_smoke_script_content(
            "core.bootstrap.smoke_suite"
        ),
        "scripts/validate/pytest_suite.py": _runtime_local_pytest_script_content(),
        "src/core/bootstrap/__init__.py": _runtime_bootstrap_init_content(),
        "src/core/bootstrap/backtest_smoke.py": _runtime_backtest_bootstrap_module_content(),
        "src/core/bootstrap/champion_smoke.py": _runtime_champion_smoke_module_content(),
        "src/core/bootstrap/evaluate_champion_smoke.py": _runtime_evaluate_champion_smoke_module_content(),
        "src/core/bootstrap/fixture_smoke.py": _runtime_bootstrap_module_content(),
        "src/core/bootstrap/model_smoke.py": _runtime_model_smoke_module_content(),
        "src/core/bootstrap/smoke_suite.py": _runtime_smoke_suite_module_content(),
        "src/core/server.py": _local_api_server_content(),
        "src/core/utils/diffing/__init__.py": _runtime_diffing_init_content(),
        "src/genesis_core_v2_cli/__init__.py": _genesis_core_v2_cli_init_content(),
        "src/genesis_core_v2_cli/console_scripts.py": _genesis_core_v2_cli_console_scripts_content(),
        "tests/governance/test_pyproject_console_scripts.py": _pyproject_console_scripts_test_content(),
        "tests/runtime/test_installed_console_scripts.py": _runtime_installed_console_scripts_test_content(),
        "tests/runtime/test_backtest_bootstrap_smoke.py": _runtime_backtest_bootstrap_test_content(),
        "tests/runtime/test_champion_smoke.py": _runtime_champion_smoke_test_content(),
        "tests/runtime/test_evaluate_champion_smoke.py": _runtime_evaluate_champion_smoke_test_content(),
        "tests/governance/test_v2_seed_boundaries.py": _v2_boundary_test_content(),
        "tests/runtime/test_backtest_engine_fixture_smoke.py": _runtime_backtest_engine_smoke_test_content(),
        "tests/runtime/test_local_env_template.py": _runtime_local_env_template_test_content(),
        "tests/runtime/test_local_api_shell_script.py": _runtime_local_api_shell_script_test_content(),
        "tests/runtime/test_local_mcp_script.py": _runtime_local_mcp_script_test_content(),
        "tests/runtime/test_local_pytest_script.py": _runtime_local_pytest_script_test_content(),
        "tests/runtime/test_local_precommit_config.py": _runtime_local_precommit_config_test_content(),
        "tests/runtime/test_local_vscode_extensions.py": _runtime_local_vscode_extensions_test_content(),
        "tests/runtime/test_local_mcp_setup.py": _runtime_local_mcp_setup_test_content(),
        "tests/runtime/test_local_smoke_scripts.py": _runtime_local_smoke_scripts_test_content(),
        "tests/runtime/test_local_vscode_launch.py": _runtime_local_vscode_launch_test_content(),
        "tests/runtime/test_local_vscode_settings.py": _runtime_local_vscode_settings_test_content(),
        "tests/runtime/test_local_vscode_tasks.py": _runtime_local_vscode_tasks_test_content(),
        "tests/runtime/test_model_smoke.py": _runtime_model_smoke_test_content(),
        "tests/runtime/test_evaluate_pipeline_smoke.py": _runtime_pipeline_smoke_test_content(),
        "tests/runtime/test_runtime_fixture_smoke.py": _runtime_bootstrap_test_content(),
        "tests/runtime/test_smoke_suite.py": _runtime_smoke_suite_test_content(),
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
        "phase": "runtime_seed_with_local_api_shell",
        "authorizing": False,
        "entry_roots": list(PHASE_ONE_ROOTS),
        "excluded_modules": list(EXCLUDED_MODULE_PREFIXES),
        "excluded_relative_paths": sorted(EXCLUDED_RELATIVE_PATHS),
        "excluded_path_prefixes": list(EXCLUDED_PATH_PREFIXES),
        "championless_fallback_contract": dict(CHAMPIONLESS_FALLBACK_CONTRACT),
        "explicit_stateful_admissions": list(EXPLICIT_STATEFUL_ADMISSIONS),
        "verify_before_include_paths": list(VERIFY_BEFORE_INCLUDE_PATHS),
        "source_of_truth_repo": "Genesis-Core",
        "skeleton_priority": "prioritize_v2_skeleton_completeness_before_content_migration",
        "workflow_files": [
            ".pre-commit-config.yaml",
            "AGENTS.md",
            ".github/copilot-instructions.md",
            "docs/SKELETON_SCOPE.md",
        ],
        "precommit_hook_ids": [
            "black",
            "ruff",
            "check-added-large-files",
            "check-merge-conflict",
            "check-yaml",
            "end-of-file-fixer",
            "trailing-whitespace",
            "check-json",
        ],
        "local_tooling_surfaces": [
            ".vscode/extensions.json",
            ".vscode/launch.json",
            ".vscode/mcp.json",
            ".vscode/settings.json",
            ".vscode/tasks.json",
            "config/mcp_settings.json",
            "mcp_server/server.py",
            "scripts/api/api_shell.py",
            "scripts/mcp/mcp_stdio.py",
            "scripts/smoke/backtest_smoke.py",
            "scripts/smoke/champion_smoke.py",
            "scripts/smoke/evaluate_champion_smoke.py",
            "scripts/smoke/fixture_smoke.py",
            "scripts/smoke/model_smoke.py",
            "scripts/smoke/smoke_suite.py",
            "scripts/validate/pytest_suite.py",
        ],
        "workspace_extension_recommendations": [
            "ms-python.python",
            "ms-python.vscode-pylance",
            "charliermarsh.ruff",
        ],
        "workspace_task_labels": [
            "genesis-v2: api shell",
            "genesis-v2: mcp stdio",
            "genesis-v2: smoke suite",
            "genesis-v2: pytest",
        ],
        "workspace_launch_labels": [
            "genesis-v2: api shell",
            "genesis-v2: mcp stdio",
            "genesis-v2: smoke suite",
            "genesis-v2: pytest",
        ],
        "workspace_settings_keys": [
            "python.analysis.extraPaths",
            "python.envFile",
            "python.testing.cwd",
            "python.testing.pytestArgs",
            "python.testing.pytestEnabled",
            "python.testing.unittestEnabled",
        ],
        "workspace_verification": {
            "extensions": {
                "workspace_file": ".vscode/extensions.json",
                "runtime_test_file": "tests/runtime/test_local_vscode_extensions.py",
            },
            "launch": {
                "workspace_file": ".vscode/launch.json",
                "runtime_test_file": "tests/runtime/test_local_vscode_launch.py",
            },
            "settings": {
                "workspace_file": ".vscode/settings.json",
                "runtime_test_file": "tests/runtime/test_local_vscode_settings.py",
            },
            "tasks": {
                "workspace_file": ".vscode/tasks.json",
                "runtime_test_file": "tests/runtime/test_local_vscode_tasks.py",
            },
        },
        "bootstrap_verification": {
            "env_template": {
                "tracked_file": ".env.example",
                "runtime_test_file": "tests/runtime/test_local_env_template.py",
            },
            "precommit": {
                "tracked_file": ".pre-commit-config.yaml",
                "runtime_test_file": "tests/runtime/test_local_precommit_config.py",
            },
        },
        "mcp_verification": {
            "workspace_registration": {
                "workspace_file": ".vscode/mcp.json",
                "config_file": "config/mcp_settings.json",
                "runtime_test_file": "tests/runtime/test_local_mcp_setup.py",
            },
            "local_launcher": {
                "tracked_file": "scripts/mcp/mcp_stdio.py",
                "runtime_test_file": "tests/runtime/test_local_mcp_script.py",
            },
        },
        "api_entrypoints": {
            "module_command": "python -m uvicorn core.server:app --app-dir src --reload",
            "console_scripts": ["genesis-v2-api-shell"],
            "script_commands": [
                "python scripts/api/api_shell.py",
                "python scripts/api/api_shell.py --reload",
            ],
        },
        "mcp_entrypoints": {
            "console_scripts": ["genesis-v2-mcp-stdio"],
            "editable_install_command": 'python -m pip install -e ".[mcp]"',
            "module_command": "python -m mcp_server.server",
            "script_commands": [
                "python scripts/mcp/mcp_stdio.py",
                "python scripts/mcp/mcp_stdio.py --print-config",
            ],
        },
        "pytest_entrypoints": {
            "console_scripts": ["genesis-v2-pytest"],
            "editable_install_command": 'python -m pip install -e ".[dev]"',
            "module_command": "python -m pytest -q",
            "script_commands": [
                "python scripts/validate/pytest_suite.py",
                "python scripts/validate/pytest_suite.py tests/runtime/test_local_api_shell_script.py -q",
            ],
        },
        "pyproject_tooling_sections": [
            "tool.pytest.ini_options.norecursedirs",
            "tool.ruff.extend-exclude",
            "tool.ruff.lint",
            "tool.black.extend-exclude",
        ],
        "workspace_loop_env": {"PYTHONPATH": "${workspaceFolder}/src"},
        "copied_files": sorted(copied_paths),
        "generated_files": sorted(generated_paths),
        "smoke_entrypoints": {
            "editable_install_command": 'python -m pip install -e ".[dev]"',
            "module_commands": [
                "python -m core.bootstrap.model_smoke",
                "python -m core.bootstrap.champion_smoke",
                "python -m core.bootstrap.evaluate_champion_smoke",
                "python -m core.bootstrap.fixture_smoke",
                "python -m core.bootstrap.backtest_smoke",
                "python -m core.bootstrap.smoke_suite",
            ],
            "script_commands": [
                "python scripts/smoke/fixture_smoke.py",
                "python scripts/smoke/backtest_smoke.py",
                "python scripts/smoke/champion_smoke.py",
                "python scripts/smoke/evaluate_champion_smoke.py",
                "python scripts/smoke/model_smoke.py",
                "python scripts/smoke/smoke_suite.py",
            ],
            "console_scripts": [
                "genesis-v2-champion-smoke",
                "genesis-v2-evaluate-champion-smoke",
                "genesis-v2-fixture-smoke",
                "genesis-v2-backtest-smoke",
                "genesis-v2-model-smoke",
                "genesis-v2-smoke-suite",
            ],
        },
        "install_verification": {
            "editable_install_command": 'python -m pip install -e ".[dev,mcp]"',
            "installed_console_script_test_command": "pytest tests/runtime/test_installed_console_scripts.py -q",
            "installed_console_script_test_file": "tests/runtime/test_installed_console_scripts.py",
            "optional_mcp_install_command": 'python -m pip install -e ".[mcp]"',
        },
        "blocked_imports": blocked_imports,
        "output_hashes": output_hashes,
        "notes": [
            "Runtime-first seed with local-only API shell generated locally.",
            "Workflow files make the V2 seed self-describing as a skeleton-first repository.",
            "Local stdio MCP tooling is admitted with a safe V2-specific config; remote MCP surfaces remain excluded.",
            "Generated `.vscode/tasks.json` and `.vscode/launch.json` provide repeatable local API/MCP/smoke/test loops via `PYTHONPATH=${workspaceFolder}/src`.",
            "Generated `.vscode/settings.json` aligns Python analysis and pytest discovery with the V2 `src` layout.",
            "Generated `.vscode/extensions.json` recommends Python/Pylance/Ruff extensions for the V2 editor workflow.",
            "Generated `.env.example` mirrors the narrow local placeholder `.env` for tracked bootstrap guidance.",
            "Generated `.pre-commit-config.yaml` keeps a narrow local formatting/lint/sanity hook loop tracked in the seed.",
            "Generated `pyproject.toml` carries narrow local pytest/ruff/black QA defaults for the V2 workspace.",
            "Generated `scripts/mcp/mcp_stdio.py` provides a non-installed local MCP stdio entrypoint against the V2 repo root and config path.",
            "Generated `scripts/api/api_shell.py` provides a non-installed local API entrypoint against the V2 `src` layout.",
            "Generated `scripts/validate/pytest_suite.py` provides a non-installed local pytest entrypoint against the V2 `src` layout.",
            "Generated `scripts/smoke/*.py` provide non-installed local smoke entrypoints against the V2 `src` layout.",
            "Exchange-facing, paper, public-data, and UI service edges are intentionally excluded.",
            "Pipeline, Optuna, and optimizer-only closure are intentionally excluded.",
            "Legacy `core.strategy.features` surface intentionally excluded.",
            "Only explicitly admitted stateful artifacts were carried over; champions and runtime state remained excluded.",
            "Generated `.env` contains placeholder local-shell values only.",
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
    source_model_paths = _source_config_model_paths(repo_root)

    if blocked_imports:
        raise SeedGenerationError(
            "Blocked excluded dependency detected during seed generation:\n"
            + "\n".join(blocked_imports)
        )

    source_head = _git_short_head(repo_root)
    copied_paths = [
        source.relative_path
        for source in source_files
        if source.relative_path not in GENERATED_SOURCE_OVERRIDES
    ] + source_model_paths
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
    _copy_source_config_models(destination, repo_root)
    _write_generated_files(destination, source_head=source_head)
    _write_manifest(destination, payload)
    return payload


def main() -> int:
    repo_root = _repo_root()
    parser = argparse.ArgumentParser(
        description="Materialize the Genesis-Core-V2 runtime-first seed with admitted local API and MCP shell"
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
