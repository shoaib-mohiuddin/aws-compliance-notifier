variable "lambda_function_name" {
  type        = string
  default     = "aws_compliance_notifier"
  description = "Name of the Lambda function"
}

variable "event_rule_name" {
  type        = string
  description = "Name for the Eventbridge Rule"
}

variable "cron" {
  type        = string
  description = "Cron expression for the Eventbridge Rule schedule"
}

variable "lambda_arn" {
  type        = string
  description = "ARN of the Lambda function to be triggered by the Eventbridge Rule"
}

variable "eventbridge_role_arn" {
  type        = string
  description = "ARN of the IAM role that Eventbridge will assume to invoke the Lambda function"
}

variable "input_json" {
  type        = string
  description = "JSON input to be passed to the Lambda function when triggered by the Eventbridge Rule"
}