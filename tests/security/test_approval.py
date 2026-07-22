"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, security]
tags: [L9_TEST, approval, separation-of-duties]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from l9_deploy.canonical import file_sha256, sha256_digest
from l9_deploy.contracts.models import ApprovalReceipt
from l9_deploy.evidence.approval import verify_approval_receipt
from l9_deploy.errors import AuthorizationError


def approval_documents(tmp_path: Path) -> tuple[dict[str, object], Path]:
    history = [
        {
            "state": "approved",
            "submitted_at": "2026-07-21T12:00:01Z",
            "user": {"login": "reviewer"},
            "environments": [{"name": "production"}],
        }
    ]
    history_path = tmp_path / "history.json"
    history_path.write_text(json.dumps(history) + "\n", encoding="utf-8")
    document: dict[str, object] = {
        "schema": "l9.approval-receipt/v1",
        "approval_id": "c6969d36-a4dd-4a01-89b1-64ec114cb9fd",
        "request_id": "0b6d09a6-1a48-4c84-87af-6f2902fcd59f",
        "environment": "production",
        "plan_digest": "sha256:" + "a" * 64,
        "requester": "requester",
        "approved": True,
        "approved_by": "reviewer",
        "approved_at": "2026-07-21T12:00:01Z",
        "authorization_method": "github_protected_environment_review",
        "workflow": {
            "repository": "Quantum-L9/l9-deployment-platform",
            "run_id": 123,
            "run_attempt": 1,
            "job_id": 456,
            "workflow_ref": (
                "Quantum-L9/l9-deployment-platform/.github/workflows/"
                "deploy-dispatch.yml@refs/heads/main"
            ),
            "environment": "production",
            "approval_api_url": (
                "https://api.github.com/repos/Quantum-L9/l9-deployment-platform/"
                "actions/runs/123/approvals"
            ),
            "approval_record_digest": file_sha256(history_path),
        },
    }
    document["receipt_digest"] = sha256_digest(document)
    return document, history_path


def test_approval_contract_rejects_self_approval(tmp_path: Path) -> None:
    document, _ = approval_documents(tmp_path)
    document["approved_by"] = document["requester"]
    with pytest.raises(ValidationError, match="different identities"):
        ApprovalReceipt.model_validate(document)


def test_approval_verifier_rejects_unmatched_history(
    tmp_path: Path, schema_registry
) -> None:  # type: ignore[no-untyped-def]
    document, history_path = approval_documents(tmp_path)
    document["approved_by"] = "different-reviewer"
    digest_input = dict(document)
    digest_input.pop("receipt_digest")
    document["receipt_digest"] = sha256_digest(digest_input)
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(document) + "\n", encoding="utf-8")
    with pytest.raises(AuthorizationError, match="not backed"):
        verify_approval_receipt(
            receipt_path,
            history_path,
            schema_registry,
            request_id="0b6d09a6-1a48-4c84-87af-6f2902fcd59f",
            requester="requester",
            environment="production",
            plan_digest="sha256:" + "a" * 64,
            expected_run_id=123,
        )
