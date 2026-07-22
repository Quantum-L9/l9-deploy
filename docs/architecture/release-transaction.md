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
# Release transaction

A release is accepted only after schema validation, source allowlist resolution, deployment-profile
digest verification, clean CI status verification, immutable GHCR digest verification, and an
environment lock. Planning is deterministic. The engine then performs backup, migration, image pull,
candidate start, health probes, state promotion, and receipt publication in that order.

Mutating steps are idempotency-bound by request digest. A failed candidate is stopped, the previous
verified image is restored, health is checked again, and a rollback receipt is emitted. Production
approval binds the operator, environment, and plan digest. A receipt is valid only when its schema and
canonical digest validate.
