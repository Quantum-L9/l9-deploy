#!/usr/bin/env python3
"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [governance, validation]
tags: [L9_CONTRACT, metadata-gate]
owner: platform
status: active
--- /L9_META ---
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    completed = subprocess.run(
        [sys.executable, str(root / "scripts/inject-l9-meta.py"), "--root", str(root), "--check"],
        check=False,
        text=True,
        capture_output=True,
    )
    if completed.returncode:
        sys.stderr.write(completed.stderr)
        return completed.returncode
    sys.stdout.write(completed.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
