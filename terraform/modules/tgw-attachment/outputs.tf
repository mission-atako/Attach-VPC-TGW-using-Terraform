output "tgw_vpc_attachment_id" {
  value       = aws_ec2_transit_gateway_vpc_attachment.this.id
  description = "The ID of the TGW VPC attachment"
}

