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

import subprocess
import sys
from pathlib import Path

import yaml


def test_all_consumer_templates_render_and_parse(tmp_path: Path, repo_root: Path) -> None:
    for profile in ["container-service", "stateful-container", "worker-service", "scheduled-job"]:
        destination = tmp_path / profile
        subprocess.run(
            [
                sys.executable,
                str(repo_root / "scripts/package-adoption-kit.py"),
                "--profile",
                profile,
                "--project-id",
                "sample-app",
                "--repository",
                "Quantum-L9/Sample-App",
                "--image",
                "ghcr.io/quantum-l9/sample-app",
                "--destination",
                str(destination),
            ],
            check=True,
            cwd=repo_root,
        )
        parsed = yaml.safe_load((destination / ".l9/deployment.yaml").read_text(encoding="utf-8"))
        assert parsed["project"]["id"] == "sample-app"
        workflow = (destination / ".github/workflows/release.yml").read_text(encoding="utf-8")
        assert "{{PROJECT" not in workflow
        assert "{{REPOSITORY" not in workflow
        assert "{{IMAGE" not in workflow
        assert "verify-command: npm run verify:all" in workflow
