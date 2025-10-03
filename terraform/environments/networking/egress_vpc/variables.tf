variable "env" {
  type = string
  description = "Name of environment"
}

variable "region" {
  type = string
  description = "Region for deployment"
}

variable "vpc_cidr" {
  type = string
}
