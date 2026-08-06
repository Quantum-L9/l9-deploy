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
from typing import cast

import yaml
from pydantic import JsonValue

from ..contracts.models import DeploymentProfile
from ..errors import ContractError


def render_compose(
    profile: DeploymentProfile,
    image_ref: str,
    environment: str,
    runtime_env_path: str,
) -> str:
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
        service["environment"] = cast(JsonValue, runtime.environment)
    if not runtime_env_path.startswith(
        f"/srv/l9/projects/{project}/{environment}/releases/"
    ) or not runtime_env_path.endswith("/runtime.env"):
        raise ContractError("Compose runtime environment must be release-owned")
    service["env_file"] = ["${L9_RUNTIME_ENV_FILE:?L9_RUNTIME_ENV_FILE is required}"]
    if runtime.container_port:
        service["expose"] = [runtime.container_port]
    volumes: list[JsonValue] = []
    for item in runtime.volumes:
        suffix = ":ro" if item.read_only else ""
        volumes.append(f"{item.source}:{item.target}{suffix}")
    for volume in profile.storage.persistent_volumes:
        volumes.append(f"/srv/l9/data/{project}/{volume.name}:{volume.mount_path}")
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
