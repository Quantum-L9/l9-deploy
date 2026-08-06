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

import json
import os
import re
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from ..errors import ExecutionError
from ..subprocesses import run_command

ENV_KEY_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@contextmanager
def rendered_environment(
    project: str,
    environment: str,
    secret_path: str = "/",  # noqa: S107
) -> Iterator[Path]:
    result = run_command(
        [
            "infisical",
            "export",
            "--format=json",
            "--projectId",
            project,
            "--env",
            environment,
            "--path",
            secret_path,
        ],
        timeout=120,
    )
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ExecutionError("Infisical export returned invalid JSON") from exc
    if not isinstance(value, list):
        raise ExecutionError("Infisical export did not return a secret list")
    fd, raw_path = tempfile.mkstemp(prefix="l9-runtime-", suffix=".env")
    path = Path(raw_path)
    try:
        seen: set[str] = set()
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            for item in value:
                if not isinstance(item, dict):
                    raise ExecutionError("Infisical secret entry must be an object")
                key = item.get("secretKey")
                secret = item.get("secretValue")
                if not isinstance(key, str) or ENV_KEY_PATTERN.fullmatch(key) is None:
                    raise ExecutionError("Infisical secret key is not a valid environment name")
                if key in seen:
                    raise ExecutionError("Infisical export contains a duplicate secret key")
                if not isinstance(secret, str) or any(char in secret for char in "\r\n\x00"):
                    raise ExecutionError("Infisical secret cannot be rendered safely")
                seen.add(key)
                handle.write(f"{key}={secret}\n")
        path.chmod(0o600)
        yield path
    finally:
        path.unlink(missing_ok=True)
