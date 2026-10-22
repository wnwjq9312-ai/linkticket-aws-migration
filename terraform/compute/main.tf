
locals {
  name_prefix = "${lower(var.project_name)}-${var.environment}"
}

resource "aws_instance" "web" {
  count = var.web_instance_count

  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.web_subnet_ids[count.index]
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
    Name = "${local.name_prefix}-web-${count.index + 1}"
    Role = "WEB"
  }
}

resource "aws_instance" "was" {
  count = var.was_instance_count

  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = var.was_subnet_ids[count.index]
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
    Name = "${local.name_prefix}-was-${count.index + 1}"
    Role = "WAS"
  }
}
