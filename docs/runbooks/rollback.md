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

Use the protected `Rollback` workflow with project, environment, incident ID, expected rollback-plan
digest, and approval evidence. Do not invoke ad hoc Compose commands during normal recovery.

## Preconditions

- Independent protected-environment approval is valid for the exact rollback plan.
- Previous runtime state includes image digest, release identity, and configuration identity.
- The previous release directory and its mode-`0600` `runtime.env` exist.
- The target host lock is held.

Missing configuration identity or a missing previous env file fails closed before remote mutation.

## Transaction

1. Select the previous digest-addressed release directory.
2. Start the previous immutable image using that release's `runtime.env`.
3. Verify executable health evidence.
4. Republish the previous image and configuration identity only after health succeeds.
5. Emit the rollback receipt and preserve the failed candidate for incident evidence unless cleanup
   policy explicitly classifies it as safe to remove.

Container rollback does not imply database rollback. Use the database restore runbook only when its
policy and evidence independently authorize restoration.

## Evidence to retain

Retain the source SHA, request digest, plan digest, current and previous image digests, current and
previous configuration identities, approval receipt and history, health evidence, command output,
rollback receipt, incident ID, and operator identity. Never retain the contents of `runtime.env` in
logs or artifacts.
