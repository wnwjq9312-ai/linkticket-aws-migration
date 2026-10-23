terraform {
  required_version = ">= 1.10.0" # backend의 use_lockfile(S3 네이티브 락)을 쓰려면 1.10 이상

  backend "s3" {
    bucket       = "linkticket-terraform-state"
    key          = "linkticket/database/terraform.tfstate"
    region       = "ap-northeast-2"
    encrypt      = true
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.50, < 7.0"
    }
  }
}

provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project   = var.project
      Area      = "database"
      Env       = var.environment
      ManagedBy = "terraform"
    }
  }
}
