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
# Rollback

Use the rollback workflow with project, environment, plan digest, and approval receipt. The engine restores only the previous verified digest from runtime state. Confirm rollback receipt PASS and run status plus health verification.

## Evidence to retain

Retain the source SHA, plan digest, image digest, approval receipt, command output, resulting receipt, and operator identity.
