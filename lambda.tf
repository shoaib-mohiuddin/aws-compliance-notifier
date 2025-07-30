data "aws_caller_identity" "current" {}
data "aws_ses_email_identity" "ses" {
  email = "shoaibmm7@gmail.com" # <-- Replace with a SES verified email address
}

data "archive_file" "python_script_file" {
  type        = "zip"
  source_dir  = "${path.module}/python/"
  output_path = "${path.module}/files/lambda-function.zip"
}

resource "aws_lambda_function" "audit_lambda" {
  filename      = data.archive_file.python_script_file.output_path
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda_exec.arn
  handler       = "${var.lambda_function_name}.lambda_handler"

  source_code_hash = filebase64sha256(data.archive_file.python_script_file.output_path)

  runtime = "python3.12"
  timeout = 900

  environment {
    variables = {
      EMAIL_FROM = data.aws_ses_email_identity.ses.email # <-- SES verified email address
      EMAIL_TO   = jsonencode(var.email_recipients)      # <-- Add additional email addresses as needed
    }
  }

}

resource "aws_lambda_permission" "allow_cloudwatch_event" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.audit_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_event_rule.arn
}

resource "aws_cloudwatch_event_rule" "lambda_event_rule" {
  name        = "${var.lambda_function_name}_event_rule"
  description = "Trigger for Lambda function to audit EBS volumes"

  schedule_expression = "cron(0 12 * * ? *)" # <-- Define the schedule here, e.g., daily at 12:00 UTC
  state               = "ENABLED"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule = aws_cloudwatch_event_rule.lambda_event_rule.name
  arn  = aws_lambda_function.audit_lambda.arn

  input = jsonencode({
    "account_id"       = data.aws_caller_identity.current.account_id,      # <-- Replace with your AWS account ID
    "regions"          = ["${var.region}", "ap-northeast-3"],              # <-- Specify the region to analyze
    "modules_in_scope" = ["ebs_gp2", "ebs_unencrypted", "security_groups"] # <-- Specify the modules to analyze
  })

}
