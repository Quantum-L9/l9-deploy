#!/usr/bin/env python3
"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [repository, release-tooling]
tags: [L9_META, deployment-platform, release-validation]
owner: platform
status: active
--- /L9_META ---

Validate release metadata, checksums, inventory completeness, and archive byte parity.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
import zipfile
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from _bootstrap import add_repository_src, remove_repository_bytecode

add_repository_src()

from l9_deploy.canonical import file_sha256, sha256_digest  # noqa: E402
from l9_deploy.contracts.models import RepositoryReleaseReceipt  # noqa: E402
from l9_deploy.release_inventory import (  # noqa: E402
    is_forbidden_release_path,
    release_files,
)

REQUIRED_ARTIFACTS = {
    "README.md",
    "RUNBOOK.md",
    "MANIFEST.md",
    "MANIFEST.json",
    "CHANGE_SUMMARY.md",
    "VALIDATION.md",
    "UNKNOWN_REGISTER.md",
    "FINAL_TREE.md",
    "REGRESSION_GUARD.md",
    "TRACEABILITY_MAP.yaml",
    "checksums.sha256",
}
CANONICAL_ROOT = "l9-deployment-platform"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a release-ready repository pack")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--receipt", type=Path)
    return parser.parse_args()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _version(root: Path) -> str:
    sources = {
        "pyproject": re.search(
            r'^version = "([^"]+)"$',
            (root / "pyproject.toml").read_text(encoding="utf-8"),
            re.MULTILINE,
        ),
        "runtime": re.search(
            r'^__version__ = "([^"]+)"$',
            (root / "src/l9_deploy/__init__.py").read_text(encoding="utf-8"),
            re.MULTILINE,
        ),
        "lock": re.search(
            r'name = "l9-deployment-platform"\nversion = "([^"]+)"',
            (root / "uv.lock").read_text(encoding="utf-8"),
        ),
        "changelog": re.search(
            r"^## ([0-9]+\.[0-9]+\.[0-9]+) -",
            (root / "CHANGELOG.md").read_text(encoding="utf-8"),
            re.MULTILINE,
        ),
    }
    if any(value is None for value in sources.values()):
        raise ValueError("one or more release version sources are missing")
    versions = {value.group(1) for value in sources.values() if value is not None}
    if len(versions) != 1:
        raise ValueError(f"release version sources disagree: {sorted(versions)}")
    return versions.pop()


def _all_repository_files(root: Path) -> list[Path]:
    return sorted(
        (path for path in root.rglob("*") if path.is_file() or path.is_symlink()),
        key=lambda path: path.relative_to(root).as_posix(),
    )


def _validate_root(root: Path) -> dict[str, object]:
    errors: list[str] = []
    eligible = release_files(root)
    actual = {path.relative_to(root).as_posix() for path in eligible}
    forbidden = []
    for path in _all_repository_files(root):
        relative = PurePosixPath(path.relative_to(root).as_posix())
        if path.is_symlink() or is_forbidden_release_path(relative):
            forbidden.append(relative.as_posix())
    if forbidden:
        errors.append("forbidden release residue: " + ", ".join(sorted(forbidden)[:20]))

    missing_required = sorted(REQUIRED_ARTIFACTS - actual)
    if missing_required:
        errors.append("missing required release artifacts: " + ", ".join(missing_required))
    if errors:
        raise ValueError("\n".join(errors))

    version = _version(root)
    manifest = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("version") != version:
        errors.append("manifest version does not match package version")
    entries = manifest.get("files")
    if not isinstance(entries, list):
        errors.append("manifest files must be a list")
        entries = []
    exclusions = manifest.get("self_exclusions", [])
    if not isinstance(exclusions, list) or not all(isinstance(item, str) for item in exclusions):
        errors.append("manifest self_exclusions must be a string list")
        exclusions = []
    expected_manifest = actual - set(exclusions)
    manifested = {
        str(entry.get("path"))
        for entry in entries
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    if expected_manifest != manifested:
        errors.append(
            "manifest inventory mismatch: "
            f"missing={sorted(expected_manifest - manifested)[:10]} "
            f"extra={sorted(manifested - expected_manifest)[:10]}"
        )
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            continue
        path = root / str(entry["path"])
        if not path.is_file():
            continue
        if entry.get("size_bytes") != path.stat().st_size or entry.get("sha256") != _sha256(path):
            errors.append(f"manifest digest or size mismatch: {entry['path']}")

    checksum_lines = (root / "checksums.sha256").read_text(encoding="utf-8").splitlines()
    checksums: dict[str, str] = {}
    for line in checksum_lines:
        digest, separator, relative = line.partition("  ")
        if not separator or not re.fullmatch(r"[a-f0-9]{64}", digest):
            errors.append(f"malformed checksum line: {line!r}")
            continue
        if relative in checksums:
            errors.append(f"duplicate checksum path: {relative}")
        checksums[relative] = digest
    expected_checksums = actual - {"checksums.sha256"}
    if set(checksums) != expected_checksums:
        errors.append("checksum inventory does not match release files")
    for relative, digest in checksums.items():
        path = root / relative
        if path.is_file() and _sha256(path) != digest:
            errors.append(f"checksum mismatch: {relative}")

    if errors:
        raise ValueError("\n".join(errors))
    return {"status": "PASS", "files": len(actual), "version": version}


def _validate_archive(archive: Path, root: Path) -> dict[str, object]:
    expected = {path.relative_to(root).as_posix(): path for path in release_files(root)}
    with zipfile.ZipFile(archive) as handle:
        infos = [info for info in handle.infolist() if not info.is_dir()]
        names = [info.filename for info in infos]
        if len(names) != len(set(names)):
            raise ValueError("archive contains duplicate member names")

        roots = {PurePosixPath(name).parts[0] for name in names if PurePosixPath(name).parts}
        if roots != {CANONICAL_ROOT}:
            raise ValueError(f"archive must contain one canonical root, found {sorted(roots)}")

        archived: dict[str, zipfile.ZipInfo] = {}
        forbidden: list[str] = []
        for info in infos:
            parts = PurePosixPath(info.filename).parts
            if len(parts) < 2:
                forbidden.append(info.filename)
                continue
            relative = PurePosixPath(*parts[1:])
            mode = (info.external_attr >> 16) & 0xFFFF
            is_symlink = stat.S_IFMT(mode) == stat.S_IFLNK
            if is_forbidden_release_path(relative) or is_symlink:
                forbidden.append(info.filename)
                continue
            archived[relative.as_posix()] = info
        if forbidden:
            raise ValueError("archive contains forbidden residue: " + ", ".join(forbidden[:20]))

        if set(archived) != set(expected):
            raise ValueError(
                "archive inventory mismatch: "
                f"missing={sorted(set(expected) - set(archived))[:10]} "
                f"extra={sorted(set(archived) - set(expected))[:10]}"
            )
        for relative, source in expected.items():
            info = archived[relative]
            archived_digest = hashlib.sha256(handle.read(info)).hexdigest()
            if archived_digest != _sha256(source):
                raise ValueError(f"archive content mismatch: {relative}")
            source_mode = 0o755 if source.stat().st_mode & stat.S_IXUSR else 0o644
            archived_mode = (info.external_attr >> 16) & 0o777
            if archived_mode != source_mode:
                raise ValueError(
                    f"archive mode mismatch: {relative} "
                    f"expected={oct(source_mode)} actual={oct(archived_mode)}"
                )

        bad = handle.testzip()
        if bad is not None:
            raise ValueError(f"archive integrity failure: {bad}")
    return {"status": "PASS", "files": len(infos), "content_match": True}


def _zip_datetime(epoch: int) -> tuple[int, int, int, int, int, int]:
    import time

    value = time.gmtime(max(epoch, 315532800))
    return (
        value.tm_year,
        value.tm_mon,
        value.tm_mday,
        value.tm_hour,
        value.tm_min,
        value.tm_sec // 2 * 2,
    )


def _validate_release_receipt(
    receipt_path: Path,
    archive: Path,
    root: Path,
) -> dict[str, object]:
    raw = json.loads(receipt_path.read_text(encoding="utf-8"))
    receipt = RepositoryReleaseReceipt.model_validate(raw)
    digest_input = deepcopy(raw)
    supplied_digest = digest_input.pop("receipt_digest", None)
    if supplied_digest != sha256_digest(digest_input):
        raise ValueError("release receipt digest mismatch")
    if receipt.version != _version(root):
        raise ValueError("release receipt version does not match source")
    if receipt.archive_name != archive.name:
        raise ValueError("release receipt archive name mismatch")
    if receipt.archive_sha256 != file_sha256(archive):
        raise ValueError("release receipt archive digest mismatch")
    if receipt.archive_size_bytes != archive.stat().st_size:
        raise ValueError("release receipt archive size mismatch")
    if receipt.source_manifest_sha256 != file_sha256(root / "MANIFEST.json"):
        raise ValueError("release receipt source manifest mismatch")
    expected_built_at = (
        datetime.fromtimestamp(receipt.source_date_epoch, UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )
    if receipt.built_at.isoformat().replace("+00:00", "Z") != expected_built_at:
        raise ValueError("release receipt built_at does not match source_date_epoch")
    with zipfile.ZipFile(archive) as handle:
        infos = [item for item in handle.infolist() if not item.is_dir()]
        if receipt.archive_files != len(infos):
            raise ValueError("release receipt archive file count mismatch")
        expected_timestamp = _zip_datetime(receipt.source_date_epoch)
        timestamps = {item.date_time for item in infos}
        if timestamps != {expected_timestamp}:
            raise ValueError("archive timestamps do not match release receipt")
    return {
        "status": "PASS",
        "receipt_digest": receipt.receipt_digest,
        "archive_sha256": receipt.archive_sha256,
    }


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    remove_repository_bytecode(root)
    result: dict[str, object] = {"root": _validate_root(root)}
    archive = args.archive.resolve() if args.archive is not None else None
    receipt = args.receipt.resolve() if args.receipt is not None else None
    if receipt is not None and archive is None:
        raise ValueError("--receipt requires --archive")
    if archive is not None:
        result["archive"] = _validate_archive(archive, root)
    if receipt is not None and archive is not None:
        result["receipt"] = _validate_release_receipt(receipt, archive, root)
    sys.stdout.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
