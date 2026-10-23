# S3 Gateway VPC Endpoint for private APP subnets.
# This is additive: it does not modify the VPC, subnets, route tables, or NAT resources.
# AWS automatically adds the S3 prefix-list route to the listed route tables.
# The S3-specific route is more specific than 0.0.0.0/0, so it can coexist with NAT routes.

resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.this.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"

  route_table_ids = [
    aws_route_table.app["app_a"].id,
    aws_route_table.app["app_c"].id,
  ]

  tags = {
    Name = "${var.project_name}-${var.environment}-s3-gateway-endpoint"
  }
}
