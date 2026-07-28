"""--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [planning]
tags: [L9_CONTRACT, backup]
owner: platform
status: active
--- /L9_META ---"""

from __future__ import annotations

from ..contracts.models import DeploymentProfile


def backup_required(profile: DeploymentProfile) -> bool:
    """Return whether deployment mutation requires a verified pre-deploy backup.

    Backup is mandatory when the migration policy says so or when any validated
    persistent volume declares the ``before_deploy`` policy. The function accepts
    the typed contract only, so configuration drift fails during model validation
    instead of being silently tolerated here.
    """

    if profile.migrations.enabled and profile.migrations.backup_required:
        return True
    return any(
        volume.backup_policy == "before_deploy" for volume in profile.storage.persistent_volumes
    )
