variable "aws_region" {
  description = "AWS region. Seoul is ap-northeast-2."
  type        = string
  default     = "ap-northeast-2"
}

variable "project_name" {
  description = "Resource name prefix."
  type        = string
  default     = "linkticket"
}

variable "environment" {
  description = "Environment name."
  type        = string
  default     = "prd"
}

variable "vpc_cidr" {
  description = "VPC IPv4 CIDR."
  type        = string
  default     = "10.0.0.0/16"

  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr must be a valid IPv4 CIDR block."
  }
}

variable "enable_nat_gateway" {
  description = "Enable one NAT Gateway in public-a. NAT Gateway and EIP can incur charges."
  type        = bool
  default     = false
}
