region = "us-west-2"            # your region
name   = "tgw-attachment"

tgw_id = ""  # existing TGW
vpc_id = ""  # VPC to attach

# One subnet ID per AZ you want attached (usually private subnets)
subnet_ids = [
  "subnet-0948351169f34807a",   # us-west-2a
  
 
]

# OPTIONAL: add routes in your VPC to send traffic to TGW
vpc_route_table_ids = [
  "rtb-06ebca3b3d7dd97ac", "rtb-08934097a3613e126"
]
remote_cidrs = [
  # e.g., "10.20.0.0/16", "172.16.0.0/12"
  "10.0.0.0/8", "0.0.0.0/0"
]
