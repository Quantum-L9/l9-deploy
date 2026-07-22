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
# Bootstrap Management Runner

Provision management with OpenTofu, generate inventory, run bootstrap and harden playbooks, obtain a short-lived repository runner registration token, supply the pinned runner tarball SHA-256, run configure-runner, and verify host conformance. Never reuse the registration token or attach this runner to public repositories.

## Evidence to retain

Retain the source SHA, plan digest, image digest, approval receipt, command output, resulting receipt, and operator identity.
