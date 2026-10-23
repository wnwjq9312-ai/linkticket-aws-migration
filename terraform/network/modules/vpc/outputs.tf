output "vpc_id" {
  description = "VPC ID."
  value       = aws_vpc.this.id
}

output "vpc_cidr" {
  description = "VPC CIDR."
  value       = aws_vpc.this.cidr_block
}

output "internet_gateway_id" {
  description = "Internet Gateway ID."
  value       = aws_internet_gateway.this.id
}

output "subnet_ids" {
  description = "Subnet IDs keyed by subnet role."
  value       = { for key, subnet in aws_subnet.this : key => subnet.id }
}

output "subnet_cidrs" {
  description = "Subnet CIDRs keyed by subnet role."
  value       = { for key, subnet in local.subnets : key => subnet.cidr }
}

output "nat_gateway_enabled" {
  description = "Whether NAT Gateway creation is enabled."
  value       = var.enable_nat_gateway
}

output "security_group_ids" {
  description = "Named LinkTicket security-group IDs keyed by role."
  value = {
    alb        = aws_security_group.alb.id
    web        = aws_security_group.web.id
    was        = aws_security_group.was.id
    redis      = aws_security_group.redis.id
    rds        = aws_security_group.rds.id
    efs        = aws_security_group.efs.id
    monitoring = aws_security_group.monitoring.id
  }
}

output "default_security_group_id" {
  description = "VPC default security group ID; rules are emptied and workloads should not use it."
  value       = aws_default_security_group.this.id
}
