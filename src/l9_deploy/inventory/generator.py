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
from typing import Any

import yaml

from ..canonical import atomic_write_text
from ..errors import ContractError

_HOSTNAME = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
)


def _load_profile(root: Path, profile_path: str) -> dict[str, Any]:
    candidate = (root / profile_path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ContractError(f"deployment profile escapes repository root: {profile_path}")
    if not candidate.is_file():
        raise ContractError(f"deployment profile is missing: {profile_path}")
    value = yaml.safe_load(candidate.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError(f"deployment profile must be an object: {profile_path}")
    return value


def _caddy_sites_by_server(
    fleet: dict[str, Any], repository_root: Path
) -> dict[str, list[dict[str, str]]]:
    sites: dict[str, list[dict[str, str]]] = {}
    seen: dict[str, set[str]] = {}
    for project in sorted(fleet["projects"], key=lambda item: item["id"]):
        public_environments = [
            (environment, config)
            for environment, config in sorted(project["environments"].items())
            if config.get("public_hostnames")
        ]
        if not public_environments:
            continue

        profile = _load_profile(repository_root, project["profile_path"])
        runtime = profile.get("runtime")
        network = profile.get("network")
        if not isinstance(runtime, dict) or not isinstance(network, dict):
            raise ContractError(f"deployment profile is missing runtime/network: {project['id']}")
        ingress = network.get("public_ingress")
        if not isinstance(ingress, dict):
            raise ContractError(f"deployment profile is missing public ingress: {project['id']}")
        profile_hostnames = tuple(str(item) for item in ingress.get("hostnames", []))
        profile_hostname_set = set(profile_hostnames)
        container_port = runtime.get("container_port")

        for environment, config in public_environments:
            coordinate = f"{project['id']}:{environment}"
            hostnames = tuple(str(item) for item in config["public_hostnames"])
            if not ingress.get("enabled"):
                raise ContractError(
                    f"fleet exposes public hostnames for disabled ingress: {coordinate}"
                )
            if ingress.get("tls") != "automatic":
                raise ContractError(
                    f"fleet-managed Caddy ingress requires tls=automatic: {coordinate}"
                )
            if not set(hostnames).issubset(profile_hostname_set):
                raise ContractError(
                    f"fleet public hostnames drift from deployment profile: {coordinate}"
                )
            if not isinstance(container_port, int) or not 1 <= container_port <= 65535:
                raise ContractError(f"public ingress requires a valid container port: {coordinate}")
            for hostname in hostnames:
                if not _HOSTNAME.fullmatch(hostname):
                    raise ContractError(f"invalid public hostname: {hostname}")
                for server_id in sorted(config["server_ids"]):
                    claimed = seen.setdefault(server_id, set())
                    if hostname in claimed:
                        raise ContractError(
                            f"duplicate public hostname on server {server_id}: {hostname}"
                        )
                    claimed.add(hostname)
                    sites.setdefault(server_id, []).append(
                        {
                            "environment": environment,
                            "hostname": hostname,
                            "project_id": project["id"],
                            "upstream": f"127.0.0.1:{container_port}",
                        }
                    )
    for entries in sites.values():
        entries.sort(key=lambda item: (item["hostname"], item["project_id"], item["environment"]))
    return sites


def generate_ansible_inventory(
    fleet: dict[str, Any],
    output: Path,
    repository_root: Path | None = None,
) -> dict[str, Any]:
    root = (repository_root or Path.cwd()).resolve()
    caddy_sites = _caddy_sites_by_server(fleet, root)
    groups: dict[str, dict[str, Any]] = {}
    for server in fleet["servers"]:
        host_vars = {
            "ansible_host": server["private_ip"],
            "ansible_user": server["ssh"]["user"],
            "ansible_port": server["ssh"]["port"],
            "l9_server_id": server["id"],
            "l9_environment": server["environment"],
            "l9_roles": server["roles"],
            "l9_caddy_sites": caddy_sites.get(server["id"], []),
        }
        for role in server["roles"]:
            groups.setdefault(role, {"hosts": {}})["hosts"][server["id"]] = host_vars
        groups.setdefault(server["environment"], {"hosts": {}})["hosts"][server["id"]] = host_vars
    inventory = {"all": {"children": groups}}
    atomic_write_text(output, yaml.safe_dump(inventory, sort_keys=True), mode=0o640)
    return inventory
