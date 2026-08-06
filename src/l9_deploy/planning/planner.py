"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [planning]
tags: [L9_CONTRACT, deterministic-plan]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

from datetime import UTC, datetime

from ..canonical import sha256_digest
from ..contracts.models import DeploymentPlan, PlanStep, ReleaseState, VerifiedRequest
from ..inventory.resolver import resolve_target
from .backups import backup_required
from .migrations import migration_step
from .topology import target_server_ids


def build_plan(
    verified: VerifiedRequest,
    previous_release: ReleaseState | dict[str, object] | None = None,
    created_at: str | None = None,
) -> DeploymentPlan:
    request = verified.document
    profile = verified.profile
    target = resolve_target(verified.fleet, verified.project, request.target.environment)
    steps: list[PlanStep] = [
        PlanStep(id="verify", kind="verify", mutating=False, timeout_seconds=120),
    ]
    if backup_required(profile):
        steps.append(PlanStep(id="backup", kind="backup", mutating=True, timeout_seconds=900))
    migration = migration_step(profile)
    steps.extend(
        [
            PlanStep(id="pull", kind="pull", mutating=True, timeout_seconds=600),
            PlanStep(id="render", kind="render", mutating=True, timeout_seconds=120),
        ]
    )
    if migration is not None and migration.details.get("mode") == "pre_start":
        steps.append(migration)
    steps.append(PlanStep(id="deploy", kind="deploy", mutating=True, timeout_seconds=600))
    if migration is not None and migration.details.get("mode") == "post_start":
        steps.append(migration)
    steps.extend(
        [
            PlanStep(
                id="health",
                kind="health",
                mutating=False,
                timeout_seconds=profile.health.post_deploy.timeout_seconds,
                details=profile.health.post_deploy.model_dump(
                    mode="json", by_alias=True, exclude_none=True
                ),
            ),
            PlanStep(id="promote", kind="promote", mutating=True, timeout_seconds=120),
            PlanStep(
                id="cleanup",
                kind="cleanup",
                mutating=True,
                timeout_seconds=300,
                details={"retain": profile.release.retain_successful_releases},
            ),
        ]
    )
    previous = (
        previous_release
        if isinstance(previous_release, ReleaseState) or previous_release is None
        else ReleaseState.model_validate(previous_release)
    )
    payload = {
        "schema": "l9.deployment-plan/v1",
        "request_id": request.request_id,
        "requested_by": request.requested_by,
        "project_id": verified.project.id,
        "environment": request.target.environment,
        "source_commit_sha": request.source.commit_sha,
        "image_ref": request.artifact.image_ref,
        "profile_digest": request.profile.digest,
        "target_servers": target_server_ids(target.servers),
        "previous_release": previous.model_dump(mode="json", by_alias=True) if previous else None,
        "steps": [step.model_dump(mode="json", by_alias=True) for step in steps],
        "created_at": created_at or datetime.now(UTC).isoformat(),
    }
    payload["plan_digest"] = sha256_digest(payload)
    return DeploymentPlan.model_validate(payload)
