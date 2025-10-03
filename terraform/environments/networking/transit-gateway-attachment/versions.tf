terraform {
  backend "s3" {
    bucket         = "backend-statefile4terraform"
    key            = "tgw-attachment/terraform.tfstate"
    region         = "us-west-2"
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 6.0.0"
    }
  }
}