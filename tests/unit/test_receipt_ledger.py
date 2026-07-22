"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, unit]
tags: [L9_TEST, receipt-ledger, immutability]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from l9_deploy.contracts.models import ReceiptStep
from l9_deploy.evidence.ledger import ReceiptLedger
from l9_deploy.evidence.receipts import create_deployment_receipt
from l9_deploy.errors import ContractError


def receipt_document() -> dict[str, object]:
    receipt = create_deployment_receipt(
        request_id="request-001",
        project_id="seo-bot",
        environment="staging",
        status="PASS",
        started_at="2026-07-21T12:00:00Z",
        source_commit_sha="a" * 40,
        image_ref="ghcr.io/quantum-l9/seo-bot@sha256:" + "b" * 64,
        plan_digest="sha256:" + "c" * 64,
        previous_release=None,
        steps=[ReceiptStep(step_id="verify", kind="verify", status="PASS")],
    )
    return receipt.model_dump(mode="json", by_alias=True)


def test_receipt_storage_is_create_only(tmp_path: Path) -> None:
    ledger = ReceiptLedger(tmp_path / "ledger")
    document = receipt_document()
    ledger.publish(document)
    with pytest.raises(ContractError, match="collision"):
        ledger.publish(document)


def test_receipt_tampering_breaks_ledger_verification(tmp_path: Path) -> None:
    ledger = ReceiptLedger(tmp_path / "ledger")
    published = ledger.publish(receipt_document())
    document = json.loads(published.canonical_path.read_text(encoding="utf-8"))
    document["status"] = "FAIL"
    published.canonical_path.write_text(json.dumps(document) + "\n", encoding="utf-8")
    with pytest.raises(ContractError, match="receipt digest"):
        ledger.verify()


def test_hash_chain_tampering_is_detected(tmp_path: Path) -> None:
    ledger = ReceiptLedger(tmp_path / "ledger")
    ledger.publish(receipt_document())
    entry = json.loads(ledger.index_path.read_text(encoding="utf-8"))
    entry["previous_entry_digest"] = "sha256:" + "d" * 64
    ledger.index_path.write_text(json.dumps(entry) + "\n", encoding="utf-8")
    with pytest.raises(ContractError, match="digest is invalid"):
        ledger.verify()
