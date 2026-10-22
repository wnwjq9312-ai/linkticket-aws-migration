variable "project_name" {
  description = "Project name"
  type        = string
  default     = "LINKTICKET"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "prd"
}

variable "ami_id" {
  description = "AMI ID for WEB and WAS EC2 instances"
  type        = string
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}





variable "instance_profile_name" {
  description = "IAM Instance Profile for EC2 SSM access"
  type        = string
}

variable "web_instance_count" {
  description = "Number of WEB EC2 instances"
  type        = number
  default     = 1

  validation {
    condition     = var.web_instance_count >= 1 && var.web_instance_count <= 2
    error_message = "WEB instance count must be 1 or 2."
  }
}

variable "was_instance_count" {
  description = "Number of WAS EC2 instances"
  type        = number
  default     = 1

  validation {
    condition     = var.was_instance_count >= 1 && var.was_instance_count <= 2
    error_message = "WAS instance count must be 1 or 2."
  }
}
