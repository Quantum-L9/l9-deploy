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


def generate_ansible_inventory(fleet: dict[str, Any], output: Path) -> dict[str, Any]:
    groups: dict[str, dict[str, Any]] = {}
    for server in fleet["servers"]:
        host_vars = {
            "ansible_host": server["private_ip"],
            "ansible_user": server["ssh"]["user"],
            "ansible_port": server["ssh"]["port"],
            "l9_server_id": server["id"],
            "l9_environment": server["environment"],
            "l9_roles": server["roles"],
        }
        for role in server["roles"]:
            groups.setdefault(role, {"hosts": {}})["hosts"][server["id"]] = host_vars
        groups.setdefault(server["environment"], {"hosts": {}})["hosts"][server["id"]] = host_vars
    inventory = {"all": {"children": groups}}
    atomic_write_text(output, yaml.safe_dump(inventory, sort_keys=True), mode=0o640)
    return inventory
