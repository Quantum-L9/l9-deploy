"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer:
- tests
tags:
- L9_META
- deployment-platform
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import pytest
import yaml

from l9_deploy.contracts.models import DeploymentProfile
from l9_deploy.errors import ContractError
from l9_deploy.execution.compose import render_compose
from l9_deploy.execution.images import require_digest_ref


def test_compose_uses_runtime_digest_variable(profile) -> None:  # type: ignore[no-untyped-def]
    image = "ghcr.io/quantum-l9/seo-bot@sha256:" + "a" * 64
    typed_profile = DeploymentProfile.model_validate(profile)
    runtime_env = (
        "/srv/l9/projects/seo-bot/staging/releases/" + "b" * 64 + "/runtime.env"
    )
    document = yaml.safe_load(
        render_compose(typed_profile, image, "staging", runtime_env)
    )
    assert document["services"]["app"]["image"].startswith("${L9_IMAGE_REF:")
    assert document["services"]["app"]["env_file"] == [
        "${L9_RUNTIME_ENV_FILE:?L9_RUNTIME_ENV_FILE is required}"
    ]


def test_image_reference_requires_immutable_ghcr_digest() -> None:
    require_digest_ref("ghcr.io/quantum-l9/seo-bot@sha256:" + "a" * 64)
    with pytest.raises(ContractError):
        require_digest_ref("ghcr.io/quantum-l9/seo-bot:latest")
