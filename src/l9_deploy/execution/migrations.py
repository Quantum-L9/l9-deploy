"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [execution]
tags: [L9_CONTRACT, migration, typed-profile]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Protocol

from pydantic import JsonValue

from ..canonical import sha256_digest
from ..contracts.models import DeploymentProfile


class Executor(Protocol):
    def run(self, command: Sequence[str], **kwargs: object) -> object: ...


def execute_migration(
    executor: Executor,
    profile: DeploymentProfile,
    image_ref: str,
    env_file: str,
) -> dict[str, JsonValue]:
    configuration = profile.migrations
    docker_command = [
        "docker",
        "run",
        "--rm",
        "--network",
        "l9-runtime",
        "--env-file",
        env_file,
        image_ref,
        *configuration.command,
    ]
    result = executor.run(docker_command, timeout=configuration.timeout_seconds)
    return {
        "completed_at": datetime.now(UTC).isoformat(),
        "command_digest": sha256_digest(docker_command),
        "stdout_digest": sha256_digest(getattr(result, "stdout", "")),
        "rollback_safe": configuration.rollback_safe,
    }
