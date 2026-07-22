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
resource "hcloud_firewall" "this" {
  name = var.name
  labels = var.labels
  dynamic "rule" {
    for_each = var.rules
    content { direction=rule.value.direction; protocol=rule.value.protocol; port=try(rule.value.port,null); source_ips=try(rule.value.source_ips,null); destination_ips=try(rule.value.destination_ips,null); description=try(rule.value.description,null) }
  }
}
