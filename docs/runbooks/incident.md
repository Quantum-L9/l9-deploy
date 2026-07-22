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
# Incident

Freeze environment concurrency, preserve workflow artifacts and receipts, capture runtime state, stop further dispatches, restore the previous verified digest when safe, rotate exposed credentials, reconcile host state, and record the incident and recovery evidence.

## Evidence to retain

Retain the source SHA, plan digest, image digest, approval receipt, command output, resulting receipt, and operator identity.
