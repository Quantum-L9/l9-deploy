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
resource "hcloud_zone" "this" { name=var.zone_name; mode="primary" }
resource "hcloud_zone_record" "this" { for_each=var.records; zone_id=hcloud_zone.this.id; name=each.value.name; type=each.value.type; value=each.value.value; ttl=each.value.ttl }
