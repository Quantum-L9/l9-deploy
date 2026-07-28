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

from pathlib import Path

from ..subprocesses import CommandResult, run_command


def syntax_check(playbook: Path, inventory: Path) -> CommandResult:
    return run_command(["ansible-playbook", "-i", str(inventory), "--syntax-check", str(playbook)])


def check(
    playbook: Path, inventory: Path, limit: str | None = None, timeout: int = 1200
) -> CommandResult:
    command = ["ansible-playbook", "-i", str(inventory), "--check", "--diff", str(playbook)]
    if limit:
        command.extend(["--limit", limit])
    return run_command(command, timeout=timeout)


def apply(
    playbook: Path, inventory: Path, limit: str | None = None, timeout: int = 1800
) -> CommandResult:
    command = ["ansible-playbook", "-i", str(inventory), str(playbook)]
    if limit:
        command.extend(["--limit", limit])
    return run_command(command, timeout=timeout)
