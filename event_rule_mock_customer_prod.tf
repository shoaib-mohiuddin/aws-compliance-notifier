module "mock_customer_prod" {
  source               = "./module-eventbridge"               # <-- DONOT CHANGE THIS
  lambda_arn           = aws_lambda_function.audit_lambda.arn # <-- DONOT CHANGE THIS
  eventbridge_role_arn = aws_iam_role.iam_for_eventbridge.arn # <-- DONOT CHANGE THIS

  event_rule_name = "event_rule_mock_customer_prod"
  cron            = "cron(00 23 * * ? *)"
  account_id      = "398649119307" # <-- Replace with Customer AWS account ID
  regions         = ["eu-west-1"]  # <-- Specify the regions to analyze

  # Enable the checks customers want to run
  # Set to true to enable the check, false to disable it
  enable_gp2_check        = false
  enable_encryption_check = true
  enable_sg_check         = false

  # Exclude specific volumes or security group rules from the checks
  exclude_gp2_volumes         = [] # <-- Specify gp2 volumes to exclude
  exclude_unencrypted_volumes = [] # <-- Specify unencrypted volumes to exclude
  exclude_sg_rules            = [] # <-- Specify security group rules to exclude
}