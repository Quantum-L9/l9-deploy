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
variable "server_type" { type=string }
variable "image" { type=string }
variable "location" { type=string }
variable "ssh_key_ids" { type=list(number) }
variable "network_id" { type=number }
variable "private_ip" { type=string }
variable "firewall_ids" { type=list(number); default=[] }
variable "placement_group_id" { type=number; default=null }
variable "user_data" { type=string; default=null }
variable "labels" { type=map(string); default={} }
variable "public_net_enabled" { type=bool; default=true }
variable "prevent_destroy" { type=bool; default=true }
