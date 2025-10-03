module "tgw" {
  source  = "terraform-aws-modules/transit-gateway/aws"
  version = "~> 2.0"

  name                                   = "${var.env}-tgw"
  description                            = "${var.env} tgw"
  enable_auto_accept_shared_attachments  = true
  enable_default_route_table_propagation = true
  share_tgw                              = true
  ram_principals = [data.aws_organizations_organization.org.arn]
  vpc_attachments = {}
}

