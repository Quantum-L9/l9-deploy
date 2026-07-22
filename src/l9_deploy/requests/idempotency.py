"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [requests, state]
tags: [L9_CONTRACT, idempotency, two-phase]
owner: platform
status: active
--- /L9_META ---

Two-phase idempotency state for convergent deployment transactions.
"""
from __future__ import annotations

import fcntl
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from ..canonical import atomic_write_json, load_structured
from ..contracts.models import IdempotencyDocument, IdempotencyEntry
from ..errors import AuthorizationError


class IdempotencyStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.lock_path = path.with_suffix(path.suffix + ".lock")

    @contextmanager
    def _locked(self) -> Iterator[None]:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def _load(self) -> IdempotencyDocument:
        if not self.path.exists():
            return IdempotencyDocument.model_validate(
                {"schema": "l9.idempotency-store/v1", "entries": {}}
            )
        value = load_structured(self.path)
        try:
            return IdempotencyDocument.model_validate(value)
        except ValueError as exc:
            raise AuthorizationError("idempotency store is malformed") from exc

    def _write(self, state: IdempotencyDocument) -> None:
        atomic_write_json(self.path, state.model_dump(mode="json", by_alias=True))

    @staticmethod
    def _with_entries(
        state: IdempotencyDocument,
        entries: dict[str, IdempotencyEntry],
    ) -> IdempotencyDocument:
        return IdempotencyDocument.model_validate(
            {"schema": state.schema_id, "entries": entries}
        )

    @staticmethod
    def _entry(
        *,
        request_digest: str,
        status: str,
        receipt_digest: str | None = None,
        reason: str | None = None,
    ) -> IdempotencyEntry:
        return IdempotencyEntry.model_validate(
            {
                "request_digest": request_digest,
                "status": status,
                "updated_at": datetime.now(UTC),
                "receipt_digest": receipt_digest,
                "reason": reason,
            }
        )

    def begin(self, key: str, request_digest: str) -> IdempotencyEntry | None:
        with self._locked():
            state = self._load()
            existing = state.entries.get(key)
            if existing is not None:
                if existing.request_digest != request_digest:
                    raise AuthorizationError(
                        "idempotency key was reused with a different request"
                    )
                if existing.status != "FAIL":
                    return existing
                # A failed transaction may be retried with the same request digest.
                # Reset it explicitly so the persisted state reflects active work.
                try:
                    retry = self._entry(
                        request_digest=request_digest,
                        status="IN_PROGRESS",
                    )
                    entries = dict(state.entries)
                    entries[key] = retry
                    self._write(self._with_entries(state, entries))
                except ValueError as exc:
                    raise AuthorizationError(
                        "invalid idempotency key or request digest"
                    ) from exc
                return None

            try:
                entry = self._entry(
                    request_digest=request_digest,
                    status="IN_PROGRESS",
                )
                entries = dict(state.entries)
                entries[key] = entry
                self._write(self._with_entries(state, entries))
            except ValueError as exc:
                raise AuthorizationError(
                    "invalid idempotency key or request digest"
                ) from exc
            return None

    def prepare_completion(self, key: str, receipt_digest: str) -> None:
        self._set(key, "PREPARED", receipt_digest=receipt_digest)

    def complete(self, key: str, receipt_digest: str) -> None:
        self._set(key, "COMPLETE", receipt_digest=receipt_digest)

    def fail(self, key: str, reason: str) -> None:
        self._set(key, "FAIL", reason=reason)

    def get(self, key: str) -> IdempotencyEntry | None:
        with self._locked():
            return self._load().entries.get(key)

    def _set(
        self,
        key: str,
        status: str,
        *,
        receipt_digest: str | None = None,
        reason: str | None = None,
    ) -> None:
        with self._locked():
            state = self._load()
            current = state.entries.get(key)
            if current is None:
                raise AuthorizationError(f"unknown idempotency key: {key}")

            if current.status == "COMPLETE":
                if status == "COMPLETE" and current.receipt_digest == receipt_digest:
                    return
                raise AuthorizationError("completed idempotency state is immutable")
            if current.status == "PREPARED" and status == "PREPARED":
                if current.receipt_digest == receipt_digest:
                    return
                raise AuthorizationError("prepared receipt digest cannot be replaced")
            allowed = {
                "IN_PROGRESS": {"PREPARED", "FAIL"},
                "PREPARED": {"COMPLETE", "FAIL"},
                "FAIL": set(),
            }
            if status not in allowed[current.status]:
                raise AuthorizationError(
                    f"invalid idempotency transition: {current.status} -> {status}"
                )

            try:
                updated = self._entry(
                    request_digest=current.request_digest,
                    status=status,
                    receipt_digest=(
                        receipt_digest if status in {"PREPARED", "COMPLETE"} else None
                    ),
                    reason=reason if status == "FAIL" else None,
                )
                entries = dict(state.entries)
                entries[key] = updated
                self._write(self._with_entries(state, entries))
            except ValueError as exc:
                raise AuthorizationError("invalid idempotency transition payload") from exc
