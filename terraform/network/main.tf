module "vpc" {
  source = "./modules/vpc"

  aws_region        = "ap-northeast-2"
  project_name      = "linkticket"
  environment       = "prd"
  vpc_cidr          = "10.0.0.0/16"

  # Keep false while reviewing the plan. NAT Gateway incurs charges when created.
  enable_nat_gateway = false
}
