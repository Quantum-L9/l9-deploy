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
    assert "${{ runner.temp }}/l9-deploy-release" in text
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


def test_deploy_dispatch_seals_the_consumer_profile_from_validate_to_deploy() -> None:
    workflow = load_workflow(ROOT / ".github/workflows/deploy-dispatch.yml")
    jobs = workflow["jobs"]
    validate_steps = jobs["validate"]["steps"]
    assert isinstance(validate_steps, list)
    named = [str(step.get("name") or step.get("id") or step.get("uses")) for step in validate_steps]
    evidence_index = named.index("Download immutable source-run evidence")
    resolve_index = named.index("Resolve immutable consumer deployment profile")
    metadata_index = named.index("metadata")
    assert evidence_index < resolve_index < metadata_index

    resolve = validate_steps[resolve_index]
    assert resolve["env"] == {"GH_TOKEN": "${{ secrets.DEPLOYMENT_EVIDENCE_READ_TOKEN }}"}
    resolve_run = str(resolve["run"])
    # Exact source coordinates from the request itself, never a floating ref.
    assert "jq -er '.source.repository' request.json" in resolve_run
    assert "jq -er '.source.commit_sha' request.json" in resolve_run
    assert "jq -er '.profile.path' request.json" in resolve_run
    assert "grep -Eq '^[a-f0-9]{40}$'" in resolve_run
    assert '"repos/$source_repo/contents/$profile_path?ref=$commit_sha"' in resolve_run
    # Only a regular file at the requested path, with its Git object id re-derived
    # from the decoded bytes, is sealed.
    assert "test \"$(jq -r '.type' profile-object.json)\" = file" in resolve_run
    assert 'test "$(jq -r \'.path\' profile-object.json)" = "$profile_path"' in resolve_run
    assert "git hash-object" in resolve_run
    assert 'sealed="artifacts/deployment-profile/$profile_path"' in resolve_run

    metadata = validate_steps[metadata_index]
    assert "--profile-root artifacts/deployment-profile" in str(metadata["run"])

    upload = next(
        step
        for step in validate_steps
        if str(step.get("uses", "")).startswith("actions/upload-artifact@")
    )
    assert upload["with"]["name"] == "validated-deployment-${{ github.run_id }}"
    uploaded = str(upload["with"]["path"]).split()
    assert "plan.json" in uploaded
    assert "artifacts/deployment-profile" in uploaded
    assert upload["with"]["include-hidden-files"] is True

    deploy_steps = jobs["deploy"]["steps"]
    assert isinstance(deploy_steps, list)
    deploy_runs = "\n".join(str(step.get("run", "")) for step in deploy_steps)
    assert "--profile-root artifacts/deployment/artifacts/deployment-profile" in deploy_runs
    # The private runner consumes sealed bytes only; it never resolves source.
    assert "gh api" not in deploy_runs
    assert "/contents/" not in deploy_runs
    assert "gh run download" not in deploy_runs
    downloads = [
        step
        for step in deploy_steps
        if str(step.get("uses", "")).startswith("actions/download-artifact@")
    ]
    for download in downloads:
        assert download["with"]["name"] in {
            "validated-deployment-${{ github.run_id }}",
            "deployment-approval-${{ github.run_id }}",
        }


def test_configure_hosts_binds_approval_to_generated_plan() -> None:
    path = ROOT / ".github/workflows/configure-hosts.yml"
    workflow = load_workflow(path)
    triggers = workflow.get("on", workflow.get(True))
    assert isinstance(triggers, dict)
    inputs = triggers["workflow_dispatch"]["inputs"]
    assert "server-id" in inputs
    assert "allow-environment-wide" in inputs
    assert "expected-plan-digest" not in inputs

    text = path.read_text(encoding="utf-8")
    assert "Build deterministic configuration plan" in text
    assert "Recompute and verify approved configuration plan" in text
    assert "plan-digest: ${{ needs.plan.outputs.plan-digest }}" in text

    configure = workflow["jobs"]["configure"]
    assert isinstance(configure, dict)
    steps = configure["steps"]
    assert isinstance(steps, list)
    named_steps = {
        step.get("name"): step
        for step in steps
        if isinstance(step, dict) and isinstance(step.get("name"), str)
    }
    plan_steps = workflow["jobs"]["plan"]["steps"]
    assert isinstance(plan_steps, list)
    plan = next(
        step
        for step in plan_steps
        if isinstance(step, dict) and step.get("name") == "Build deterministic configuration plan"
    )
    verify = named_steps["Recompute and verify approved configuration plan"]
    assert "--output" not in str(plan["run"])
    assert "--output" not in str(verify["run"])
    assert "--fleet" not in str(plan["run"])
    assert "--fleet" not in str(verify["run"])
    assert "--inventory" not in str(plan["run"])
    assert "--inventory" not in str(verify["run"])
    assert '--playbook "$TARGET_PLAYBOOK"' in str(plan["run"])
    assert '--playbook "$TARGET_PLAYBOOK"' in str(verify["run"])
    assert "> configuration-plan.json" in str(plan["run"])
    assert "> configuration-plan.current.json" in str(verify["run"])
    assert "umask 027" in str(plan["run"])
    assert "umask 027" in str(verify["run"])

    check = named_steps["Check configuration"]
    apply = named_steps["Apply configuration"]
    for step in (check, apply):
        run = str(step["run"])
        assert "${{" not in run
        env = step.get("env")
        assert isinstance(env, dict)
        assert env["TARGET_PLAYBOOK"] == "${{ inputs.playbook }}"
        assert env["TARGET_LIMIT"] == "${{ steps.verify-plan.outputs.limit }}"
        assert '--playbook "ansible/playbooks/${TARGET_PLAYBOOK}.yml"' in run
        assert '--limit "$TARGET_LIMIT"' in run

    apply_env = apply["env"]
    assert isinstance(apply_env, dict)
    assert apply_env["APPROVED_PLAN_DIGEST"] == "${{ needs.plan.outputs.plan-digest }}"
    assert apply_env["CONFIG_REQUESTER"] == "${{ github.actor }}"
    assert '--expected-plan-digest "$APPROVED_PLAN_DIGEST"' in str(apply["run"])
    assert '--requester "$CONFIG_REQUESTER"' in str(apply["run"])


def test_workflow_inventory_covers_every_workflow() -> None:
    inventory = (ROOT / "docs/operations/workflow-inventory.md").read_text(encoding="utf-8")
    workflow_names = {path.name for path in (ROOT / ".github/workflows").glob("*.yml")}
    documented = set(re.findall(r"`([^`]+\.yml)`", inventory))
    assert documented == workflow_names
    assert "No workflow is classified obsolete" in inventory
    assert "No new scanner, linter, or CI framework" in inventory


def test_mutating_workflows_require_private_control_repository() -> None:
    mutating = {
        "configure-hosts.yml",
        "deploy-dispatch.yml",
        "provision-apply.yml",
        "rollback.yml",
        "runner-maintenance.yml",
    }
    for name in mutating:
        text = (ROOT / ".github/workflows" / name).read_text(encoding="utf-8")
        assert "./.github/actions/require-private-repository" in text
