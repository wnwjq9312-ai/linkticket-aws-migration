locals {
  db_major_version = join(".", slice(split(".", var.db_engine_version), 0, 2))
  db_family        = "mariadb${local.db_major_version}"
  db_identifier    = "${var.project}-${var.environment}-mariadb"
}

############################################
# 서브넷 그룹, 파라미터 그룹, (선택) 옵션 그룹
############################################
resource "aws_db_subnet_group" "this" {
  name        = "${var.project}-db-subnet-group"
  description = "Private DB subnets in AZ-a and AZ-c"
  subnet_ids  = local.db_subnet_ids

  tags = {
    Name = "${var.project}-db-subnet-group"
  }
}

resource "aws_db_parameter_group" "this" {
  name_prefix = "${var.project}-mariadb-"
  family      = local.db_family
  description = "LINKTICKET MariaDB parameters"

  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }

  parameter {
    name  = "collation_server"
    value = "utf8mb4_unicode_ci"
  }

  parameter {
    name  = "time_zone"
    value = var.db_time_zone
  }

  dynamic "parameter" {
    for_each = var.db_allow_trigger_creation ? [1] : []

    content {
      name  = "log_bin_trust_function_creators"
      value = "1"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_db_option_group" "audit" {
  count = var.db_enable_audit_log ? 1 : 0

  name_prefix              = "${var.project}-mariadb-"
  option_group_description = "MariaDB audit plugin"
  engine_name              = "mariadb"
  major_engine_version     = local.db_major_version

  option {
    option_name = "MARIADB_AUDIT_PLUGIN"

    option_settings {
      name  = "SERVER_AUDIT_EVENTS"
      value = "CONNECT,QUERY_DDL,QUERY_DCL"
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

############################################
# RDS 인스턴스 (Multi-AZ를 켜면 다른 AZ의 Standby는 AWS가 자동으로 만든다)
############################################
resource "aws_db_instance" "this" {
  identifier = local.db_identifier

  engine         = "mariadb"
  engine_version = var.db_engine_version
  instance_class = var.db_instance_class
  port           = 3306

  db_name  = var.db_name
  username = var.db_master_username

  # 비밀번호를 코드와 state에 두지 않고 RDS가 Secrets Manager에서 관리한다
  manage_master_user_password   = true
  master_user_secret_kms_key_id = aws_kms_key.this["rds"].arn

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage
  storage_type          = "gp3"
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.this["rds"].arn

  multi_az               = var.db_multi_az
  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [local.rds_sg_id]
  publicly_accessible    = false

  parameter_group_name = aws_db_parameter_group.this.name
  option_group_name    = var.db_enable_audit_log ? aws_db_option_group.audit[0].name : null

  # 백업 02:00~02:30 KST(UTC 17:00), 점검 일요일 03:00~04:00 KST(UTC 토요일 18:00)
  backup_retention_period = var.db_backup_retention_days
  backup_window           = "17:00-17:30"
  maintenance_window      = "sat:18:00-sat:19:00"
  copy_tags_to_snapshot   = true

  auto_minor_version_upgrade = true
  apply_immediately          = false

  deletion_protection       = var.db_deletion_protection
  skip_final_snapshot       = false
  final_snapshot_identifier = "${local.db_identifier}-final"

  enabled_cloudwatch_logs_exports = var.db_enable_audit_log ? ["audit", "error", "slowquery"] : ["error", "slowquery"]

  tags = {
    Name = local.db_identifier
  }
}
