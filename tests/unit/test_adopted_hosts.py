"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, unit]
tags: [L9_TEST, adopted-host, authorization]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest
from pydantic import ValidationError

from l9_deploy import cli
from l9_deploy.contracts.models import ServerProfile
from l9_deploy.errors import AuthorizationError
from l9_deploy.execution.remote import LocalExecutor


def _c1_server() -> dict[str, object]:
    return {
        "schema": "l9.server-profile/v1",
        "id": "c1",
        "environment": "staging",
        "provider": "hetzner",
        "lifecycle": "adopted",
        "private_ip": None,
        "public_ip": "46.62.243.82",
        "ssh": {"user": "root", "port": 22},
        "roles": ["application"],
        "labels": {"protection": "c1"},
        "conformance": {"profile": "adopted-c1", "max_age_hours": 24},
    }


def _fleet() -> dict[str, object]:
    project = {
        "id": "l9-cognitive-runtime",
        "repository": "Quantum-L9/l9-cognitive-runtime",
        "profile_path": "integrations/consumers/l9-cognitive-runtime.deployment.yaml",
        "environments": {
            "staging": {
                "server_ids": ["c1"],
                "infisical_environment": "staging",
                "public_hostnames": ["mcp-staging.quantumaipartners.com"],
            }
        },
    }
    return {
        "schema": "l9.fleet-inventory/v1",
        "management": {"runner_server_id": "runner", "private_cidr": "10.90.1.0/24"},
        "environments": {
            "staging": {
                "approval_required": False,
                "concurrency_group": "l9-staging",
                "allowed_source_refs": ["refs/heads/main"],
            }
        },
        "servers": [_c1_server()],
        "projects": [project],
    }


def test_adopted_server_uses_public_ip_as_connection_address() -> None:
    server = ServerProfile.model_validate(_c1_server())
    assert server.private_ip is None
    assert server.public_ip == "46.62.243.82"
    assert server.connection_address == "46.62.243.82"
    host = cli._host_from_server(server)
    assert host.address == "46.62.243.82"
    assert host.user == "root"


def test_adopted_server_requires_observed_public_ip() -> None:
    server = _c1_server()
    server["public_ip"] = None
    with pytest.raises(ValidationError, match="adopted servers require public_ip"):
        ServerProfile.model_validate(server)


def test_managed_server_still_requires_private_ip() -> None:
    server = _c1_server()
    server["lifecycle"] = "managed"
    with pytest.raises(ValidationError, match="managed servers require private_ip"):
        ServerProfile.model_validate(server)


def test_adopted_runtime_mutation_requires_explicit_capability(tmp_path: Path) -> None:
    fleet = _fleet()
    project = fleet["projects"][0]  # type: ignore[index]
    assert isinstance(project, dict)
    args = argparse.Namespace(
        local_executor_root=str(tmp_path),
        timeout=10,
        allow_adopted_host_mutation=False,
    )
    with pytest.raises(AuthorizationError, match="allow-adopted-host-mutation"):
        cli._target_executor(args, fleet, project, "staging", mutation=True)

    args.allow_adopted_host_mutation = True
    executor = cli._target_executor(args, fleet, project, "staging", mutation=True)
    assert isinstance(executor, LocalExecutor)
