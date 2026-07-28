"""--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [planning]
tags: [L9_CONTRACT, topology]
owner: platform
status: active
--- /L9_META ---"""

from __future__ import annotations

from ..contracts.models import ServerProfile


def target_server_ids(servers: tuple[ServerProfile, ...]) -> tuple[str, ...]:
    return tuple(sorted(server.id for server in servers))
