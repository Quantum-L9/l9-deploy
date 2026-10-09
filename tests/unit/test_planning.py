"""--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests]
tags: [L9_TEST, planning]
owner: platform
status: active
--- /L9_META ---"""

from __future__ import annotations

import copy
from typing import Any

import pytest
import yaml

from l9_deploy.canonical import file_sha256
from l9_deploy.contracts.models import DeploymentProfile
from l9_deploy.errors import ContractError
from l9_deploy.planning.planner import build_plan, required_service_probes
from l9_deploy.requests.verifier import verify_request


def get_verified(deployment_context, schema_registry):  # type: ignore[no-untyped-def]
    return verify_request(
        deployment_context["request"],
        deployment_context["fleet"],
        schema_registry,
        deployment_context["root"],
        evidence_root=deployment_context["evidence_root"],
        bundle_validator=deployment_context["bundle_validator"],
    )


def _probe(*command: str) -> dict[str, Any]:
    return {
        "type": "command",
        "command": list(command),
        "timeout_seconds": 5,
        "attempts": 1,
        "interval_seconds": 1,
    }


def verified_with_services(deployment_context, schema_registry, services):  # type: ignore[no-untyped-def]
    """Re-seal the fixture profile with ``services`` and verify the request against it."""
    profile_path = deployment_context["profile_path"]
    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    profile["services"] = services
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    request = copy.deepcopy(deployment_context["request"])
    request["profile"]["digest"] = file_sha256(profile_path)
    return verify_request(
        request,
        deployment_context["fleet"],
        schema_registry,
        deployment_context["root"],
        evidence_root=deployment_context["evidence_root"],
        bundle_validator=deployment_context["bundle_validator"],
    )


def test_plan_is_deterministic_for_fixed_timestamp(deployment_context, schema_registry) -> None:  # type: ignore[no-untyped-def]
    verified = get_verified(deployment_context, schema_registry)
    timestamp = "2026-07-21T12:01:00Z"
    first = build_plan(verified, created_at=timestamp)
    second = build_plan(verified, created_at=timestamp)
    assert first == second
    assert first.plan_digest.startswith("sha256:")
    schema_registry.validate(first.model_dump(mode="json", by_alias=True), "deployment-plan")


def test_stateful_plan_orders_backup_before_migration_and_deploy(
    deployment_context, schema_registry
) -> None:  # type: ignore[no-untyped-def]
    plan = build_plan(
        get_verified(deployment_context, schema_registry),
        created_at="2026-07-21T12:01:00Z",
    )
    kinds = [step.kind for step in plan.steps]
    assert kinds.index("backup") < kinds.index("migration") < kinds.index("deploy")
    assert kinds[-2:] == ["promote", "cleanup"]


def test_plan_refuses_required_service_with_mode_none(deployment_context, schema_registry) -> None:  # type: ignore[no-untyped-def]
    # B1: a required dependency that declares no mode is contradictory.
    verified = verified_with_services(
        deployment_context, schema_registry, {"cache": {"mode": "none", "required": True}}
    )
    with pytest.raises(ContractError, match="service cache is declared required but has mode none"):
        build_plan(verified, created_at="2026-07-21T12:01:00Z")


@pytest.mark.parametrize("mode", ["external", "managed_on_fleet"])
def test_plan_refuses_required_service_without_probe(
    deployment_context, schema_registry, mode: str
) -> None:  # type: ignore[no-untyped-def]
    # B2: a required dependency with nothing to observe cannot be qualified.
    verified = verified_with_services(
        deployment_context, schema_registry, {"postgres": {"mode": mode, "required": True}}
    )
    with pytest.raises(
        ContractError, match=f"required {mode} service postgres declares no readiness probe"
    ):
        build_plan(verified, created_at="2026-07-21T12:01:00Z")


def test_plan_does_not_gate_on_optional_or_absent_services(
    deployment_context, schema_registry
) -> None:  # type: ignore[no-untyped-def]
    # B7: optional and mode-none-not-required services are not a gate and are
    # never qualified.
    verified = verified_with_services(
        deployment_context,
        schema_registry,
        {
            "cache": {"mode": "external", "required": False},
            "unused": {"mode": "none", "required": False},
        },
    )
    plan = build_plan(verified, created_at="2026-07-21T12:01:00Z")
    assert required_service_probes(verified.profile) == ()
    assert [step.kind for step in plan.steps].count("health") == 1


def test_required_service_probes_are_name_ordered_and_exact(
    deployment_context,
) -> None:  # type: ignore[no-untyped-def]
    # B6: a deliberately unordered source map yields a deterministic, exact set.
    profile_document = copy.deepcopy(deployment_context["profile"])
    profile_document["services"] = {
        "zeta": {"mode": "external", "required": True, "probe": _probe("service-ready", "zeta")},
        "alpha": {
            "mode": "managed_on_fleet",
            "required": True,
            "probe": _probe("service-ready", "alpha"),
        },
        "optional": {"mode": "external", "required": False},
        "mid": {"mode": "external", "required": True, "probe": _probe("service-ready", "mid")},
    }
    profile = DeploymentProfile.model_validate(profile_document)
    qualified = required_service_probes(profile)
    assert [name for name, _ in qualified] == ["alpha", "mid", "zeta"]
    assert [probe.command for _, probe in qualified] == [
        ("service-ready", "alpha"),
        ("service-ready", "mid"),
        ("service-ready", "zeta"),
    ]


def _profile_with_probe(deployment_context, probe: dict[str, Any]) -> DeploymentProfile:  # type: ignore[no-untyped-def]
    """Type the fixture profile directly (no schema pass) with one required service probe."""
    document = copy.deepcopy(deployment_context["profile"])
    document["services"] = {"postgres": {"mode": "external", "required": True, "probe": probe}}
    return DeploymentProfile.model_validate(document)


@pytest.mark.parametrize(
    ("probe", "message"),
    [
        # R2 / C4: command and database probes need an executable argument vector.
        ({"type": "command", "timeout_seconds": 5}, "command readiness probe needs a non-empty"),
        (
            {"type": "command", "command": [], "timeout_seconds": 5},
            "command readiness probe needs a non-empty",
        ),
        (
            {"type": "command", "command": [" "], "timeout_seconds": 5},
            "command readiness probe needs a non-empty",
        ),
        ({"type": "database", "timeout_seconds": 5}, "database readiness probe needs a non-empty"),
        # R2 / C5: tcp probes need a usable host and port.
        ({"type": "tcp", "timeout_seconds": 5}, "tcp readiness probe needs a host and a port"),
        (
            {"type": "tcp", "host": "", "port": 5432, "timeout_seconds": 5},
            "tcp readiness probe needs a host and a port",
        ),
        (
            {"type": "tcp", "host": "db.internal", "timeout_seconds": 5},
            "tcp readiness probe needs a host and a port",
        ),
        (
            {"type": "tcp", "host": "db.internal", "port": 0, "timeout_seconds": 5},
            "tcp readiness probe port 0 is not a usable port",
        ),
        (
            {"type": "tcp", "host": "db.internal", "port": 70000, "timeout_seconds": 5},
            "tcp readiness probe port 70000 is not a usable port",
        ),
        # R1 / C6: an http probe would target the application, never the dependency.
        (
            {"type": "http", "path": "/ready", "expected_status": 200, "timeout_seconds": 5},
            "declares an http readiness probe",
        ),
        ({"type": "http", "timeout_seconds": 5}, "declares an http readiness probe"),
    ],
)
def test_required_service_probe_must_be_executable_by_the_generic_runner(
    deployment_context, probe: dict[str, Any], message: str
) -> None:  # type: ignore[no-untyped-def]
    # R2 (and R1 for http): a type-valid probe the runner could not execute, or
    # whose target would be the application rather than the dependency, is
    # refused at qualification, before build_plan can produce an approvable plan.
    profile = _profile_with_probe(deployment_context, probe)
    with pytest.raises(ContractError, match=f"required service postgres {message}"):
        required_service_probes(profile)


def test_plan_refuses_http_required_service_probe_that_passes_the_schema(
    deployment_context, schema_registry
) -> None:  # type: ignore[no-untyped-def]
    # R1 / C2 at planning: the probe schema accepts an http probe with a path and
    # status, but the only HTTP origin the platform knows is the application's
    # base URL, so an application 200 would be recorded as dependency readiness.
    # The sealed, schema-valid profile is refused before a plan exists.
    verified = verified_with_services(
        deployment_context,
        schema_registry,
        {
            "postgres": {
                "mode": "external",
                "required": True,
                "probe": {
                    "type": "http",
                    "path": "/health",
                    "expected_status": 200,
                    "timeout_seconds": 5,
                },
            }
        },
    )
    with pytest.raises(
        ContractError, match="http probes are issued against the application's own base URL"
    ):
        build_plan(verified, created_at="2026-07-21T12:01:00Z")


def test_tcp_command_and_database_service_probes_qualify_through_the_sealed_path(
    deployment_context, schema_registry
) -> None:  # type: ignore[no-untyped-def]
    # C3: probes that name their own target remain executable and reach a plan.
    verified = verified_with_services(
        deployment_context,
        schema_registry,
        {
            "postgres": {
                "mode": "managed_on_fleet",
                "required": True,
                "probe": {"type": "tcp", "host": "10.90.10.20", "port": 5432, "timeout_seconds": 5},
            },
            "redis": {
                "mode": "external",
                "required": True,
                "probe": _probe("redis-cli", "-h", "10.90.10.21", "ping"),
            },
            "ledger": {
                "mode": "external",
                "required": True,
                "probe": {
                    "type": "database",
                    "command": ["pg_isready", "-h", "10.90.10.20"],
                    "timeout_seconds": 5,
                },
            },
        },
    )
    qualified = required_service_probes(verified.profile)
    assert [(name, probe.type) for name, probe in qualified] == [
        ("ledger", "database"),
        ("postgres", "tcp"),
        ("redis", "command"),
    ]
    plan = build_plan(verified, created_at="2026-07-21T12:01:00Z")
    assert [step.kind for step in plan.steps].count("health") == 1


def test_service_declarations_do_not_change_plan_shape(deployment_context, schema_registry) -> None:  # type: ignore[no-untyped-def]
    # The plan carries no service metadata; the declaration is bound by the
    # sealed profile digest the plan already carries.
    baseline = build_plan(
        get_verified(deployment_context, schema_registry), created_at="2026-07-21T12:01:00Z"
    )
    verified = verified_with_services(
        deployment_context,
        schema_registry,
        {"postgres": {"mode": "external", "required": True, "probe": _probe("service-ready")}},
    )
    plan = build_plan(verified, created_at="2026-07-21T12:01:00Z")
    assert [step.model_dump(mode="json", by_alias=True) for step in plan.steps] == [
        step.model_dump(mode="json", by_alias=True) for step in baseline.steps
    ]
    document = plan.model_dump(mode="json", by_alias=True)
    assert "services" not in document
    assert document["profile_digest"] == verified.document.profile.digest
    schema_registry.validate(document, "deployment-plan")
