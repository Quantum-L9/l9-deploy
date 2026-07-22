"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, compliance]
tags: [L9_TEST, portability, path-confinement, release-metadata]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import importlib
import re
import subprocess
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from l9_deploy.contracts.models import DeploymentPlan, DeploymentProfile, FleetInventory
from l9_deploy.execution.remote import LocalExecutor

ROOT = Path(__file__).resolve().parents[2]


def _run_script(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_operational_scripts_bootstrap_clean_checkout(tmp_path: Path) -> None:
    help_scripts = (
        "scripts/collect-github-approval.py",
        "scripts/package-adoption-kit.py",
        "scripts/prepare-deployment.py",
        "scripts/promote-request.py",
    )
    for script in help_scripts:
        result = _run_script(script, "--help")
        assert result.returncode == 0, f"{script}: {result.stderr}"

    contracts = _run_script("scripts/validate-contracts.py")
    assert contracts.returncode == 0, contracts.stderr

    inventory = _run_script(
        "scripts/generate-inventory.py",
        "--output",
        str(tmp_path / "hosts.yml"),
    )
    assert inventory.returncode == 0, inventory.stderr
    assert (tmp_path / "hosts.yml").is_file()


def test_importing_package_main_has_no_process_side_effect() -> None:
    module = importlib.import_module("l9_deploy.__main__")
    assert callable(module.main)


def test_release_version_is_consistent() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    runtime = (ROOT / "src/l9_deploy/__init__.py").read_text(encoding="utf-8")
    lockfile = (ROOT / "uv.lock").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

    package_version = re.search(r'^version = "([^"]+)"$', pyproject, re.MULTILINE)
    runtime_version = re.search(r'^__version__ = "([^"]+)"$', runtime, re.MULTILINE)
    lock_version = re.search(
        r'name = "l9-deployment-platform"\nversion = "([^"]+)"',
        lockfile,
    )
    changelog_version = re.search(r"^## ([0-9]+\.[0-9]+\.[0-9]+) -", changelog, re.MULTILINE)
    assert package_version and runtime_version and lock_version and changelog_version
    versions = {
        package_version.group(1),
        runtime_version.group(1),
        lock_version.group(1),
        changelog_version.group(1),
    }
    assert len(versions) == 1, f"release version drift: {sorted(versions)}"


def test_typed_contracts_reject_path_traversal(
    profile: dict[str, object], deployment_context: dict[str, object]
) -> None:
    bad_profile = dict(profile)
    bad_project = dict(bad_profile["project"])  # type: ignore[arg-type]
    bad_project["id"] = "../../escape"
    bad_profile["project"] = bad_project
    with pytest.raises(ValidationError):
        DeploymentProfile.model_validate(bad_profile)

    bad_fleet = dict(deployment_context["fleet"])  # type: ignore[arg-type]
    bad_projects = [dict(item) for item in bad_fleet["projects"]]  # type: ignore[index]
    bad_projects[0]["profile_path"] = "../outside.yaml"
    bad_fleet["projects"] = bad_projects
    with pytest.raises(ValidationError):
        FleetInventory.model_validate(bad_fleet)


def test_deployment_plan_rejects_unsafe_project_id(
    deployment_context: dict[str, object], schema_registry
) -> None:  # type: ignore[no-untyped-def]
    from l9_deploy.planning.planner import build_plan
    from l9_deploy.requests.verifier import verify_request

    verified = verify_request(
        deployment_context["request"],  # type: ignore[arg-type]
        deployment_context["fleet"],  # type: ignore[arg-type]
        schema_registry,
        deployment_context["root"],  # type: ignore[arg-type]
        evidence_root=deployment_context["evidence_root"],  # type: ignore[arg-type]
        bundle_validator=deployment_context["bundle_validator"],  # type: ignore[arg-type]
    )
    plan = build_plan(verified, created_at="2026-07-21T12:00:01Z").model_dump(
        mode="json", by_alias=True
    )
    plan["project_id"] = "../escape"
    with pytest.raises(ValidationError):
        DeploymentPlan.model_validate(plan)


def test_local_executor_rejects_escape(tmp_path: Path) -> None:
    executor = LocalExecutor(tmp_path / "root")
    with pytest.raises(ValueError, match="escapes its root"):
        executor.write_text(Path("../escape.txt"), "blocked")
    assert not (tmp_path / "escape.txt").exists()


def test_workflow_validator_runs_as_standalone_script() -> None:
    result = _run_script("scripts/validate-workflows.py")
    assert result.returncode == 0, result.stderr


def test_workflow_validator_rejects_duplicate_mapping_keys(tmp_path: Path) -> None:
    workflows = tmp_path / ".github/workflows"
    workflows.mkdir(parents=True)
    (workflows / "duplicate.yml").write_text(
        """name: Duplicate
on: workflow_dispatch
permissions:
  actions: read
  actions: write
jobs: {}
""",
        encoding="utf-8",
    )
    result = _run_script(
        "scripts/validate-workflows.py",
        "--root",
        str(tmp_path),
    )
    assert result.returncode != 0
    assert "duplicate key" in result.stderr
