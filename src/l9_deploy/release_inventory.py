"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [repository, release-tooling]
tags: [L9_META, deployment-platform, release-inventory]
owner: platform
status: active
--- /L9_META ---

Canonical release-file eligibility shared by generation, packaging, and validation.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath
from typing import Final

FORBIDDEN_PARTS: Final = frozenset(
    {
        ".git",
        ".venv",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
        "build",
        "dist",
        "htmlcov",
    }
)
FORBIDDEN_SUFFIXES: Final = frozenset({".pyc", ".pyo", ".zip", ".tar", ".gz", ".tgz"})
FORBIDDEN_NAMES: Final = frozenset({".DS_Store", ".coverage", "coverage.xml"})


def is_forbidden_release_path(relative: PurePosixPath) -> bool:
    return (
        relative.is_absolute()
        or not relative.parts
        or any(part in {"", ".", ".."} for part in relative.parts)
        or any(part in FORBIDDEN_PARTS for part in relative.parts)
        or relative.suffix.lower() in FORBIDDEN_SUFFIXES
        or relative.name in FORBIDDEN_NAMES
    )


def release_files(root: Path) -> list[Path]:
    root = root.resolve()
    return sorted(
        (
            path
            for path in root.rglob("*")
            if path.is_file()
            and not is_forbidden_release_path(
                PurePosixPath(path.relative_to(root).as_posix())
            )
        ),
        key=lambda path: path.relative_to(root).as_posix(),
    )
