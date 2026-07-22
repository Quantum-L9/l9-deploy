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
variable "zone_name" { type=string }
variable "records" { type=map(object({ name=string, type=string, value=string, ttl=optional(number,300) })) }
