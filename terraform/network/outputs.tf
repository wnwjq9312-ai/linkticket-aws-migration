output "vpc_id" {
  description = "VPC ID from the VPC module."
  value       = module.vpc.vpc_id
}

output "subnet_ids" {
  description = "Subnet IDs keyed by role."
  value       = module.vpc.subnet_ids
}

output "subnet_cidrs" {
  description = "Subnet CIDRs keyed by role."
  value       = module.vpc.subnet_cidrs
}

output "security_group_ids" {
  description = "Named security-group IDs keyed by role."
  value       = module.vpc.security_group_ids
}

output "default_security_group_id" {
  description = "Default SG ID (do not attach workloads to it)."
  value       = module.vpc.default_security_group_id
}
