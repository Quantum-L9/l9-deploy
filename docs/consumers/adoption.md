<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- documentation
- consumers
tags:
- L9_META
- deployment-platform
owner: platform
status: active
/L9_META -->
# Consumer Adoption

Consumer repositories remain thin. They own application source, Dockerfile, health behavior,
migration commands, and `.l9/deployment.yaml`; they do not own deployment infrastructure or the
deployment runner.

Use an explicitly authorized `l9-ci-core` release interface for the consumer's release channel.
The current container-release implementation is owned at
`Quantum-L9/l9-ci-core/.github/actions/container-release`; do not copy that action or invent a
`.github/workflows/container-release.yml` interface in either the consumer or `l9-deploy`.

Register the canonical deployment profile path and environment placement in
`fleet/registry.yaml`. Before production use, prove staging deployment, health, rollback, and any
required backup/restore behavior.
