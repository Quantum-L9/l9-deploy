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
from pathlib import Path

import pytest
import yaml

from l9_deploy.canonical import file_sha256
from l9_deploy.errors import AuthorizationError, ContractError
from l9_deploy.requests.parser import parse_repository_dispatch
from l9_deploy.requests.verifier import resolve_registered_profile, verify_request


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


def test_request_verifier_rejects_public_hostname_drift(
    deployment_context, schema_registry
) -> None:  # type: ignore[no-untyped-def]
    root = deployment_context["root"]
    assert isinstance(root, Path)
    profile_path = root / "profiles/seo-bot.yaml"
    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    profile["network"]["public_ingress"] = {
        "enabled": True,
        "hostnames": ["mcp.example.com"],
        "tls": "automatic",
    }
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")

    request = copy.deepcopy(deployment_context["request"])
    request["profile"]["digest"] = file_sha256(profile_path)
    fleet = copy.deepcopy(deployment_context["fleet"])
    fleet["projects"][0]["environments"]["staging"]["public_hostnames"] = ["wrong.example.com"]
    with pytest.raises(AuthorizationError, match="public hostnames"):
        verify_request(
            request,
            fleet,
            schema_registry,
            root,
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


def _verify_with(deployment_context, schema_registry, *, request=None, fleet=None, root=None):  # type: ignore[no-untyped-def]
    return verify_request(
        request if request is not None else deployment_context["request"],
        fleet if fleet is not None else deployment_context["fleet"],
        schema_registry,
        root if root is not None else deployment_context["root"],
        evidence_root=deployment_context["evidence_root"],
        bundle_validator=deployment_context["bundle_validator"],
    )


def _rewrite_profile(deployment_context, request, mutate) -> None:  # type: ignore[no-untyped-def]
    profile_path = deployment_context["profile_path"]
    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    mutate(profile)
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")
    request["profile"]["digest"] = file_sha256(profile_path)


def test_request_verifier_rejects_unregistered_source_repository(
    deployment_context, schema_registry
) -> None:  # type: ignore[no-untyped-def]
    request = copy.deepcopy(deployment_context["request"])
    request["source"]["repository"] = "Quantum-L9/Other-Bot"
    with pytest.raises(AuthorizationError, match="not registered for deployment"):
        _verify_with(deployment_context, schema_registry, request=request)
    assert not deployment_context["bundle_validator"].calls


def test_request_verifier_rejects_source_commit_drift(deployment_context, schema_registry) -> None:  # type: ignore[no-untyped-def]
    request = copy.deepcopy(deployment_context["request"])
    request["source"]["commit_sha"] = "f" * 40
    with pytest.raises(AuthorizationError, match="source commit mismatch"):
        _verify_with(deployment_context, schema_registry, request=request)


def test_request_verifier_rejects_source_run_drift(deployment_context, schema_registry) -> None:  # type: ignore[no-untyped-def]
    request = copy.deepcopy(deployment_context["request"])
    request["source"]["run_id"] = request["source"]["run_id"] + 1
    with pytest.raises(AuthorizationError, match="source run mismatch"):
        _verify_with(deployment_context, schema_registry, request=request)


def test_request_verifier_rejects_profile_path_outside_fleet_registration(
    deployment_context, schema_registry
) -> None:  # type: ignore[no-untyped-def]
    request = copy.deepcopy(deployment_context["request"])
    request["profile"]["path"] = "profiles/other.yaml"
    with pytest.raises(AuthorizationError, match="path does not match fleet registration"):
        _verify_with(deployment_context, schema_registry, request=request)


def test_request_verifier_never_falls_back_outside_the_profile_root(
    deployment_context, schema_registry, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    # The registered path exists in the request's own tree, but the profile root
    # handed to the verifier is empty: no other location is consulted.
    empty_root = tmp_path / "empty-profile-root"
    empty_root.mkdir()
    with pytest.raises(ContractError, match="missing from the profile root"):
        _verify_with(deployment_context, schema_registry, root=empty_root)
    assert not deployment_context["bundle_validator"].calls


def test_request_verifier_rejects_symlinked_profile_even_with_matching_digest(
    deployment_context, schema_registry, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    profile_path = deployment_context["profile_path"]
    outside = tmp_path / "outside-root" / "substituted.yaml"
    outside.parent.mkdir()
    outside.write_bytes(profile_path.read_bytes())
    profile_path.unlink()
    profile_path.symlink_to(outside)
    request = copy.deepcopy(deployment_context["request"])
    request["profile"]["digest"] = file_sha256(outside)
    with pytest.raises(AuthorizationError, match="crosses a symlink"):
        _verify_with(deployment_context, schema_registry, request=request)


def test_request_verifier_checks_digest_before_parsing_bytes(
    deployment_context, schema_registry
) -> None:  # type: ignore[no-untyped-def]
    # Garbage bytes under the registered path with the original digest claim: the
    # digest mismatch is reported, never a parse error from interpreting them.
    deployment_context["profile_path"].write_bytes(b"\x00not-a-profile: [\n")
    with pytest.raises(AuthorizationError, match="profile digest mismatch"):
        verified(deployment_context, schema_registry)


def test_request_verifier_rejects_profile_identity_drift(
    deployment_context, schema_registry
) -> None:  # type: ignore[no-untyped-def]
    request = copy.deepcopy(deployment_context["request"])
    _rewrite_profile(
        deployment_context, request, lambda profile: profile["project"].update({"id": "other-bot"})
    )
    with pytest.raises(AuthorizationError, match="project id does not match"):
        _verify_with(deployment_context, schema_registry, request=request)

    request = copy.deepcopy(deployment_context["request"])

    def substitute_image(profile):  # type: ignore[no-untyped-def]
        profile["project"]["id"] = "seo-bot"
        profile["artifact"]["image"] = "ghcr.io/quantum-l9/other"

    _rewrite_profile(deployment_context, request, substitute_image)
    with pytest.raises(AuthorizationError, match="image repository is not allowed"):
        _verify_with(deployment_context, schema_registry, request=request)


def test_resolve_registered_profile_confines_paths(tmp_path: Path) -> None:
    (tmp_path / "profiles").mkdir()
    (tmp_path / "profiles" / "app.yaml").write_text("schema: x\n", encoding="utf-8")
    assert (
        resolve_registered_profile(tmp_path, "profiles/app.yaml")
        == tmp_path / "profiles" / "app.yaml"
    )
    for escape in ("../app.yaml", "profiles/../../app.yaml", "/etc/passwd", "/profiles/app.yaml"):
        with pytest.raises(AuthorizationError, match="not confined"):
            resolve_registered_profile(tmp_path, escape)
    with pytest.raises(ContractError, match="missing from the profile root"):
        resolve_registered_profile(tmp_path, "profiles/absent.yaml")
    with pytest.raises(ContractError, match="missing from the profile root"):
        resolve_registered_profile(tmp_path, "profiles")
