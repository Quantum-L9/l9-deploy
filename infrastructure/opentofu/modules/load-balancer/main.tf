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
resource "hcloud_load_balancer" "this" { name=var.name; load_balancer_type=var.load_balancer_type; location=var.location; labels=var.labels }
resource "hcloud_load_balancer_network" "this" { load_balancer_id=hcloud_load_balancer.this.id; network_id=var.network_id }
resource "hcloud_load_balancer_service" "this" { load_balancer_id=hcloud_load_balancer.this.id; protocol="tcp"; listen_port=var.listen_port; destination_port=var.destination_port; health_check { protocol="tcp"; port=var.destination_port; interval=15; timeout=10; retries=3 } }
resource "hcloud_load_balancer_target" "server" { for_each=toset([for id in var.targets : tostring(id)]); type="server"; load_balancer_id=hcloud_load_balancer.this.id; server_id=tonumber(each.value); use_private_ip=true }
