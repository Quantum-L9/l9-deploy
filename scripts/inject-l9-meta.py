#!/usr/bin/env python3
"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [governance, tooling]
tags: [L9_CONTRACT, metadata-injector]
owner: platform
status: active
--- /L9_META ---

Idempotently inject the repository L9_META contract into supported tracked text files.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Final

import yaml

EXCLUDED_PARTS: Final = {".git", ".venv", ".pytest_cache", "__pycache__", "dist", "build"}
COMMENT_SUFFIXES: Final = {
    ".yaml", ".yml", ".tf", ".hcl", ".toml", ".lock", ".sh", ".j2", ".cfg",
    ".editorconfig", ".gitignore", ".service",
}
COMMENT_NAMES: Final = {"Makefile", "CODEOWNERS", "l9-backup-verify", "l9-postgres-backup"}
HTML_SUFFIXES: Final = {".md"}
JSON_SUFFIXES: Final = {".json"}
PYTHON_SUFFIXES: Final = {".py"}


def metadata(path: Path) -> dict[str, object]:
    layer = "tests" if "tests" in path.parts else "repository"
    return {
        "l9_schema": 1,
        "origin": "l9-deployment-platform",
        "layer": [layer],
        "tags": ["L9_META", "deployment-platform"],
        "owner": "platform",
        "status": "active",
    }


def comment_block(meta: dict[str, object]) -> str:
    lines = ["# --- L9_META ---"]
    lines.extend(f"# {line}" for line in yaml.safe_dump(meta, sort_keys=False).strip().splitlines())
    lines.append("# --- /L9_META ---")
    return "\n".join(lines) + "\n"


def html_block(meta: dict[str, object]) -> str:
    body = yaml.safe_dump(meta, sort_keys=False).strip()
    return f"<!-- L9_META\n{body}\n/L9_META -->\n"


def python_block(meta: dict[str, object]) -> str:
    body = yaml.safe_dump(meta, sort_keys=False).strip()
    return f'"""\n--- L9_META ---\n{body}\n--- /L9_META ---\n"""\n'


def inject_text(path: Path, text: str) -> str:
    if "L9_META" in text:
        return text
    meta = metadata(path)
    if path.suffix in PYTHON_SUFFIXES:
        block = python_block(meta)
        if text.startswith("#!"):
            first, rest = text.split("\n", 1)
            return first + "\n" + block + rest
        return block + text
    if path.suffix in HTML_SUFFIXES:
        return html_block(meta) + text
    if path.suffix in COMMENT_SUFFIXES or path.name in COMMENT_NAMES:
        block = comment_block(meta)
        if text.startswith("#!"):
            first, rest = text.split("\n", 1)
            return first + "\n" + block + rest
        return block + text
    if path.suffix in JSON_SUFFIXES:
        value = json.loads(text)
        if not isinstance(value, dict):
            raise ValueError(f"JSON metadata requires an object root: {path}")
        ordered = {"x-l9-meta": meta, **value}
        return json.dumps(ordered, indent=2, sort_keys=False) + "\n"
    raise ValueError(f"unsupported metadata file type: {path}")


def load_exclusions(root: Path) -> set[str]:
    document = yaml.safe_load((root / ".l9/metadata-exclusions.yaml").read_text(encoding="utf-8"))
    return {str(item["path"]) for item in document["exclusions"]}


def candidates(root: Path, exclusions: set[str]) -> list[Path]:
    result: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or any(part in EXCLUDED_PARTS for part in path.parts):
            continue
        relative = path.relative_to(root).as_posix()
        if relative in exclusions:
            continue
        if (
            path.suffix in PYTHON_SUFFIXES | HTML_SUFFIXES | COMMENT_SUFFIXES | JSON_SUFFIXES
            or path.name in COMMENT_NAMES
        ):
            result.append(path)
    return sorted(result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    exclusions = load_exclusions(root)
    changed: list[str] = []
    missing: list[str] = []
    for path in candidates(root, exclusions):
        text = path.read_text(encoding="utf-8")
        if "L9_META" not in text:
            missing.append(path.relative_to(root).as_posix())
            if not args.check:
                path.write_text(inject_text(path, text), encoding="utf-8")
                changed.append(path.relative_to(root).as_posix())
    if args.check and missing:
        sys.stderr.write("missing L9_META:\n" + "\n".join(missing) + "\n")
        return 1
    result = {
        "status": "PASS",
        "changed": changed,
        "checked": len(candidates(root, exclusions)),
    }
    sys.stdout.write(json.dumps(result) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
