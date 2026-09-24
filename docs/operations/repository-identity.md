<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- documentation
- operations
tags:
- L9_META
- repository-identity
owner: platform
status: active
/L9_META -->
# Repository Identity

## Canonical live identity

- Repository: `Quantum-L9/l9-deploy`
- URL: `https://github.com/Quantum-L9/l9-deploy`
- Package/distribution name: `l9-deploy`
- OIDC repository claim: `Quantum-L9/l9-deploy`
- Repository-scoped runner target: `Quantum-L9/l9-deploy`
- Approval-receipt workflow repository: `Quantum-L9/l9-deploy`
- Release-receipt repository: `Quantum-L9/l9-deploy`
- Source archive root and basename: `l9-deploy`
- Deployment dispatch destination: `Quantum-L9/l9-deploy`

These values are authoritative for runtime guards, schemas, workflows, release artifacts,
integration contracts, operator commands, and new evidence.

## Legacy quarantine

The former repository identity is disabled for live trust decisions. Historical identity is
documented only under `docs/archive/`.

The existing OpenTofu remote-state prefix is a persisted storage namespace, not repository identity.
It remains an explicit compatibility exception until state migration is separately authorized and
verified. It must never be accepted as an OIDC claim, runner target, approval repository, dispatch
destination, release-receipt repository, interface provider, or new package/archive identity.

## Ownership

`l9-ci-core` owns release orchestration and dispatch construction. `l9-deploy` owns request
verification and deployment mutation. Executable copies of l9-ci-core release workflows are
forbidden here.
