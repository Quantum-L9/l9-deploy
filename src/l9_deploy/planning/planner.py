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
from ..contracts.models import (
    DeploymentPlan,
    DeploymentProfile,
    HealthProbe,
    PlanStep,
    ReleaseState,
    VerifiedRequest,
)
from ..errors import AuthorizationError, ContractError
from ..inventory.resolver import resolve_target
from .backups import backup_required
from .migrations import migration_step
from .topology import target_server_ids

_UNSEALED_PLAN_DIGEST = "sha256:" + "0" * 64


def plan_digest_of(document: dict[str, object]) -> str:
    """Return the digest of a plan document's content, ignoring its ``plan_digest``.

    The digest is taken over the plan's canonical wire form (the alias-bound JSON
    dump of ``DeploymentPlan``), so a plan serialized to ``plan.json`` and loaded
    again reproduces its own digest. Approval binds to this value; anything that
    changes the content, ``profile_digest`` included, changes the digest.
    """
    return sha256_digest({key: value for key, value in document.items() if key != "plan_digest"})


def verify_plan_digest(plan: DeploymentPlan) -> None:
    """Refuse a plan whose ``plan_digest`` string does not match its content."""
    if plan_digest_of(plan.model_dump(mode="json", by_alias=True)) != plan.plan_digest:
        raise AuthorizationError("plan digest does not match plan content")


def required_service_probes(profile: DeploymentProfile) -> tuple[tuple[str, HealthProbe], ...]:
    """Qualify the profile's declared service prerequisites for deployment.

    Returns ``(name, probe)`` for every ``required: true`` service in
    deterministic name order. The consumer owns which services it needs and how
    their readiness is observed; this platform only checks that a required claim
    is coherent and observable:

    - ``required: true`` with ``mode: none`` is contradictory and is refused;
    - ``required: true`` in ``external`` or ``managed_on_fleet`` mode without a
      typed probe cannot be qualified and is refused (blocked, never assumed);
    - ``required: false`` services are not a deployment gate and are not
      returned, so nothing is ever claimed about them.

    A probe is readiness evidence only. It does not provision, own, or render
    the dependency, and success means exactly what the supplied probe checks.
    """
    qualified: list[tuple[str, HealthProbe]] = []
    for name in sorted(profile.services):
        service = profile.services[name]
        if not service.required:
            continue
        if service.mode == "none":
            raise ContractError(
                f"service {name} is declared required but has mode none; "
                "a required dependency must be external or managed_on_fleet"
            )
        if service.probe is None:
            raise ContractError(
                f"required {service.mode} service {name} declares no readiness probe; "
                "deployment is blocked until the consumer profile supplies one"
            )
        qualified.append((name, service.probe))
    return tuple(qualified)


def build_plan(
    verified: VerifiedRequest,
    previous_release: ReleaseState | dict[str, object] | None = None,
    created_at: str | None = None,
) -> DeploymentPlan:
    request = verified.document
    profile = verified.profile
    # Preflight: an unqualifiable service declaration never reaches a plan that
    # could be approved. The plan shape is unchanged; the declaration itself is
    # already bound by the sealed profile digest the plan carries.
    required_service_probes(profile)
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
        "plan_digest": _UNSEALED_PLAN_DIGEST,
    }
    # Canonicalize through the contract model first so the digest covers exactly
    # the bytes a later stage reloads from plan.json (verify_plan_digest).
    canonical = DeploymentPlan.model_validate(payload).model_dump(mode="json", by_alias=True)
    canonical["plan_digest"] = plan_digest_of(canonical)
    plan = DeploymentPlan.model_validate(canonical)
    verify_plan_digest(plan)
    return plan
