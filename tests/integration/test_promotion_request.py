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

import json
import subprocess
import sys
from pathlib import Path

from l9_deploy.canonical import sha256_digest


def test_promotion_preserves_image_and_targets_production(tmp_path: Path, repo_root: Path) -> None:
    request = {
        "schema": "l9.deployment-request/v1",
        "request_id": "8b52d352-82e0-4dc1-9309-b8b57805e198",
        "idempotency_key": "release:Quantum-L9/SEO-Bot:" + "a" * 40 + ":staging",
        "source": {
            "repository": "Quantum-L9/SEO-Bot",
            "commit_sha": "a" * 40,
            "ref": "refs/tags/v1.0.0",
            "run_id": 1,
        },
        "artifact": {
            "image": "ghcr.io/quantum-l9/seo-bot",
            "digest": "sha256:" + "b" * 64,
            "image_ref": "ghcr.io/quantum-l9/seo-bot@sha256:" + "b" * 64,
            "architecture": "linux/amd64",
        },
        "profile": {
            "path": "integrations/consumers/seo-bot.deployment.yaml",
            "digest": "sha256:" + "c" * 64,
        },
        "evidence": {
            "schema": "l9.release-evidence-reference/v1",
            "schema_version": "1.0.0",
            "sdk_version": "1.0.0",
            "workflow_run_id": 1,
            "artifact_name": "l9-release-evidence-1",
            "bundle_path": "finding-bundle.json",
            "gate_binding_path": "ci-gate-binding.json",
            "artifact_binding_path": "release-artifact-binding.json",
            "bundle_digest": "sha256:" + "d" * 64,
            "gate_binding_digest": "sha256:" + "e" * 64,
            "artifact_binding_digest": "sha256:" + "f" * 64,
            "provenance_reference": "oci://proof",
            "sbom_reference": "oci://sbom",
        },
        "target": {"environment": "staging"},
        "requested_by": "tester",
        "requested_at": "2026-07-21T00:00:00Z",
    }
    receipt = {
        "schema": "l9.deployment-receipt/v1",
        "status": "PASS",
        "environment": "staging",
        "image_ref": request["artifact"]["image_ref"],
    }
    request_path = tmp_path / "request.json"
    receipt_path = tmp_path / "receipt.json"
    output_path = tmp_path / "production.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    subprocess.run(
        [
            sys.executable,
            str(repo_root / "scripts/promote-request.py"),
            "--request",
            str(request_path),
            "--staging-receipt",
            str(receipt_path),
            "--expected-staging-receipt-digest",
            sha256_digest(receipt),
            "--output",
            str(output_path),
            "--schemas",
            str(repo_root / "schemas/v1"),
        ],
        check=True,
        cwd=repo_root,
    )
    promoted = json.loads(output_path.read_text(encoding="utf-8"))
    assert promoted["target"]["environment"] == "production"
    assert promoted["artifact"]["image_ref"] == request["artifact"]["image_ref"]
    assert promoted["request_id"] != request["request_id"]
