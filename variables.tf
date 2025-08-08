variable "lambda_function_name" {
  type        = string
  default     = "aws_compliance_notifier"
  description = "Name of the Lambda function"
}

variable "email_recipients" {
  type        = list(string)
  description = "List of email addresses to receive notifications"
}

variable "region" {
  type        = string
  description = "AWS region where the resources will be deployed"
  default     = "eu-west-1"
}