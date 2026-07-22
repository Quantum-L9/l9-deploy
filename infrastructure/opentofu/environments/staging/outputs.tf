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
output "servers" { value={for key,value in module.server : key=>{id=value.id,private_ip=value.private_ip,public_ip=value.ipv4_address}} }
