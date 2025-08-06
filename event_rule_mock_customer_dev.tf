module "mock_customer" {
  source               = "./module-eventbridge"               # <-- DONOT CHANGE THIS
  lambda_arn           = aws_lambda_function.audit_lambda.arn # <-- DONOT CHANGE THIS
  eventbridge_role_arn = aws_iam_role.iam_for_eventbridge.arn # <-- DONOT CHANGE THIS

  event_rule_name = "event_rule-mock-customer_dev"
  cron            = "cron(0 23 * * ? *)"
  input_json = jsonencode({
    "account_id" : "398649119307",                                          # <-- Replace with Customer AWS account ID
    "regions" : ["eu-west-3", "ap-northeast-3"],                            # <-- Specify the region to analyze
    "modules_in_scope" : ["ebs_gp2", "ebs_unencrypted", "security_groups"], # <-- Specify the modules to analyze
    "exclusions" : {                                                        # <-- Specify exclusions if needed
      "ebs_gp2_volume_ids" : ["vol-0734f6bd3d7493fab", "vol-0123456789abcdef0"],
      "ebs_unencrypted_volume_ids" : ["vol-0abc123def456ghij", "vol-092c4ddee1d04b97d"],
      "security_group_rule_ids" : ["sgr-02a51edd597a9d868", "sgr-0fa6a6b2a8541a804"]
    }
  })

}