"""--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests]
tags: [L9_TEST, request-verification]
owner: platform
status: active
--- /L9_META ---"""

from __future__ import annotations

import copy

import pytest

from l9_deploy.errors import AuthorizationError, ContractError
from l9_deploy.requests.parser import parse_repository_dispatch
from l9_deploy.requests.verifier import verify_request


def verified(deployment_context, schema_registry):  # type: ignore[no-untyped-def]
    return verify_request(
        deployment_context["request"],
        deployment_context["fleet"],
        schema_registry,
        deployment_context["root"],
        evidence_root=deployment_context["evidence_root"],
        bundle_validator=deployment_context["bundle_validator"],
    )


def test_repository_dispatch_parser_accepts_bounded_payload(
    deployment_context,
) -> None:  # type: ignore[no-untyped-def]
    request = deployment_context["request"]
    assert (
        parse_repository_dispatch({"action": "l9.release.requested.v1", "client_payload": request})
        == request
    )


def test_repository_dispatch_parser_rejects_unknown_action() -> None:
    with pytest.raises(ContractError):
        parse_repository_dispatch({"action": "surprise", "client_payload": {}})


def test_request_verifier_accepts_registered_digest(deployment_context, schema_registry) -> None:  # type: ignore[no-untyped-def]
    result = verified(deployment_context, schema_registry)
    assert result.project.id == "seo-bot"
    assert result.environment.server_ids == ("seo-staging-01",)
    assert deployment_context["bundle_validator"].calls


def test_request_verifier_rejects_profile_drift(deployment_context, schema_registry) -> None:  # type: ignore[no-untyped-def]
    request = copy.deepcopy(deployment_context["request"])
    request["profile"]["digest"] = "sha256:" + "0" * 64
    with pytest.raises(AuthorizationError, match="profile digest mismatch"):
        verify_request(
            request,
            deployment_context["fleet"],
            schema_registry,
            deployment_context["root"],
            evidence_root=deployment_context["evidence_root"],
            bundle_validator=deployment_context["bundle_validator"],
        )


def test_request_verifier_rejects_mutable_or_mismatched_image(
    deployment_context, schema_registry
) -> None:  # type: ignore[no-untyped-def]
    request = copy.deepcopy(deployment_context["request"])
    request["artifact"]["image_ref"] = "ghcr.io/quantum-l9/seo-bot@sha256:" + "f" * 64
    with pytest.raises(ValueError, match="image_ref"):
        verify_request(
            request,
            deployment_context["fleet"],
            schema_registry,
            deployment_context["root"],
            evidence_root=deployment_context["evidence_root"],
            bundle_validator=deployment_context["bundle_validator"],
        )


def test_request_verifier_rejects_bad_source_ref(deployment_context, schema_registry) -> None:  # type: ignore[no-untyped-def]
    request = copy.deepcopy(deployment_context["request"])
    request["source"]["ref"] = "refs/heads/feature/not-approved"
    with pytest.raises(AuthorizationError, match="source ref mismatch"):
        verify_request(
            request,
            deployment_context["fleet"],
            schema_registry,
            deployment_context["root"],
            evidence_root=deployment_context["evidence_root"],
            bundle_validator=deployment_context["bundle_validator"],
        )


def test_request_verifier_rejects_self_authored_ci_receipt(
    deployment_context, schema_registry
) -> None:  # type: ignore[no-untyped-def]
    binding_path = deployment_context["evidence_root"] / "release-artifact-binding.json"
    binding = __import__("json").loads(binding_path.read_text(encoding="utf-8"))
    binding["source"]["commit_sha"] = "f" * 40
    binding_path.write_text(__import__("json").dumps(binding), encoding="utf-8")
    with pytest.raises(AuthorizationError):
        verified(deployment_context, schema_registry)
