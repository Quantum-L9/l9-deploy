"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, compliance]
tags: [L9_TEST, alignment, trust-boundary]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import yaml


def test_all_eligible_files_carry_l9_meta(repo_root: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(repo_root / "scripts/verify-l9-meta.py")],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_no_self_issued_approval_path_remains(repo_root: Path) -> None:
    paths = [repo_root / ".github", repo_root / "integrations", repo_root / "scripts"]
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for base in paths
        for path in base.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    assert "create-approval-receipt.py" not in combined
    assert '--approved-by "${{ github.actor }}"' not in combined
    assert "collect-github-approval.py" in combined


def test_external_gate_and_status_free_artifact_binding(repo_root: Path) -> None:
    workflow = (repo_root / "integrations/l9-ci-core/container-release.yml").read_text(
        encoding="utf-8"
    )
    assert "ci-gate-binding.json" in workflow
    assert "l9.release-artifact-binding/v1" in workflow
    assert "l9.ci-release-receipt/v1" not in workflow
    binding_fragment = workflow.split("l9.release-artifact-binding/v1", maxsplit=1)[1]
    assert 'status:"PASS"' not in binding_fragment


def test_transport_classification_is_explicit(repo_root: Path) -> None:
    document = yaml.safe_load(
        (repo_root / ".l9/transport-classification.yaml").read_text(encoding="utf-8")
    )
    assert document["classification"] == "infrastructure_control_plane"
    assert document["constellation_node"] is False
    assert document["transport_packet"]["required_when_addressing_constellation_nodes"] is True
    assert document["gate"]["required_for_follow_up_constellation_work"] is True


def test_production_python_contains_no_print_calls(repo_root: Path) -> None:
    violations: list[str] = []
    for base in (repo_root / "src", repo_root / "scripts"):
        for path in base.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == "print":
                        violations.append(f"{path.relative_to(repo_root)}:{node.lineno}")
    assert violations == []
