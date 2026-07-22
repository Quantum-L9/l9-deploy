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
resource "hcloud_network" "this" { name = var.name; ip_range = var.ip_range; labels = var.labels }
resource "hcloud_network_subnet" "this" { for_each = var.subnets; network_id = hcloud_network.this.id; type = each.value.type; network_zone = each.value.network_zone; ip_range = each.value.ip_range }
