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

Use `runner-maintenance.yml` only while the dedicated runner is healthy enough to execute the
maintenance job. If it is offline or jobs remain queued, use the out-of-band bootstrap runbook
instead.

For direct operator rotation, export a fresh repository-scoped registration token and the verified
runner archive SHA-256:

```bash
export L9_RUNNER_REGISTRATION_TOKEN='<short-lived-token>'
export L9_RUNNER_SHA256='<64-hex-sha256>'
bash scripts/rotate-runner.sh
```

The configuration must target `Quantum-L9/l9-deploy`. After rotation, confirm the runner is online
and carries `l9-deployment` and `hetzner-private` labels. Revoke obsolete credentials and verify
that no consumer pull-request workflow can target this runner.

## Evidence to retain

Retain the source SHA, approval receipt when the workflow path is used, operator identity, runner
archive SHA-256, Ansible output, and GitHub runner registration/label evidence.
