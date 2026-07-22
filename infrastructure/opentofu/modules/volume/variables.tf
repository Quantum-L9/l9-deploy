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
variable "size" { type=number }
variable "location" { type=string }
variable "server_id" { type=number; default=null }
variable "format" { type=string; default="ext4" }
variable "delete_protection" { type=bool; default=true }
variable "labels" { type=map(string); default={} }
