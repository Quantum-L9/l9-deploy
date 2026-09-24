#!/usr/bin/env python3
"""
--- L9_META ---
l9_schema: 1
origin: l9-deploy
layer: [governance, validation]
tags: [L9_CONTRACT, repository-identity]
owner: platform
status: active
--- /L9_META ---

Reject legacy repository identity in live control-plane surfaces.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_REPOSITORY = "Quantum-L9/" + "l9-deployment-platform"
LEGACY_NAME = "l9-" + "deployment-platform"
CANONICAL_REPOSITORY = "Quantum-L9/l9-deploy"

LIVE_ROOTS = (
    ROOT / "src",
    ROOT / "schemas",
    ROOT / "scripts",
    ROOT / ".github",
    ROOT / "integrations",
    ROOT / "templates",
)
ROOT_FILES = (ROOT / "pyproject.toml", ROOT / "uv.lock", ROOT / "Makefile")
STATE_COMPATIBILITY_PATHS = {
    ".github/workflows/drift-detect.yml",
    ".github/workflows/provision-plan.yml",
}
FORBIDDEN_BARE_FORMS = (
    'name = "' + LEGACY_NAME + '"',
    'CANONICAL_ROOT = "' + LEGACY_NAME + '"',
    "../" + LEGACY_NAME + ".zip",
    "../" + LEGACY_NAME + "-dist",
    LEGACY_NAME + "-release",
)


def _files() -> list[Path]:
    files = [path for root in LIVE_ROOTS for path in root.rglob("*") if path.is_file()]
    files.extend(path for path in ROOT_FILES if path.is_file())
    return sorted(set(files))


def main() -> int:
    findings: list[str] = []
    for path in _files():
        relative = path.relative_to(ROOT).as_posix()
        if relative == "scripts/validate-repository-identity.py":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if LEGACY_REPOSITORY in text:
            findings.append(f"{relative}: legacy repository coordinate remains live")
        for form in FORBIDDEN_BARE_FORMS:
            if form in text:
                findings.append(f"{relative}: legacy live artifact identity remains: {form}")
        if LEGACY_NAME in text and relative in STATE_COMPATIBILITY_PATHS:
            for line in text.splitlines():
                if LEGACY_NAME in line and "tofu.tfstate" not in line and "origin:" not in line:
                    findings.append(f"{relative}: legacy token is not confined to persisted state")
    if findings:
        sys.stderr.write("\n".join(sorted(set(findings))) + "\n")
        return 1
    sys.stdout.write(f"repository identity aligned: {CANONICAL_REPOSITORY}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
