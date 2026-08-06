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

import os
import signal
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from .errors import ExecutionError, OperationalLimitError
from .redaction import SECRET_KEY, redact_text


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str


def run_command(
    command: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    timeout: int = 300,
    input_text: str | None = None,
    check: bool = True,
) -> CommandResult:
    if not command:
        raise ValueError("command must contain at least one argument")
    if timeout < 1:
        raise ValueError("timeout must be at least one second")
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    process = subprocess.Popen(
        list(command),
        cwd=cwd,
        env=merged_env,
        text=True,
        stdin=subprocess.PIPE if input_text is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(input=input_text, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        os.killpg(process.pid, signal.SIGTERM)
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate(timeout=5)
        raise OperationalLimitError(f"command timed out after {timeout}s: {command[0]}") from exc
    explicit_secrets = (
        tuple(value for key, value in env.items() if SECRET_KEY.search(key) and value)
        if env
        else ()
    )
    result = CommandResult(
        tuple(command),
        process.returncode,
        redact_text(stdout, explicit_secrets),
        redact_text(stderr, explicit_secrets),
    )
    if check and result.returncode != 0:
        raise ExecutionError(
            f"command failed ({result.returncode}): {command[0]}: {result.stderr.strip()}"
        )
    return result
