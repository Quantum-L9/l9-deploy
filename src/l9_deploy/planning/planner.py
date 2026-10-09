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


_SERVICE_PROBE_GUIDANCE = (
    "declare a tcp probe with the dependency's host and port, or a command or "
    "database probe whose command runs on the deployment target"
)


def _require_executable_service_probe(name: str, probe: HealthProbe) -> None:
    """Refuse a required-service probe the generic runner could not execute.

    ``HealthProbe`` is one shape for four probe types, so a type-valid probe can
    still lack what ``run_probe`` needs. Those shapes are refused here, before a
    plan can be approved, instead of at runtime after host mutation has begun.
    The requirements mirror the runner exactly: TCP needs a usable host and
    port; command and database need a non-empty argument vector.

    An ``http`` probe is refused for a required service outright. The runner
    issues HTTP probes against the application's own base URL (the only HTTP
    origin the platform knows), so an application response cannot stand as
    evidence that an independent dependency is ready, and the contract carries
    no binding that would make an application-proxied readiness path explicit.
    Reinterpreting ``host``/``port`` as an HTTP origin would originate a target
    the consumer never approved, so the consumer is directed to the probe types
    that do name their target.
    """
    kind = probe.type
    if kind == "http":
        raise ContractError(
            f"required service {name} declares an http readiness probe; http probes "
            "are issued against the application's own base URL and cannot qualify an "
            f"independent dependency: {_SERVICE_PROBE_GUIDANCE}"
        )
    if kind == "tcp":
        if not probe.host or not probe.host.strip() or probe.port is None:
            raise ContractError(
                f"required service {name} tcp readiness probe needs a host and a port; "
                f"{_SERVICE_PROBE_GUIDANCE}"
            )
        if not 1 <= probe.port <= 65535:
            raise ContractError(
                f"required service {name} tcp readiness probe port {probe.port} is not "
                "a usable port (1-65535)"
            )
    elif not probe.command or not all(argument.strip() for argument in probe.command):
        # command and database probes are an argument vector run on the target.
        raise ContractError(
            f"required service {name} {kind} readiness probe needs a non-empty command; "
            f"{_SERVICE_PROBE_GUIDANCE}"
        )


def required_service_probes(profile: DeploymentProfile) -> tuple[tuple[str, HealthProbe], ...]:
    """Qualify the profile's declared service prerequisites for deployment.

    Returns ``(name, probe)`` for every ``required: true`` service in
    deterministic name order. The consumer owns which services it needs and how
    their readiness is observed; this platform only checks that a required claim
    is coherent and observable:

    - ``required: true`` with ``mode: none`` is contradictory and is refused;
    - ``required: true`` in ``external`` or ``managed_on_fleet`` mode without a
      typed probe cannot be qualified and is refused (blocked, never assumed);
    - a probe the generic runner could not execute (missing host/port, empty
      command) or whose target would be the application rather than the
      dependency (``http``) is refused before a plan exists;
    - ``required: false`` services are not a deployment gate and are not
      returned, so nothing is ever claimed about them.

    A probe is readiness evidence only. It does not provision, own, or render
    the dependency, and success means exactly what the supplied probe checks.
    Whether the dependency answers remains a runtime fact; this preflight only
    establishes that the question can be asked.
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
        _require_executable_service_probe(name, service.probe)
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
