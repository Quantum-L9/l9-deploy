<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- repository
tags:
- L9_META
- deployment-platform
owner: platform
status: active
/L9_META -->
# L9 Deploy Specification

## Identity

Canonical repository, package, runner, OIDC, approval, dispatch, release-receipt, interface, and new
archive identity is `Quantum-L9/l9-deploy` / `l9-deploy`.

The retired identity is invalid on live trust surfaces. The existing OpenTofu state key prefix is
retained only as an explicitly classified persisted storage namespace pending a separately authorized
state migration.

## Purpose

Provision Hetzner infrastructure, reconcile hosts, validate bounded release requests, deploy exact OCI
digests, orchestrate backups and migrations, verify health, roll back eligible runtime failures, and
emit immutable operational evidence.

## Exclusions

This repository does not own application source, CI finding reconstruction, image registry
implementation, secret storage, central observability, or organization-wide CI orchestration.

## External owners

- `l9-ci-sdk`: canonical CI evidence.
- `l9-ci-core`: CI/release orchestration and bounded deployment dispatch.
- `Quantum-L9/.github`: organization interface registry and starter projections.
- Infisical: secret authority.
- GHCR: image registry.
- GitHub protected environments: human approval enforcement.

## Public contracts

- `l9.deployment-request/v1`
- `l9.deployment-profile/v1`
- `l9.deployment-plan/v1`
- `l9.approval-receipt/v1`
- `l9.deployment-receipt/v1`
- `l9.rollback-receipt/v1`
- `l9.infrastructure-plan/v1`
- `l9.repository-release-receipt/v1`

Unknown schema majors fail closed.

## Runtime profiles

Implemented v1 profiles are `container-service`, `worker-service`, `stateful-container`,
`scheduled-job`, and `external-platform`.

## Infrastructure

OpenTofu owns desired infrastructure state. Ansible owns host configuration. Planning and apply are
separate; apply consumes the exact approved plan artifact. Destructive changes require explicit
authorization.

Existing state remains under the historical storage prefix until a separately validated state
migration is authorized. That storage path is not accepted as repository identity.

## Deployment runner

The dedicated runner is repository-scoped to `Quantum-L9/l9-deploy`, carries
`l9-deployment,hetzner-private`, and is not a general CI host. Existing registration must match the
canonical repository. Offline-runner recovery is out-of-band through the bootstrap runbook.

## OIDC and secrets

Only jobs that consume Infisical may request job-scoped `id-token: write`. Approval and validation
jobs receive no OIDC permission. Runtime secret material is never committed or attached as workflow
evidence.

## Release and rollback

Deployment identity is immutable image plus release-owned runtime configuration. Health failure may
trigger runtime rollback when policy permits. Database rollback is never inferred from container
rollback.

## Receipts

Canonical receipts are create-only and content-addressed. The ledger is hash-chained; latest pointers
are convenience views only.

## Readiness

Production readiness requires current source CI plus external evidence for private repository
visibility, OIDC claim policy, runner registration/labels/availability, infrastructure plan/drift,
staging deployment, rollback, backup, and restore.
