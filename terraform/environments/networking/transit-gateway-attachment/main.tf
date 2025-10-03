module "key" {

    source = "../../../modules/tgw-attachment"
    region = var.region
    name   = var.name
    tgw_id = var.tgw_id
    vpc_id = var.vpc_id
    subnet_ids = var.subnet_ids
    vpc_route_table_ids = var.vpc_route_table_ids
    remote_cidrs = var.remote_cidrs
}