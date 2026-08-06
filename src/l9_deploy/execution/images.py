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

import re
from collections.abc import Sequence
from typing import Protocol

from ..errors import ContractError, ExecutionError

IMAGE_REF = re.compile(r"^ghcr\.io/[a-z0-9._-]+/[a-z0-9._/-]+@sha256:[a-f0-9]{64}$")


class Executor(Protocol):
    def run(self, command: Sequence[str], **kwargs: object) -> object: ...


def require_digest_ref(image_ref: str) -> None:
    if not IMAGE_REF.fullmatch(image_ref):
        raise ContractError(f"image reference must be an exact GHCR digest: {image_ref}")


def pull_image(executor: Executor, image_ref: str, timeout: int = 600) -> None:
    require_digest_ref(image_ref)
    executor.run(["docker", "pull", image_ref], timeout=timeout)


def inspect_repo_digest(executor: Executor, image_ref: str) -> str:
    require_digest_ref(image_ref)
    result = executor.run(
        ["docker", "image", "inspect", image_ref, "--format", '{{join .RepoDigests "\\n"}}']
    )
    stdout = getattr(result, "stdout", "")
    if image_ref not in stdout.splitlines():
        raise ExecutionError("pulled image does not expose the requested repository digest")
    return image_ref
