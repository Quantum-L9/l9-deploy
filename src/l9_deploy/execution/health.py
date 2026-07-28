"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [execution]
tags: [L9_CONTRACT, health, typed-probe]
owner: platform
status: active
--- /L9_META ---
"""

from __future__ import annotations

import socket
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from typing import Protocol
from urllib.parse import urlsplit

from pydantic import JsonValue

from ..contracts.models import HealthProbe
from ..errors import ExecutionError


class Executor(Protocol):
    def run(self, command: Sequence[str], **kwargs: object) -> object: ...


def run_probe(
    probe: HealthProbe, executor: Executor | None = None, base_url: str | None = None
) -> dict[str, JsonValue]:
    last_error = "probe not executed"
    for attempt in range(1, probe.attempts + 1):
        try:
            kind = probe.type
            if kind == "http":
                if not base_url or probe.path is None or probe.expected_status is None:
                    raise ExecutionError("HTTP probe requires base_url, path, and expected_status")
                if urlsplit(base_url).scheme not in {"http", "https"}:
                    raise ExecutionError("HTTP probe base_url must use http or https")
                url = base_url.rstrip("/") + probe.path
                request = urllib.request.Request(url, method="GET")  # noqa: S310
                with urllib.request.urlopen(  # noqa: S310
                    request, timeout=probe.timeout_seconds
                ) as response:
                    if response.status != probe.expected_status:
                        raise ExecutionError(f"unexpected HTTP status {response.status}")
            elif kind == "tcp":
                if probe.host is None or probe.port is None:
                    raise ExecutionError("TCP probe requires host and port")
                connection = socket.create_connection(
                    (probe.host, probe.port), timeout=probe.timeout_seconds
                )
                connection.close()
            elif kind in {"command", "database"}:
                if executor is None or probe.command is None:
                    raise ExecutionError(f"{kind} probe requires executor and command")
                executor.run(probe.command, timeout=probe.timeout_seconds)
            else:
                raise ExecutionError(f"unsupported probe type: {kind}")
            return {"attempt": attempt, "type": kind}
        except (OSError, urllib.error.URLError, ExecutionError) as exc:
            last_error = str(exc)
            if attempt < probe.attempts:
                time.sleep(probe.interval_seconds)
    raise ExecutionError(f"health probe failed after {probe.attempts} attempts: {last_error}")
