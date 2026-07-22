"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [execution]
tags: [L9_CONTRACT, backup, typed-profile]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from pydantic import JsonValue

from ..canonical import sha256_digest
from ..contracts.models import DeploymentProfile
from ..errors import ExecutionError


class Executor(Protocol):
    def run(self, command: Sequence[str], **kwargs: object) -> object: ...


def create_backup(
    executor: Executor,
    profile: DeploymentProfile,
    project_id: str,
    environment: str,
    request_id: str,
) -> dict[str, JsonValue]:
    configuration = profile.backup
    if configuration is None:
        raise ExecutionError("backup is required but the deployment profile has no backup contract")
    substitutions = {"project": project_id, "environment": environment, "request_id": request_id}
    backup_command = [part.format_map(substitutions) for part in configuration.command]
    result = executor.run(backup_command, timeout=configuration.timeout_seconds)
    return {
        "created_at": datetime.now(UTC).isoformat(),
        "command_digest": sha256_digest(backup_command),
        "stdout_digest": sha256_digest(getattr(result, "stdout", "")),
    }


def verify_backup(executor: Executor, path: Path) -> dict[str, JsonValue]:
    result = executor.run(["test", "-s", str(path)], check=False)
    return {
        "status": "PASS" if getattr(result, "returncode", 1) == 0 else "FAIL",
        "path": str(path),
    }
