#!/usr/bin/env python3
"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [governance, validation]
tags: [L9_CONTRACT, recursive-alignment]
owner: platform
status: active
--- /L9_META ---

Validate repository-specific L9 alignment without applying runtime-node rules to the
non-node infrastructure control plane.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Final

import yaml
from _bootstrap import add_repository_src

add_repository_src()

from l9_deploy.contracts.alias_policy import allowed_alias_call_ids  # noqa: E402

ROOT: Final = Path(__file__).resolve().parents[1]
PRODUCTION_ROOTS: Final = (ROOT / "src", ROOT / "scripts")
SCANNER_EXCLUSIONS: Final = {
    ROOT / "scripts" / "fast-contract-scan.py",
    ROOT / "scripts" / "validate-alignment.py",
}
REQUIRED_TYPED_MODELS: Final = {
    "DeploymentRequest",
    "ReleaseEvidenceReference",
    "DeploymentProfile",
    "ServerProfile",
    "FleetInventory",
    "DeploymentPlan",
    "PlanStep",
    "ApprovalReceipt",
    "DeploymentReceipt",
    "ReleaseState",
}


def python_findings() -> list[str]:
    findings: list[str] = []
    forbidden_packet = "Packet" + "Envelope"
    for base in PRODUCTION_ROOTS:
        for path in sorted(base.rglob("*.py")):
            if path in SCANNER_EXCLUSIONS or "__pycache__" in path.parts:
                continue
            relative = path.relative_to(ROOT).as_posix()
            text = path.read_text(encoding="utf-8")
            if forbidden_packet in text:
                findings.append(f"{relative}: deprecated packet contract reference")
            tree = ast.parse(text, filename=relative)
            allowed_aliases = allowed_alias_call_ids(tree, relative)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in {"print", "eval", "exec", "compile"}:
                        findings.append(f"{relative}:{node.lineno}: prohibited call {node.func.id}")
                    if (
                        node.func.id == "Field"
                        and any(keyword.arg == "alias" for keyword in node.keywords)
                        and id(node) not in allowed_aliases
                    ):
                        findings.append(
                            f"{relative}:{node.lineno}: Pydantic alias violates NAME-001"
                        )
                if isinstance(node, ast.Raise):
                    exception = node.exc
                    if isinstance(exception, ast.Call):
                        exception = exception.func
                    if (
                        isinstance(exception, ast.Name)
                        and exception.id == "Not" + "ImplementedError"
                    ):
                        findings.append(f"{relative}:{node.lineno}: unimplemented production path")
                if isinstance(node, ast.ExceptHandler):
                    if node.type is None:
                        findings.append(f"{relative}:{node.lineno}: bare except")
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                        findings.append(f"{relative}:{node.lineno}: swallowed exception")
    return findings


def transport_findings() -> list[str]:
    path = ROOT / ".l9" / "transport-classification.yaml"
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    expected = {
        "classification": "infrastructure_control_plane",
        "constellation_node": False,
    }
    findings = [
        f"{path.relative_to(ROOT)}: {key} must be {value!r}"
        for key, value in expected.items()
        if document.get(key) != value
    ]
    transport = document.get("transport_packet", {})
    gate = document.get("gate", {})
    if transport.get("required_when_addressing_constellation_nodes") is not True:
        findings.append(
            "transport classification must require TransportPacket for node interaction"
        )
    if gate.get("required_for_follow_up_constellation_work") is not True:
        findings.append(
            "transport classification must require Gate for constellation follow-up work"
        )
    return findings


def trust_boundary_findings() -> list[str]:
    findings: list[str] = []
    release = (ROOT / "integrations/l9-ci-core/container-release.yml").read_text(encoding="utf-8")
    for required in (
        "ci-gate-binding.json",
        "finding-bundle.json",
        "l9-ci bundle validate",
        "l9.release-artifact-binding/v1",
    ):
        if required not in release:
            findings.append(f"container release integration missing {required}")
    if "l9.ci-release-receipt/v1" in release:
        findings.append("container release integration reconstructs a CI release receipt")
    mutating = {
        "configure-hosts.yml",
        "deploy-dispatch.yml",
        "provision-apply.yml",
        "rollback.yml",
        "runner-maintenance.yml",
    }
    for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
        if path.name not in mutating:
            continue
        text = path.read_text(encoding="utf-8")
        if "collect-approval" not in text or "approval-history.json" not in text:
            findings.append(
                f"{path.relative_to(ROOT)}: mutating workflow lacks independent approval"
            )
        forbidden_approver = "--approved-by " + '"${{ github.actor }}"'
        if forbidden_approver in text:
            findings.append(f"{path.relative_to(ROOT)}: triggering actor is used as approver")
    return findings


def typed_contract_findings() -> list[str]:
    path = ROOT / "src" / "l9_deploy" / "contracts" / "models.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    classes = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    missing = sorted(REQUIRED_TYPED_MODELS - classes)
    findings = [f"typed canonical contract is missing: {name}" for name in missing]
    source = path.read_text(encoding="utf-8")
    for required in (
        'extra="forbid"',
        "frozen=True",
        "validate_by_alias=True",
        "validate_by_name=False",
        "serialize_by_alias=True",
    ):
        if required not in source:
            findings.append(f"canonical contract base is missing {required}")
    for package in ("planning", "execution"):
        for candidate in sorted((ROOT / "src" / "l9_deploy" / package).rglob("*.py")):
            if "dict[str, Any]" in candidate.read_text(encoding="utf-8"):
                findings.append(
                    f"{candidate.relative_to(ROOT)}: canonical core retains dict[str, Any]"
                )
    verifier = ROOT / "src" / "l9_deploy" / "requests" / "verifier.py"
    if "dict[str, Any]" in verifier.read_text(encoding="utf-8"):
        findings.append(f"{verifier.relative_to(ROOT)}: verified request boundary is untyped")
    return findings


def main() -> int:
    findings = (
        python_findings()
        + transport_findings()
        + trust_boundary_findings()
        + typed_contract_findings()
    )
    if findings:
        sys.stderr.write("\n".join(sorted(findings)) + "\n")
        return 1
    sys.stdout.write("recursive alignment validation passed\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
