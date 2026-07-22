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
variable "name" { type = string }
variable "rules" { type = list(object({ direction=string, protocol=string, port=optional(string), source_ips=optional(list(string)), destination_ips=optional(list(string)), description=optional(string) })) }
variable "labels" { type=map(string); default={} }
