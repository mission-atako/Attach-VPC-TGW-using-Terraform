module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1"

  name = "${var.env}-vpc"
  cidr = var.vpc_cidr

  enable_dns_hostnames               = true
  create_database_subnet_route_table = false
  create_database_nat_gateway_route  = false

  ## Flow Logs
  enable_flow_log                                 = true
  create_flow_log_cloudwatch_iam_role             = true
  create_flow_log_cloudwatch_log_group            = true
  flow_log_traffic_type                           = "ALL"
  flow_log_cloudwatch_log_group_retention_in_days = 30

  ## Subnets 
  azs                    = local.azs
  private_subnets        = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 3, (k * 2))]
  public_subnets         = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 4, ((k * 4) + 2))]
  intra_subnets             = [for k, v in local.azs : cidrsubnet(var.vpc_cidr, 5, ((k * 8) + 6))]
  private_subnet_suffix  = "egress"
  public_subnet_suffix   = "public"
  intra_subnet_suffix    = "firewall"

  ## Nat Gateway
  enable_nat_gateway     = true
  single_nat_gateway     = true
  one_nat_gateway_per_az = false

  ### Tags ###
  public_subnet_tags          = { Tier = "Public" }
  public_route_table_tags     = { Tier = "Public" }
  private_subnet_tags         = { Tier = "Egress" }
  private_route_table_tags    = { Tier = "Egress" }
  intra_subnet_tags         = { Tier = "Firewall" }
  intra_route_table_tags    = { Tier = "Firewall" }
  igw_tags                    = { Name = "${var.env}-igw" }
  nat_gateway_tags            = { Name = "${var.env}-ngw" }
  nat_eip_tags                = { Name = "${var.env}-ngw" }
  default_network_acl_tags    = { Name = "${var.env}-default" }
  default_security_group_tags = { Name = "${var.env}-default" }

  tags = {
    Terraform   = "true"
    Environment = var.env
  }

}
