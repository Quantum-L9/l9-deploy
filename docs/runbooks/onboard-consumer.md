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
# Onboard Consumer

Render an adoption kit, commit `.l9/deployment.yaml` and the thin release workflow in the consumer, add the project and environment placement to `fleet/registry.yaml`, merge the public `l9-ci-core` release kernel, register it in `Quantum-L9/.github`, and validate a staging release before production.

## Evidence to retain

Retain the source SHA, plan digest, image digest, approval receipt, command output, resulting receipt, and operator identity.
