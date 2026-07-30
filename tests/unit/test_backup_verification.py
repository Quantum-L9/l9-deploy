"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, unit]
tags: [L9_TEST, backup, verify-command]
owner: platform
--- /L9_META ---
"""

from __future__ import annotations

from typing import Any

from l9_deploy.contracts.models import BackupConfig
from l9_deploy.execution.backups import verify_backup_command
from l9_deploy.subprocesses import CommandResult


class RecordingExecutor:
    def __init__(self, returncode: int = 0) -> None:
        self.returncode = returncode
        self.commands: list[list[str]] = []

    def run(self, command, **kwargs: Any) -> CommandResult:  # type: ignore[no-untyped-def]
        command_list = list(command)
        self.commands.append(command_list)
        return CommandResult(tuple(command_list), self.returncode, "", "")


def test_verify_backup_command_runs_declared_command_and_reports_pass() -> None:
    config = BackupConfig(
        command=("backup", "{project}"),
        verify_command=("verify", "{project}", "{environment}"),
        restore_test_command=("restore",),
        timeout_seconds=60,
    )
    executor = RecordingExecutor(returncode=0)

    result = verify_backup_command(executor, config, "seo-bot", "production", "req-1")

    assert executor.commands == [["verify", "seo-bot", "production"]]
    assert result["status"] == "PASS"
    assert "command_digest" in result


def test_verify_backup_command_reports_fail_on_nonzero_return() -> None:
    config = BackupConfig(
        command=("backup",),
        verify_command=("verify",),
        restore_test_command=("restore",),
        timeout_seconds=60,
    )
    executor = RecordingExecutor(returncode=2)

    result = verify_backup_command(executor, config, "seo-bot", "production", "req-1")

    assert result["status"] == "FAIL"


def test_verify_backup_command_skips_when_no_verify_command_declared() -> None:
    config = BackupConfig(
        command=("backup",),
        verify_command=(),
        restore_test_command=("restore",),
        timeout_seconds=60,
    )
    executor = RecordingExecutor(returncode=0)

    result = verify_backup_command(executor, config, "seo-bot", "production", "req-1")

    assert executor.commands == []
    assert result["status"] == "SKIPPED"
