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

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest

from l9_deploy.canonical import file_sha256, sha256_digest
from l9_deploy.contracts.models import ReleaseState
from l9_deploy.evidence.ledger import ReceiptLedger
from l9_deploy.execution.engine import execute_plan
from l9_deploy.planning.planner import build_plan
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

    def run(self, command, **kwargs):  # type: ignore[no-untyped-def]
        command_list = list(command)
        self.commands.append((command_list, dict(kwargs)))
        if command_list[:4] == ["docker", "image", "inspect", self.image_ref]:
            return CommandResult(tuple(command_list), 0, self.image_ref + "\n", "")
        if command_list and command_list[0] == "test":
            return CommandResult(tuple(command_list), 0, "", "")
        if command_list == ["true"]:
            if self.fail_health:
                raise RuntimeError("health failed")
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
            "repository": "Quantum-L9/l9-deployment-platform",
            "run_id": run_id,
            "run_attempt": 1,
            "job_id": 777,
            "workflow_ref": (
                "Quantum-L9/l9-deployment-platform/.github/workflows/"
                "deploy-dispatch.yml@refs/heads/main"
            ),
            "environment": environment,
            "approval_api_url": (
                "https://api.github.com/repos/Quantum-L9/l9-deployment-platform/"
                f"actions/runs/{run_id}/approvals"
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
    compose_commands = [
        item
        for item in executor.commands
        if item[0][:3] == ["docker", "compose", "-f"]
    ]
    assert compose_commands[0][1]["env"]["L9_IMAGE_REF"] == plan.image_ref


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
    executor = FakeExecutor(tmp_path / "remote", plan.image_ref, fail_health=True)
    with pytest.raises(RuntimeError, match="health failed"):
        execute(
            plan=plan,
            deployment_context=deployment_context,
            executor=executor,
            tmp_path=tmp_path,
        )
    state_path = tmp_path / "remote/srv/l9/projects/seo-bot/staging/state.json"
    state = json.loads(state_path.read_text(encoding="utf-8"))
    assert state["current"]["image_ref"] == previous.image_ref
    assert ReceiptLedger(tmp_path / "receipts/ledger").verify()["entries"] == 1


def test_receipt_publication_failure_restores_state(
    deployment_context, schema_registry, tmp_path: Path, monkeypatch
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
