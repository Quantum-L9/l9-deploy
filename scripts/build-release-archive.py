#!/usr/bin/env python3
"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [repository, release-tooling]
tags: [L9_META, deployment-platform, deterministic-archive]
owner: platform
status: active
--- /L9_META ---

Build a deterministic, single-root repository ZIP from the validated release tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from _bootstrap import add_repository_src, remove_repository_bytecode

add_repository_src()

from l9_deploy.canonical import atomic_write_json, file_sha256, sha256_digest  # noqa: E402
from l9_deploy.contracts.models import RepositoryReleaseReceipt  # noqa: E402
from l9_deploy.release_inventory import release_files  # noqa: E402

CANONICAL_ROOT = "l9-deployment-platform"
ZIP_EPOCH = 315532800  # 1980-01-01T00:00:00Z, the earliest portable ZIP timestamp.


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build deterministic repository release ZIP")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--receipt", type=Path)
    parser.add_argument(
        "--source-date-epoch",
        type=int,
        default=int(os.environ.get("SOURCE_DATE_EPOCH", ZIP_EPOCH)),
    )
    return parser.parse_args()


def _zip_datetime(epoch: int) -> tuple[int, int, int, int, int, int]:
    clamped = max(epoch, ZIP_EPOCH)
    value = time.gmtime(clamped)
    # ZIP timestamps have two-second precision.
    return (
        value.tm_year,
        value.tm_mon,
        value.tm_mday,
        value.tm_hour,
        value.tm_min,
        value.tm_sec // 2 * 2,
    )


def _mode(path: Path) -> int:
    executable = bool(path.stat().st_mode & stat.S_IXUSR)
    return 0o755 if executable else 0o644


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _version(root: Path) -> str:
    import re

    match = re.search(
        r'^version = "([^"]+)"$',
        (root / "pyproject.toml").read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if match is None:
        raise ValueError("project version is absent from pyproject.toml")
    return match.group(1)


def _built_at(source_date_epoch: int) -> str:
    return (
        datetime.fromtimestamp(max(source_date_epoch, ZIP_EPOCH), UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def create_release_receipt(
    *,
    root: Path,
    archive: Path,
    archive_files: int,
    source_date_epoch: int,
) -> RepositoryReleaseReceipt:
    payload: dict[str, object] = {
        "schema": "l9.repository-release-receipt/v1",
        "repository": "Quantum-L9/l9-deployment-platform",
        "version": _version(root),
        "archive_name": archive.name,
        "archive_sha256": file_sha256(archive),
        "archive_size_bytes": archive.stat().st_size,
        "archive_files": archive_files,
        "source_manifest_sha256": file_sha256(root / "MANIFEST.json"),
        "source_date_epoch": max(source_date_epoch, ZIP_EPOCH),
        "built_at": _built_at(source_date_epoch),
    }
    payload["receipt_digest"] = sha256_digest(payload)
    return RepositoryReleaseReceipt.model_validate(payload)


def write_release_receipt(path: Path, receipt: RepositoryReleaseReceipt) -> None:
    atomic_write_json(
        path,
        receipt.model_dump(mode="json", by_alias=True),
        mode=0o644,
    )


def build_archive(root: Path, output: Path, source_date_epoch: int) -> dict[str, object]:
    root = root.resolve()
    output = output.resolve()
    if root == output or root in output.parents:
        raise ValueError("archive output must be outside the repository root")

    files = release_files(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp")
    temporary.unlink(missing_ok=True)
    timestamp = _zip_datetime(source_date_epoch)

    try:
        with zipfile.ZipFile(
            temporary,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
            strict_timestamps=True,
        ) as archive:
            for path in files:
                relative = PurePosixPath(path.relative_to(root).as_posix())
                name = f"{CANONICAL_ROOT}/{relative.as_posix()}"
                info = zipfile.ZipInfo(name, date_time=timestamp)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (_mode(path) & 0xFFFF) << 16
                info.flag_bits |= 0x800  # UTF-8 file names.
                archive.writestr(
                    info,
                    path.read_bytes(),
                    compress_type=zipfile.ZIP_DEFLATED,
                    compresslevel=9,
                )
        with zipfile.ZipFile(temporary) as archive:
            bad = archive.testzip()
            if bad is not None:
                raise ValueError(f"archive integrity failure: {bad}")
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)

    return {
        "status": "PASS",
        "archive": str(output),
        "files": len(files),
        "sha256": _sha256(output),
        "source_date_epoch": max(source_date_epoch, ZIP_EPOCH),
    }


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    remove_repository_bytecode(root)
    output = args.output.resolve()
    if args.receipt is not None:
        receipt_path = args.receipt.resolve()
        if receipt_path == root or root in receipt_path.parents:
            raise ValueError("release receipt must be written outside the repository root")
    else:
        receipt_path = None

    result = build_archive(root, output, args.source_date_epoch)
    if receipt_path is not None:
        receipt = create_release_receipt(
            root=root,
            archive=output,
            archive_files=int(result["files"]),
            source_date_epoch=args.source_date_epoch,
        )
        write_release_receipt(receipt_path, receipt)
        result["receipt"] = str(receipt_path)
        result["receipt_digest"] = receipt.receipt_digest

    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
