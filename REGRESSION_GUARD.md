<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- validation
tags:
- L9_META
- regression-guard
owner: platform
status: active
/L9_META -->
# Regression Guard

The repository must fail validation when any of these regressions appear:

- a live trust surface references the retired repository identity;
- repository guard or approval verification accepts a non-canonical repository;
- a new repository release receipt names a non-canonical repository;
- a release/archive/package uses the retired live identity;
- executable `l9-ci-core` release orchestration is copied into `l9-deploy`;
- workflow-level OIDC is granted;
- an approval job receives OIDC;
- a job receives OIDC without the approved Infisical exchange;
- a public pull-request workflow targets the self-hosted deployment runner;
- the runner desired repository differs from `Quantum-L9/l9-deploy`;
- an infrastructure apply is not bound to the exact approved plan;
- mutable image tags enter deployment execution;
- a canonical receipt can be replaced;
- generated release artifacts are treated as current proof without regeneration.

Persisted OpenTofu state keys are compatibility data and must not be generalized into repository
identity.
