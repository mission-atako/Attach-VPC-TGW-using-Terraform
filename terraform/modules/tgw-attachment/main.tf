# Attach your VPC to the Transit Gateway
resource "aws_ec2_transit_gateway_vpc_attachment" "this" {
  vpc_id             = var.vpc_id
  transit_gateway_id = var.tgw_id

  # IMPORTANT: one subnet **per AZ** you want attached (typically private subnets)
  subnet_ids = var.subnet_ids

  # Common toggles
  dns_support                         = "enable"
  ipv6_support                        = "disable"
  appliance_mode_support              = "disable"
  transit_gateway_default_route_table_association = var.associate_with_default_tgw_rt ? "enable" : "disable"
  transit_gateway_default_route_table_propagation = var.propagate_to_default_tgw_rt ? "enable" : "disable"

  tags = merge(
    {
      Name = "${var.name}-tgw-attachment"
    },
    var.tags
  )
}

# OPTIONAL: add routes in your VPC route tables that point selected CIDRs to the TGW
# If you don't need this yet, leave var.vpc_route_table_ids or var.remote_cidrs empty.
locals {
  rt_cidr_pairs = {
    for pair in setproduct(var.vpc_route_table_ids, var.remote_cidrs) :
    "${pair[0]}|${pair[1]}" => { rt_id = pair[0], cidr = pair[1] }
  }
}

resource "aws_route" "to_tgw" {
  for_each = local.rt_cidr_pairs

  route_table_id         = each.value.rt_id
  destination_cidr_block = each.value.cidr
  transit_gateway_id     = var.tgw_id

  # ensure the attachment exists first
  depends_on = [aws_ec2_transit_gateway_vpc_attachment.this]
}
