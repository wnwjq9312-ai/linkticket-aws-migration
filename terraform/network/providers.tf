provider "aws" {
  region = "ap-northeast-2"

  default_tags {
    tags = {
      Project = "linkticket"
      Owner   = "A"
      Env     = "prd"
      Managed = "Terraform"
    }
  }
}
