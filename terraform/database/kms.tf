# 용도별 KMS 키(ISMS-P 2.7.2 암호키 관리). 키마다 월 비용이 별도로 붙는다.
locals {
  kms_keys = {
    rds    = "RDS storage and managed master secret"
    backup = "DB backup and migration bucket"
    nft    = "NFT asset bucket"
    efs    = "EFS image storage"
  }

  # 키 정책을 직접 지정하는 키(나머지는 AWS 기본 정책 사용)
  kms_keys_with_policy = ["rds", "efs"]
}

data "aws_caller_identity" "current" {}

# 키 정책: 항상 계정 root 위임 문장(IAM 정책으로 권한을 줄 수 있게 함)을 먼저 두고,
# 서비스가 키를 쓰는 데 필요한 문장만 키별로 더한다. root 문장을 지우면 키에 접근할 수 없게 될 수 있다.
data "aws_iam_policy_document" "key" {
  for_each = toset(local.kms_keys_with_policy)

  statement {
    sid       = "EnableIAMUserPermissions"
    effect    = "Allow"
    actions   = ["kms:*"]
    resources = ["*"]

    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"]
    }
  }

  # EFS 키: AWS 문서(Encrypting data at rest)는 고객 관리형 키를 쓸 때 EFS 서비스 주체를
  # kms:ViaService 조건과 함께 허용하라고 안내한다. EFS가 요구하는 권한은
  # GenerateDataKeyWithoutPlaintext(GenerateDataKey*에 포함), CreateGrant, DescribeKey.
  dynamic "statement" {
    for_each = each.key == "efs" ? [1] : []

    content {
      sid    = "AllowEFSServiceUseOfKey"
      effect = "Allow"
      actions = [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:CreateGrant",
        "kms:DescribeKey",
      ]
      resources = ["*"]

      principals {
        type        = "Service"
        identifiers = ["elasticfilesystem.amazonaws.com"]
      }

      condition {
        test     = "StringEquals"
        variable = "kms:ViaService"
        values   = ["elasticfilesystem.${var.region}.amazonaws.com"]
      }
    }
  }

  # RDS 키: 마스터 비밀번호 시크릿을 같은 키로 암호화하므로 Secrets Manager를 통한 사용을 허용한다.
  # 계정 안에서 Secrets Manager를 거치는 요청으로만 한정한다.
  dynamic "statement" {
    for_each = each.key == "rds" ? [1] : []

    content {
      sid    = "AllowSecretsManagerUseOfKey"
      effect = "Allow"
      actions = [
        "kms:Encrypt",
        "kms:Decrypt",
        "kms:ReEncrypt*",
        "kms:GenerateDataKey*",
        "kms:CreateGrant",
        "kms:DescribeKey",
      ]
      resources = ["*"]

      principals {
        type        = "AWS"
        identifiers = ["*"]
      }

      condition {
        test     = "StringEquals"
        variable = "kms:CallerAccount"
        values   = [data.aws_caller_identity.current.account_id]
      }

      condition {
        test     = "StringEquals"
        variable = "kms:ViaService"
        values   = ["secretsmanager.${var.region}.amazonaws.com"]
      }
    }
  }
}

resource "aws_kms_key" "this" {
  for_each = local.kms_keys

  description             = "${var.project} ${each.key}: ${each.value}"
  enable_key_rotation     = true
  deletion_window_in_days = 30

  # null이면 AWS 기본 키 정책(root 위임)을 그대로 쓴다
  policy = contains(local.kms_keys_with_policy, each.key) ? data.aws_iam_policy_document.key[each.key].json : null

  tags = {
    Name = "${var.project}-${each.key}"
  }
}

resource "aws_kms_alias" "this" {
  for_each = local.kms_keys

  name          = "alias/${var.project}-${each.key}"
  target_key_id = aws_kms_key.this[each.key].key_id
}
