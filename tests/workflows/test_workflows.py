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

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SHA_ACTION = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[a-f0-9]{40}$")
VERSIONED_L9 = re.compile(r"^Quantum-L9/[A-Za-z0-9_.-]+/.+@v[1-9][0-9]*$")


def load_workflow(path: Path) -> dict:  # type: ignore[type-arg]
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_all_workflows_are_valid_yaml() -> None:
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        load_workflow(path)


def test_external_actions_are_pinned_or_governed() -> None:
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        workflow = load_workflow(path)
        for job in workflow.get("jobs", {}).values():
            if not isinstance(job, dict):
                continue
            for step in job.get("steps", []) or []:
                if not isinstance(step, dict) or "uses" not in step:
                    continue
                action = step["uses"]
                assert (
                    action.startswith("./")
                    or SHA_ACTION.fullmatch(action)
                    or VERSIONED_L9.fullmatch(action)
                ), f"untrusted action reference in {path}: {action}"


def test_pull_request_jobs_never_use_self_hosted_runner() -> None:
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        workflow = load_workflow(path)
        triggers = workflow.get("on", workflow.get(True))
        if not isinstance(triggers, dict) or "pull_request" not in triggers:
            continue
        for job in workflow.get("jobs", {}).values():
            if isinstance(job, dict):
                assert "self-hosted" not in str(job.get("runs-on"))

def test_validation_workflow_enforces_coverage_floor() -> None:
    text = (ROOT / ".github/workflows/validate.yml").read_text(encoding="utf-8")
    assert "--cov=l9_deploy" in text
    assert "--cov-report=xml" in text
    assert "--cov-fail-under=75" in text
    assert "--cov-branch" in text


def test_release_workflow_uses_detached_outputs_and_receipt_binding() -> None:
    text = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "${{ runner.temp }}/l9-deployment-platform-release" in text
    assert text.count("--receipt") >= 2
    assert "--out-dir" in text
    assert "PYTHONDONTWRITEBYTECODE" in text
    assert '"dist/' not in text
    assert "'dist/" not in text

