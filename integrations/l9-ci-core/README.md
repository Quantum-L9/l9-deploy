<!-- L9_META
l9_schema: 1
origin: l9-deployment-platform
layer:
- repository
tags:
- L9_META
- deployment-platform
owner: platform
status: active
/L9_META -->
# l9-ci-core integration

`container-release.yml` is the complete proposed reusable kernel for `Quantum-L9/l9-ci-core`.
It validates the consumer, runs the consumer-owned verification command, builds exactly one OCI
image, publishes it to GHCR by immutable digest, attaches SBOM and provenance attestations, and
submits a bounded deployment request to the private deployment control plane.

The authoritative copy must be reviewed and merged in `l9-ci-core`, published under its normal
`@v1` compatibility discipline, and listed in the organization workflow interface registry.
Consumer repositories remain thin callers and never receive access to the deployment runner.
