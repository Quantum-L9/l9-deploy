"""--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests]
tags: [L9_TEST, planning]
owner: platform
status: active
--- /L9_META ---"""
from __future__ import annotations

from l9_deploy.planning.planner import build_plan
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


def test_plan_is_deterministic_for_fixed_timestamp(
    deployment_context, schema_registry
) -> None:  # type: ignore[no-untyped-def]
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
