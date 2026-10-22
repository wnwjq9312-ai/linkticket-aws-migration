# ==========================================================
# Existing LINKTICKET VPC
# ==========================================================

data "aws_vpc" "linkticket" {
  filter {
    name   = "cidr-block"
    values = ["10.0.0.0/16"]
  }

  filter {
    name   = "tag:Name"
    values = ["linkticket-prd-vpc"]
  }
}

# ==========================================================
# Private APP Subnets
# ==========================================================

data "aws_subnet" "app_a" {
  vpc_id = data.aws_vpc.linkticket.id

  filter {
    name   = "tag:Name"
    values = ["linkticket-prd-app-a"]
  }

  availability_zone = "ap-northeast-2a"
}

data "aws_subnet" "app_c" {
  vpc_id = data.aws_vpc.linkticket.id

  filter {
    name   = "tag:Name"
    values = ["linkticket-prd-app-c"]
  }

  availability_zone = "ap-northeast-2c"
}

# ==========================================================
# Existing Security Groups
# ==========================================================

data "aws_security_group" "web" {
  vpc_id = data.aws_vpc.linkticket.id

  filter {
    name   = "group-name"
    values = ["linkticket-prd-web-sg"]
  }
}

data "aws_security_group" "was" {
  vpc_id = data.aws_vpc.linkticket.id

  filter {
    name   = "group-name"
    values = ["linkticket-prd-was-sg"]
  }
}
