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
# l9-ci-core integration

`Quantum-L9/l9-ci-core` is the sole owner of container release orchestration and the
`l9.release.requested.v1` dispatch implementation.

This repository keeps only the consumer-side integration contract at
`.l9/integration-contracts/ci-core.contract.yaml`. It must not carry a copied executable
container-release workflow because that would create a competing source of truth.

`l9-deploy` consumes the bounded release request, validates canonical CI evidence, and owns
deployment mutation and receipts. Consumer repositories remain thin callers and never receive
deployment-runner credentials.
