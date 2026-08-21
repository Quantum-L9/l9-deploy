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
# Network topology

`l9-deploy-01` is the sole deployment runner. It connects outbound to GitHub and reaches managed
hosts through Hetzner private networking. Managed hosts accept administrative SSH only from the
runner private address. Public ingress is limited to application ports, normally 80 and 443. Host
`nftables` rules protect private interfaces because cloud firewalls do not replace host controls for
private east-west traffic.

Management, staging, and production occupy separate private subnets. The fleet registry is the
source of host identity, connection addresses, allowed source references, and environment approval
policy. No application workload or database runs on the deployment runner.

## Adopted hosts

A server with `lifecycle: adopted` is an existing host whose infrastructure and edge configuration
are not owned by the normal l9-deploy provisioning/configuration plane. It must publish an observed
`public_ip`; l9-deploy uses that address only as its SSH connection coordinate. No private address is
invented to satisfy the managed-host schema.

Adopted hosts are excluded from configuration-plan targets, and the runtime/Caddy Ansible path fails
closed before roles execute. Runtime mutation additionally requires the normal approval receipt plus
explicit `--allow-adopted-host-mutation`. This lets the fleet describe an existing protected host
without silently claiming authority to reconfigure it.
