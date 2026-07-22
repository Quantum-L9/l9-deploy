"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [evidence]
tags: [L9_CONTRACT, publisher]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

from pathlib import Path

from ..canonical import atomic_write_json
from ..redaction import redact
from .ledger import PublishedReceipt, ReceiptLedger


def publish_json(path: Path, document: dict[str, object]) -> None:
    """Publish a non-canonical JSON artifact. Receipts must use publish_receipt."""
    atomic_write_json(path, redact(document), mode=0o600)


def publish_receipt(
    ledger_root: Path,
    document: dict[str, object],
    *,
    latest_pointer: Path | None = None,
) -> PublishedReceipt:
    published = ReceiptLedger(ledger_root).publish(document)
    if latest_pointer is not None:
        pointer = {
            "schema": "l9.receipt-pointer/v1",
            "authoritative": False,
            "receipt_digest": published.receipt_digest,
            "ledger_entry_digest": published.ledger_entry_digest,
            "canonical_path": str(published.canonical_path),
        }
        atomic_write_json(latest_pointer, pointer, mode=0o600)
    return published
