#!/usr/bin/env python3
"""
--- L9_META ---
l9_schema: 1
origin: l9-deployment-platform
layer: [governance, validation]
tags: [L9_CONTRACT, fast-preflight]
owner: platform
status: active
--- /L9_META ---

Fast local projection of critical L9 deployment-platform rules.
Canonical CI evidence is produced by Semgrep and normalized by l9-ci-sdk.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Final

from _bootstrap import add_repository_src

add_repository_src()

from l9_deploy.contracts.alias_policy import allowed_alias_call_ids  # noqa: E402

ROOTS: Final = ("src", "scripts")
EXCLUDED: Final = {"scripts/fast-contract-scan.py"}
FORBIDDEN_TEXT: Final = {
    "Packet" + "Envelope": "DEPR-001",
    "# " + "TODO": "STUB-002",
    "# " + "PLACEHOLDER": "STUB-003",
    "# " + "FIX" + "ME": "STUB-004",
    "# " + "X" + "XX": "STUB-005",
    "# " + "HA" + "CK": "STUB-006",
}


@dataclass(frozen=True)
class Finding:
    rule_id: str
    path: str
    line: int
    message: str


class Visitor(ast.NodeVisitor):
    def __init__(self, path: str, allowed_aliases: frozenset[int]) -> None:
        self.path = path
        self.allowed_aliases = allowed_aliases
        self.findings: list[Finding] = []
        self.protocol_depth = 0

    def add(self, rule_id: str, node: ast.AST, message: str) -> None:
        self.findings.append(Finding(rule_id, self.path, getattr(node, "lineno", 1), message))

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "print"}:
            self.add(f"SEC-{node.func.id.upper()}", node, f"{node.func.id} is prohibited")
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "yaml"
            and node.func.attr == "load"
        ):
            safe = any(
                keyword.arg == "Loader"
                and isinstance(keyword.value, ast.Attribute)
                and isinstance(keyword.value.value, ast.Name)
                and keyword.value.value.id == "yaml"
                and keyword.value.attr == "SafeLoader"
                for keyword in node.keywords
            )
            if not safe:
                self.add("SEC-007", node, "yaml.load requires yaml.SafeLoader")
        if (
            isinstance(node.func, ast.Name)
            and node.func.id == "Field"
            and any(keyword.arg == "alias" for keyword in node.keywords)
            and id(node) not in self.allowed_aliases
        ):
            self.add(
                "NAME-001",
                node,
                "Pydantic aliases are prohibited outside the schema identity exception",
            )
        self.generic_visit(node)

    @staticmethod
    def _is_protocol_base(base: ast.expr) -> bool:
        return (isinstance(base, ast.Name) and base.id == "Protocol") or (
            isinstance(base, ast.Attribute)
            and isinstance(base.value, ast.Name)
            and base.value.id == "typing"
            and base.attr == "Protocol"
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        is_protocol = any(self._is_protocol_base(base) for base in node.bases)
        self.protocol_depth += int(is_protocol)
        self.generic_visit(node)
        self.protocol_depth -= int(is_protocol)

    def _check_stub_body(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if self.protocol_depth or any(
            isinstance(decorator, ast.Name) and decorator.id == "abstractmethod"
            for decorator in node.decorator_list
        ):
            return
        if len(node.body) != 1:
            return
        statement = node.body[0]
        is_stub = isinstance(statement, ast.Pass) or (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and statement.value.value is Ellipsis
        )
        if is_stub:
            self.add("STUB-007", node, "pass-only or ellipsis-only function is prohibited")

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._check_stub_body(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._check_stub_body(node)
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        exception = node.exc
        if isinstance(exception, ast.Call):
            exception = exception.func
        if isinstance(exception, ast.Name) and exception.id == "Not" + "ImplementedError":
            self.add("STUB-001", node, "unimplemented production exceptions are prohibited")
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is None:
            self.add("ERR-001", node, "bare except is prohibited")
        if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
            self.add("ERR-002", node, "swallowed exceptions are prohibited")
        self.generic_visit(node)


def scan(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for directory in ROOTS:
        for path in sorted((root / directory).rglob("*.py")):
            relative = path.relative_to(root).as_posix()
            if relative in EXCLUDED or "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for token, rule_id in FORBIDDEN_TEXT.items():
                for match in re.finditer(re.escape(token), text):
                    line = text.count("\n", 0, match.start()) + 1
                    findings.append(Finding(rule_id, relative, line, f"forbidden token: {token}"))
            try:
                tree = ast.parse(text, filename=relative)
            except SyntaxError as exc:
                findings.append(Finding("PARSE-001", relative, exc.lineno or 1, str(exc)))
                continue
            visitor = Visitor(relative, allowed_alias_call_ids(tree, relative))
            visitor.visit(tree)
            findings.extend(visitor.findings)
    return sorted(findings, key=lambda item: (item.path, item.line, item.rule_id))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    findings = scan(root)
    payload = {
        "schema": "l9.fast-contract-scan/v1",
        "status": "FAIL" if findings else "PASS",
        "findings": [asdict(item) for item in findings],
    }
    stream = sys.stderr if findings else sys.stdout
    stream.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
