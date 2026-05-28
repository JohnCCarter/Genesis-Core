from __future__ import annotations

import importlib.util
import json
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

EXPECTED_VERIFY_BEFORE_INCLUDE_PATHS = [
    "config/runtime.json",
    "config/runtime.seed.json",
    "config/strategy/champions/**",
    "data/**",
]


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


def test_generate_seed_emits_narrow_backtest_defaults(tmp_path: Path) -> None:
    seed_module = _load_open_v2_runtime_seed_module()
    destination = tmp_path / "Genesis-Core-V2"

    seed_module.generate_seed(destination, clean=True, dry_run=False)

    defaults_path = destination / "config" / "backtest_defaults.yaml"

    assert defaults_path.exists()
    assert yaml.safe_load(defaults_path.read_text(encoding="utf-8")) == EXPECTED_BACKTEST_DEFAULTS


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

    assert manifest["explicit_stateful_admissions"] == EXPECTED_EXPLICIT_STATEFUL_ADMISSIONS
    assert manifest["verify_before_include_paths"] == EXPECTED_VERIFY_BEFORE_INCLUDE_PATHS
