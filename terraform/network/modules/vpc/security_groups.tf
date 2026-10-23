# LinkTicket security-group chain.
# All custom security groups use explicit standalone ingress/egress rule resources.
# The default security group is emptied as specified in the SG design workbook.

resource "aws_security_group" "alb" {
  name        = "${var.project_name}-${var.environment}-alb-sg"
  description = "Public entry point for HTTPS and HTTP-to-HTTPS redirect"
  vpc_id      = aws_vpc.this.id
  ingress     = []
  egress      = []

  tags = { Name = "${var.project_name}-${var.environment}-alb-sg" }
}

resource "aws_security_group" "web" {
  name        = "${var.project_name}-${var.environment}-web-sg"
  description = "WEB tier; accepts HTTP only from ALB"
  vpc_id      = aws_vpc.this.id
  ingress     = []
  egress      = []

  tags = { Name = "${var.project_name}-${var.environment}-web-sg" }
}

resource "aws_security_group" "was" {
  name        = "${var.project_name}-${var.environment}-was-sg"
  description = "WAS tier; accepts application traffic only from WEB"
  vpc_id      = aws_vpc.this.id
  ingress     = []
  egress      = []

  tags = { Name = "${var.project_name}-${var.environment}-was-sg" }
}

resource "aws_security_group" "redis" {
  name        = "${var.project_name}-${var.environment}-redis-sg"
  description = "Redis tier; accepts cache traffic only from WAS"
  vpc_id      = aws_vpc.this.id
  ingress     = []
  egress      = []

  tags = { Name = "${var.project_name}-${var.environment}-redis-sg" }
}

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Database tier; accepts database traffic only from WAS"
  vpc_id      = aws_vpc.this.id
  ingress     = []
  egress      = []

  tags = { Name = "${var.project_name}-${var.environment}-rds-sg" }
}

resource "aws_security_group" "efs" {
  name        = "${var.project_name}-${var.environment}-efs-sg"
  description = "EFS mount target; accepts NFS only from WEB"
  vpc_id      = aws_vpc.this.id
  ingress     = []
  egress      = []

  tags = { Name = "${var.project_name}-${var.environment}-efs-sg" }
}

resource "aws_security_group" "monitoring" {
  name        = "${var.project_name}-${var.environment}-monitoring-sg"
  description = "Prometheus/Grafana monitoring host; no inbound ports, use SSM port forwarding"
  vpc_id      = aws_vpc.this.id
  ingress     = []
  egress      = []

  tags = { Name = "${var.project_name}-${var.environment}-monitoring-sg" }
}

# The VPC default SG is created automatically by AWS. Manage it to remove all rules.
# Do not attach workloads to this group; use the named groups above instead.
resource "aws_default_security_group" "this" {
  vpc_id  = aws_vpc.this.id
  ingress = []
  egress  = []

  tags = { Name = "${var.project_name}-${var.environment}-default-sg" }
}

# -------------------- INGRESS --------------------

resource "aws_vpc_security_group_ingress_rule" "alb_https_from_internet" {
  security_group_id = aws_security_group.alb.id
  description       = "Public HTTPS entry point"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "alb_http_redirect_from_internet" {
  security_group_id = aws_security_group.alb.id
  description       = "HTTP listener redirects clients to HTTPS"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_ingress_rule" "web_from_alb" {
  security_group_id            = aws_security_group.web.id
  description                  = "ALB forwards HTTP requests and health checks to WEB"
  ip_protocol                  = "tcp"
  from_port                    = 80
  to_port                      = 80
  referenced_security_group_id = aws_security_group.alb.id
}

resource "aws_vpc_security_group_ingress_rule" "was_from_web" {
  security_group_id            = aws_security_group.was.id
  description                  = "WEB to Gunicorn/Django on TCP 8082"
  ip_protocol                  = "tcp"
  from_port                    = 8082
  to_port                      = 8082
  referenced_security_group_id = aws_security_group.web.id
}

resource "aws_vpc_security_group_ingress_rule" "redis_from_was" {
  security_group_id            = aws_security_group.redis.id
  description                  = "WAS to Redis cache/session service"
  ip_protocol                  = "tcp"
  from_port                    = 6379
  to_port                      = 6379
  referenced_security_group_id = aws_security_group.was.id
}

resource "aws_vpc_security_group_ingress_rule" "rds_from_was" {
  security_group_id            = aws_security_group.rds.id
  description                  = "WAS to RDS database"
  ip_protocol                  = "tcp"
  from_port                    = 3306
  to_port                      = 3306
  referenced_security_group_id = aws_security_group.was.id
}

resource "aws_vpc_security_group_ingress_rule" "efs_from_web" {
  security_group_id            = aws_security_group.efs.id
  description                  = "WEB mounts EFS over NFS"
  ip_protocol                  = "tcp"
  from_port                    = 2049
  to_port                      = 2049
  referenced_security_group_id = aws_security_group.web.id
}

resource "aws_vpc_security_group_ingress_rule" "web_node_exporter_from_monitoring" {
  security_group_id            = aws_security_group.web.id
  description                  = "Prometheus scrapes WEB node_exporter"
  ip_protocol                  = "tcp"
  from_port                    = 9100
  to_port                      = 9100
  referenced_security_group_id = aws_security_group.monitoring.id
}

resource "aws_vpc_security_group_ingress_rule" "web_nginx_exporter_from_monitoring" {
  security_group_id            = aws_security_group.web.id
  description                  = "Prometheus scrapes Nginx exporter"
  ip_protocol                  = "tcp"
  from_port                    = 9113
  to_port                      = 9113
  referenced_security_group_id = aws_security_group.monitoring.id
}

resource "aws_vpc_security_group_ingress_rule" "was_node_exporter_from_monitoring" {
  security_group_id            = aws_security_group.was.id
  description                  = "Prometheus scrapes WAS node_exporter"
  ip_protocol                  = "tcp"
  from_port                    = 9100
  to_port                      = 9100
  referenced_security_group_id = aws_security_group.monitoring.id
}

resource "aws_vpc_security_group_ingress_rule" "redis_node_exporter_from_monitoring" {
  security_group_id            = aws_security_group.redis.id
  description                  = "Prometheus scrapes Redis node_exporter"
  ip_protocol                  = "tcp"
  from_port                    = 9100
  to_port                      = 9100
  referenced_security_group_id = aws_security_group.monitoring.id
}

# -------------------- EGRESS --------------------
# Security groups are stateful, but explicit egress rules restrict new outbound connections.

resource "aws_vpc_security_group_egress_rule" "alb_to_web" {
  security_group_id            = aws_security_group.alb.id
  description                  = "ALB forwards requests and health checks to WEB"
  ip_protocol                  = "tcp"
  from_port                    = 80
  to_port                      = 80
  referenced_security_group_id = aws_security_group.web.id
}

resource "aws_vpc_security_group_egress_rule" "web_to_was" {
  security_group_id            = aws_security_group.web.id
  description                  = "WEB to WAS application port"
  ip_protocol                  = "tcp"
  from_port                    = 8082
  to_port                      = 8082
  referenced_security_group_id = aws_security_group.was.id
}

resource "aws_vpc_security_group_egress_rule" "web_to_efs" {
  security_group_id            = aws_security_group.web.id
  description                  = "WEB mounts EFS over NFS"
  ip_protocol                  = "tcp"
  from_port                    = 2049
  to_port                      = 2049
  referenced_security_group_id = aws_security_group.efs.id
}

resource "aws_vpc_security_group_egress_rule" "web_http_outbound" {
  security_group_id = aws_security_group.web.id
  description       = "Package repositories and HTTP services via configured route/NAT"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "web_https_outbound" {
  security_group_id = aws_security_group.web.id
  description       = "SSM, CloudWatch Agent, HTTPS services via configured route/NAT or endpoints"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "was_to_rds" {
  security_group_id            = aws_security_group.was.id
  description                  = "WAS to RDS database"
  ip_protocol                  = "tcp"
  from_port                    = 3306
  to_port                      = 3306
  referenced_security_group_id = aws_security_group.rds.id
}

resource "aws_vpc_security_group_egress_rule" "was_to_redis" {
  security_group_id            = aws_security_group.was.id
  description                  = "WAS to Redis cache/session service"
  ip_protocol                  = "tcp"
  from_port                    = 6379
  to_port                      = 6379
  referenced_security_group_id = aws_security_group.redis.id
}

resource "aws_vpc_security_group_egress_rule" "was_http_outbound" {
  security_group_id = aws_security_group.was.id
  description       = "Package repositories via configured route/NAT"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "was_https_outbound" {
  security_group_id = aws_security_group.was.id
  description       = "S3 public endpoint traffic, SSM, and CloudWatch via route/NAT or endpoints"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "redis_http_outbound" {
  security_group_id = aws_security_group.redis.id
  description       = "Package repositories via configured route/NAT"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "redis_https_outbound" {
  security_group_id = aws_security_group.redis.id
  description       = "SSM and HTTPS services via configured route/NAT or endpoints"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "monitoring_to_web_node_exporter" {
  security_group_id            = aws_security_group.monitoring.id
  description                  = "Prometheus scrapes WEB node_exporter"
  ip_protocol                  = "tcp"
  from_port                    = 9100
  to_port                      = 9100
  referenced_security_group_id = aws_security_group.web.id
}

resource "aws_vpc_security_group_egress_rule" "monitoring_to_web_nginx_exporter" {
  security_group_id            = aws_security_group.monitoring.id
  description                  = "Prometheus scrapes Nginx exporter"
  ip_protocol                  = "tcp"
  from_port                    = 9113
  to_port                      = 9113
  referenced_security_group_id = aws_security_group.web.id
}

resource "aws_vpc_security_group_egress_rule" "monitoring_to_was_node_exporter" {
  security_group_id            = aws_security_group.monitoring.id
  description                  = "Prometheus scrapes WAS node_exporter"
  ip_protocol                  = "tcp"
  from_port                    = 9100
  to_port                      = 9100
  referenced_security_group_id = aws_security_group.was.id
}

resource "aws_vpc_security_group_egress_rule" "monitoring_to_redis_node_exporter" {
  security_group_id            = aws_security_group.monitoring.id
  description                  = "Prometheus scrapes Redis node_exporter"
  ip_protocol                  = "tcp"
  from_port                    = 9100
  to_port                      = 9100
  referenced_security_group_id = aws_security_group.redis.id
}

resource "aws_vpc_security_group_egress_rule" "monitoring_http_outbound" {
  security_group_id = aws_security_group.monitoring.id
  description       = "Package repositories via configured route/NAT"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
  cidr_ipv4         = "0.0.0.0/0"
}

resource "aws_vpc_security_group_egress_rule" "monitoring_https_outbound" {
  security_group_id = aws_security_group.monitoring.id
  description       = "SSM and CloudWatch API access via route/NAT or endpoints"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
  cidr_ipv4         = "0.0.0.0/0"
}
