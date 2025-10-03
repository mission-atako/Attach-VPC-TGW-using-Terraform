region = "us-west-2"            # your region
name   = "prod-app1"

tgw_id = "tgw-080386f6a9382f91a"  # existing TGW
vpc_id = "vpc-0e4f2f3acddde5586"  # VPC to attach

# One subnet ID per AZ you want attached (usually private subnets)
subnet_ids = [
  "subnet-0948351169f34807a",   # us-west-2a
 
]

# OPTIONAL: add routes in your VPC to send traffic to TGW
vpc_route_table_ids = [
  "project-rtb-private1-us-west-2a"
]
remote_cidrs = [
  # e.g., "10.20.0.0/16", "172.16.0.0/12"
]
