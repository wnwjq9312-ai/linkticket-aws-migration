# ==========================================================
# Existing EICE Security Group (Managed by Network Team)
# ==========================================================

data "aws_security_group" "eice" {
  vpc_id = data.aws_vpc.linkticket.id

  filter {
    name   = "group-name"
    values = ["linkticket-prd-eice-sg"]
  }
}

# ==========================================================
# EC2 Instance Connect Endpoint
# ==========================================================

resource "aws_ec2_instance_connect_endpoint" "linkticket" {
  subnet_id          = data.aws_subnet.app_a.id
  security_group_ids = [data.aws_security_group.eice.id]

  preserve_client_ip = false

  tags = {
    Name        = "${local.name_prefix}-eice"
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}
