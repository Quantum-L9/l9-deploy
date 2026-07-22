"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [tests, compliance]
tags: [L9_TEST, deterministic-archive, release-integrity]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath
from types import ModuleType

import pytest

from l9_deploy.release_inventory import is_forbidden_release_path, release_files

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"


def _load_script(module_name: str, filename: str) -> ModuleType:
    path = SCRIPTS / filename
    sys.path.insert(0, str(SCRIPTS))
    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.remove(str(SCRIPTS))


def _snapshot_repository(target: Path) -> Path:
    target.mkdir(parents=True)
    for source in release_files(ROOT):
        relative = source.relative_to(ROOT)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    return target


def _rewrite_archive(
    source: Path,
    target: Path,
    *,
    omit: str | None = None,
    mutate: str | None = None,
) -> None:
    with zipfile.ZipFile(source) as reader, zipfile.ZipFile(target, "w") as writer:
        for info in reader.infolist():
            if info.is_dir() or info.filename == omit:
                continue
            payload = reader.read(info)
            if info.filename == mutate:
                payload += b"\nmodified\n"
            writer.writestr(info, payload)


def test_release_archive_is_deterministic_and_matches_source(tmp_path: Path) -> None:
    builder = _load_script("l9_build_release_archive_test", "build-release-archive.py")
    validator = _load_script("l9_validate_release_pack_test", "validate-release-pack.py")
    snapshot = _snapshot_repository(tmp_path / "repo")
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"

    first_result = builder.build_archive(snapshot, first, builder.ZIP_EPOCH)
    second_result = builder.build_archive(snapshot, second, builder.ZIP_EPOCH)
    first_receipt = builder.create_release_receipt(
        root=snapshot,
        archive=first,
        archive_files=int(first_result["files"]),
        source_date_epoch=builder.ZIP_EPOCH,
    )
    receipt_path = tmp_path / "release.receipt.json"
    builder.write_release_receipt(receipt_path, first_receipt)

    assert first.read_bytes() == second.read_bytes()
    assert first_result["sha256"] == second_result["sha256"]
    assert validator._validate_archive(first, snapshot) == {
        "status": "PASS",
        "files": first_result["files"],
        "content_match": True,
    }
    receipt_result = validator._validate_release_receipt(
        receipt_path, first, snapshot
    )
    assert receipt_result["status"] == "PASS"
    assert receipt_result["archive_sha256"] == first_receipt.archive_sha256


def test_release_archive_validation_rejects_missing_and_modified_files(
    tmp_path: Path,
) -> None:
    builder = _load_script("l9_build_release_archive_failure_test", "build-release-archive.py")
    validator = _load_script("l9_validate_release_pack_failure_test", "validate-release-pack.py")
    snapshot = _snapshot_repository(tmp_path / "repo")
    source = tmp_path / "source.zip"
    builder.build_archive(snapshot, source, builder.ZIP_EPOCH)

    with zipfile.ZipFile(source) as archive:
        members = [info.filename for info in archive.infolist() if not info.is_dir()]
    assert members

    missing = tmp_path / "missing.zip"
    _rewrite_archive(source, missing, omit=members[0])
    with pytest.raises(ValueError, match="archive inventory mismatch"):
        validator._validate_archive(missing, snapshot)

    modified = tmp_path / "modified.zip"
    _rewrite_archive(source, modified, mutate=members[0])
    with pytest.raises(ValueError, match="archive content mismatch"):
        validator._validate_archive(modified, snapshot)

def test_release_receipt_rejects_archive_digest_tampering(tmp_path: Path) -> None:
    builder = _load_script("l9_build_release_receipt_test", "build-release-archive.py")
    validator = _load_script("l9_validate_release_receipt_test", "validate-release-pack.py")
    snapshot = _snapshot_repository(tmp_path / "repo")
    archive = tmp_path / "release.zip"
    result = builder.build_archive(snapshot, archive, builder.ZIP_EPOCH)
    receipt = builder.create_release_receipt(
        root=snapshot,
        archive=archive,
        archive_files=int(result["files"]),
        source_date_epoch=builder.ZIP_EPOCH,
    ).model_dump(mode="json", by_alias=True)
    receipt["archive_sha256"] = "sha256:" + "0" * 64
    receipt["receipt_digest"] = builder.sha256_digest(
        {key: value for key, value in receipt.items() if key != "receipt_digest"}
    )
    receipt_path = tmp_path / "tampered.receipt.json"
    builder.atomic_write_json(receipt_path, receipt, mode=0o644)

    with pytest.raises(ValueError, match="archive digest mismatch"):
        validator._validate_release_receipt(receipt_path, archive, snapshot)


def test_release_inventory_rejects_coverage_residue(tmp_path: Path) -> None:
    validator = _load_script("l9_validate_coverage_residue_test", "validate-release-pack.py")
    snapshot = _snapshot_repository(tmp_path / "repo")
    (snapshot / ".coverage").write_text("coverage residue", encoding="utf-8")
    (snapshot / "artifacts").mkdir(exist_ok=True)
    (snapshot / "artifacts/coverage.xml").write_text("<coverage />", encoding="utf-8")

    assert is_forbidden_release_path(PurePosixPath(".coverage"))
    assert is_forbidden_release_path(PurePosixPath("artifacts/coverage.xml"))
    with pytest.raises(ValueError, match="forbidden release residue"):
        validator._validate_root(snapshot)



def test_release_artifact_generation_does_not_create_bytecode_residue(
    tmp_path: Path,
) -> None:
    snapshot = _snapshot_repository(tmp_path / "repo")
    environment = os.environ.copy()
    environment.pop("PYTHONDONTWRITEBYTECODE", None)
    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate-release-artifacts.py",
            "--generated-at",
            "315532800",
        ],
        cwd=snapshot,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert not list(snapshot.rglob("__pycache__"))
    assert not list(snapshot.rglob("*.pyc"))
