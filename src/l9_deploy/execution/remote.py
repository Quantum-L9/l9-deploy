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

import base64
import shlex
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from ..subprocesses import CommandResult, run_command


@dataclass(frozen=True)
class Host:
    server_id: str
    address: str
    user: str
    port: int = 22


class RemoteExecutor:
    def __init__(self, host: Host, timeout: int = 300) -> None:
        self.host = host
        self.timeout = timeout

    def run(
        self,
        command: Sequence[str],
        *,
        timeout: int | None = None,
        env: Mapping[str, str] | None = None,
        check: bool = True,
    ) -> CommandResult:
        exports = ""
        if env:
            exports = (
                "export "
                + " ".join(f"{key}={shlex.quote(value)}" for key, value in sorted(env.items()))
                + "; "
            )
        remote = exports + shlex.join(command)
        return run_command(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                "StrictHostKeyChecking=yes",
                "-p",
                str(self.host.port),
                f"{self.host.user}@{self.host.address}",
                remote,
            ],
            timeout=timeout or self.timeout,
            check=check,
        )

    def write_text(self, path: Path, text: str, mode: int = 0o600) -> None:
        encoded = base64.b64encode(text.encode()).decode()
        parent = shlex.quote(str(path.parent))
        target = shlex.quote(str(path))
        command = (
            f"set -euo pipefail; mkdir -p {parent}; "
            f"tmp=$(mktemp {parent}/.l9-write.XXXXXX); "
            f'printf %s {shlex.quote(encoded)} | base64 -d > "$tmp"; '
            f'chmod {mode:o} "$tmp"; mv "$tmp" {target}'
        )
        self.run(["bash", "-lc", command])


class LocalExecutor:
    def __init__(self, root: Path, timeout: int = 300) -> None:
        self.root = root
        self.timeout = timeout
        self.root.mkdir(parents=True, exist_ok=True)

    def run(
        self,
        command: Sequence[str],
        *,
        timeout: int | None = None,
        env: Mapping[str, str] | None = None,
        check: bool = True,
    ) -> CommandResult:
        return run_command(
            command,
            cwd=self.root,
            timeout=timeout or self.timeout,
            env=env,
            check=check,
        )

    def write_text(self, path: Path, text: str, mode: int = 0o600) -> None:
        root = self.root.resolve()
        relative = path.relative_to("/") if path.is_absolute() else path
        target = (root / relative).resolve()
        if target != root and root not in target.parents:
            raise ValueError("local executor write path escapes its root")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        target.chmod(mode)
