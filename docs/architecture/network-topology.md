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
source of host identity, private addresses, allowed source references, and environment approval
policy. No application workload or database runs on the deployment runner.
