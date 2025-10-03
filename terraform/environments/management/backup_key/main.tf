provider "aws" {
  region = "us-west-2"
}

module "key" {
  source = "../../../modules/org_kms_key"
  replica_regions = ["us-east-1"]
  aws_service     = "backup.amazonaws.com"
  alias           = "alias/backup-mrk"
}