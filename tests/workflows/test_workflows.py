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


def _permissions(value: object) -> dict[str, str]:
    assert isinstance(value, dict)
    return {str(key): str(item) for key, item in value.items()}


def _job_consumes_infisical_oidc(job: dict[object, object]) -> bool:
    steps = job.get("steps", [])
    assert isinstance(steps, list)
    return any(
        isinstance(step, dict) and "scripts/infisical-oidc-env.sh" in str(step.get("run", ""))
        for step in steps
    )


def test_oidc_permission_is_job_scoped_to_infisical_consumers() -> None:
    oidc_jobs: set[tuple[str, str]] = set()
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        workflow = load_workflow(path)
        workflow_permissions = _permissions(workflow.get("permissions", {}))
        assert workflow_permissions.get("id-token") != "write", path
        for job_name, raw_job in workflow.get("jobs", {}).items():
            assert isinstance(raw_job, dict)
            job_permissions = _permissions(raw_job.get("permissions", {}))
            has_oidc = job_permissions.get("id-token") == "write"
            consumes_oidc = _job_consumes_infisical_oidc(raw_job)
            assert has_oidc == consumes_oidc, f"OIDC mismatch in {path}:{job_name}"
            if has_oidc:
                oidc_jobs.add((path.name, str(job_name)))
    assert oidc_jobs == {
        ("deploy-dispatch.yml", "deploy"),
        ("drift-detect.yml", "plan"),
        ("provision-apply.yml", "apply"),
        ("provision-plan.yml", "plan"),
    }


def test_deployment_approval_jobs_cannot_request_oidc() -> None:
    for path in sorted((ROOT / ".github/workflows").glob("*.yml")):
        workflow = load_workflow(path)
        authorize = workflow.get("jobs", {}).get("authorize")
        if isinstance(authorize, dict):
            permissions = _permissions(authorize.get("permissions", {}))
            assert permissions.get("id-token") != "write", path


def test_deploy_dispatch_preserves_minimum_approved_wiring() -> None:
    workflow = load_workflow(ROOT / ".github/workflows/deploy-dispatch.yml")
    jobs = workflow["jobs"]
    assert isinstance(jobs, dict)
    deploy = jobs["deploy"]
    assert isinstance(deploy, dict)
    assert set(deploy["needs"]) == {"validate", "authorize"}
    permissions = _permissions(deploy["permissions"])
    assert permissions == {
        "contents": "read",
        "actions": "read",
        "packages": "read",
        "attestations": "read",
        "id-token": "write",
    }
    steps = deploy["steps"]
    assert isinstance(steps, list)
    runs = "\n".join(str(step.get("run", "")) for step in steps if isinstance(step, dict))
    assert "scripts/infisical-oidc-env.sh" in runs
    assert "verify-attestation.sh" in runs
    assert "uv run l9-deploy deploy" in runs
    assert "--expected-plan-digest" in runs
    assert "--approval-receipt" in runs
    assert "--approval-history" in runs


def test_workflow_inventory_covers_every_workflow() -> None:
    inventory = (ROOT / "docs/operations/workflow-inventory.md").read_text(encoding="utf-8")
    workflow_names = {path.name for path in (ROOT / ".github/workflows").glob("*.yml")}
    documented = set(re.findall(r"`([^`]+\.yml)`", inventory))
    assert documented == workflow_names
    assert "No workflow is classified obsolete" in inventory
    assert "No new scanner, linter, or CI framework" in inventory
