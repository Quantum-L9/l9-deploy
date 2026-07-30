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
from ..contracts.models import BackupConfig, DeploymentProfile
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


def verify_backup_command(
    executor: Executor,
    configuration: BackupConfig,
    project_id: str,
    environment: str,
    request_id: str,
) -> dict[str, JsonValue]:
    """Run the profile-declared backup ``verify_command`` after a pre-deploy backup.

    The deployment-profile schema requires ``verify_command`` and consumer
    profiles populate it, yet the deploy transaction created the backup and
    recorded ``PASS`` without ever confirming the artifact. This closes that
    producer→consumer gap so ``backup_required`` truly yields the *verified*
    pre-deploy backup its contract promises. A profile that declares no
    ``verify_command`` (an empty tuple) is reported ``SKIPPED`` so behaviour is
    unchanged for such profiles.
    """
    if not configuration.verify_command:
        return {"status": "SKIPPED", "reason": "profile declares no backup verify_command"}
    substitutions = {"project": project_id, "environment": environment, "request_id": request_id}
    command = [part.format_map(substitutions) for part in configuration.verify_command]
    result = executor.run(command, timeout=configuration.timeout_seconds, check=False)
    return {
        "status": "PASS" if getattr(result, "returncode", 1) == 0 else "FAIL",
        "command_digest": sha256_digest(command),
    }
