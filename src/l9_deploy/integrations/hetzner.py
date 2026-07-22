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

import json
from typing import Any

from ..subprocesses import run_command


def server(server_id: str) -> dict[str, Any]:
    result = run_command(["hcloud", "server", "describe", server_id, "-o", "json"], timeout=60)
    value = json.loads(result.stdout)
    if not isinstance(value, dict):
        raise ValueError("hcloud returned an invalid server document")
    return value
