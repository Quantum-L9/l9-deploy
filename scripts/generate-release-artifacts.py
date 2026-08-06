#!/usr/bin/env python3
"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [repository, release-tooling]
tags: [L9_META, deployment-platform, manifest, checksums]
owner: platform
status: active
--- /L9_META ---

Generate the repository manifest, responsibility map, final tree, and checksum index.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
from datetime import UTC, datetime
from pathlib import Path

from _bootstrap import add_repository_src, remove_repository_bytecode

add_repository_src()

from l9_deploy.release_inventory import release_files  # noqa: E402

SELF_EXCLUSIONS = ("MANIFEST.json", "MANIFEST.md", "checksums.sha256")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate deterministic release inventory files")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--generated-at")
    return parser.parse_args()


def _version(root: Path) -> str:
    match = re.search(
        r'^version = "([^"]+)"$',
        (root / "pyproject.toml").read_text(encoding="utf-8"),
        re.MULTILINE,
    )
    if match is None:
        raise ValueError("project version is absent from pyproject.toml")
    return match.group(1)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _responsibility(path: str) -> str:
    top = path.split("/", maxsplit=1)[0]
    roles = {
        ".github": "GitHub governance and workflow orchestration",
        ".l9": "L9 ownership, policy, compatibility, and integration contracts",
        "ansible": "host configuration and conformance",
        "deployment": "runtime profiles, policies, probes, and templates",
        "docs": "architecture, operations, security, and consumer guidance",
        "fleet": "fleet desired state and environment registration",
        "infrastructure": "OpenTofu infrastructure desired state",
        "integrations": "cross-repository integration projections",
        "schemas": "versioned public JSON contracts",
        "scripts": "operator, validation, and release tooling",
        "src": "deployment control-plane implementation",
        "templates": "consumer adoption templates",
        "tests": "behavioral, contract, security, and regression tests",
        "validation": "machine-readable validation evidence",
    }
    return roles.get(top, "repository governance, packaging, or operator entrypoint")


def _write_final_tree(root: Path, paths: list[str]) -> None:
    lines = [
        "<!-- L9_META",
        "l9_schema: 1",
        "origin: l9-deployment-platform",
        "layer: [repository]",
        "tags: [L9_META, deployment-platform, final-tree]",
        "owner: platform",
        "status: active",
        "/L9_META -->",
        "# Final Repository Tree",
        "",
        "```text",
        "l9-deployment-platform/",
    ]
    for index, path in enumerate(paths):
        branch = "└──" if index == len(paths) - 1 else "├──"
        lines.append(f"{branch} {path}")
    lines.extend(["```", ""])
    (root / "FINAL_TREE.md").write_text("\n".join(lines), encoding="utf-8")


def _generated_at(value: str | None) -> str:
    if value and value.isdigit():
        return datetime.fromtimestamp(int(value), UTC).isoformat().replace("+00:00", "Z")
    if value:
        return value
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    remove_repository_bytecode(root)
    generated_at = _generated_at(args.generated_at or os.environ.get("SOURCE_DATE_EPOCH"))

    initial_paths = [path.relative_to(root).as_posix() for path in release_files(root)]
    _write_final_tree(root, initial_paths)

    files = release_files(root)
    entries: list[dict[str, object]] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        if relative in SELF_EXCLUSIONS:
            continue
        media_type = mimetypes.guess_type(relative)[0] or "application/octet-stream"
        entries.append(
            {
                "path": relative,
                "size_bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "media_type": media_type,
            }
        )

    version = _version(root)
    manifest = {
        "x-l9-meta": {
            "l9_schema": 1,
            "origin": "l9-deployment-platform",
            "layer": ["repository"],
            "tags": ["L9_META", "deployment-platform"],
            "owner": "platform",
            "status": "active",
        },
        "schema": "l9.repository-manifest/v1",
        "repository": "Quantum-L9/l9-deployment-platform",
        "version": version,
        "generated_at": generated_at,
        "file_count": len(entries),
        "total_size_bytes": sum(int(entry["size_bytes"]) for entry in entries),
        "self_exclusions": list(SELF_EXCLUSIONS),
        "files": entries,
    }
    (root / "MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )

    responsibility_rows: list[tuple[str, str, int]] = []
    for prefix in (
        ".github",
        ".l9",
        "src",
        "schemas",
        "scripts",
        "tests",
        "validation",
        "infrastructure",
        "ansible",
        "deployment",
        "fleet",
        "integrations",
        "templates",
        "docs",
    ):
        count = sum(1 for entry in entries if str(entry["path"]).split("/", 1)[0] == prefix)
        if count:
            responsibility_rows.append((prefix, _responsibility(prefix), count))

    lines = [
        "<!-- L9_META",
        "l9_schema: 1",
        "origin: l9-deployment-platform",
        "layer: [repository]",
        "tags: [L9_META, deployment-platform, manifest]",
        "owner: platform",
        "status: active",
        "/L9_META -->",
        "# Repository Manifest",
        "",
        "## Summary",
        "",
        "- Repository: `Quantum-L9/l9-deployment-platform`",
        f"- Version: `{version}`",
        f"- Manifested files: **{len(entries)}**",
        f"- Manifested bytes: **{manifest['total_size_bytes']}**",
        "",
        "`MANIFEST.json`, `MANIFEST.md`, and `checksums.sha256` are excluded from the JSON ",
        "manifest to avoid self-referential hashes. The checksum index covers both manifest files.",
        "",
        "## Responsibility map",
        "",
        "| Path family | Responsibility | Files |",
        "|---|---|---:|",
    ]
    lines.extend(
        f"| `{prefix}/` | {role} | {count} |" for prefix, role, count in responsibility_rows
    )
    lines.extend(
        [
            "",
            "## File inventory",
            "",
            "| Path | Responsibility | Bytes | SHA-256 |",
            "|---|---|---:|---|",
        ]
    )
    for entry in entries:
        relative = str(entry["path"])
        lines.append(
            f"| `{relative}` | {_responsibility(relative)} | {entry['size_bytes']} | "
            f"`{entry['sha256']}` |"
        )
    lines.append("")
    (root / "MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")

    checksum_paths = [path for path in release_files(root) if path.name != "checksums.sha256"]
    checksum_lines = [
        f"{_sha256(path)}  {path.relative_to(root).as_posix()}" for path in checksum_paths
    ]
    (root / "checksums.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
