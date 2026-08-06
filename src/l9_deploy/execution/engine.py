"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [execution]
tags: [L9_CONTRACT, transaction, rollback]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from pydantic import JsonValue, TypeAdapter

from ..contracts.models import (
    DeploymentPlan,
    DeploymentProfile,
    HealthProbe,
    ReceiptStep,
    ReleaseState,
)
from ..contracts.validator import SchemaRegistry
from ..errors import AuthorizationError, ExecutionError
from ..evidence.approval import verify_approval_receipt
from ..evidence.ledger import ReceiptLedger
from ..evidence.publisher import publish_receipt
from ..evidence.receipts import create_deployment_receipt
from ..requests.idempotency import IdempotencyStore
from .backups import create_backup
from .compose import compose_path, render_compose
from .health import run_probe
from .images import inspect_repo_digest, pull_image, require_digest_ref
from .locks import environment_lock
from .migrations import execute_migration
from .promotion import promote
from .releases import (
    bind_release_runtime_env,
    cleanup_release_directories,
    materialize_release_runtime_env,
    remove_release_directory,
    validate_release_runtime_env_path,
)
from .rollback import rollback_release

LOGGER = logging.getLogger(__name__)


class Executor(Protocol):
    def run(self, command: Sequence[str], **kwargs: object) -> object: ...
    def write_text(self, path: Path, text: str, mode: int = 0o600) -> None: ...


def execute_plan(
    *,
    plan: DeploymentPlan | dict[str, object],
    profile: DeploymentProfile | dict[str, object],
    executor: Executor,
    expected_plan_digest: str,
    approval_receipt: Path,
    approval_history: Path,
    approval_run_id: int | None,
    latest_pointer: Path,
    receipt_ledger_root: Path,
    lock_root: Path,
    idempotency_store: IdempotencyStore,
    request_digest: str,
    base_url: str | None = None,
    runtime_env_file: Path | None = None,
) -> dict[str, object]:
    registry = SchemaRegistry(Path(__file__).resolve().parents[3] / "schemas" / "v1")
    typed_plan = plan if isinstance(plan, DeploymentPlan) else DeploymentPlan.model_validate(plan)
    typed_profile = (
        profile
        if isinstance(profile, DeploymentProfile)
        else DeploymentProfile.model_validate(profile)
    )
    registry.validate(typed_plan.model_dump(mode="json", by_alias=True), "deployment-plan")
    registry.validate(
        typed_profile.model_dump(mode="json", by_alias=True, exclude_none=True),
        "deployment-profile",
    )
    if typed_plan.plan_digest != expected_plan_digest:
        raise AuthorizationError("expected plan digest does not match plan")
    verify_approval_receipt(
        approval_receipt,
        approval_history,
        registry,
        request_id=typed_plan.request_id,
        requester=typed_plan.requested_by,
        environment=typed_plan.environment,
        plan_digest=typed_plan.plan_digest,
        expected_run_id=approval_run_id,
    )
    prior = idempotency_store.begin(typed_plan.request_id, request_digest)
    if prior and prior.status == "COMPLETE":
        return {
            "status": "PASS",
            "idempotent_replay": True,
            "receipt_digest": prior.receipt_digest,
        }
    if prior and prior.status == "PREPARED":
        if prior.receipt_digest is None:
            raise ExecutionError("prepared idempotency state lacks a receipt digest")
        recovered = ReceiptLedger(receipt_ledger_root).load_receipt(prior.receipt_digest)
        try:
            idempotency_store.complete(typed_plan.request_id, prior.receipt_digest)
        except Exception as exc:
            LOGGER.warning(
                "idempotency finalization remains pending after receipt recovery",
                extra={"request_id": typed_plan.request_id, "error_type": type(exc).__name__},
            )
        return recovered

    started = datetime.now(UTC).isoformat()
    step_results: list[ReceiptStep] = []
    previous = typed_plan.previous_release
    candidate = bind_release_runtime_env(
        ReleaseState(
            request_id=typed_plan.request_id,
            source_commit_sha=typed_plan.source_commit_sha,
            image_ref=typed_plan.image_ref,
            plan_digest=typed_plan.plan_digest,
        ),
        typed_plan.project_id,
        typed_plan.environment,
    )
    candidate_runtime_env = validate_release_runtime_env_path(
        candidate, typed_plan.project_id, typed_plan.environment
    )
    if candidate_runtime_env is None:
        raise ExecutionError("candidate runtime configuration identity is unavailable")
    rollback_probe = next(
        (
            HealthProbe.model_validate(step.details)
            for step in typed_plan.steps
            if step.kind == "health"
        ),
        None,
    )
    if previous is not None and previous.plan_digest == candidate.plan_digest:
        raise ExecutionError(
            "candidate release identity collides with the active release directory"
        )
    if typed_profile.release.automatic_rollback and previous is not None:
        if rollback_probe is None:
            raise ExecutionError("automatic rollback requires a health probe")
        if (
            validate_release_runtime_env_path(
                previous, typed_plan.project_id, typed_plan.environment
            )
            is None
        ):
            raise ExecutionError(
                "previous release lacks runtime configuration identity; deployment is blocked"
            )
    promoted = False
    try:
        with environment_lock(lock_root, typed_plan.environment):
            require_digest_ref(typed_plan.image_ref)
            if previous is not None:
                previous_runtime_env = validate_release_runtime_env_path(
                    previous, typed_plan.project_id, typed_plan.environment
                )
                if previous_runtime_env is not None:
                    executor.run(["test", "-f", str(previous_runtime_env)])
            if runtime_env_file is not None:
                candidate = materialize_release_runtime_env(
                    executor,
                    candidate,
                    typed_plan.project_id,
                    typed_plan.environment,
                    runtime_env_file.read_text(encoding="utf-8"),
                )
            else:
                executor.run(["test", "-f", str(candidate_runtime_env)])
            for step in typed_plan.steps:
                details: dict[str, JsonValue]
                kind = step.kind
                if kind == "verify":
                    details = {}
                elif kind == "backup":
                    details = create_backup(
                        executor,
                        typed_profile,
                        typed_plan.project_id,
                        typed_plan.environment,
                        typed_plan.request_id,
                    )
                elif kind == "pull":
                    pull_image(executor, typed_plan.image_ref, step.timeout_seconds)
                    inspect_repo_digest(executor, typed_plan.image_ref)
                    details = {"image_ref": typed_plan.image_ref}
                elif kind == "render":
                    compose = render_compose(
                        typed_profile,
                        typed_plan.image_ref,
                        typed_plan.environment,
                        str(candidate_runtime_env),
                    )
                    path = compose_path(typed_plan.project_id, typed_plan.environment)
                    executor.write_text(path, compose, mode=0o640)
                    details = {"path": str(path)}
                elif kind == "migration":
                    details = execute_migration(
                        executor,
                        typed_profile,
                        typed_plan.image_ref,
                        str(candidate_runtime_env),
                    )
                elif kind == "deploy":
                    path = compose_path(typed_plan.project_id, typed_plan.environment)
                    executor.run(["docker", "network", "inspect", "l9-runtime"], check=False)
                    executor.run(["docker", "network", "create", "l9-runtime"], check=False)
                    executor.run(
                        [
                            "docker",
                            "compose",
                            "--env-file",
                            str(candidate_runtime_env),
                            "-f",
                            str(path),
                            "up",
                            "-d",
                            "--remove-orphans",
                        ],
                        env={
                            "L9_IMAGE_REF": typed_plan.image_ref,
                            "L9_RUNTIME_ENV_FILE": str(candidate_runtime_env),
                        },
                        timeout=step.timeout_seconds,
                    )
                    details = {}
                elif kind == "health":
                    probe = HealthProbe.model_validate(step.details)
                    details = run_probe(
                        probe,
                        executor=executor,
                        base_url=base_url,
                    )
                elif kind == "promote":
                    details = TypeAdapter(dict[str, JsonValue]).validate_python(
                        promote(
                            executor,
                            typed_plan.project_id,
                            typed_plan.environment,
                            candidate,
                            previous_release=previous,
                        )
                    )
                    promoted = True
                elif kind == "cleanup":
                    executor.run(["docker", "image", "prune", "-f"], check=False)
                    details = TypeAdapter(dict[str, JsonValue]).validate_python(
                        cleanup_release_directories(
                            executor,
                            candidate,
                            previous,
                            typed_plan.project_id,
                            typed_plan.environment,
                        )
                    )
                else:
                    raise ExecutionError(f"unsupported plan step: {kind}")
                step_results.append(
                    ReceiptStep(step_id=step.id, kind=kind, status="PASS", details=details)
                )

        receipt = create_deployment_receipt(
            request_id=typed_plan.request_id,
            project_id=typed_plan.project_id,
            environment=typed_plan.environment,
            status="PASS",
            started_at=started,
            source_commit_sha=typed_plan.source_commit_sha,
            image_ref=typed_plan.image_ref,
            plan_digest=typed_plan.plan_digest,
            previous_release=previous,
            steps=step_results,
        )
        receipt_document = receipt.model_dump(mode="json", by_alias=True)
        registry.validate(receipt_document, "deployment-receipt")
        idempotency_store.prepare_completion(typed_plan.request_id, receipt.receipt_digest)
        publish_receipt(
            receipt_ledger_root,
            receipt_document,
            latest_pointer=latest_pointer,
        )
        try:
            idempotency_store.complete(typed_plan.request_id, receipt.receipt_digest)
        except Exception as exc:
            LOGGER.warning(
                "deployment committed with idempotency finalization pending",
                extra={"request_id": typed_plan.request_id, "error_type": type(exc).__name__},
            )
        return receipt_document
    except Exception as exc:
        rollback_result: dict[str, JsonValue] | None = None
        if (
            typed_profile.release.automatic_rollback
            and previous is not None
            and rollback_probe is not None
        ):
            try:
                rollback_result = TypeAdapter(dict[str, JsonValue]).validate_python(
                    rollback_release(
                        executor,
                        typed_plan.project_id,
                        typed_plan.environment,
                        previous,
                        failed_release=candidate if promoted else None,
                        health_probe=rollback_probe,
                        base_url=base_url,
                        publish_state=promoted,
                    )
                )
            except Exception as rollback_exc:
                rollback_result = {"status": "FAIL", "error": str(rollback_exc)}
        if not promoted:
            try:
                remove_release_directory(
                    executor, candidate, typed_plan.project_id, typed_plan.environment
                )
            except Exception as cleanup_exc:
                if rollback_result is None:
                    rollback_result = {
                        "status": "FAIL",
                        "error": f"candidate cleanup failed: {cleanup_exc}",
                    }
        idempotency_store.fail(typed_plan.request_id, str(exc))
        failed = create_deployment_receipt(
            request_id=typed_plan.request_id,
            project_id=typed_plan.project_id,
            environment=typed_plan.environment,
            status="FAIL",
            started_at=started,
            source_commit_sha=typed_plan.source_commit_sha,
            image_ref=typed_plan.image_ref,
            plan_digest=typed_plan.plan_digest,
            previous_release=previous,
            steps=[
                *step_results,
                ReceiptStep(
                    step_id="transaction-failure",
                    kind="rollback",
                    status="FAIL",
                    details={"error": str(exc), "rollback": rollback_result},
                ),
            ],
            unknowns=["database state was not automatically rolled back"],
        )
        failed_document = failed.model_dump(mode="json", by_alias=True)
        registry.validate(failed_document, "deployment-receipt")
        try:
            publish_receipt(
                receipt_ledger_root,
                failed_document,
                latest_pointer=latest_pointer,
            )
        except Exception as publication_exc:
            raise ExecutionError(
                f"deployment failed and failure receipt publication also failed: {publication_exc}"
            ) from exc
        raise
