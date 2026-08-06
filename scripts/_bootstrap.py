"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [repository, tooling]
tags: [L9_META, deployment-platform, script-bootstrap]
owner: platform
status: active
--- /L9_META ---

Repository-local import bootstrap for directly executed operational scripts.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

# Operational scripts must not contaminate a frozen release tree with bytecode.
sys.dont_write_bytecode = True


def add_repository_src() -> Path:
    """Add the repository ``src`` directory to ``sys.path`` exactly once."""
    root = Path(__file__).resolve().parents[1]
    source = root / "src"
    source_text = str(source)
    if source_text not in sys.path:
        sys.path.insert(0, source_text)
    return root


def remove_repository_bytecode(root: Path | None = None) -> None:
    """Remove interpreter residue created while invoking repository tooling directly."""
    repository = root.resolve() if root is not None else Path(__file__).resolve().parents[1]
    for base_name in ("src", "scripts", "tests"):
        base = repository / base_name
        if not base.exists():
            continue
        for cache in sorted(base.rglob("__pycache__"), reverse=True):
            if cache.is_dir():
                shutil.rmtree(cache)
        for suffix in ("*.pyc", "*.pyo"):
            for artifact in base.rglob(suffix):
                artifact.unlink(missing_ok=True)
