"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, compliance]
tags: [L9_TEST, coverage, release-quality]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import tomllib
from pathlib import Path

from l9_deploy.release_inventory import is_forbidden_release_path

ROOT = Path(__file__).resolve().parents[2]


def test_coverage_is_a_warning_free_merge_gate() -> None:
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    addopts = config["tool"]["pytest"]["ini_options"]["addopts"]
    report = config["tool"]["coverage"]["report"]
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    workflow = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")

    assert "-W error" in addopts
    for command_surface in (makefile, workflow):
        assert "--cov=l9_deploy" in command_surface
        assert "--cov-branch" in command_surface
        assert "--cov-report=xml" in command_surface
        assert "--cov-fail-under=75" in command_surface
    assert report["fail_under"] >= 75


def test_coverage_outputs_cannot_enter_release_archives() -> None:
    assert is_forbidden_release_path(Path(".coverage"))
    assert is_forbidden_release_path(Path("coverage.xml"))
    assert is_forbidden_release_path(Path("artifacts/coverage.xml"))
