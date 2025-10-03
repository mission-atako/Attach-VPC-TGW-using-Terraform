module "key" {
    source = "../../../modules/transit-gateway-attachment"
    region = var.region
    name   = var.name
    tgw_id = var.tgw_id
    vpc_id = var.vpc
    subnet_ids = var.subnet
    vpc_route_table_ids = var.vpc_route_table_ids
    remote_cidrs = var.remote_cidrs
}