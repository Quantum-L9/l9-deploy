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
variable "name" { type=string }
variable "type" { type=string; default="spread" }
variable "labels" { type=map(string); default={} }
