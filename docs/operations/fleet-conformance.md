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
# Fleet conformance

Fleet conformance compares every registered host with its required user, SSH, firewall, Docker,
time-sync, unattended-upgrade, storage, runner, and release-directory expectations. Reports expire
according to each server profile. Unknown or unreachable hosts are not healthy. Run conformance after
provisioning, configuration changes, runner rotation, and on the scheduled workflow.
