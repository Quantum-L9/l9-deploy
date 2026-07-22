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
output "id" { value=hcloud_load_balancer.this.id }
output "ipv4" { value=hcloud_load_balancer.this.ipv4 }
