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
module "firewall" {
 source="../../modules/firewall"
 name="l9-staging"
 rules=[
  {direction="in",protocol="tcp",port="22",source_ips=[var.management_cidr],description="Management runner SSH"},
  {direction="in",protocol="tcp",port="80",source_ips=["0.0.0.0/0","::/0"],description="HTTP ingress"},
  {direction="in",protocol="tcp",port="443",source_ips=["0.0.0.0/0","::/0"],description="HTTPS ingress"},
  {direction="out",protocol="tcp",port="443",destination_ips=["0.0.0.0/0","::/0"],description="Registry and APIs"},
  {direction="out",protocol="udp",port="53",destination_ips=["0.0.0.0/0","::/0"],description="DNS"},
  {direction="out",protocol="tcp",port="53",destination_ips=["0.0.0.0/0","::/0"],description="DNS"}
 ]
 labels={environment="staging",managed_by="l9-deployment-platform"}
}
module "server" {
 for_each=var.servers
 source="../../modules/server"
 name=each.key
 server_type=each.value.server_type
 image="ubuntu-24.04"
 location=var.location
 ssh_key_ids=var.ssh_key_ids
 network_id=var.network_id
 private_ip=each.value.private_ip
 firewall_ids=[module.firewall.id]
 labels=merge({environment="staging",managed_by="l9-deployment-platform"},{for role in each.value.roles : "role-${role}"=>"true"})
 public_net_enabled=each.value.public_net_enabled
 prevent_destroy=true
}
