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
variable "ssh_key_ids" { type=list(number) }
variable "location" { type=string; default="fsn1" }
variable "network_zone" { type=string; default="eu-central" }
variable "runner_server_type" { type=string; default="cpx22" }
variable "runner_private_ip" { type=string; default="10.90.1.10" }
variable "operator_source_cidrs" { type=list(string); default=[] }
