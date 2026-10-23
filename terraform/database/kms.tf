# 용도별 KMS 키(ISMS-P 2.7.2 암호키 관리). 키마다 월 비용이 별도로 붙는다.
locals {
  kms_keys = {
    rds    = "RDS storage and managed master secret"
    backup = "DB backup and migration bucket"
    nft    = "NFT asset bucket"
    efs    = "EFS image storage"
  }
}

resource "aws_kms_key" "this" {
  for_each = local.kms_keys

  description             = "${var.project} ${each.key}: ${each.value}"
  enable_key_rotation     = true
  deletion_window_in_days = 30

  tags = {
    Name = "${var.project}-${each.key}"
  }
}

resource "aws_kms_alias" "this" {
  for_each = local.kms_keys

  name          = "alias/${var.project}-${each.key}"
  target_key_id = aws_kms_key.this[each.key].key_id
}
