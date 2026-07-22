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
output "id" { value=hcloud_server.this.id }
output "name" { value=hcloud_server.this.name }
output "ipv4_address" { value=hcloud_server.this.ipv4_address }
output "private_ip" { value=hcloud_server_network.this.ip }
