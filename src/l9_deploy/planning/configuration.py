"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer:
- repository
tags:
- L9_META
- deployment-platform
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import cast

import yaml
from pydantic import JsonValue

from ..canonical import file_sha256, sha256_digest
from ..errors import AuthorizationError, ContractError

_FULL_SHA = re.compile(r"^[a-f0-9]{40}$")
_SERVER_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_ENVIRONMENT = re.compile(r"^[a-z][a-z0-9-]{1,31}$")


def _confined_file(root: Path, path: Path) -> Path:
    candidate = path.resolve()
    if candidate != root and root not in candidate.parents:
        raise ContractError(f"configuration plan path escapes repository root: {path}")
    if not candidate.is_file():
        raise ContractError(f"configuration plan file is missing: {path}")
    return candidate


def _relative(root: Path, path: Path) -> str:
    return path.relative_to(root).as_posix()


def _fleet_document(path: Path) -> dict[str, JsonValue]:
    value: object = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError("fleet inventory must be an object")
    servers = value.get("servers")
    if not isinstance(servers, list):
        raise ContractError("fleet inventory must contain servers")
    return cast(dict[str, JsonValue], value)


def _resolve_limit(
    fleet: dict[str, JsonValue],
    environment: str,
    server_id: str,
    allow_environment_wide: bool,
) -> tuple[str, str | None, bool]:
    servers = fleet.get("servers")
    if not isinstance(servers, list):
        raise ContractError("fleet inventory must contain servers")
    if server_id:
        if not _SERVER_ID.fullmatch(server_id):
            raise ContractError("invalid server-id")
        matches = [
            server
            for server in servers
            if isinstance(server, dict) and server.get("id") == server_id
        ]
        if len(matches) != 1:
            raise AuthorizationError("server-id is not uniquely registered in fleet inventory")
        if matches[0].get("environment") != environment:
            raise AuthorizationError("server-id does not belong to the selected environment")
        if matches[0].get("lifecycle", "managed") == "adopted":
            raise AuthorizationError(
                "adopted servers are outside the normal host-configuration plane"
            )
        return server_id, server_id, False
    if not allow_environment_wide:
        raise AuthorizationError(
            "environment-wide configuration requires explicit allow-environment-wide"
        )
    adopted = [
        str(server.get("id"))
        for server in servers
        if isinstance(server, dict)
        and server.get("environment") == environment
        and server.get("lifecycle", "managed") == "adopted"
    ]
    if adopted:
        raise AuthorizationError(
            "environment-wide configuration cannot include adopted servers: "
            + ", ".join(sorted(adopted))
        )
    return environment, None, True


def build_configuration_plan(
    *,
    repository_root: Path,
    repository_revision: str,
    fleet_path: Path,
    playbook_path: Path,
    inventory_path: Path,
    environment: str,
    server_id: str = "",
    allow_environment_wide: bool = False,
) -> dict[str, JsonValue]:
    root = repository_root.resolve()
    if not _FULL_SHA.fullmatch(repository_revision):
        raise ContractError("repository revision must be a full lowercase Git SHA")
    if not _ENVIRONMENT.fullmatch(environment):
        raise ContractError("invalid configuration environment")

    fleet_file = _confined_file(root, fleet_path)
    playbook_file = _confined_file(root, playbook_path)
    inventory_file = _confined_file(root, inventory_path)
    fleet = _fleet_document(fleet_file)
    limit, resolved_server_id, environment_wide = _resolve_limit(
        fleet,
        environment,
        server_id,
        allow_environment_wide,
    )

    document: dict[str, JsonValue] = {
        "format": "l9.configuration-plan/v1",
        "repository_revision": repository_revision,
        "environment": environment,
        "target": {
            "limit": limit,
            "server_id": resolved_server_id,
            "environment_wide": environment_wide,
        },
        "fleet": {
            "path": _relative(root, fleet_file),
            "digest": file_sha256(fleet_file),
        },
        "playbook": {
            "path": _relative(root, playbook_file),
            "digest": file_sha256(playbook_file),
        },
        "inventory": {
            "path": _relative(root, inventory_file),
            "digest": file_sha256(inventory_file),
        },
    }
    document["plan_digest"] = sha256_digest(document)
    return document
