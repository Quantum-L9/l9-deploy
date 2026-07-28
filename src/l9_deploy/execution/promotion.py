"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [execution]
tags: [L9_CONTRACT, runtime-state]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from ..canonical import sha256_digest
from ..contracts.models import ReleaseState


class Executor(Protocol):
    def run(self, command: Sequence[str], **kwargs: object) -> object: ...
    def write_text(self, path: Path, text: str, mode: int = 0o600) -> None: ...


def state_path(project_id: str, environment: str) -> Path:
    return Path(f"/srv/l9/projects/{project_id}/{environment}/state.json")


def write_runtime_state(
    executor: Executor,
    project_id: str,
    environment: str,
    current: ReleaseState,
    previous: ReleaseState | None,
) -> dict[str, object]:
    path = state_path(project_id, environment)
    state: dict[str, object] = {
        "schema": "l9.runtime-state/v1",
        "current": current.model_dump(mode="json", by_alias=True),
        "previous": previous.model_dump(mode="json", by_alias=True) if previous else None,
        "promoted_at": datetime.now(UTC).isoformat(),
    }
    executor.write_text(path, json.dumps(state, indent=2, sort_keys=True) + "\n", mode=0o600)
    return {"status": "PASS", "state_path": str(path), "state_digest": sha256_digest(state)}


def promote(
    executor: Executor,
    project_id: str,
    environment: str,
    release: ReleaseState,
    previous_release: ReleaseState | None = None,
) -> dict[str, object]:
    return write_runtime_state(
        executor,
        project_id,
        environment,
        current=release,
        previous=previous_release,
    )
