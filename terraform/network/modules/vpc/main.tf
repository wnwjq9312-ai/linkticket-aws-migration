resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.project_name}-${var.environment}-vpc"
  }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.project_name}-${var.environment}-igw"
  }
}

locals {
  subnets = {
    public_a = {
      name = "${var.project_name}-${var.environment}-public-a"
      cidr = "10.0.1.0/24"
      az   = "${var.aws_region}a"
      tier = "Public"
    }
    public_c = {
      name = "${var.project_name}-${var.environment}-public-c"
      cidr = "10.0.2.0/24"
      az   = "${var.aws_region}c"
      tier = "Public"
    }
    app_a = {
      name = "${var.project_name}-${var.environment}-app-a"
      cidr = "10.0.11.0/24"
      az   = "${var.aws_region}a"
      tier = "Private-APP"
    }
    app_c = {
      name = "${var.project_name}-${var.environment}-app-c"
      cidr = "10.0.12.0/24"
      az   = "${var.aws_region}c"
      tier = "Private-APP"
    }
    db_a = {
      name = "${var.project_name}-${var.environment}-db-a"
      cidr = "10.0.21.0/24"
      az   = "${var.aws_region}a"
      tier = "Private-DB"
    }
    db_c = {
      name = "${var.project_name}-${var.environment}-db-c"
      cidr = "10.0.22.0/24"
      az   = "${var.aws_region}c"
      tier = "Private-DB"
    }
  }
}

resource "aws_subnet" "this" {
  for_each = local.subnets

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = false

  tags = {
    Name = each.value.name
    Tier = each.value.tier
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name = "${var.project_name}-${var.environment}-public-rt"
  }
}

resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this.id
}

resource "aws_route_table_association" "public" {
  for_each = toset(["public_a", "public_c"])

  subnet_id      = aws_subnet.this[each.value].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "app" {
  for_each = toset(["app_a", "app_c"])
  vpc_id   = aws_vpc.this.id

  tags = {
    Name = "${var.project_name}-${var.environment}-${each.value}-rt"
  }
}

resource "aws_route_table_association" "app" {
  for_each = aws_route_table.app

  subnet_id      = aws_subnet.this[each.key].id
  route_table_id = each.value.id
}

resource "aws_route_table" "db" {
  for_each = toset(["db_a", "db_c"])
  vpc_id   = aws_vpc.this.id

  tags = {
    Name = "${var.project_name}-${var.environment}-${each.value}-rt"
  }
}

resource "aws_route_table_association" "db" {
  for_each = aws_route_table.db

  subnet_id      = aws_subnet.this[each.key].id
  route_table_id = each.value.id
}

resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? 1 : 0
  domain = "vpc"

  tags = {
    Name = "${var.project_name}-${var.environment}-nat-eip"
  }
}

resource "aws_nat_gateway" "this" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.this["public_a"].id

  depends_on = [aws_internet_gateway.this]

  tags = {
    Name = "${var.project_name}-${var.environment}-nat-a"
  }
}

resource "aws_route" "app_nat" {
  for_each = var.enable_nat_gateway ? aws_route_table.app : {}

  route_table_id         = each.value.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.this[0].id
}
