# --- L9_META ---
# l9_schema: 1
# origin: l9-deployment-platform
# layer:
# - repository
# tags:
# - L9_META
# - deployment-platform
# owner: platform
# status: active
# --- /L9_META ---
provider "hcloud" { token=var.hcloud_token }
module "network" {
  source="../../modules/network"
  name="l9-management"
  ip_range="10.90.0.0/16"
  subnets={ management={ip_range="10.90.1.0/24",network_zone=var.network_zone}, staging={ip_range="10.90.10.0/24",network_zone=var.network_zone}, production={ip_range="10.90.20.0/24",network_zone=var.network_zone} }
  labels={managed_by="l9-deployment-platform"}
}
module "runner_firewall" {
  source="../../modules/firewall"
  name="l9-deploy-runner"
  rules=concat([
    {direction="out",protocol="tcp",port="443",destination_ips=["0.0.0.0/0","::/0"],description="GitHub, GHCR, Infisical, and APIs"},
    {direction="out",protocol="tcp",port="22",destination_ips=["10.90.0.0/16"],description="Private fleet SSH"},
    {direction="out",protocol="icmp",destination_ips=["10.90.0.0/16"],description="Private fleet diagnostics"}
  ], [for cidr in var.operator_source_cidrs : {direction="in",protocol="tcp",port="22",source_ips=[cidr],description="Approved operator SSH"}])
  labels={managed_by="l9-deployment-platform"}
}
module "runner" {
  source="../../modules/server"
  name="l9-deploy-01"
  server_type=var.runner_server_type
  image="ubuntu-24.04"
  location=var.location
  ssh_key_ids=var.ssh_key_ids
  network_id=module.network.id
  private_ip=var.runner_private_ip
  firewall_ids=[module.runner_firewall.id]
  labels={role="management",managed_by="l9-deployment-platform"}
  public_net_enabled=true
  prevent_destroy=true
}
