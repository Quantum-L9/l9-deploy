"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer:
- tests
tags:
- L9_META
- deployment-platform
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def test_each_opentofu_environment_has_required_files() -> None:
    for environment in ("management", "staging", "production"):
        root = ROOT / "infrastructure/opentofu/environments" / environment
        assert (root / "main.tf").is_file()
        assert (root / "variables.tf").is_file()
        assert (root / "outputs.tf").is_file()
        assert (root / "backend.tf").is_file()


def test_all_ansible_playbooks_are_yaml_objects() -> None:
    for path in sorted((ROOT / "ansible/playbooks").glob("*.yml")):
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(value, list)
        assert value


def test_runner_is_repository_scoped_in_defaults() -> None:
    defaults = yaml.safe_load(
        (ROOT / "ansible/roles/github_runner/defaults/main.yml").read_text(encoding="utf-8")
    )
    assert defaults["l9_runner_repository"] == "Quantum-L9/l9-deployment-platform"
    assert "public" not in defaults["l9_runner_labels"]
