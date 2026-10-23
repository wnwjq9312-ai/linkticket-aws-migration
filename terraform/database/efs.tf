# 공연 이미지 저장소. AWS에서 NFS를 쓰는 관리형 서비스가 EFS다.
# 온프레미스의 NFS(10.10.4.103:/RAID/web-storage -> /nfs-storage)를 대체하며,
# 양쪽 AZ의 마운트 타깃으로 WEB 서버 두 대가 같은 파일을 본다.

############################################
# 파일 시스템, 마운트 타깃, 접근 포인트
############################################
resource "aws_efs_file_system" "images" {
  creation_token = "${var.project}-web-images"

  encrypted        = true
  kms_key_id       = aws_kms_key.this["efs"].arn
  performance_mode = "generalPurpose"
  throughput_mode  = "elastic"

  tags = {
    Name = "${var.project}-web-images"
  }
}

# AZ마다 하나씩. 같은 AZ의 서버가 자기 AZ의 마운트 타깃을 쓰면 AZ 간 전송 요금이 없다.
resource "aws_efs_mount_target" "images" {
  for_each = toset(local.efs_subnet_ids)

  file_system_id  = aws_efs_file_system.images.id
  subnet_id       = each.value
  security_groups = [local.efs_sg_id]
}

# 온프레미스의 all_squash(anonuid=2000), 디렉터리 권한 750과 같은 효과.
# 접근 포인트로 마운트하면 클라이언트의 실제 uid와 무관하게 항상 uid/gid 2000으로 읽고 쓴다.
resource "aws_efs_access_point" "web" {
  file_system_id = aws_efs_file_system.images.id

  posix_user {
    uid = var.efs_posix_uid
    gid = var.efs_posix_uid
  }

  root_directory {
    path = var.efs_root_path

    creation_info {
      owner_uid   = var.efs_posix_uid
      owner_gid   = var.efs_posix_uid
      permissions = "0750"
    }
  }

  tags = {
    Name = "${var.project}-web-storage"
  }
}

resource "aws_efs_backup_policy" "images" {
  count = var.efs_enable_backup ? 1 : 0

  file_system_id = aws_efs_file_system.images.id

  backup_policy {
    status = "ENABLED"
  }
}

############################################
# 파일 시스템 정책: TLS가 아닌 접속은 거부, 마운트 타깃 경유 접속만 허용
############################################
data "aws_iam_policy_document" "efs" {
  statement {
    sid    = "AllowMountViaMountTarget"
    effect = "Allow"

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    actions = [
      "elasticfilesystem:ClientMount",
      "elasticfilesystem:ClientWrite",
    ]

    resources = [aws_efs_file_system.images.arn]

    condition {
      test     = "Bool"
      variable = "elasticfilesystem:AccessedViaMountTarget"
      values   = ["true"]
    }
  }

  statement {
    sid     = "DenyNonTLS"
    effect  = "Deny"
    actions = ["*"]

    principals {
      type        = "AWS"
      identifiers = ["*"]
    }

    resources = [aws_efs_file_system.images.arn]

    condition {
      test     = "Bool"
      variable = "aws:SecureTransport"
      values   = ["false"]
    }
  }
}

resource "aws_efs_file_system_policy" "images" {
  file_system_id = aws_efs_file_system.images.id
  policy         = data.aws_iam_policy_document.efs.json
}
