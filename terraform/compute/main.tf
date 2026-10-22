
locals {
  name_prefix = "${lower(var.project_name)}-${var.environment}"
}

# ==========================================================
# WEB EC2
# Initial: Private APP AZ-a
# Scale-out: AZ-a / AZ-c
# ==========================================================

resource "aws_instance" "web" {
  count = var.web_instance_count

  ami           = var.ami_id
  instance_type = var.instance_type

  subnet_id = var.web_subnet_ids[
    count.index % length(var.web_subnet_ids)
  ]

  vpc_security_group_ids = [var.web_sg_id]
  iam_instance_profile   = var.instance_profile_name

  associate_public_ip_address = false

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

  tags = {
    Name        = "${local.name_prefix}-web-${count.index + 1}"
    Project     = var.project_name
    Environment = var.environment
    Role        = "WEB"
    ManagedBy   = "Terraform"
  }
}

# ==========================================================
# WAS EC2
# Initial: Private APP AZ-c
# Scale-out: AZ-c / AZ-a
# ==========================================================

resource "aws_instance" "was" {
  count = var.was_instance_count

  ami           = var.ami_id
  instance_type = var.instance_type

  subnet_id = var.was_subnet_ids[
    count.index % length(var.was_subnet_ids)
  ]

  vpc_security_group_ids = [var.was_sg_id]
  iam_instance_profile   = var.instance_profile_name

  associate_public_ip_address = false

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    volume_size           = 20
    volume_type           = "gp3"
    encrypted             = true
    delete_on_termination = true
  }

  tags = {
    Name        = "${local.name_prefix}-was-${count.index + 1}"
    Project     = var.project_name
    Environment = var.environment
    Role        = "WAS"
    ManagedBy   = "Terraform"
  }
}
