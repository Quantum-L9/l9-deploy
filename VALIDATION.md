<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- validation
tags:
- L9_META
- deployment-platform
owner: platform
status: active
/L9_META -->
# Validation Status

## Evidence rule

Committed validation documents are status and policy summaries. They are not a substitute for
revision-bound GitHub checks, workflow artifacts, deployment receipts, infrastructure plans, fleet
conformance, or restore-test evidence.

Historical PASS claims from earlier repository revisions are archived evidence only.

## Source validation

A source revision is eligible for release only when its repository-native validation and organization
CI are green for that exact revision. The validation stack includes:

- Ruff lint and formatting
- strict mypy
- pytest with branch coverage floor
- JSON Schema and typed-contract parity
- workflow policy validation
- L9 metadata validation
- fast contract scan
- recursive alignment validation
- canonical repository-identity validation
- centralized contract gates
- shell syntax validation

## Operational validation

Production readiness additionally requires current external evidence for:

1. GitHub repository visibility is private.
2. canonical OIDC repository claim succeeds and legacy/unrelated claims are rejected.
3. the dedicated runner is online, repository-scoped to `Quantum-L9/l9-deploy`, and carries
   `l9-deployment` plus `hetzner-private`.
4. OpenTofu management, staging, and production plans/drift checks execute successfully.
5. fleet conformance executes successfully on the dedicated runner.
6. staging deploy and health verification succeed.
7. rollback rehearsal succeeds.
8. required backup verification and restore testing succeed.

Missing operational evidence is BLOCKED or UNKNOWN, never PASS.

## Release artifacts

`make release-prepare` regenerates `MANIFEST.json`, `MANIFEST.md`, `FINAL_TREE.md`, and
`checksums.sha256` for the frozen source release. The detached repository-release receipt binds the
generated archive to that frozen inventory.

Do not use a tracked generated artifact from another revision as current evidence.

## Current readiness policy

Until every mandatory operational gate above has revision-bound evidence, production readiness is
`NotReady`.
