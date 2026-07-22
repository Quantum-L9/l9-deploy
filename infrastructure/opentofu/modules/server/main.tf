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
resource "hcloud_server" "this" {
  name = var.name
  server_type = var.server_type
  image = var.image
  location = var.location
  ssh_keys = var.ssh_key_ids
  firewall_ids = var.firewall_ids
  placement_group_id = var.placement_group_id
  user_data = var.user_data
  labels = var.labels
  public_net { ipv4_enabled = var.public_net_enabled; ipv6_enabled = var.public_net_enabled }
  lifecycle { prevent_destroy = var.prevent_destroy }
}
resource "hcloud_server_network" "this" { server_id=hcloud_server.this.id; network_id=var.network_id; ip=var.private_ip }
