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
variable "hcloud_token" { type=string; sensitive=true }
variable "network_id" { type=number }
variable "management_cidr" { type=string; default="10.90.1.0/24" }
variable "location" { type=string; default="fsn1" }
variable "ssh_key_ids" { type=list(number) }
variable "servers" {
  type=map(object({ private_ip=string, server_type=string, public_net_enabled=optional(bool,true), roles=set(string) }))
  default={}
}
