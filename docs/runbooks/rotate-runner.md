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
# Rotate Runner

Create a fresh short-lived registration token, verify the approved runner archive checksum, run runner-maintenance, confirm repository scope and required labels, revoke obsolete credentials, and verify no consumer workflow can target the runner.

## Evidence to retain

Retain the source SHA, plan digest, image digest, approval receipt, command output, resulting receipt, and operator identity.
