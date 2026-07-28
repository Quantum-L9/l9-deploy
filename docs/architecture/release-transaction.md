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

## Configuration identity

A release is identified by both immutable image digest and release-owned runtime configuration.
Candidate preparation creates `releases/<plan-digest>/runtime.env` atomically with mode `0600`.
Migration and Compose receive that same path. Promotion publishes image and configuration identity as
one state transition. A pre-promotion failure leaves active state unchanged and deletes only the
candidate release.

Rollback preflights the previous configuration identity and env-file existence, restores the previous
image using that env, verifies health, and only then restores the state pointer. Database restoration
is not part of this transaction.
