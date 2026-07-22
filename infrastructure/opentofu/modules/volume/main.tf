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
resource "hcloud_volume" "this" { name=var.name; size=var.size; location=var.location; server_id=var.server_id; format=var.format; delete_protection=var.delete_protection; labels=var.labels }
