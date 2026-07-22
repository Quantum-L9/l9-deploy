"""--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [inventory]
tags: [L9_CONTRACT, target-resolution]
owner: platform
status: active
--- /L9_META ---"""
from __future__ import annotations

from ..contracts.models import FleetInventory, FleetProject, ResolvedTarget
from ..errors import ContractError


def resolve_target(
    fleet: FleetInventory | dict[str, object],
    project: FleetProject | dict[str, object],
    environment: str,
) -> ResolvedTarget:
    typed_fleet = (
        fleet if isinstance(fleet, FleetInventory) else FleetInventory.model_validate(fleet)
    )
    typed_project = (
        project if isinstance(project, FleetProject) else FleetProject.model_validate(project)
    )
    registration = typed_project.environments[environment]
    server_by_id = {server.id: server for server in typed_fleet.servers}
    missing = [server_id for server_id in registration.server_ids if server_id not in server_by_id]
    if missing:
        raise ContractError(f"fleet project references unknown servers: {', '.join(missing)}")
    servers = tuple(server_by_id[server_id] for server_id in sorted(registration.server_ids))
    wrong_environment = [server.id for server in servers if server.environment != environment]
    if wrong_environment:
        raise ContractError(
            "project target server environment mismatch: " + ", ".join(wrong_environment)
        )
    return ResolvedTarget(project_id=typed_project.id, environment=environment, servers=servers)
