terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-2"
}

resource "aws_cloudwatch_log_group" "django" {
  name              = "/ticketing/was/django"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "ssh" {
  name              = "/ticketing/was/ssh"
  retention_in_days = 7
}



resource "aws_cloudwatch_dashboard" "subin" {
  dashboard_name = "Subin-Monitoring-Dashboard"
  dashboard_body = "{\"widgets\":[]}"
}


