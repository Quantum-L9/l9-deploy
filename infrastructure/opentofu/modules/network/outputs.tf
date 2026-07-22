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
output "id" { value = hcloud_network.this.id }
output "name" { value = hcloud_network.this.name }
output "subnet_ids" { value = { for key, value in hcloud_network_subnet.this : key => value.id } }
