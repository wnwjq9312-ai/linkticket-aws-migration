############################################
# 공통
############################################
variable "region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"
}

variable "project" {
  description = "리소스 이름 접두어"
  type        = string
  default     = "linkticket"
}

variable "environment" {
  description = "환경 이름(구조도의 VPC 이름이 linkticket-prd)"
  type        = string
  default     = "prd"
}

############################################
# 다른 담당 영역에서 읽어 오는 값
############################################
variable "state_bucket" {
  description = "state 파일이 있는 S3 버킷"
  type        = string
  default     = "linkticket-terraform-state"
}

variable "network_state_key" {
  description = "네트워크 담당 state의 키(vpc_id, subnet_ids output을 읽는다)"
  type        = string
  default     = "linkticket/network/terraform.tfstate"
}

variable "db_subnet_keys" {
  description = "RDS 서브넷 그룹에 쓸 서브넷. 네트워크 state의 subnet_ids 맵 키(Private-DB AZ-a, AZ-c)"
  type        = list(string)
  default     = ["db_a", "db_c"]
}

variable "efs_subnet_keys" {
  description = "EFS 마운트 타깃을 둘 서브넷. 네트워크 state의 subnet_ids 맵 키(WEB 서버가 있는 Private-APP AZ-a, AZ-c)"
  type        = list(string)
  default     = ["app_a", "app_c"]
}

############################################
# RDS
############################################
variable "db_engine_version" {
  description = "MariaDB 버전. 사전 결정안 기준 10.11(또는 11.4). 메이저만 쓰면 마이너는 AWS 기본값"
  type        = string
  default     = "10.11"
}

variable "db_instance_class" {
  description = "임시값. 서버 스펙과 접속량 자료를 받은 뒤 부하 테스트로 정할 것"
  type        = string
  default     = "db.t4g.micro"
}

variable "db_allocated_storage" {
  description = "초기 스토리지(GiB). 현재 데이터는 약 1MB"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "스토리지 자동 확장 상한(GiB)"
  type        = number
  default     = 100
}

variable "db_secret_use_cmk" {
  description = "마스터 비밀번호 시크릿을 직접 만든 RDS 키로 암호화할지. false면 AWS 관리형 키(aws/secretsmanager). RDS 생성 실패 원인을 분리할 때만 false로 두고, 관리 대상이 된 뒤에는 키를 바꿀 수 없음"
  type        = bool
  default     = true
}

variable "db_name" {
  description = "초기 DB 이름. 인수인계 문서는 ticketing_db, 저장소 설정은 linkticket이라 운영 값을 확인해야 함"
  type        = string
  default     = "ticketing_db"
}

variable "db_master_username" {
  description = "마스터 계정 이름. 비밀번호는 RDS가 Secrets Manager에서 관리"
  type        = string
  default     = "linkticket_admin"
}

variable "db_multi_az" {
  description = "Multi-AZ 여부. 구조도는 Primary AZ-a, Standby AZ-c"
  type        = bool
  default     = true
}

variable "db_backup_retention_days" {
  description = "자동 백업 보관 기간(일). 사전 결정안 제안값 14일(1~35)"
  type        = number
  default     = 14
}

variable "db_deletion_protection" {
  description = "삭제 보호"
  type        = bool
  default     = true
}

variable "db_time_zone" {
  description = "DB 시간대. 온프레미스 DB 값을 확인해서 맞출 것(Django는 USE_TZ=True라 UTC로 저장)"
  type        = string
  default     = "Asia/Seoul"
}

variable "db_allow_trigger_creation" {
  description = "Trigger/Routine을 만들어야 할 때만 true(log_bin_trust_function_creators=1). 저장소 마이그레이션에는 없음"
  type        = bool
  default     = false
}

variable "db_enable_audit_log" {
  description = "MariaDB 감사 플러그인과 audit 로그 CloudWatch 전송. ISMS-P 2.9.4 접속기록 관리 관점에서 true 권장"
  type        = bool
  default     = false
}

############################################
# S3
############################################
variable "backup_bucket_name" {
  description = "DB 백업·이관 파일 버킷 이름(S3 전체에서 유일해야 함)"
  type        = string
  default     = "linkticket-db-backup"
}

variable "nft_bucket_name" {
  description = "NFT 자산 비공개 버킷 이름(S3 전체에서 유일해야 함)"
  type        = string
  default     = "linkticket-nft-assets"
}

variable "backup_expire_days" {
  description = "백업 버킷 backup/ 경로 파일의 보관 일수. RDS 자동 백업 보관 기간과 맞출 것"
  type        = number
  default     = 14
}

variable "nft_noncurrent_expire_days" {
  description = "NFT 버킷에서 덮어쓰기·삭제된 이전 버전을 보관할 일수"
  type        = number
  default     = 365
}

############################################
# EFS (공연 이미지 저장소, 온프레미스 NFS 대체)
############################################
variable "efs_enable_backup" {
  description = "EFS 자동 백업(AWS Backup) 사용 여부"
  type        = bool
  default     = true
}

variable "efs_posix_uid" {
  description = "접근 포인트가 강제할 uid/gid. 온프레미스 NFS의 webshare(2000)와 동일"
  type        = number
  default     = 2000
}

variable "efs_root_path" {
  description = "EFS 안의 루트 디렉터리(온프레미스 /RAID/web-storage 대응)"
  type        = string
  default     = "/web-storage"
}

variable "efs_mount_path" {
  description = "EC2에서 마운트할 경로. Nginx /static/ alias와 같아야 하므로 기존 /nfs-storage 유지"
  type        = string
  default     = "/nfs-storage"
}
