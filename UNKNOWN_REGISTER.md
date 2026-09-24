<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- validation
tags:
- L9_META
- unknown-register
owner: platform
status: active
/L9_META -->
# Unknown Register

Only unresolved evidence capable of changing operational readiness belongs here.

- **EXT-001 GitHub visibility:** repository policy requires private visibility. The actual external
  setting must be verified private before production authorization.
- **EXT-002 OIDC claim policy:** positive exchange for `Quantum-L9/l9-deploy` and negative rejection
  of the retired repository identity have not been established by repository source alone.
- **EXT-003 Runner availability:** the dedicated runner must be proven online, repository-scoped to
  `Quantum-L9/l9-deploy`, and labeled `l9-deployment,hetzner-private`.
- **EXT-004 Infrastructure execution:** current management, staging, and production OpenTofu
  plan/drift evidence is required.
- **EXT-005 Fleet conformance:** one current successful conformance run is required after runner
  recovery.
- **EXT-006 Staging transaction:** one current immutable-digest deployment with health evidence is
  required.
- **EXT-007 Rollback rehearsal:** rollback of the staged release, including release-owned
  configuration, must be proven.
- **EXT-008 Recovery:** required backup verification and restore testing must be proven for stateful
  consumers before production use.

Historical validation reports do not resolve these Unknowns.
