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

import fcntl
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from ..errors import ExecutionError


@contextmanager
def environment_lock(lock_root: Path, environment: str, blocking: bool = False) -> Iterator[None]:
    lock_root.mkdir(parents=True, exist_ok=True)
    lock_path = lock_root / f"{environment}.lock"
    with lock_path.open("a+", encoding="utf-8") as handle:
        operation = fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB)
        try:
            fcntl.flock(handle.fileno(), operation)
        except BlockingIOError as exc:
            raise ExecutionError(f"deployment lock is already held for {environment}") from exc
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
