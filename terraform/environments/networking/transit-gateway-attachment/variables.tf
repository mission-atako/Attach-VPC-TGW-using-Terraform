variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "name" {
  description = "Base name for tags"
  type        = string
  default     = "example"
}

variable "tags" {
  description = "Extra tags for all resources"
  type        = map(string)
  default     = {}
}

variable "tgw_id" {
  description = "Existing Transit Gateway ID (tgw-xxxxxxxxxxxxxxxxx)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID to attach (vpc-xxxxxxxxxxxxxxxxx)"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs in distinct AZs to use for the attachment (one per AZ)"
  type        = list(string)
}

variable "associate_with_default_tgw_rt" {
  description = "Associate attachment with the TGW's default route table"
  type        = bool
  default     = true
}

variable "propagate_to_default_tgw_rt" {
  description = "Propagate routes from this attachment to the TGW's default route table"
  type        = bool
  default     = true
}

# Optional: add VPC routes to send traffic to TGW
variable "vpc_route_table_ids" {
  description = "VPC route tables to update with routes to the TGW"
  type        = list(string)
  default     = []
}

variable "remote_cidrs" {
  description = "CIDR blocks reachable over the TGW (e.g., other VPCs or on-prem)"
  type        = list(string)
  default     = []
}
