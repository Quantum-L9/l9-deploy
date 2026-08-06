#!/usr/bin/env python3
"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer:
- repository
tags:
- L9_META
- deployment-platform
owner: platform
status: active
--- /L9_META ---
"""

import argparse

from _bootstrap import add_repository_src

add_repository_src()

from l9_deploy.cli import main as cli_main  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", required=True)
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--destination", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return cli_main(
        [
            "adoption",
            "render",
            "--profile",
            args.profile,
            "--project-id",
            args.project_id,
            "--repository",
            args.repository,
            "--image",
            args.image,
            "--destination",
            args.destination,
            "--non-interactive",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
