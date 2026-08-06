"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [execution]
tags: [L9_CONTRACT, rollback, convergence]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from pydantic import JsonValue

from ..contracts.models import ReleaseState
from ..errors import ExecutionError
from .promotion import write_runtime_state


class Executor(Protocol):
    def run(self, command: Sequence[str], **kwargs: object) -> object: ...
    def write_text(self, path: Path, text: str, mode: int = 0o600) -> None: ...


def rollback_release(
    executor: Executor,
    project_id: str,
    environment: str,
    previous_release: ReleaseState | None,
    failed_release: ReleaseState | None = None,
) -> dict[str, JsonValue]:
    if previous_release is None:
        raise ExecutionError("previous release is unavailable; automatic rollback is blocked")
    image_ref = previous_release.image_ref
    compose = f"/srv/l9/projects/{project_id}/{environment}/compose.yaml"
    executor.run(["docker", "pull", image_ref], timeout=600)
    executor.run(
        ["docker", "compose", "-f", compose, "up", "-d", "--remove-orphans"],
        env={"L9_IMAGE_REF": image_ref},
        timeout=600,
    )
    state_result = write_runtime_state(
        executor,
        project_id,
        environment,
        current=previous_release,
        previous=failed_release,
    )
    return {
        "status": "PASS",
        "restored_image_ref": image_ref,
        "restored_state_digest": state_result["state_digest"],
    }
