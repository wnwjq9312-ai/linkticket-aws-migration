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
