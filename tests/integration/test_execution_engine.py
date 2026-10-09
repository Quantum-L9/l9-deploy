"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, integration]
tags: [L9_TEST, deployment-transaction, rollback]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

import functools
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest
import yaml

from l9_deploy import cli
from l9_deploy.canonical import file_sha256, sha256_digest
from l9_deploy.contracts.models import ReleaseState
from l9_deploy.errors import AuthorizationError, ContractError, ExecutionError
from l9_deploy.evidence.ledger import ReceiptLedger
from l9_deploy.execution.engine import execute_plan
from l9_deploy.execution.promotion import write_runtime_state
from l9_deploy.execution.releases import bind_release_runtime_env
from l9_deploy.planning.planner import build_plan, plan_digest_of
from l9_deploy.requests.idempotency import IdempotencyStore
from l9_deploy.requests.verifier import verify_request
from l9_deploy.subprocesses import CommandResult


@dataclass
class FakeExecutor:
    root: Path
    image_ref: str
    fail_health: bool = False

    def __post_init__(self) -> None:
        self.commands: list[tuple[list[str], dict[str, Any]]] = []
        self.health_calls = 0

    def run(self, command, **kwargs):  # type: ignore[no-untyped-def]
        command_list = list(command)
        self.commands.append((command_list, dict(kwargs)))
        if command_list[:4] == ["docker", "image", "inspect", self.image_ref]:
            return CommandResult(tuple(command_list), 0, self.image_ref + "\n", "")
        if command_list and command_list[0] == "test":
            return CommandResult(tuple(command_list), 0, "", "")
        if command_list == ["true"]:
            self.health_calls += 1
            if self.fail_health and self.health_calls == 1:
                raise RuntimeError("health failed")
            return CommandResult(tuple(command_list), 0, "", "")
        if command_list and command_list[0] == "find":
            return CommandResult(tuple(command_list), 0, "", "")
        return CommandResult(tuple(command_list), 0, "ok\n", "")

    def write_text(self, path: Path, text: str, mode: int = 0o600) -> None:
        target = self.root / path.relative_to("/")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        target.chmod(mode)


def verified(deployment_context, schema_registry):  # type: ignore[no-untyped-def]
    return verify_request(
        deployment_context["request"],
        deployment_context["fleet"],
        schema_registry,
        deployment_context["root"],
        evidence_root=deployment_context["evidence_root"],
        bundle_validator=deployment_context["bundle_validator"],
    )


def approval(
    root: Path,
    *,
    request_id: str,
    requester: str,
    environment: str,
    plan_digest: str,
    run_id: int = 555,
) -> tuple[Path, Path]:
    approved_at = "2026-07-21T12:00:02+00:00"
    history = [
        {
            "state": "approved",
            "submitted_at": approved_at,
            "user": {"login": "independent-reviewer"},
            "environments": [{"name": environment}],
        }
    ]
    history_path = root / "approval-history.json"
    history_path.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")
    document: dict[str, object] = {
        "schema": "l9.approval-receipt/v1",
        "approval_id": "c6969d36-a4dd-4a01-89b1-64ec114cb9fd",
        "request_id": request_id,
        "environment": environment,
        "plan_digest": plan_digest,
        "requester": requester,
        "approved": True,
        "approved_by": "independent-reviewer",
        "approved_at": approved_at,
        "authorization_method": "github_protected_environment_review",
        "workflow": {
            "repository": "Quantum-L9/l9-deploy",
            "run_id": run_id,
            "run_attempt": 1,
            "job_id": 777,
            "workflow_ref": (
                "Quantum-L9/l9-deploy/.github/workflows/deploy-dispatch.yml@refs/heads/main"
            ),
            "environment": environment,
            "approval_api_url": (
                f"https://api.github.com/repos/Quantum-L9/l9-deploy/actions/runs/{run_id}/approvals"
            ),
            "approval_record_digest": file_sha256(history_path),
        },
    }
    document["receipt_digest"] = sha256_digest(document)
    receipt_path = root / "approval-receipt.json"
    receipt_path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt_path, history_path


def execute(
    *,
    plan,
    deployment_context,
    executor,
    tmp_path: Path,
    store: IdempotencyStore | None = None,
    sleep=None,
):  # type: ignore[no-untyped-def]
    approval_path, history_path = approval(
        tmp_path,
        request_id=plan.request_id,
        requester=plan.requested_by,
        environment=plan.environment,
        plan_digest=plan.plan_digest,
    )
    runtime_env = tmp_path / "runtime.env"
    runtime_env.write_text("SAFE_VALUE=1\n", encoding="utf-8")
    return execute_plan(
        plan=plan,
        profile=deployment_context["profile"],
        executor=executor,
        expected_plan_digest=plan.plan_digest,
        approval_receipt=approval_path,
        approval_history=history_path,
        approval_run_id=555,
        latest_pointer=tmp_path / "receipts/latest/deployment.json",
        receipt_ledger_root=tmp_path / "receipts/ledger",
        lock_root=tmp_path / "locks",
        idempotency_store=store or IdempotencyStore(tmp_path / "idempotency.json"),
        request_digest="sha256:" + "e" * 64,
        runtime_env_file=runtime_env,
        sleep=sleep if sleep is not None else (lambda _seconds: None),
    )


def test_execute_plan_writes_immutable_receipt_and_runtime_state(
    deployment_context, schema_registry, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    plan = build_plan(
        verified(deployment_context, schema_registry), created_at="2026-07-21T12:00:01Z"
    )
    executor = FakeExecutor(tmp_path / "remote", plan.image_ref)
    receipt = execute(
        plan=plan,
        deployment_context=deployment_context,
        executor=executor,
        tmp_path=tmp_path,
    )

    assert receipt["status"] == "PASS"
    schema_registry.validate(receipt, "deployment-receipt")
    assert ReceiptLedger(tmp_path / "receipts/ledger").verify()["entries"] == 1
    state_path = tmp_path / "remote/srv/l9/projects/seo-bot/staging/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["current"]["image_ref"] == plan.image_ref
    compose_commands = [item for item in executor.commands if item[0][:2] == ["docker", "compose"]]
    assert compose_commands[0][1]["env"]["L9_IMAGE_REF"] == plan.image_ref
    candidate_env = state["current"]["runtime_env_path"]
    assert candidate_env in compose_commands[0][0]
    assert compose_commands[0][1]["env"]["L9_RUNTIME_ENV_FILE"] == candidate_env
    migration_commands = [
        command for command, _ in executor.commands if command[:2] == ["docker", "run"]
    ]
    assert candidate_env in migration_commands[0]
    assert "/srv/l9/projects/seo-bot/staging/runtime.env" not in str(executor.commands)


BACKUP_VERIFY_COMMAND = [
    "/usr/local/sbin/l9-backup-verify",
    "/srv/l9/backups/seo-bot/production/latest.sql.gz",
]


def test_execute_plan_runs_declared_backup_verify_command(
    deployment_context, schema_registry, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    plan = build_plan(
        verified(deployment_context, schema_registry), created_at="2026-07-21T12:00:01Z"
    )
    executor = FakeExecutor(tmp_path / "remote", plan.image_ref)
    receipt = execute(
        plan=plan,
        deployment_context=deployment_context,
        executor=executor,
        tmp_path=tmp_path,
    )

    assert receipt["status"] == "PASS"
    executed = [item[0] for item in executor.commands]
    assert BACKUP_VERIFY_COMMAND in executed
    backup_step = next(step for step in receipt["steps"] if step["kind"] == "backup")
    assert backup_step["details"]["verification"]["status"] == "PASS"


def test_backup_verification_failure_aborts_before_mutation(
    deployment_context, schema_registry, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    @dataclass
    class VerifyFailingExecutor(FakeExecutor):
        def run(self, command, **kwargs):  # type: ignore[no-untyped-def]
            command_list = list(command)
            if command_list == BACKUP_VERIFY_COMMAND:
                self.commands.append((command_list, dict(kwargs)))
                return CommandResult(tuple(command_list), 1, "", "verification failed")
            return super().run(command, **kwargs)

    plan = build_plan(
        verified(deployment_context, schema_registry), created_at="2026-07-21T12:00:01Z"
    )
    executor = VerifyFailingExecutor(tmp_path / "remote", plan.image_ref)
    with pytest.raises(ExecutionError, match="backup verification failed"):
        execute(
            plan=plan,
            deployment_context=deployment_context,
            executor=executor,
            tmp_path=tmp_path,
        )

    executed = [item[0] for item in executor.commands]
    # Deploy aborts before any container mutation (pull/render/compose up).
    assert not any(item[:2] == ["docker", "compose"] for item in executed)
    # A FAIL receipt is still recorded in the ledger.
    assert ReceiptLedger(tmp_path / "receipts/ledger").verify()["entries"] == 1


def test_post_deploy_stabilization_window_is_honored_before_health(
    deployment_context, schema_registry, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    plan = build_plan(
        verified(deployment_context, schema_registry), created_at="2026-07-21T12:00:01Z"
    )
    executor = FakeExecutor(tmp_path / "remote", plan.image_ref)
    waited: list[float] = []
    receipt = execute(
        plan=plan,
        deployment_context=deployment_context,
        executor=executor,
        tmp_path=tmp_path,
        sleep=waited.append,
    )

    expected = deployment_context["profile"]["release"]["stabilization_seconds"]
    assert expected > 0
    # The configured stabilization window is now consumed exactly once, before health.
    assert waited == [expected]
    health_steps = [step for step in receipt["steps"] if step["kind"] == "health"]
    assert health_steps
    assert health_steps[0]["details"]["stabilization_seconds"] == expected


def test_idempotent_replay_does_not_execute_again(
    deployment_context, schema_registry, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    plan = build_plan(
        verified(deployment_context, schema_registry), created_at="2026-07-21T12:00:01Z"
    )
    store = IdempotencyStore(tmp_path / "idempotency.json")
    first = execute(
        plan=plan,
        deployment_context=deployment_context,
        executor=FakeExecutor(tmp_path / "remote", plan.image_ref),
        tmp_path=tmp_path,
        store=store,
    )
    replay_executor = FakeExecutor(tmp_path / "remote-2", plan.image_ref)
    replay = execute(
        plan=plan,
        deployment_context=deployment_context,
        executor=replay_executor,
        tmp_path=tmp_path,
        store=store,
    )
    assert replay == {
        "status": "PASS",
        "idempotent_replay": True,
        "receipt_digest": first["receipt_digest"],
    }
    assert replay_executor.commands == []


def test_health_failure_rolls_back_container_and_state(
    deployment_context, schema_registry, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    previous = bind_release_runtime_env(
        ReleaseState(
            request_id="previous-request",
            source_commit_sha="c" * 40,
            image_ref="ghcr.io/quantum-l9/seo-bot@sha256:" + "d" * 64,
            plan_digest="sha256:" + "f" * 64,
        ),
        "seo-bot",
        "staging",
    )
    plan = build_plan(
        verified(deployment_context, schema_registry),
        previous_release=previous,
        created_at="2026-07-21T12:00:01Z",
    )
    executor = FakeExecutor(tmp_path / "remote", plan.image_ref, fail_health=True)
    write_runtime_state(executor, "seo-bot", "staging", previous, None)
    state_path = tmp_path / "remote/srv/l9/projects/seo-bot/staging/state.json"
    state_before = state_path.read_bytes()
    with pytest.raises(RuntimeError, match="health failed"):
        execute(
            plan=plan,
            deployment_context=deployment_context,
            executor=executor,
            tmp_path=tmp_path,
        )
    assert state_path.read_bytes() == state_before
    rollback_commands = [
        command for command, _ in executor.commands if command[:2] == ["docker", "compose"]
    ]
    assert str(previous.runtime_env_path) in rollback_commands[-1]
    candidate_directory = str(
        Path(
            "/srv/l9/projects/seo-bot/staging/releases/" + plan.plan_digest.removeprefix("sha256:")
        )
    )
    assert (["rm", "-rf", "--", candidate_directory], {}) in executor.commands
    assert ReceiptLedger(tmp_path / "receipts/ledger").verify()["entries"] == 1


def test_receipt_publication_failure_restores_state(
    deployment_context, schema_registry, tmp_path: Path, monkeypatch
) -> None:  # type: ignore[no-untyped-def]
    previous = bind_release_runtime_env(
        ReleaseState(
            request_id="previous-request",
            source_commit_sha="c" * 40,
            image_ref="ghcr.io/quantum-l9/seo-bot@sha256:" + "d" * 64,
            plan_digest="sha256:" + "f" * 64,
        ),
        "seo-bot",
        "staging",
    )
    plan = build_plan(
        verified(deployment_context, schema_registry),
        previous_release=previous,
        created_at="2026-07-21T12:00:01Z",
    )
    calls = {"count": 0}
    from l9_deploy.execution import engine as engine_module

    real_publish = engine_module.publish_receipt

    def fail_first(*args, **kwargs):  # type: ignore[no-untyped-def]
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("publication failed")
        return real_publish(*args, **kwargs)

    monkeypatch.setattr(engine_module, "publish_receipt", fail_first)
    executor = FakeExecutor(tmp_path / "remote", plan.image_ref)
    with pytest.raises(RuntimeError, match="publication failed"):
        execute(
            plan=plan,
            deployment_context=deployment_context,
            executor=executor,
            tmp_path=tmp_path,
        )
    state = json.loads(
        (tmp_path / "remote/srv/l9/projects/seo-bot/staging/state.json").read_text(encoding="utf-8")
    )
    assert state["current"]["image_ref"] == previous.image_ref


def test_candidate_release_identity_cannot_collide_with_active_release(
    deployment_context, schema_registry, tmp_path: Path, monkeypatch
) -> None:  # type: ignore[no-untyped-def]
    verified_request = verified(deployment_context, schema_registry)
    initial_plan = build_plan(verified_request, created_at="2026-07-21T12:00:01Z")
    previous = bind_release_runtime_env(
        ReleaseState(
            request_id="previous-request",
            source_commit_sha="c" * 40,
            image_ref="ghcr.io/quantum-l9/seo-bot@sha256:" + "d" * 64,
            plan_digest=initial_plan.plan_digest,
        ),
        "seo-bot",
        "staging",
    )
    plan = initial_plan.model_copy(update={"previous_release": previous})
    executor = FakeExecutor(tmp_path / "remote", plan.image_ref)

    # A plan that names itself as its own previous release can only be forged:
    # the content-bound digest check rejects it first. Stub that check so the
    # collision guard behind it stays exercised as defense in depth.
    from l9_deploy.execution import engine as engine_module

    monkeypatch.setattr(engine_module, "verify_plan_digest", lambda _plan: None)
    with pytest.raises(ExecutionError, match="collides with the active release"):
        execute(
            plan=plan,
            deployment_context=deployment_context,
            executor=executor,
            tmp_path=tmp_path,
        )

    assert executor.commands == []


def test_legacy_previous_release_without_configuration_identity_fails_before_mutation(
    deployment_context, schema_registry, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    previous = ReleaseState(
        request_id="previous-request",
        source_commit_sha="c" * 40,
        image_ref="ghcr.io/quantum-l9/seo-bot@sha256:" + "d" * 64,
        plan_digest="sha256:" + "f" * 64,
    )
    plan = build_plan(
        verified(deployment_context, schema_registry),
        previous_release=previous,
        created_at="2026-07-21T12:00:01Z",
    )
    executor = FakeExecutor(tmp_path / "remote", plan.image_ref)

    with pytest.raises(ExecutionError, match="lacks runtime configuration identity"):
        execute(
            plan=plan,
            deployment_context=deployment_context,
            executor=executor,
            tmp_path=tmp_path,
        )

    assert executor.commands == []
    assert not (tmp_path / "remote/srv/l9/projects/seo-bot/staging/state.json").exists()


def test_idempotency_finalization_failure_is_recoverable_without_rollback(
    deployment_context, schema_registry, tmp_path: Path, monkeypatch
) -> None:  # type: ignore[no-untyped-def]
    plan = build_plan(
        verified(deployment_context, schema_registry), created_at="2026-07-21T12:00:01Z"
    )
    store = IdempotencyStore(tmp_path / "idempotency.json")
    real_complete = store.complete
    calls = {"count": 0}

    def fail_once(key: str, receipt_digest: str) -> None:
        calls["count"] += 1
        if calls["count"] == 1:
            raise RuntimeError("idempotency finalization failed")
        real_complete(key, receipt_digest)

    monkeypatch.setattr(store, "complete", fail_once)
    executor = FakeExecutor(tmp_path / "remote", plan.image_ref)
    receipt = execute(
        plan=plan,
        deployment_context=deployment_context,
        executor=executor,
        tmp_path=tmp_path,
        store=store,
    )
    assert receipt["status"] == "PASS"
    prepared = store.get(plan.request_id)
    assert prepared is not None
    assert prepared.status == "PREPARED"
    assert prepared.receipt_digest == receipt["receipt_digest"]
    state_path = tmp_path / "remote/srv/l9/projects/seo-bot/staging/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["current"]["image_ref"] == plan.image_ref
    assert ReceiptLedger(tmp_path / "receipts/ledger").verify()["entries"] == 1

    replay_executor = FakeExecutor(tmp_path / "replay-remote", plan.image_ref)
    recovered = execute(
        plan=plan,
        deployment_context=deployment_context,
        executor=replay_executor,
        tmp_path=tmp_path,
        store=store,
    )
    assert recovered["receipt_digest"] == receipt["receipt_digest"]
    assert replay_executor.commands == []
    committed = store.get(plan.request_id)
    assert committed is not None
    assert committed.status == "COMPLETE"


def _prepare_deployment(
    deployment_context: dict[str, Any],
    repo_root: Path,
    tmp_path: Path,
    profile_root: Path,
) -> tuple[Path, Path, dict[str, str], subprocess.CompletedProcess[str]]:
    """Run the real validate-stage preflight exactly as deploy-dispatch does."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    request_path = tmp_path / "request.json"
    request_path.write_text(
        json.dumps(deployment_context["request"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    fleet_path = tmp_path / "fleet.yaml"
    fleet_path.write_text(
        yaml.safe_dump(deployment_context["fleet"], sort_keys=False), encoding="utf-8"
    )
    plan_path = tmp_path / "plan.json"
    github_output = tmp_path / "github-output.txt"
    # The canonical bundle validator is the external l9-ci CLI; the preflight
    # fails closed without it, so the handoff test provides a stand-in on PATH.
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir(exist_ok=True)
    stub = fake_bin / "l9-ci"
    stub.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    stub.chmod(0o755)
    env = {
        **os.environ,
        "PATH": f"{fake_bin}{os.pathsep}{os.environ.get('PATH', '')}",
        "GITHUB_OUTPUT": str(github_output),
    }
    result = subprocess.run(
        [
            sys.executable,
            "scripts/prepare-deployment.py",
            "--request",
            str(request_path),
            "--evidence-root",
            str(deployment_context["evidence_root"]),
            "--profile-root",
            str(profile_root),
            "--fleet",
            str(fleet_path),
            "--plan",
            str(plan_path),
            "--root",
            str(repo_root),
        ],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    outputs: dict[str, str] = {}
    if github_output.exists():
        for line in github_output.read_text(encoding="utf-8").splitlines():
            key, _, value = line.partition("=")
            outputs[key] = value
    return plan_path, fleet_path, outputs, result


def _deploy_arguments(
    *,
    repo_root: Path,
    tmp_path: Path,
    plan_path: Path,
    fleet_path: Path,
    profile_root: Path,
    plan: dict[str, Any],
    run_name: str,
    expected_plan_digest: str | None = None,
) -> list[str]:
    (tmp_path / run_name).mkdir(parents=True, exist_ok=True)
    approval_path, history_path = approval(
        tmp_path / run_name,
        request_id=plan["request_id"],
        requester=plan["requested_by"],
        environment=plan["environment"],
        plan_digest=plan["plan_digest"],
    )
    runtime_env = tmp_path / run_name / "runtime.env"
    runtime_env.write_text("SAFE_VALUE=1\n", encoding="utf-8")
    return [
        "deploy",
        "--root",
        str(repo_root),
        "--plan",
        str(plan_path),
        "--profile-root",
        str(profile_root),
        "--fleet",
        str(fleet_path),
        "--environment",
        plan["environment"],
        "--expected-plan-digest",
        expected_plan_digest or plan["plan_digest"],
        "--approval-receipt",
        str(approval_path),
        "--approval-history",
        str(history_path),
        "--approval-run-id",
        "555",
        "--runtime-env-file",
        str(runtime_env),
        "--idempotency-store",
        str(tmp_path / run_name / "idempotency.json"),
        "--lock-root",
        str(tmp_path / run_name / "locks"),
        "--receipt-ledger-root",
        str(tmp_path / run_name / "ledger"),
        "--output",
        str(tmp_path / run_name / "latest/deployment.json"),
        "--local-executor-root",
        str(tmp_path / run_name / "remote"),
        "--json",
    ]


def test_validate_to_execute_handoff_consumes_only_sealed_profile_bytes(
    deployment_context, schema_registry, repo_root: Path, tmp_path: Path, monkeypatch, capsys
) -> None:  # type: ignore[no-untyped-def]
    # Stage 1 (validate job): the consumer profile materialized from the exact
    # source commit lives under its own root, never under the l9-deploy checkout.
    source_root = deployment_context["root"]
    registered_path = deployment_context["fleet"]["projects"][0]["profile_path"]
    source_profile = source_root / registered_path
    plan_path, fleet_path, outputs, result = _prepare_deployment(
        deployment_context, repo_root, tmp_path, source_root
    )
    assert result.returncode == 0, result.stderr
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    schema_registry.validate(plan, "deployment-plan")
    assert outputs["plan_digest"] == plan["plan_digest"]
    assert outputs["project_id"] == plan["project_id"] == "seo-bot"
    assert plan["profile_digest"] == deployment_context["request"]["profile"]["digest"]
    assert plan["profile_digest"] == file_sha256(source_profile)
    # The plan is deterministic and its digest is content-bound: rebuilding from the
    # same verified request reproduces it, and plan.json reproduces its own digest.
    expected_plan = build_plan(
        verified(deployment_context, schema_registry), created_at=plan["created_at"]
    ).model_dump(mode="json", by_alias=True)
    assert plan == expected_plan
    assert plan_digest_of(plan) == plan["plan_digest"]

    # Stage 2 (artifact boundary): the validate job uploads request, plan and
    # the profile root; the deploy job downloads them under artifacts/deployment.
    artifact_root = tmp_path / "artifacts" / "deployment"
    sealed_root = artifact_root / "artifacts" / "deployment-profile"
    shutil.copytree(
        source_root / Path(registered_path).parts[0], sealed_root / Path(registered_path).parts[0]
    )
    shutil.copy(plan_path, artifact_root / "plan.json")
    sealed_profile = sealed_root / registered_path
    assert file_sha256(sealed_profile) == plan["profile_digest"]

    # Stage 3: after validation the consumer source and any platform-local copy
    # change. The approved execution must not see those bytes.
    mutated = yaml.safe_load(source_profile.read_text(encoding="utf-8"))
    mutated["release"]["stabilization_seconds"] = 0
    source_profile.write_text(yaml.safe_dump(mutated, sort_keys=False), encoding="utf-8")
    assert file_sha256(source_profile) != plan["profile_digest"]

    executors: list[FakeExecutor] = []

    def fake_target_executor(args, fleet, project, environment, *, mutation=False):  # type: ignore[no-untyped-def]
        assert mutation is True
        executor = FakeExecutor(Path(args.local_executor_root), plan["image_ref"])
        executors.append(executor)
        return executor

    monkeypatch.setattr(cli, "_target_executor", fake_target_executor)
    waited: list[float] = []
    monkeypatch.setattr(cli, "execute_plan", functools.partial(execute_plan, sleep=waited.append))

    def run(run_name: str, profile_root: Path, **overrides: Any) -> int:
        arguments = _deploy_arguments(
            repo_root=repo_root,
            tmp_path=tmp_path,
            plan_path=artifact_root / "plan.json",
            fleet_path=fleet_path,
            profile_root=profile_root,
            plan=plan,
            run_name=run_name,
            **overrides,
        )
        capsys.readouterr()
        return cli.main(arguments)

    # Stage 4 (deploy job): the sealed bytes are the ones the plan was built from.
    assert run("sealed", sealed_root) == 0
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["status"] == "PASS"
    assert receipt["plan_digest"] == plan["plan_digest"]
    assert len(executors) == 1
    compose = [
        command for command, _ in executors[0].commands if command[:2] == ["docker", "compose"]
    ]
    assert compose, "sealed profile execution reached the container step"
    assert ReceiptLedger(tmp_path / "sealed" / "ledger").verify()["entries"] == 1
    # The sealed profile's stabilization window (not the mutated source's 0) ran.
    sealed_stabilization = deployment_context["profile"]["release"]["stabilization_seconds"]
    assert sealed_stabilization > 0
    assert waited == [sealed_stabilization]
    health = next(step for step in receipt["steps"] if step["kind"] == "health")
    assert health["details"]["stabilization_seconds"] == sealed_stabilization

    # The mutated source tree (the platform-local or consumer file as it is now)
    # is refused: the plan is not permission to load whatever is on disk.
    assert run("mutated-source", source_root) == AuthorizationError.exit_code
    assert "does not match the approved plan profile digest" in capsys.readouterr().err
    assert len(executors) == 1

    # Stage 5: tamper with the sealed file after approval. Execution refuses before
    # the executor exists, so no backup, pull, render, migration, compose or
    # promotion command runs and no receipt is recorded for the attempt.
    sealed_profile.write_bytes(sealed_profile.read_bytes() + b"\n# tampered after approval\n")
    assert run("tampered", sealed_root) == AuthorizationError.exit_code
    assert "does not match the approved plan profile digest" in capsys.readouterr().err
    assert len(executors) == 1
    assert not (tmp_path / "tampered" / "ledger").exists()
    assert not (tmp_path / "tampered" / "idempotency.json").exists()

    # A missing sealed document is an absence, not a cue to look elsewhere.
    sealed_profile.unlink()
    assert run("absent", sealed_root) == ContractError.exit_code
    assert "missing from the profile root" in capsys.readouterr().err
    assert len(executors) == 1

    # Approval stays bound to the deterministic plan digest.
    shutil.copy(plan_path, artifact_root / "plan.json")
    shutil.copytree(
        source_root / Path(registered_path).parts[0],
        sealed_root / Path(registered_path).parts[0],
        dirs_exist_ok=True,
    )
    assert run("wrong-digest", sealed_root, expected_plan_digest="sha256:" + "0" * 64) == (
        AuthorizationError.exit_code
    )
    assert "expected plan digest does not match plan" in capsys.readouterr().err
    assert len(executors) == 1

    # Stage 6: edit the sealed artifact consistently. The sealed profile now holds
    # the mutated bytes and plan.json's profile_digest is rewritten to match them,
    # while the approved plan_digest string is left untouched. The digest string is
    # not trusted on its own: the plan content no longer hashes to it.
    assert file_sha256(sealed_profile) != plan["profile_digest"]
    forged = dict(plan)
    forged["profile_digest"] = file_sha256(sealed_profile)
    (artifact_root / "plan.json").write_text(
        json.dumps(forged, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    assert run("forged-plan", sealed_root) == AuthorizationError.exit_code
    assert "plan digest does not match plan content" in capsys.readouterr().err
    assert len(executors) == 1
    assert not (tmp_path / "forged-plan" / "ledger").exists()


def test_prepare_deployment_fails_closed_on_source_substitution(
    deployment_context, repo_root: Path, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    # A request whose profile path is not the fleet registration never reaches
    # the planner, and an empty profile root is never backfilled from the checkout.
    import copy

    substituted = copy.deepcopy(deployment_context)
    substituted["request"] = copy.deepcopy(deployment_context["request"])
    substituted["request"]["profile"]["path"] = "integrations/consumers/seo-bot.deployment.yaml"
    plan_path, _, outputs, result = _prepare_deployment(
        substituted, repo_root, tmp_path / "substituted", deployment_context["root"]
    )
    assert result.returncode != 0
    assert "AuthorizationError: deployment profile path does not match fleet registration" in (
        result.stderr
    )
    assert not plan_path.exists()
    assert outputs == {}

    empty_root = tmp_path / "empty-profile-root"
    empty_root.mkdir()
    plan_path, _, outputs, result = _prepare_deployment(
        deployment_context, repo_root, tmp_path / "empty", empty_root
    )
    assert result.returncode != 0
    assert "ContractError: registered deployment profile is missing from the profile root" in (
        result.stderr
    )
    assert not plan_path.exists()
    assert outputs == {}
