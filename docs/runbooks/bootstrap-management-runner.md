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

Use this path when the dedicated self-hosted runner is unavailable and therefore cannot repair itself
through `runner-maintenance.yml`.

1. Provision or reconcile management infrastructure with the approved OpenTofu plan.
2. Generate the Ansible inventory and establish trusted SSH access to the management host.
3. Obtain a fresh repository-scoped registration token for `Quantum-L9/l9-deploy`.
4. Verify the SHA-256 of the pinned GitHub Actions runner archive.
5. Export the runtime-only values and execute the bootstrap script:

```bash
export L9_RUNNER_REGISTRATION_TOKEN='<short-lived-token>'
export L9_RUNNER_SHA256='<64-hex-sha256>'
bash scripts/bootstrap-runner.sh ansible/inventories/generated/hosts.yml
```

The runner role fails closed if an existing `.runner` registration does not identify
`https://github.com/Quantum-L9/l9-deploy`. Do not reuse a token or bypass that scope check.

After bootstrap, verify host conformance and confirm the GitHub runner is online with the required
`l9-deployment` and `hetzner-private` labels before relying on scheduled fleet jobs.

## Evidence to retain

Retain the source SHA, infrastructure plan digest, operator identity, runner archive SHA-256,
Ansible output, host-conformance result, and GitHub runner registration/label evidence.
