"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [execution]
tags: [L9_CONTRACT, compose, typed-profile]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import JsonValue

from ..contracts.models import DeploymentProfile
from ..errors import ContractError


def render_compose(profile: DeploymentProfile, image_ref: str, environment: str) -> str:
    runtime = profile.runtime
    project = profile.project.id
    service: dict[str, JsonValue] = {
        "image": "${L9_IMAGE_REF:?L9_IMAGE_REF is required}",
        "restart": "unless-stopped",
        "stop_grace_period": f"{runtime.stop_grace_seconds}s",
        "security_opt": ["no-new-privileges:true"],
    }
    if runtime.command:
        service["command"] = list(runtime.command)
    if runtime.read_only_root_filesystem:
        service["read_only"] = True
    if runtime.environment:
        service["environment"] = runtime.environment
    service["env_file"] = [f"/srv/l9/projects/{project}/{environment}/runtime.env"]
    if runtime.container_port:
        service["expose"] = [runtime.container_port]
    volumes: list[str] = []
    for item in runtime.volumes:
        suffix = ":ro" if item.read_only else ""
        volumes.append(f"{item.source}:{item.target}{suffix}")
    for item in profile.storage.persistent_volumes:
        volumes.append(f"/srv/l9/data/{project}/{item.name}:{item.mount_path}")
    if volumes:
        service["volumes"] = volumes
    document: dict[str, JsonValue] = {
        "name": project,
        "services": {"app": service},
        "networks": {"default": {"name": "l9-runtime", "external": True}},
    }
    rendered = yaml.safe_dump(document, sort_keys=False)
    if "/var/run/docker.sock" in rendered:
        raise ContractError("Docker socket mounts are prohibited")
    return rendered


def compose_path(project_id: str, environment: str) -> Path:
    return Path(f"/srv/l9/projects/{project_id}/{environment}/compose.yaml")
