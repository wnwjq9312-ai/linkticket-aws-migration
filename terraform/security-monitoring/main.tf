terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region  = "ap-northeast-2"
  profile = "linkticket-d"
}

resource "aws_cloudwatch_log_group" "django" {
  name              = "/ticketing/was/django"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "ssh" {
  name              = "/ticketing/was/ssh"
  retention_in_days = 7
}





resource "aws_cloudtrail" "security" {
  name                          = "Subin-Security-Trail"
  s3_bucket_name                = "aws-cloudtrail-logs-034220092639-7779365b"
  include_global_service_events = true
  is_multi_region_trail         = true
  enable_log_file_validation    = true
  enable_logging                = true

  kms_key_id = "arn:aws:kms:ap-northeast-2:034220092639:key/06247988-3d14-4892-a0cd-f85edf291f62"


  tags = {
    Project = "Ticketing"
  }

  advanced_event_selector {
    name = "관리 이벤트 선택기"

    field_selector {
      field  = "eventCategory"
      equals = ["Management"]
    }
  }
}





resource "aws_sns_topic" "security_alerts" {
  name = "Subin-Security-Alerts"

  tags = {
    Project = "Ticketing"
  }
}


resource "aws_sns_topic_subscription" "security_email" {
  topic_arn = aws_sns_topic.security_alerts.arn
  protocol  = "email"
  endpoint  = "subinseol0808@gmail.com"
}




resource "aws_cloudwatch_log_metric_filter" "django_errors" {
  name           = "Ticketing-Django-Errors"
  log_group_name = aws_cloudwatch_log_group.django.name
  pattern        = "ERROR"

  metric_transformation {
    name          = "DjangoErrorCount"
    namespace     = "Ticketing/Security"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "django_errors" {
  alarm_name          = "Ticketing-Django-Errors-Alarm"
  alarm_description   = "Django ERROR 로그 감지"
  namespace           = "Ticketing/Security"
  metric_name         = "DjangoErrorCount"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.security_alerts.arn]
  ok_actions    = [aws_sns_topic.security_alerts.arn]
}

resource "aws_cloudwatch_log_metric_filter" "ssh_failures" {
  name           = "Ticketing-SSH-Failures"
  log_group_name = aws_cloudwatch_log_group.ssh.name
  pattern        = "Failed password"

  metric_transformation {
    name          = "SSHLoginFailureCount"
    namespace     = "Ticketing/Security"
    value         = "1"
    default_value = "0"
  }
}

resource "aws_cloudwatch_metric_alarm" "ssh_failures" {
  alarm_name          = "Ticketing-SSH-Login-Failures-Alarm"
  alarm_description   = "SSH 로그인 실패 감지"
  namespace           = "Ticketing/Security"
  metric_name         = "SSHLoginFailureCount"
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 1
  threshold           = 1
  comparison_operator = "GreaterThanOrEqualToThreshold"
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.security_alerts.arn]
  ok_actions    = [aws_sns_topic.security_alerts.arn]
}



