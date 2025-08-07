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

variable "account_id" {
  type        = string
  description = "AWS account ID for the customer"
}

variable "regions" {
  type        = list(string)
  description = "List of AWS regions to analyze"
}

variable "enable_gp2_check" {
  type        = bool
  default     = false
  description = "Enable gp2 volume compliance check"
}

variable "enable_encryption_check" {
  type        = bool
  default     = false
  description = "Enable unencrypted volume compliance check"
}

variable "enable_sg_check" {
  type        = bool
  default     = false
  description = "Enable overly permissive security group rule check"
}


variable "exclude_gp2_volumes" {
  type        = list(string)
  default     = []
  description = "List of gp2 volumes to exclude."
}

variable "exclude_unencrypted_volumes" {
  type        = list(string)
  default     = []
  description = "List of unencrypted volumes to exclude."
}

variable "exclude_sg_rules" {
  type        = list(string)
  default     = []
  description = "List of security group rule IDs to exclude."
}
