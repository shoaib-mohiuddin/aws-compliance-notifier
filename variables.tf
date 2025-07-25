variable "lambda_function_name" {
  type        = string
  default     = "ebs_compliance_notifier"
  description = "Name of the Lambda function"
}

variable "email_recipients" {
  type        = list(string)
  description = "List of email addresses to receive notifications"
}