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
# Architecture

## System role

`l9-deploy` is the authoritative infrastructure and deployment mutation plane for Quantum-L9 hosted
services. It is not a constellation runtime node, CI evidence producer, secret authority, image
registry, or application repository.

## Control flow

```text
consumer repository
  -> l9-ci-core
  -> canonical l9-ci-sdk evidence
  -> immutable GHCR digest
  -> l9.release.requested.v1
  -> l9-deploy request verification
  -> deterministic plan
  -> protected-environment approval
  -> repository-scoped deployment runner
  -> Hetzner/private or explicitly adopted target
  -> health verification
  -> content-addressed receipt ledger
```

## Ownership

### `l9-ci-sdk`
Owns canonical CI evidence, findings, gate semantics, compatibility, and deterministic serialization.

### `l9-ci-core`
Owns release orchestration, image build/publication, SBOM and provenance, evidence binding, and the
bounded repository dispatch to `Quantum-L9/l9-deploy`.

### `Quantum-L9/.github`
Owns organization-level interface discovery and starter projections.

### `l9-deploy`
Owns OpenTofu desired state and exact-plan apply, Ansible host reconciliation, fleet inventory,
deployment request/profile contracts, approval verification, host/environment locks, deployment
transactions, backup/migration orchestration, rollback, and receipts.

## Trust-boundary contracts

- `l9.ci-gate-binding/v1`: binds canonical CI gate evidence to source identity.
- `l9.release-artifact-binding/v1`: binds the evidence to one immutable image digest.
- `l9.approval-receipt/v1`: binds an independent protected-environment reviewer to the exact
  request, environment, plan digest, workflow run, and approval-history digest.
- `l9.deployment-receipt/v1`: records the executed deployment transaction.
- `l9.repository-release-receipt/v1`: binds a deterministic source archive to repository identity,
  source manifest, version, timestamp, and archive digest.

## Deployment transaction

```text
IN_PROGRESS -> PREPARED -> authoritative receipt publication -> COMPLETE
      |
      +-> FAIL only before authoritative receipt publication
```

Replay of a `PREPARED` request loads the authoritative content-addressed receipt and completes
idempotency indexing without redeploying. A pre-publication failure may roll back runtime state when
policy permits.

## Runtime identity

A release consists of both immutable image digest and release-owned configuration. Each release has
its own protected `runtime.env` under the digest-addressed release directory. Migration, Compose,
promotion, and rollback use that release-owned configuration. The top-level mutable env file is not
release authority.

## Infrastructure transaction

OpenTofu planning emits an exact binary plan plus digest-bearing receipt. Apply consumes that exact
artifact and refuses destructive changes unless explicitly authorized. The existing remote-state
storage prefix is a compatibility namespace and is not a live repository identity.

## Runner boundary

The dedicated runner is repository-scoped to `Quantum-L9/l9-deploy` and carries the
`l9-deployment` and `hetzner-private` labels. Existing runner configuration must resolve to the
canonical repository. Consumer pull-request workflows must never target it.

## OIDC boundary

Workflow-level `id-token: write` is prohibited. Only jobs that actually exchange GitHub identity
for Infisical credentials receive job-scoped OIDC:

- `deploy-dispatch.yml/deploy`
- `drift-detect.yml/plan`
- `provision-plan.yml/plan`
- `provision-apply.yml/apply`

Approval and validation jobs do not receive OIDC.

## Implemented profiles

- `container-service`
- `worker-service`
- `stateful-container`
- `scheduled-job`
- `external-platform`

New profiles may extend execution behavior only while preserving evidence, approval, digest, lock,
receipt, and rollback invariants.
