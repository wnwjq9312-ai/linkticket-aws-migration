terraform {
  backend "s3" {
    bucket       = "linkticket-terraform-state"
    key          = "linkticket/compute/terraform.tfstate"
    region       = "ap-northeast-2"
    encrypt      = true
    use_lockfile = true
  }
}
