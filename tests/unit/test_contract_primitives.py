"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, unit]
tags: [L9_TEST, canonical-digest, rollback-policy]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from l9_deploy.contracts.models import DeploymentProfile
from l9_deploy.evidence.digests import file_sha256, sha256_digest
from l9_deploy.planning.rollback import rollback_allowed


def test_digest_exports_produce_canonical_values(tmp_path: Path) -> None:
    artifact = tmp_path / "artifact.txt"
    artifact.write_text("frontier-release\n", encoding="utf-8")

    assert sha256_digest({"b": 2, "a": 1}) == sha256_digest({"a": 1, "b": 2})
    assert file_sha256(artifact).startswith("sha256:")
    assert len(file_sha256(artifact)) == len("sha256:") + 64


def test_rollback_policy_is_read_from_validated_profile(profile: dict[str, Any]) -> None:
    enabled = DeploymentProfile.model_validate(profile)
    assert rollback_allowed(enabled) is True

    disabled_wire = deepcopy(profile)
    disabled_wire["release"]["automatic_rollback"] = False
    disabled = DeploymentProfile.model_validate(disabled_wire)
    assert rollback_allowed(disabled) is False


def test_backup_policy_uses_typed_storage_contract(profile: dict[str, Any]) -> None:
    from l9_deploy.planning.backups import backup_required

    migration_required = DeploymentProfile.model_validate(profile)
    assert backup_required(migration_required) is True

    volume_wire = deepcopy(profile)
    volume_wire["migrations"]["backup_required"] = False
    volume_wire["storage"] = {
        "persistent_volumes": [
            {
                "name": "application-data",
                "mount_path": "/srv/application/data",
                "backup_policy": "before_deploy",
            }
        ]
    }
    volume_required = DeploymentProfile.model_validate(volume_wire)
    assert backup_required(volume_required) is True

    no_backup_wire = deepcopy(volume_wire)
    no_backup_wire["storage"]["persistent_volumes"][0]["backup_policy"] = "daily"
    no_backup = DeploymentProfile.model_validate(no_backup_wire)
    assert backup_required(no_backup) is False
