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
from __future__ import annotations


class L9DeployError(Exception):
    exit_code = 1


class ContractError(L9DeployError):
    exit_code = 5


class CompatibilityError(L9DeployError):
    exit_code = 8


class AuthorizationError(L9DeployError):
    exit_code = 6


class ExecutionError(L9DeployError):
    exit_code = 3


class OperationalLimitError(L9DeployError):
    exit_code = 9
