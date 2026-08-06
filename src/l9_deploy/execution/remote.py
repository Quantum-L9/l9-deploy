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
import shlex
import tempfile
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
        input_text: str | None = None,
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
            input_text=input_text,
            check=check,
        )

    def write_text(self, path: Path, text: str, mode: int = 0o600) -> None:
        parent = shlex.quote(str(path.parent))
        target = shlex.quote(str(path))
        command = (
            f"set -euo pipefail; mkdir -p {parent}; "
            f"tmp=$(mktemp {parent}/.l9-write.XXXXXX); "
            f'trap \'rm -f -- "$tmp"\' EXIT; cat > "$tmp"; '
            f'chmod {mode:o} "$tmp"; mv -f -- "$tmp" {target}; trap - EXIT'
        )
        self.run(["bash", "-lc", command], input_text=text)


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
        input_text: str | None = None,
        check: bool = True,
    ) -> CommandResult:
        return run_command(
            command,
            cwd=self.root,
            timeout=timeout or self.timeout,
            env=env,
            input_text=input_text,
            check=check,
        )

    def write_text(self, path: Path, text: str, mode: int = 0o600) -> None:
        root = self.root.resolve()
        relative = path.relative_to("/") if path.is_absolute() else path
        target = (root / relative).resolve()
        if target != root and root not in target.parents:
            raise ValueError("local executor write path escapes its root")
        target.parent.mkdir(parents=True, exist_ok=True)
        descriptor, raw_temporary = tempfile.mkstemp(
            prefix=".l9-write.",
            dir=target.parent,
            text=True,
        )
        temporary = Path(raw_temporary)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
                handle.write(text)
            temporary.chmod(mode)
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
