module "mock_customer" {
  source               = "./module-eventbridge"               # <-- DO NOT CHANGE THIS
  lambda_arn           = aws_lambda_function.audit_lambda.arn # <-- DO NOT CHANGE THIS
  eventbridge_role_arn = aws_iam_role.iam_for_eventbridge.arn # <-- DO NOT CHANGE THIS

  event_rule_name = "event_rule_mock_customer_dev"
  cron            = "cron(00 12 * * ? *)"           # <-- Replace cron schedule 
  account_id      = "398649119307"                  # <-- Replace with Customer AWS account ID
  regions         = ["eu-west-3", "ap-northeast-3"] # <-- Specify the regions to analyze

  # Enable the checks customers want to run, Set to true to enable the check, false to disable it
  enable_gp2_check        = true
  enable_encryption_check = true
  enable_sg_check         = true

  # Optional, exclude specific volumes or security group rules from the checks
  exclude_gp2_volumes         = ["vol-08a5f859e6a301661", "vol-0123456789abcdef0"] # <-- Specify gp2 volumes to exclude
  exclude_unencrypted_volumes = ["vol-08ef5e4da3a422bd5", "vol-092c4ddee1d04b97d"] # <-- Specify unencrypted volumes to exclude
  exclude_sg_rules            = ["sgr-0f5eed85ee3f15714", "sgr-050c5125cb80f771d"] # <-- Specify security group rules to exclude
}