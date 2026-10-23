# 이 폴더의 Terraform은 DB 영역(RDS, S3, EFS, KMS)만 만든다.
# VPC, 서브넷, 라우팅, 보안 그룹은 다른 담당 영역이라 여기서 만들지도 바꾸지도 않고,
# 네트워크 담당 state(linkticket/network/terraform.tfstate)의 output에서 읽어서 쓴다.
#
#   vpc_id             : VPC ID (이 폴더에서는 현재 쓰지 않음)
#   subnet_ids         : 역할 이름을 키로 하는 맵(public_a, public_c, app_a, app_c, db_a, db_c)
#   security_group_ids : 역할 이름을 키로 하는 맵(alb, web, was, redis, rds, efs, monitoring)
#
# 필요한 권한: 네트워크 state 파일에 대한 s3:GetObject, 버킷에 대한 s3:ListBucket

data "terraform_remote_state" "network" {
  backend = "s3"

  config = {
    bucket = var.state_bucket
    key    = var.network_state_key
    region = var.region
  }
}

locals {
  net_outputs = data.terraform_remote_state.network.outputs

  subnet_ids = local.net_outputs.subnet_ids

  # RDS 서브넷 그룹: Private-DB 서브넷(AZ-a, AZ-c)
  db_subnet_ids = [for k in var.db_subnet_keys : local.subnet_ids[k]]

  # EFS 마운트 타깃: WEB 서버가 있는 Private-APP 서브넷(AZ-a, AZ-c)
  efs_subnet_ids = [for k in var.efs_subnet_keys : local.subnet_ids[k]]

  # 네트워크 담당이 만든 보안 그룹.
  #  rds-sg: 3306을 was-sg에서만 허용(네트워크 코드의 rds_from_was)
  #  efs-sg: 2049를 web-sg에서만 허용(네트워크 코드의 efs_from_web)
  rds_sg_id = local.net_outputs.security_group_ids["rds"]
  efs_sg_id = local.net_outputs.security_group_ids["efs"]
}
