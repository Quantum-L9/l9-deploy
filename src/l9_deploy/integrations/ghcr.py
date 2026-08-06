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

from ..execution.images import require_digest_ref
from ..subprocesses import run_command


def verify_remote_manifest(image_ref: str, timeout: int = 120) -> dict[str, str]:
    require_digest_ref(image_ref)
    result = run_command(["docker", "buildx", "imagetools", "inspect", image_ref], timeout=timeout)
    return {"status": "PASS", "image_ref": image_ref, "output": result.stdout}
