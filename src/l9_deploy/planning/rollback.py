"""--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [planning]
tags: [L9_CONTRACT, rollback]
owner: platform
status: active
--- /L9_META ---"""
from __future__ import annotations

from ..contracts.models import DeploymentProfile


def rollback_allowed(profile: DeploymentProfile) -> bool:
    return profile.release.automatic_rollback
