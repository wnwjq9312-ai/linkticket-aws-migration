############################################
# RDS
############################################
output "rds_endpoint" {
  description = "WAS의 DB_HOST에 넣을 RDS 엔드포인트(DNS)"
  value       = aws_db_instance.this.address
}

output "rds_port" {
  description = "WAS의 DB_PORT"
  value       = aws_db_instance.this.port
}

output "rds_db_name" {
  description = "WAS의 DB_NAME"
  value       = aws_db_instance.this.db_name
}

output "rds_master_secret_arn" {
  description = "마스터 비밀번호가 들어 있는 Secrets Manager 시크릿 ARN"
  value       = aws_db_instance.this.master_user_secret[0].secret_arn
}

############################################
# 관제(CloudWatch) 담당에게 넘길 값. 알람과 로그 보관 설정은 그쪽에서 관리한다
############################################
output "rds_instance_identifier" {
  description = "알람 dimension(DBInstanceIdentifier)에 넣을 값"
  value       = aws_db_instance.this.identifier
}

output "rds_instance_arn" {
  description = "RDS 인스턴스 ARN"
  value       = aws_db_instance.this.arn
}

output "rds_log_group_names" {
  description = "RDS가 로그를 보내는 CloudWatch Logs 그룹. RDS가 자동 생성하며 보관 기간은 기본적으로 무기한이라 관제 쪽에서 설정 필요"
  value       = [for t in aws_db_instance.this.enabled_cloudwatch_logs_exports : "/aws/rds/instance/${aws_db_instance.this.identifier}/${t}"]
}

############################################
# S3
############################################
output "backup_bucket_name" {
  description = "DB 백업·이관 파일 버킷"
  value       = aws_s3_bucket.this["backup"].bucket
}

output "nft_bucket_name" {
  description = "NFT 자산 비공개 버킷"
  value       = aws_s3_bucket.this["nft"].bucket
}

############################################
# EFS
############################################
output "efs_file_system_id" {
  description = "EFS 파일 시스템 ID"
  value       = aws_efs_file_system.images.id
}

output "efs_access_point_id" {
  description = "EFS 접근 포인트 ID"
  value       = aws_efs_access_point.web.id
}

output "efs_mount_command" {
  description = "WEB 서버(EC2)에서 실행할 마운트 명령. amazon-efs-utils 설치 필요"
  value       = "sudo mkdir -p ${var.efs_mount_path} && sudo mount -t efs -o tls,accesspoint=${aws_efs_access_point.web.id} ${aws_efs_file_system.images.id}:/ ${var.efs_mount_path}"
}

output "efs_fstab_line" {
  description = "/etc/fstab에 추가할 줄(재부팅 후에도 유지)"
  value       = "${aws_efs_file_system.images.id}:/ ${var.efs_mount_path} efs _netdev,noresvport,tls,accesspoint=${aws_efs_access_point.web.id} 0 0"
}

############################################
# KMS
############################################
output "kms_key_arns" {
  description = "용도별 KMS 키 ARN"
  value       = { for k, v in aws_kms_key.this : k => v.arn }
}
