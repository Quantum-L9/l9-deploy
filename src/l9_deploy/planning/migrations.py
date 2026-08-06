"""--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [planning]
tags: [L9_CONTRACT, migration]
owner: platform
status: active
--- /L9_META ---"""

from __future__ import annotations

from ..contracts.models import DeploymentProfile, PlanStep


def migration_step(profile: DeploymentProfile) -> PlanStep | None:
    migrations = profile.migrations
    if not migrations.enabled:
        return None
    return PlanStep(
        id="migration",
        kind="migration",
        mutating=True,
        timeout_seconds=migrations.timeout_seconds,
        details={
            "command": list(migrations.command),
            "mode": migrations.mode,
            "use_release_image": migrations.use_release_image,
            "rollback_safe": migrations.rollback_safe,
        },
    )
