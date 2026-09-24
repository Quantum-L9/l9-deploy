<!-- L9_META
l9_schema: 1
origin: l9-deploy
layer:
- documentation
- operations
tags:
- L9_META
- deployment-platform
owner: platform
status: active
/L9_META -->
# Fleet Conformance

Fleet conformance compares registered hosts with required user, SSH, firewall, Docker, time-sync,
unattended-upgrade, storage, runner, and release-directory expectations.

The scheduled workflow runs on the dedicated self-hosted runner. A queued or cancelled job is not
conformance evidence. If the runner is unavailable, recover it through
`docs/runbooks/bootstrap-management-runner.md`, confirm canonical repository scope and required
labels, then rerun conformance.

Unknown or unreachable hosts are not healthy. Run conformance after provisioning, host
configuration changes, runner rotation, and on the scheduled workflow. Retain the workflow run and
generated conformance artifact as revision-bound evidence.
