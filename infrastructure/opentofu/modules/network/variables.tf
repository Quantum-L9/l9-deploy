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
variable "ip_range" { type = string }
variable "subnets" {
  type = map(object({ ip_range = string, network_zone = string, type = optional(string, "cloud") }))
}
variable "labels" { type = map(string); default = {} }
