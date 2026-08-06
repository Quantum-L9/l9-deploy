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

from typing import Any

from ..errors import ContractError


def parse_repository_dispatch(event: dict[str, Any]) -> dict[str, Any]:
    action = event.get("action")
    if action not in (None, "l9.release.requested.v1"):
        raise ContractError(f"unexpected repository_dispatch action: {action!r}")
    payload = event.get("client_payload", event)
    if not isinstance(payload, dict):
        raise ContractError("repository_dispatch client_payload must be an object")
    return payload
