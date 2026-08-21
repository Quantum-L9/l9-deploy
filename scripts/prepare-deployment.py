#!/usr/bin/env python3
"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [github-actions, planning]
tags: [L9_CONTRACT, deployment-preflight]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from _bootstrap import add_repository_src

add_repository_src()

from l9_deploy.contracts.loader import load_document  # noqa: E402
from l9_deploy.contracts.validator import SchemaRegistry  # noqa: E402
from l9_deploy.errors import ContractError  # noqa: E402
from l9_deploy.inventory.loader import load_fleet  # noqa: E402
from l9_deploy.inventory.resolver import resolve_target  # noqa: E402
from l9_deploy.planning.planner import build_plan  # noqa: E402
from l9_deploy.requests.verifier import verify_request  # noqa: E402


def object_document(path: Path) -> dict[str, object]:
    value = load_document(path)
    if not isinstance(value, dict):
        raise TypeError(f"expected object document: {path}")
    return value


def write_output(name: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as handle:
            handle.write(f"{name}={value}\n")
    else:
        sys.stdout.write(f"{name}={value}\n")


def deployment_base_url(verified, target_address: str | None) -> str:  # type: ignore[no-untyped-def]
    ingress = verified.profile.network.public_ingress
    public_hostnames = verified.environment.public_hostnames
    if ingress.enabled and public_hostnames:
        if ingress.tls not in {"automatic", "external"}:
            raise ContractError("public ingress deployment health requires TLS")
        return f"https://{min(public_hostnames)}"
    port = verified.profile.runtime.container_port
    if port and target_address:
        # Managed private-service health stays on the private east-west fleet network.
        return f"http://{target_address}:{port}"  # NOSONAR
    return ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--evidence-root", required=True, type=Path)
    parser.add_argument("--fleet", default=Path("fleet/registry.yaml"), type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--root", default=Path.cwd(), type=Path)
    args = parser.parse_args()

    root = args.root.resolve()
    registry = SchemaRegistry(root / "schemas/v1")
    request = object_document(args.request)
    fleet = load_fleet(args.fleet, registry)
    verified = verify_request(
        request,
        fleet,
        registry,
        root,
        evidence_root=args.evidence_root,
    )
    plan = build_plan(verified)
    plan_document = plan.model_dump(mode="json", by_alias=True)
    registry.validate(plan_document, "deployment-plan")
    args.plan.parent.mkdir(parents=True, exist_ok=True)
    args.plan.write_text(
        json.dumps(plan_document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    secrets = verified.profile.secrets
    environment = plan.environment
    infisical_environment = secrets.environment_mapping[environment]
    target = resolve_target(verified.fleet, verified.project, environment)
    target_address = target.servers[0].connection_address
    base_url = deployment_base_url(verified, target_address)
    write_output("environment", environment)
    write_output("project_id", plan.project_id)
    write_output("plan_digest", plan.plan_digest)
    write_output("request_id", plan.request_id)
    write_output("requester", plan.requested_by)
    write_output("infisical_environment", infisical_environment)
    write_output("image_ref", plan.image_ref)
    write_output("source_repository", verified.document.source.repository)
    write_output("source_run_id", str(verified.document.source.run_id))
    write_output("base_url", base_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
