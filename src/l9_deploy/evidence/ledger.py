"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [evidence]
tags: [L9_CONTRACT, append-only, hash-chain]
owner: platform
status: active
--- /L9_META ---

Create-only, content-addressed receipt storage with a hash-chained append-only index.
"""

from __future__ import annotations

import fcntl
import json
import os
from copy import deepcopy
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from ..canonical import canonical_json_bytes, load_structured, sha256_digest
from ..errors import ContractError
from ..redaction import redact


@dataclass(frozen=True)
class PublishedReceipt:
    canonical_path: Path
    receipt_digest: str
    ledger_entry_digest: str


class ReceiptLedger:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.index_path = root / "index.jsonl"
        self.lock_path = root / ".index.lock"

    @staticmethod
    def _schema_slug(schema: str) -> str:
        return schema.removeprefix("l9.").replace("/", "-").replace(".", "-")

    def _canonical_path(self, document: dict[str, object]) -> Path:
        schema = document.get("schema")
        digest = document.get("receipt_digest")
        completed_at = document.get("completed_at") or document.get("approved_at")
        if not isinstance(schema, str) or not isinstance(digest, str):
            raise ContractError("canonical receipt requires schema and receipt_digest")
        if not isinstance(completed_at, str):
            raise ContractError("canonical receipt requires a completion timestamp")
        try:
            timestamp = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ContractError("canonical receipt timestamp is invalid") from exc
        digest_hex = digest.removeprefix("sha256:")
        return (
            self.root
            / self._schema_slug(schema)
            / f"{timestamp.year:04d}"
            / f"{timestamp.month:02d}"
            / f"{digest_hex}.json"
        )

    @staticmethod
    def _verify_receipt_digest(document: dict[str, object]) -> None:
        supplied = document.get("receipt_digest")
        digest_input = deepcopy(document)
        digest_input.pop("receipt_digest", None)
        if supplied != sha256_digest(digest_input):
            raise ContractError("receipt digest does not match canonical content")

    @staticmethod
    def _create_only(path: Path, payload: bytes, mode: int = 0o600) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        try:
            fd = os.open(path, flags, mode)
        except FileExistsError as exc:
            raise ContractError(f"canonical receipt collision: {path}") from exc
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            path.unlink(missing_ok=True)
            raise

    def _last_entry(self) -> tuple[int, str | None]:
        if not self.index_path.exists():
            return 0, None
        last: dict[str, object] | None = None
        with self.index_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    value = json.loads(line)
                    if not isinstance(value, dict):
                        raise ContractError("receipt ledger contains a non-object entry")
                    last = value
        if last is None:
            return 0, None
        sequence = last.get("sequence")
        digest = last.get("entry_digest")
        if not isinstance(sequence, int) or not isinstance(digest, str):
            raise ContractError("receipt ledger tail is malformed")
        return sequence, digest

    def publish(self, document: dict[str, object]) -> PublishedReceipt:
        redacted = redact(document)
        if not isinstance(redacted, dict):
            raise ContractError("redacted receipt must remain an object")
        typed = {str(key): value for key, value in redacted.items()}
        self._verify_receipt_digest(typed)
        canonical_path = self._canonical_path(typed)
        payload = json.dumps(typed, indent=2, sort_keys=True).encode() + b"\n"

        self.root.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            try:
                self._create_only(canonical_path, payload)
                sequence, previous_digest = self._last_entry()
                entry: dict[str, object] = {
                    "schema": "l9.receipt-ledger-entry/v1",
                    "sequence": sequence + 1,
                    "previous_entry_digest": previous_digest,
                    "receipt_digest": typed["receipt_digest"],
                    "receipt_schema": typed["schema"],
                    "path": canonical_path.relative_to(self.root).as_posix(),
                    "published_at": datetime.now(UTC).isoformat(),
                }
                entry["entry_digest"] = sha256_digest(entry)
                line = canonical_json_bytes(entry) + b"\n"
                fd = os.open(self.index_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
                try:
                    with os.fdopen(fd, "ab") as handle:
                        handle.write(line)
                        handle.flush()
                        os.fsync(handle.fileno())
                except Exception:
                    canonical_path.unlink(missing_ok=True)
                    raise
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        return PublishedReceipt(
            canonical_path=canonical_path,
            receipt_digest=str(typed["receipt_digest"]),
            ledger_entry_digest=str(entry["entry_digest"]),
        )

    def load_receipt(self, receipt_digest: str) -> dict[str, object]:
        if not self.index_path.exists():
            raise ContractError(f"receipt is absent from ledger: {receipt_digest}")
        with self.index_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                entry = json.loads(line)
                if not isinstance(entry, dict):
                    raise ContractError("receipt ledger contains a non-object entry")
                if entry.get("receipt_digest") != receipt_digest:
                    continue
                receipt_path = self.root / str(entry.get("path"))
                receipt = load_structured(receipt_path)
                if not isinstance(receipt, dict):
                    raise ContractError(f"ledger receipt is invalid: {receipt_path}")
                self._verify_receipt_digest(receipt)
                return {str(key): value for key, value in receipt.items()}
        raise ContractError(f"receipt is absent from ledger: {receipt_digest}")

    def verify(self) -> dict[str, object]:
        if not self.index_path.exists():
            return {"status": "PASS", "entries": 0, "head_digest": None}
        previous: str | None = None
        expected_sequence = 1
        with self.index_path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                entry = json.loads(line)
                if not isinstance(entry, dict):
                    raise ContractError(f"ledger entry {line_number} is not an object")
                supplied = entry.get("entry_digest")
                digest_input = deepcopy(entry)
                digest_input.pop("entry_digest", None)
                if supplied != sha256_digest(digest_input):
                    raise ContractError(f"ledger entry {line_number} digest is invalid")
                if entry.get("sequence") != expected_sequence:
                    raise ContractError(f"ledger sequence breaks at entry {line_number}")
                if entry.get("previous_entry_digest") != previous:
                    raise ContractError(f"ledger chain breaks at entry {line_number}")
                receipt_path = self.root / str(entry.get("path"))
                receipt = load_structured(receipt_path)
                if not isinstance(receipt, dict):
                    raise ContractError(f"ledger receipt is invalid: {receipt_path}")
                self._verify_receipt_digest(receipt)
                if receipt.get("receipt_digest") != entry.get("receipt_digest"):
                    raise ContractError(f"ledger receipt digest mismatch: {receipt_path}")
                previous = str(supplied)
                expected_sequence += 1
        return {"status": "PASS", "entries": expected_sequence - 1, "head_digest": previous}
