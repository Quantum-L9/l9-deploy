<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- documentation
- change-summary
tags:
- L9_META
- deployment-platform
owner: platform
status: active
/L9_META -->
# Change Summary

The current architecture converges on one live deployment identity: `Quantum-L9/l9-deploy`.

## Live ownership

- `l9-ci-sdk`: canonical CI evidence.
- `l9-ci-core`: release orchestration, immutable image publication, evidence binding, and bounded
  deployment dispatch.
- `l9-deploy`: infrastructure, host configuration, deployment verification/mutation, rollback, and
  operational receipts.
- `Quantum-L9/.github`: organization interface discovery and starter projections.

## Legacy disposition

The retired repository identity is invalid for OIDC, runner scope, approval receipts, repository
guards, dispatch, release receipts, interface-provider identity, package identity, or new source
archives. Historical material is archived. The existing OpenTofu state prefix remains only as a
persisted storage compatibility key pending a separately authorized state migration.

## Validation disposition

Historical release validation remains historical. Current production readiness requires
revision-bound source CI and live infrastructure, runner, staging, rollback, backup, and restore
evidence.
