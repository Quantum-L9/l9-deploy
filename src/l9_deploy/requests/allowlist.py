"""--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [authorization]
tags: [L9_CONTRACT, allowlist]
owner: platform
status: active
--- /L9_META ---"""
from __future__ import annotations

from ..contracts.models import FleetInventory, FleetProject, ProjectEnvironment
from ..errors import AuthorizationError


def find_project(
    fleet: FleetInventory | dict[str, object], repository: str
) -> FleetProject:
    typed = fleet if isinstance(fleet, FleetInventory) else FleetInventory.model_validate(fleet)
    for project in typed.projects:
        if project.repository == repository:
            return project
    raise AuthorizationError(f"repository is not registered for deployment: {repository}")


def require_environment(
    project: FleetProject | dict[str, object], environment: str
) -> ProjectEnvironment:
    typed = project if isinstance(project, FleetProject) else FleetProject.model_validate(project)
    value = typed.environments.get(environment)
    if value is None:
        raise AuthorizationError(
            f"project {typed.id} is not authorized for environment {environment}"
        )
    return value
