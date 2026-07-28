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

from pydantic import JsonValue

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from ..contracts.models import HealthProbe, ReleaseState
from ..errors import ExecutionError
from .health import run_probe
from .promotion import write_runtime_state
from .releases import validate_release_runtime_env_path


class Executor(Protocol):
    def run(self, command: Sequence[str], **kwargs: object) -> object: ...
    def write_text(self, path: Path, text: str, mode: int = 0o600) -> None: ...


def rollback_release(
    executor: Executor,
    project_id: str,
    environment: str,
    previous_release: ReleaseState | None,
    failed_release: ReleaseState | None = None,
    *,
    health_probe: HealthProbe,
    base_url: str | None = None,
    publish_state: bool = True,
) -> dict[str, JsonValue]:
    if previous_release is None:
        raise ExecutionError("previous release is unavailable; automatic rollback is blocked")
    runtime_env = validate_release_runtime_env_path(
        previous_release, project_id, environment
    )
    if runtime_env is None:
        raise ExecutionError(
            "previous release lacks runtime configuration identity; automatic rollback is blocked"
        )
    image_ref = previous_release.image_ref
    compose = f"/srv/l9/projects/{project_id}/{environment}/compose.yaml"
    executor.run(["docker", "pull", image_ref], timeout=600)
    executor.run(
        [
            "docker",
            "compose",
            "--env-file",
            str(runtime_env),
            "-f",
            compose,
            "up",
            "-d",
            "--remove-orphans",
        ],
        env={
            "L9_IMAGE_REF": image_ref,
            "L9_RUNTIME_ENV_FILE": str(runtime_env),
        },
        timeout=600,
    )
    health = run_probe(health_probe, executor=executor, base_url=base_url)
    result: dict[str, JsonValue] = {
        "status": "PASS",
        "restored_image_ref": image_ref,
        "restored_runtime_env_path": str(runtime_env),
        "health": health,
    }
    if publish_state:
        state_result = write_runtime_state(
            executor,
            project_id,
            environment,
            current=previous_release,
            previous=failed_release,
        )
        result["restored_state_digest"] = state_result["state_digest"]
    return result
