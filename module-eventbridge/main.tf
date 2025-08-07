resource "aws_cloudwatch_event_rule" "lambda_event_rule" {
  name        = "${var.event_rule_name}"
  description = "Trigger for Lambda function to audit EBS volumes"

  schedule_expression = "${var.cron}"
  state               = "ENABLED"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule = aws_cloudwatch_event_rule.lambda_event_rule.name
  arn  = "${var.lambda_arn}"
  role_arn = var.eventbridge_role_arn

  input = jsonencode({
    account_id       = var.account_id,
    regions          = var.regions,
    enabled_checks   = local.enabled_checks,
    exclusions       = local.exclusions
  })

}