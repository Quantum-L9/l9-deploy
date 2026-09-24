<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- documentation
- architecture
tags:
- L9_META
- deployment-platform
owner: platform
status: active
/L9_META -->
# Control-plane Boundaries

`l9-deploy` owns server provisioning, host reconciliation, approved release deployment, health
verification, rollback, and deployment receipts. It consumes canonical CI evidence and does not
normalize scanner output or reconstruct CI findings.

Consumer repositories own application source, Dockerfiles, health behavior, migration commands, and
their deployment profile. `l9-ci-core` owns release orchestration and bounded dispatch.
`l9-ci-sdk` owns canonical CI evidence. `Quantum-L9/.github` owns organization-level public
interface discovery.

The security contract requires the deployment repository to be private. The self-hosted runner is
repository-scoped to `Quantum-L9/l9-deploy` and must never execute consumer pull-request code.
A consumer communicates only through versioned, validated release requests containing exact source,
image, profile, and evidence identity.
