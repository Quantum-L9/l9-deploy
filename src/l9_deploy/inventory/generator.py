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

from pathlib import Path
from typing import Any

import yaml

from ..canonical import atomic_write_text
from ..errors import ContractError
from ..requests.verifier import resolve_registered_profile

_HOSTNAME_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789-")


def _is_valid_public_hostname(hostname: str) -> bool:
    if not 1 <= len(hostname) <= 253 or hostname != hostname.lower():
        return False
    labels = hostname.split(".")
    if len(labels) < 2:
        return False
    for label in labels:
        if not 1 <= len(label) <= 63:
            return False
        if label[0] == "-" or label[-1] == "-":
            return False
        if any(character not in _HOSTNAME_CHARS for character in label):
            return False
    return True


def _server_connection_address(server: dict[str, Any]) -> str:
    lifecycle = str(server.get("lifecycle", "managed"))
    field = "public_ip" if lifecycle == "adopted" else "private_ip"
    address = server.get(field)
    if not isinstance(address, str) or not address:
        raise ContractError(f"server {server.get('id', '<unknown>')} lacks {field}")
    return address


def _load_profile(profile_root: Path | None, project: dict[str, Any]) -> dict[str, Any] | None:
    """Return the consumer profile bound for ``project``, or ``None`` when none is bound.

    Profiles are consumer-owned source. They are read only from an explicit
    profile root the caller materialized from the consumer repository at an
    exact commit, laid out as ``<profile_root>/<project id>/<registered path>``,
    and never from this checkout. An absent binding is reported to the caller,
    which decides whether the affected configuration is blocked.
    """
    if profile_root is None:
        return None
    try:
        path = resolve_registered_profile(
            profile_root / str(project["id"]), str(project["profile_path"])
        )
    except ContractError:
        return None
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ContractError(f"deployment profile must be an object: {project['id']}")
    return value


def _caddy_sites_by_server(
    fleet: dict[str, Any], profile_root: Path | None
) -> tuple[dict[str, list[dict[str, str]]], list[dict[str, str]]]:
    sites: dict[str, list[dict[str, str]]] = {}
    blocked: list[dict[str, str]] = []
    seen: dict[str, set[str]] = {}
    server_by_id = {str(server["id"]): server for server in fleet["servers"]}
    for project in sorted(fleet["projects"], key=lambda item: item["id"]):
        public_environments = [
            (environment, config)
            for environment, config in sorted(project["environments"].items())
            if config.get("public_hostnames")
        ]
        if not public_environments:
            continue

        profile = _load_profile(profile_root, project)
        if profile is None:
            # Without the consumer's source-bound profile there is no port, TLS
            # mode or hostname set to project. Adopted hosts receive no generated
            # edge configuration, so the binding is recorded as blocked and the
            # rest of the fleet still renders. A managed host would have its
            # Caddy sites rewritten without this project's entry, so that
            # configuration is refused rather than silently dropped.
            for environment, config in public_environments:
                for server_id in sorted(config["server_ids"]):
                    server = server_by_id.get(server_id)
                    if server is None:
                        raise ContractError(f"fleet project references unknown server: {server_id}")
                    if server.get("lifecycle", "managed") != "adopted":
                        raise ContractError(
                            "public ingress on a managed server requires the consumer's "
                            f"source-bound deployment profile: {project['id']}:{environment} "
                            f"on {server_id}"
                        )
                blocked.append(
                    {
                        "environment": environment,
                        "project_id": project["id"],
                        "reason": "consumer deployment profile is not bound",
                    }
                )
            continue
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
                if not _is_valid_public_hostname(hostname):
                    raise ContractError(f"invalid public hostname: {hostname}")
                for server_id in sorted(config["server_ids"]):
                    server = server_by_id.get(server_id)
                    if server is None:
                        raise ContractError(f"fleet project references unknown server: {server_id}")
                    claimed = seen.setdefault(server_id, set())
                    if hostname in claimed:
                        raise ContractError(
                            f"duplicate public hostname on server {server_id}: {hostname}"
                        )
                    claimed.add(hostname)
                    # Adopted hosts keep their existing edge configuration outside the
                    # normal l9-deploy Ansible ownership plane. The hostname remains a
                    # deployment/health contract, but no Caddy mutation is generated.
                    if server.get("lifecycle", "managed") == "adopted":
                        continue
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
    return sites, blocked


def generate_ansible_inventory(
    fleet: dict[str, Any],
    output: Path,
    profile_root: Path | None = None,
) -> dict[str, Any]:
    caddy_sites, blocked_ingress = _caddy_sites_by_server(fleet, profile_root)
    groups: dict[str, dict[str, Any]] = {}
    for server in fleet["servers"]:
        host_vars = {
            "ansible_host": _server_connection_address(server),
            "ansible_user": server["ssh"]["user"],
            "ansible_port": server["ssh"]["port"],
            "l9_server_id": server["id"],
            "l9_environment": server["environment"],
            "l9_lifecycle": server.get("lifecycle", "managed"),
            "l9_roles": server["roles"],
            "l9_caddy_sites": caddy_sites.get(server["id"], []),
        }
        for role in server["roles"]:
            groups.setdefault(role, {"hosts": {}})["hosts"][server["id"]] = host_vars
        groups.setdefault(server["environment"], {"hosts": {}})["hosts"][server["id"]] = host_vars
    inventory: dict[str, Any] = {"all": {"children": groups}}
    if blocked_ingress:
        inventory["all"]["vars"] = {"l9_public_ingress_blocked": blocked_ingress}
    atomic_write_text(output, yaml.safe_dump(inventory, sort_keys=True), mode=0o640)
    return inventory
