data "aws_ses_email_identity" "ses1" {
  email = "shoaib.mohiuddin@cloudreach.com"
}

data "aws_ses_email_identity" "ses2" {
  email = "shoaibmm7@gmail.com"
}

data "archive_file" "python_script_file" {
  type        = "zip"
  source_dir  = "${path.module}/python/"
  output_path = "${path.module}/files/lambda-function.zip"
}

resource "aws_lambda_function" "audit_lambda" {
  # If the file is not in the current working directory you will need to include a 
  # path.module in the filename.
  filename      = data.archive_file.python_script_file.output_path
  function_name = var.lambda_function_name
  role          = aws_iam_role.lambda_exec.arn
  handler       = "${var.lambda_function_name}.lambda_handler"

  source_code_hash = filebase64sha256(data.archive_file.python_script_file.output_path)

  runtime = "python3.11"
  timeout = 10

  environment {
    variables = {
      SES_SENDER = data.aws_ses_email_identity.ses1.email
      SES_RECIPIENT  = data.aws_ses_email_identity.ses2.email
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

  schedule_expression = "cron(0 12 * * ? *)" # Runs every day at 12:00 UTC
  state               = "ENABLED"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule = aws_cloudwatch_event_rule.lambda_event_rule.name
  arn  = aws_lambda_function.audit_lambda.arn

}
