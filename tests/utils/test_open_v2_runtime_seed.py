from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import textwrap
import tomllib
from pathlib import Path
from types import ModuleType

import yaml

EXPECTED_BACKTEST_DEFAULTS = {
    "capital": 10000.0,
    "commission": 0.0,
    "slippage": 0.0005,
    "warmup": 120,
    "fast_window": True,
    "precompute_features": True,
}

EXPECTED_EXPLICIT_STATEFUL_ADMISSIONS = [
    "config/backtest_defaults.yaml",
    "config/models/**",
]

EXPECTED_CHAMPIONLESS_FALLBACK_CONTRACT = {
    "phase_one_champion_policy": "exclude_config_strategy_champions",
    "fallback_loader": "core.strategy.champion_loader.ChampionLoader",
    "runtime_fallback_source": "config/timeframe_configs.py",
    "runtime_behavior": "fallback_to_timeframe_configs_when_champion_missing_or_invalid",
}

EXPECTED_VERIFY_BEFORE_INCLUDE_PATHS = [
    "config/runtime.json",
    "config/runtime.seed.json",
    "config/strategy/champions/**",
    "data/**",
]

EXPECTED_API_RUNTIME_DEPS = {
    "fastapi>=0.116,<0.117",
    "uvicorn>=0.24,<0.25",
    "pydantic-settings>=2,<3",
}

EXPECTED_ADMITTED_API_SLICE_FILES = [
    "src/core/server.py",
    "src/core/api/config.py",
    "src/core/api/models.py",
    "src/core/api/status.py",
    "src/core/api/strategy.py",
    "src/core/config/validator.py",
    "src/core/config/legacy_schema_v1.json",
    "tests/integration/test_config_endpoints.py",
]

EXPECTED_WORKFLOW_FILES = [
    ".pre-commit-config.yaml",
    "AGENTS.md",
    ".github/copilot-instructions.md",
    "docs/SKELETON_SCOPE.md",
]

EXPECTED_SKELETON_PRIORITY = "prioritize_v2_skeleton_completeness_before_content_migration"

EXPECTED_LOCAL_MCP_FILES = [
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

EXPECTED_LOCAL_TASK_FILES = [
    ".vscode/tasks.json",
    "tests/runtime/test_local_vscode_tasks.py",
]

EXPECTED_LOCAL_LAUNCH_FILES = [
    ".vscode/launch.json",
    "tests/runtime/test_local_vscode_launch.py",
]

EXPECTED_LOCAL_SETTINGS_FILES = [
    ".vscode/settings.json",
    "tests/runtime/test_local_vscode_settings.py",
]

EXPECTED_LOCAL_ENV_TEMPLATE_FILES = [
    ".env.example",
    "tests/runtime/test_local_env_template.py",
]

EXPECTED_LOCAL_PRECOMMIT_FILES = [
    ".pre-commit-config.yaml",
    "tests/runtime/test_local_precommit_config.py",
]

EXPECTED_LOCAL_EXTENSION_FILES = [
    ".vscode/extensions.json",
    "tests/runtime/test_local_vscode_extensions.py",
]

EXPECTED_LOCAL_SCRIPT_FILES = [
    "scripts/smoke/backtest_smoke.py",
    "scripts/smoke/fixture_smoke.py",
    "scripts/smoke/smoke_suite.py",
    "tests/runtime/test_local_smoke_scripts.py",
]

EXPECTED_REMOTE_MCP_DEFERRED_FILES = [
    "config/mcp_settings.remote_git.json",
    "config/mcp_settings.remote_safe.json",
    "mcp_server/remote_server.py",
]

EXPECTED_MCP_OPTIONAL_DEPS = [
    "mcp>=0.9,<1",
]

EXPECTED_WORKSPACE_TASK_LABELS = [
    "genesis-v2: api shell",
    "genesis-v2: smoke suite",
    "genesis-v2: pytest",
]

EXPECTED_WORKSPACE_LAUNCH_LABELS = [
    "genesis-v2: api shell",
    "genesis-v2: smoke suite",
    "genesis-v2: pytest",
]

EXPECTED_WORKSPACE_SETTINGS_KEYS = [
    "python.analysis.extraPaths",
    "python.envFile",
    "python.testing.cwd",
    "python.testing.pytestArgs",
    "python.testing.pytestEnabled",
    "python.testing.unittestEnabled",
]

EXPECTED_WORKSPACE_EXTENSION_RECOMMENDATIONS = [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
]

EXPECTED_PYPROJECT_PYTEST_NORECURSEDIRS = [
    "cache",
    "data",
    "logs",
    "results",
    ".venv",
]

EXPECTED_PYPROJECT_RUFF_EXTEND_EXCLUDE = [
    ".venv/",
    "cache/",
    "data/",
    "logs/",
    "results/",
]

EXPECTED_PYPROJECT_RUFF_SELECT = ["E", "W", "F", "I", "B", "C4", "UP"]

EXPECTED_PYPROJECT_RUFF_IGNORE = ["E501", "B008", "C901"]

EXPECTED_PYPROJECT_BLACK_EXTEND_EXCLUDE = "(^cache/|^data/|^logs/|^results/)"

EXPECTED_LOCAL_SCRIPT_COMMANDS = [
    "python scripts/smoke/fixture_smoke.py",
    "python scripts/smoke/backtest_smoke.py",
    "python scripts/smoke/smoke_suite.py",
]

EXPECTED_PRECOMMIT_HOOK_IDS = [
    "black",
    "ruff",
    "check-added-large-files",
    "check-merge-conflict",
    "check-yaml",
    "end-of-file-fixer",
    "trailing-whitespace",
    "check-json",
]

EXPECTED_WORKSPACE_LOOP_ENV = {"PYTHONPATH": "${workspaceFolder}/src"}

EXPECTED_DEFERRED_SERVICE_EDGE_FILES = [
    "src/core/api/account.py",
    "src/core/api/info.py",
    "src/core/api/paper.py",
    "src/core/api/public.py",
    "src/core/api/ui.py",
]

EXPECTED_DEFERRED_SERVICE_EDGE_PREFIXES = [
    "src/core/io",
]

EXPECTED_DEFERRED_SERVICE_EDGE_MODULE_PREFIXES = {
    "core.api.account",
    "core.api.info",
    "core.api.paper",
    "core.api.public",
    "core.api.ui",
    "core.io",
}

EXPECTED_PRUNED_CLOSURE_FILES = [
    "src/core/pipeline.py",
    "src/core/utils/optuna_helpers.py",
    "src/core/utils/diffing/optuna_guard.py",
    "src/core/utils/diffing/results_diff.py",
    "src/core/utils/diffing/trial_cache.py",
]

EXPECTED_PRUNED_CLOSURE_PREFIXES = [
    "src/core/optimizer",
]

EXPECTED_PRUNED_MODULE_PREFIXES = {
    "core.optimizer",
    "core.pipeline",
    "core.utils.diffing.optuna_guard",
    "core.utils.diffing.results_diff",
    "core.utils.diffing.trial_cache",
    "core.utils.optuna_helpers",
}


def _source_model_file_names(repo_root: Path) -> list[str]:
    return sorted(path.name for path in (repo_root / "config" / "models").glob("*.json"))


def _load_open_v2_runtime_seed_module() -> ModuleType:
    repo_root = Path(__file__).resolve().parents[2]
    module_path = repo_root / "scripts" / "extract" / "open_v2_runtime_seed.py"
    spec = importlib.util.spec_from_file_location("test_open_v2_runtime_seed_module", module_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load module from {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_generate_seed_emits_conflict_free_console_script_targets(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    payload = tomllib.loads((destination / "pyproject.toml").read_text(encoding="utf-8"))

    assert payload["project"]["scripts"] == {
        "genesis-v2-fixture-smoke": "genesis_core_v2_cli.console_scripts:fixture_smoke_main",
        "genesis-v2-backtest-smoke": "genesis_core_v2_cli.console_scripts:backtest_smoke_main",
        "genesis-v2-smoke-suite": "genesis_core_v2_cli.console_scripts:smoke_suite_main",
    }
    assert payload["tool"]["setuptools"]["packages"]["find"]["include"] == [
        "core*",
        "genesis_core_v2_cli*",
    ]
    assert (destination / "src" / "genesis_core_v2_cli" / "console_scripts.py").exists()


def test_generate_seed_emits_narrow_pyproject_tooling_defaults(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    pyproject = tomllib.loads((destination / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))
    readme = (destination / "README.md").read_text(encoding="utf-8")
    scope_text = (destination / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")

    assert (
        pyproject["tool"]["pytest"]["ini_options"]["norecursedirs"]
        == EXPECTED_PYPROJECT_PYTEST_NORECURSEDIRS
    )
    assert pyproject["tool"]["ruff"]["extend-exclude"] == EXPECTED_PYPROJECT_RUFF_EXTEND_EXCLUDE
    assert pyproject["tool"]["ruff"]["lint"]["select"] == EXPECTED_PYPROJECT_RUFF_SELECT
    assert pyproject["tool"]["ruff"]["lint"]["ignore"] == EXPECTED_PYPROJECT_RUFF_IGNORE
    assert pyproject["tool"]["black"]["extend-exclude"] == EXPECTED_PYPROJECT_BLACK_EXTEND_EXCLUDE
    assert manifest["pyproject_tooling_sections"] == [
        "tool.pytest.ini_options.norecursedirs",
        "tool.ruff.extend-exclude",
        "tool.ruff.lint",
        "tool.black.extend-exclude",
    ]
    assert (
        "Generated `pyproject.toml` carries narrow local pytest/ruff/black QA defaults for the V2 workspace."
        in manifest["notes"]
    )
    assert "pyproject.toml" in readme
    assert "narrow local QA defaults" in readme
    assert "pyproject.toml" in scope_text


def test_generate_seed_emits_narrow_backtest_defaults(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    defaults_path = destination / "config" / "backtest_defaults.yaml"

    assert defaults_path.exists()
    assert yaml.safe_load(defaults_path.read_text(encoding="utf-8")) == EXPECTED_BACKTEST_DEFAULTS


def test_generate_seed_admits_api_service_shell_and_validator_schema(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    for relative_path in EXPECTED_ADMITTED_API_SLICE_FILES:
        assert (destination / relative_path).exists(), relative_path

    readme = (destination / "README.md").read_text(encoding="utf-8")
    assert "admitted local-only API shell (`src/core/server.py`," in readme
    assert "generated `.env` contains only\nlocal-shell placeholders" in readme
    assert "## Skeleton workflow" in readme
    assert "`docs/SKELETON_SCOPE.md` records Track A vs Track B" in readme


def test_generate_seed_emits_skeleton_workflow_files(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    for relative_path in EXPECTED_WORKFLOW_FILES:
        assert (destination / relative_path).exists(), relative_path

    agents_text = (destination / "AGENTS.md").read_text(encoding="utf-8")
    instructions_text = (destination / ".github" / "copilot-instructions.md").read_text(
        encoding="utf-8"
    )
    scope_text = (destination / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")
    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))

    assert "Prioritize V2 skeleton completeness before content migration." in agents_text
    assert (
        "Prefer generator-driven changes in `Genesis-Core` over manual drift in this repo."
        in instructions_text
    )
    assert "Track A — skeleton completeness" in scope_text
    assert "Track B — authority migration" in scope_text
    assert manifest["source_of_truth_repo"] == "Genesis-Core"
    assert manifest["skeleton_priority"] == EXPECTED_SKELETON_PRIORITY
    assert manifest["workflow_files"] == EXPECTED_WORKFLOW_FILES
    assert (
        "Workflow files make the V2 seed self-describing as a skeleton-first repository."
        in manifest["notes"]
    )


def test_generate_seed_admits_local_mcp_shell(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    for relative_path in EXPECTED_LOCAL_MCP_FILES:
        assert (destination / relative_path).exists(), relative_path

    for relative_path in EXPECTED_REMOTE_MCP_DEFERRED_FILES:
        assert not (destination / relative_path).exists(), relative_path

    pyproject = tomllib.loads((destination / "pyproject.toml").read_text(encoding="utf-8"))
    readme = (destination / "README.md").read_text(encoding="utf-8")
    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))
    vscode_payload = json.loads((destination / ".vscode" / "mcp.json").read_text(encoding="utf-8"))
    settings_payload = json.loads(
        (destination / "config" / "mcp_settings.json").read_text(encoding="utf-8")
    )

    assert pyproject["project"]["optional-dependencies"]["mcp"] == EXPECTED_MCP_OPTIONAL_DEPS
    assert vscode_payload["servers"]["genesis-core-v2"]["args"] == ["-m", "mcp_server.server"]
    assert (
        vscode_payload["servers"]["genesis-core-v2"]["env"]["GENESIS_MCP_CONFIG_PATH"]
        == "config/mcp_settings.json"
    )
    assert settings_payload["server_name"] == "genesis-core-v2"
    assert settings_payload["features"] == {
        "code_execution": False,
        "file_operations": True,
        "git_integration": True,
    }
    assert ".vscode" in settings_payload["security"]["allowed_paths"]
    assert "mcp_server" in settings_payload["security"]["allowed_paths"]
    assert "scripts" in settings_payload["security"]["allowed_paths"]
    assert "config/runtime.json" in settings_payload["security"]["blocked_patterns"]
    assert "local MCP stdio shell" in readme
    assert "Optional local MCP install:" in readme
    assert {
        ".vscode/mcp.json",
        "config/mcp_settings.json",
        "mcp_server/server.py",
    }.issubset(set(manifest["local_tooling_surfaces"]))
    assert (
        "Local stdio MCP tooling is admitted with a safe V2-specific config; remote MCP surfaces remain excluded."
        in manifest["notes"]
    )


def test_generate_seed_emits_local_vscode_task_loop(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    for relative_path in EXPECTED_LOCAL_TASK_FILES:
        assert (destination / relative_path).exists(), relative_path

    readme = (destination / "README.md").read_text(encoding="utf-8")
    scope_text = (destination / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")
    instructions_text = (destination / ".github" / "copilot-instructions.md").read_text(
        encoding="utf-8"
    )
    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))
    tasks_payload = json.loads((destination / ".vscode" / "tasks.json").read_text(encoding="utf-8"))
    tasks = {task["label"]: task for task in tasks_payload["tasks"]}

    assert tasks_payload["version"] == "2.0.0"
    assert tasks_payload["options"] == {
        "cwd": "${workspaceFolder}",
        "env": EXPECTED_WORKSPACE_LOOP_ENV,
    }
    assert manifest["workspace_task_labels"] == EXPECTED_WORKSPACE_TASK_LABELS
    assert ".vscode/tasks.json" in manifest["local_tooling_surfaces"]
    assert (
        "Generated `.vscode/tasks.json` and `.vscode/launch.json` provide repeatable local API/smoke/test loops via `PYTHONPATH=${workspaceFolder}/src`."
        in manifest["notes"]
    )
    assert tasks["genesis-v2: api shell"]["args"] == [
        "-m",
        "uvicorn",
        "core.server:app",
        "--app-dir",
        "src",
        "--reload",
    ]
    assert tasks["genesis-v2: api shell"]["isBackground"] is True
    assert tasks["genesis-v2: smoke suite"]["args"] == ["-m", "core.bootstrap.smoke_suite"]
    assert tasks["genesis-v2: pytest"]["args"] == ["-m", "pytest", "-q"]
    assert tasks["genesis-v2: pytest"]["group"] == {"kind": "test", "isDefault": True}
    assert "Local VS Code tasks:" in readme
    assert ".vscode/tasks.json" in scope_text
    assert "generated local VS Code tasks" in instructions_text


def test_generate_seed_emits_local_vscode_settings(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    for relative_path in EXPECTED_LOCAL_SETTINGS_FILES:
        assert (destination / relative_path).exists(), relative_path

    readme = (destination / "README.md").read_text(encoding="utf-8")
    scope_text = (destination / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")
    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))
    settings_payload = json.loads(
        (destination / ".vscode" / "settings.json").read_text(encoding="utf-8")
    )

    assert ".vscode/settings.json" in manifest["local_tooling_surfaces"]
    assert manifest["workspace_settings_keys"] == EXPECTED_WORKSPACE_SETTINGS_KEYS
    assert (
        "Generated `.vscode/settings.json` aligns Python analysis and pytest discovery with the V2 `src` layout."
        in manifest["notes"]
    )
    assert settings_payload["python.analysis.extraPaths"] == ["${workspaceFolder}/src"]
    assert settings_payload["python.envFile"] == "${workspaceFolder}/.env"
    assert settings_payload["python.testing.cwd"] == "${workspaceFolder}"
    assert settings_payload["python.testing.pytestArgs"] == ["-q"]
    assert settings_payload["python.testing.pytestEnabled"] is True
    assert settings_payload["python.testing.unittestEnabled"] is False
    assert ".vscode/settings.json" in readme
    assert "Python analysis/test settings" in readme
    assert ".vscode/settings.json" in scope_text


def test_generate_seed_emits_local_env_template(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    for relative_path in EXPECTED_LOCAL_ENV_TEMPLATE_FILES:
        assert (destination / relative_path).exists(), relative_path

    readme = (destination / "README.md").read_text(encoding="utf-8")
    scope_text = (destination / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")
    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))
    template_text = (destination / ".env.example").read_text(encoding="utf-8")

    assert ".env.example" in manifest["generated_files"]
    assert (
        "Generated `.env.example` mirrors the narrow local placeholder `.env` for tracked bootstrap guidance."
        in manifest["notes"]
    )
    assert "# Copy this file to .env for local use." in template_text
    assert "BEARER_TOKEN=change-me" in template_text
    assert "SYMBOL_MODE=realistic" in template_text
    assert "LOG_LEVEL=INFO" in template_text
    assert ".env.example" in readme
    assert "tracked env bootstrap template" in readme
    assert ".env.example" in scope_text


def test_generate_seed_emits_local_precommit_workflow(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    for relative_path in EXPECTED_LOCAL_PRECOMMIT_FILES:
        assert (destination / relative_path).exists(), relative_path

    readme = (destination / "README.md").read_text(encoding="utf-8")
    scope_text = (destination / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")
    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))
    pyproject = tomllib.loads((destination / "pyproject.toml").read_text(encoding="utf-8"))
    precommit_payload = yaml.safe_load(
        (destination / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    )

    hook_ids = [hook["id"] for repo in precommit_payload["repos"] for hook in repo.get("hooks", [])]

    assert ".pre-commit-config.yaml" in manifest["generated_files"]
    assert manifest["precommit_hook_ids"] == EXPECTED_PRECOMMIT_HOOK_IDS
    assert "pre-commit>=3.0" in pyproject["project"]["optional-dependencies"]["dev"]
    assert hook_ids == EXPECTED_PRECOMMIT_HOOK_IDS
    assert (
        "Generated `.pre-commit-config.yaml` keeps a narrow local formatting/lint/sanity hook loop tracked in the seed."
        in manifest["notes"]
    )
    assert ".pre-commit-config.yaml" in readme
    assert "Local pre-commit workflow" in readme
    assert ".pre-commit-config.yaml" in scope_text


def test_generate_seed_emits_local_vscode_extensions(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    for relative_path in EXPECTED_LOCAL_EXTENSION_FILES:
        assert (destination / relative_path).exists(), relative_path

    readme = (destination / "README.md").read_text(encoding="utf-8")
    scope_text = (destination / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")
    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))
    extensions_payload = json.loads(
        (destination / ".vscode" / "extensions.json").read_text(encoding="utf-8")
    )

    assert ".vscode/extensions.json" in manifest["local_tooling_surfaces"]
    assert (
        manifest["workspace_extension_recommendations"]
        == EXPECTED_WORKSPACE_EXTENSION_RECOMMENDATIONS
    )
    assert (
        "Generated `.vscode/extensions.json` recommends Python/Pylance/Ruff extensions for the V2 editor workflow."
        in manifest["notes"]
    )
    assert extensions_payload["recommendations"] == EXPECTED_WORKSPACE_EXTENSION_RECOMMENDATIONS
    assert extensions_payload["unwantedRecommendations"] == []
    assert ".vscode/extensions.json" in readme
    assert "Suggested VS Code extensions" in readme
    assert ".vscode/extensions.json" in scope_text


def test_generate_seed_emits_local_smoke_scripts(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    readme = (destination / "README.md").read_text(encoding="utf-8")
    scope_text = (destination / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")
    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))

    for relative_path in EXPECTED_LOCAL_SCRIPT_FILES:
        assert (destination / relative_path).exists(), relative_path

    assert set(EXPECTED_LOCAL_SCRIPT_FILES[:-1]).issubset(set(manifest["local_tooling_surfaces"]))
    assert manifest["smoke_entrypoints"]["script_commands"] == EXPECTED_LOCAL_SCRIPT_COMMANDS
    assert (
        "Generated `scripts/smoke/*.py` provide non-installed local smoke entrypoints against the V2 `src` layout."
        in manifest["notes"]
    )
    assert "Non-installed local smoke scripts:" in readme
    assert "python scripts/smoke/smoke_suite.py" in readme
    assert "scripts/smoke/*.py" in scope_text


def test_generate_seed_emits_local_vscode_launch_loop(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    for relative_path in EXPECTED_LOCAL_LAUNCH_FILES:
        assert (destination / relative_path).exists(), relative_path

    readme = (destination / "README.md").read_text(encoding="utf-8")
    scope_text = (destination / "docs" / "SKELETON_SCOPE.md").read_text(encoding="utf-8")
    instructions_text = (destination / ".github" / "copilot-instructions.md").read_text(
        encoding="utf-8"
    )
    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))
    launch_payload = json.loads(
        (destination / ".vscode" / "launch.json").read_text(encoding="utf-8")
    )
    launch_configs = {config["name"]: config for config in launch_payload["configurations"]}

    assert manifest["workspace_launch_labels"] == EXPECTED_WORKSPACE_LAUNCH_LABELS
    assert ".vscode/launch.json" in manifest["local_tooling_surfaces"]
    assert manifest["workspace_loop_env"] == EXPECTED_WORKSPACE_LOOP_ENV
    assert (
        "Generated `.vscode/tasks.json` and `.vscode/launch.json` provide repeatable local API/smoke/test loops via `PYTHONPATH=${workspaceFolder}/src`."
        in manifest["notes"]
    )
    assert launch_payload["version"] == "0.2.0"
    assert launch_configs["genesis-v2: api shell"]["module"] == "uvicorn"
    assert launch_configs["genesis-v2: smoke suite"]["module"] == "core.bootstrap.smoke_suite"
    assert launch_configs["genesis-v2: pytest"]["module"] == "pytest"
    assert launch_configs["genesis-v2: pytest"]["purpose"] == ["debug-test"]
    assert launch_configs["genesis-v2: smoke suite"]["env"] == EXPECTED_WORKSPACE_LOOP_ENV
    assert "Local VS Code debug profiles:" in readme
    assert ".vscode/launch.json" in scope_text
    assert "debug profiles" in instructions_text

    loop_env = dict(os.environ)
    loop_env["PYTHONPATH"] = str(destination / "src")
    completed = subprocess.run(
        [sys.executable, "-m", "core.bootstrap.smoke_suite"],
        cwd=destination,
        env=loop_env,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["suite"] == "runtime_smoke_suite_v1"
    assert payload["checks"]["fixture_smoke"] == "passed"


def test_generate_seed_emits_api_runtime_dependencies_and_placeholder_env(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    payload = tomllib.loads((destination / "pyproject.toml").read_text(encoding="utf-8"))
    dependencies = set(payload["project"]["dependencies"])

    assert EXPECTED_API_RUNTIME_DEPS.issubset(dependencies)

    env_text = (destination / ".env").read_text(encoding="utf-8")
    env_example_text = (destination / ".env.example").read_text(encoding="utf-8")
    assert "BEARER_TOKEN=change-me" in env_text
    assert "SYMBOL_MODE=realistic" in env_text
    assert "LOG_LEVEL=INFO" in env_text
    assert "# Copy this file to .env for local use." in env_example_text
    assert "BITFINEX_API_KEY=" not in env_example_text
    assert "httpx>=0.25,<0.26" not in dependencies
    assert "websockets>=12,<13" not in dependencies
    assert "BITFINEX_API_KEY=" not in env_text
    assert "optuna>=3.5,<5" not in dependencies


def test_generate_seed_clean_preserves_existing_git_directory(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"
    git_object = destination / ".git" / "objects" / "01" / "placeholder"
    stale_file = destination / "stale.txt"

    git_object.parent.mkdir(parents=True, exist_ok=True)
    git_object.write_text("keep-me", encoding="utf-8")
    stale_file.parent.mkdir(parents=True, exist_ok=True)
    stale_file.write_text("remove-me", encoding="utf-8")

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    assert git_object.exists()
    assert git_object.read_text(encoding="utf-8") == "keep-me"
    assert not stale_file.exists()
    assert (destination / "seed_manifest.json").exists()


def test_generate_seed_prunes_pipeline_optimizer_and_optuna_closure(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    for relative_path in EXPECTED_PRUNED_CLOSURE_FILES:
        assert not (destination / relative_path).exists(), relative_path

    for relative_prefix in EXPECTED_PRUNED_CLOSURE_PREFIXES:
        assert not (destination / relative_prefix).exists(), relative_prefix

    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))
    readme = (destination / "README.md").read_text(encoding="utf-8")

    assert EXPECTED_PRUNED_MODULE_PREFIXES.issubset(set(manifest["excluded_modules"]))
    assert "src/core/pipeline.py" in manifest["excluded_relative_paths"]
    assert "src/core/optimizer/" in manifest["excluded_path_prefixes"]
    assert (
        "Pipeline, Optuna, and optimizer-only closure are intentionally excluded."
        in manifest["notes"]
    )
    assert "`src/core/optimizer/**`" in readme
    assert "`src/core/utils/optuna_helpers.py`" in readme


def test_generate_seed_defers_private_exchange_service_edges(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    for relative_path in EXPECTED_DEFERRED_SERVICE_EDGE_FILES:
        assert not (destination / relative_path).exists(), relative_path

    for relative_prefix in EXPECTED_DEFERRED_SERVICE_EDGE_PREFIXES:
        assert not (destination / relative_prefix).exists(), relative_prefix

    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))
    readme = (destination / "README.md").read_text(encoding="utf-8")

    assert EXPECTED_DEFERRED_SERVICE_EDGE_MODULE_PREFIXES.issubset(
        set(manifest["excluded_modules"])
    )
    assert "src/core/io/" in manifest["excluded_path_prefixes"]
    assert (
        "Exchange-facing, paper, public-data, and UI service edges are intentionally excluded."
        in manifest["notes"]
    )
    assert "`src/core/api/{account,info,paper,public,ui}.py`" in readme
    assert "`src/core/io/**`" in readme


def test_generate_seed_copies_source_config_models_and_keeps_fixture_models_separate(
    tmp_path: Path,
) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    repo_root = Path(__file__).resolve().parents[2]
    expected_model_files = _source_model_file_names(repo_root)
    destination_model_files = _source_model_file_names(destination)

    assert destination_model_files == expected_model_files

    source_registry = json.loads(
        (repo_root / "config" / "models" / "registry.json").read_text(encoding="utf-8")
    )
    destination_registry = json.loads(
        (destination / "config" / "models" / "registry.json").read_text(encoding="utf-8")
    )
    fixture_registry = json.loads(
        (
            destination
            / "registry"
            / "fixtures"
            / "model_registry"
            / "config"
            / "models"
            / "registry.json"
        ).read_text(encoding="utf-8")
    )

    assert destination_registry == source_registry
    assert fixture_registry == {"tBTCUSD:1h": {"champion": "config/models/tBTCUSD_1h.json"}}


def test_generated_console_script_shim_prefers_local_v2_src(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"
    seed_module.generate_seed(destination, clean=True, dry_run=False)

    repo_root = Path(__file__).resolve().parents[2]
    repo_src_literal = json.dumps(str((repo_root / "src").resolve()))
    destination_src_literal = json.dumps(str((destination / "src").resolve()))
    shim_path_literal = json.dumps(
        str((destination / "src" / "genesis_core_v2_cli" / "console_scripts.py").resolve())
    )

    code = textwrap.dedent(
        f"""
        import importlib.util
        import pathlib
        import sys

        repo_src = pathlib.Path({repo_src_literal})
        destination_src = pathlib.Path({destination_src_literal})
        sys.path = [str(repo_src)] + [
            path for path in sys.path if pathlib.Path(path).resolve() != destination_src.resolve()
        ]

        spec = importlib.util.spec_from_file_location(
            "genesis_core_v2_cli.console_scripts",
            pathlib.Path({shim_path_literal}),
        )
        if spec is None or spec.loader is None:
            raise AssertionError("Unable to load generated console script shim")

        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        raise SystemExit(module.fixture_smoke_main())
        """
    )

    completed = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        check=True,
    )

    assert '"action": "NONE"' in completed.stdout
    assert '"prob_model": "seed_model_fixture_v1"' in completed.stdout


def test_generate_seed_keeps_runtime_state_data_and_champion_authority_out_of_phase_one(
    tmp_path: Path,
) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    assert not (destination / "config" / "runtime.json").exists()
    assert not (destination / "config" / "runtime.seed.json").exists()
    assert not (destination / "config" / "strategy" / "champions").exists()
    assert not (destination / "data").exists()

    manifest = json.loads((destination / "seed_manifest.json").read_text(encoding="utf-8"))
    readme = (destination / "README.md").read_text(encoding="utf-8")

    assert manifest["championless_fallback_contract"] == EXPECTED_CHAMPIONLESS_FALLBACK_CONTRACT
    assert manifest["explicit_stateful_admissions"] == EXPECTED_EXPLICIT_STATEFUL_ADMISSIONS
    assert manifest["verify_before_include_paths"] == EXPECTED_VERIFY_BEFORE_INCLUDE_PATHS
    assert "Phase 1 intentionally excludes `config/strategy/champions/**`" in readme
    assert "`config/timeframe_configs.py` through `ChampionLoader`" in readme
