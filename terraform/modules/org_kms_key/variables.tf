variable "aws_service" {
  description = "AWS service that can use this key"
  type        = string
}

variable "deletion_window_in_days" {
  description = "Deletion window for KMS key"
  default     = 30
  type        = number
}

variable "alias" {
  description = "Key alias"
  default     = ""
  type        = string
}

variable "replica_regions" {
  description = "Regions for replica keys"
  type        = list(string)
}
