
output "web_instance_ids" {
  description = "WEB EC2 instance IDs"
  value       = aws_instance.web[*].id
}

output "web_private_ips" {
  description = "WEB EC2 private IP addresses"
  value       = aws_instance.web[*].private_ip
}

output "was_instance_ids" {
  description = "WAS EC2 instance IDs"
  value       = aws_instance.was[*].id
}

output "was_private_ips" {
  description = "WAS EC2 private IP addresses"
  value       = aws_instance.was[*].private_ip
}
