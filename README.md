# AWS Compliance Notifier

A Lambda-based solution to identify non-compliant AWS resources across multiple regions. The Lambda function will be hosted in cr-opsdev account (830657588137) and will be used to orchestrate the compliance run in the customer accounts.

It performs following key audits:

  - Unencrypted EBS Volumes
  - EBS Volumes using gp2 storage type
  - Overly permissive security group rules

The Lambda function assumes role in the customer account, analyzes above resources, generates CSV reports, and emails support@cloudreach.com with detailed findings, which helps align with best practices for security and cost optimization.

**TODO:** Create a SES email identity for the support email in cr-opsdev account - this will be used as both sender and recipient.

## How It Works

1. Lambda sits in the cr-opsdev account.
2. Each **customer account** must have a IAM role (`CloudreachAWSComplianceRole`).
3. An **EventBridge rule** in cr-opsdev to trigger the Lambda with customer account context.
4. Lambda:
   - Assumes the customer's IAM role.
   - Runs compliance checks on selected modules (encryption, gp2, security groups, etc).
   - Sends an email report via Amazon SES.

## Onboarding a Customer 

#### Step 1: Create IAM Role in Customer account
Create a cross-account role for the Lambda in the Customer account. Use the CloudFormation template `cnf-customer-iam-role-manual.yml` (need a better name??)
```
aws cloudformation deploy \
  --template-file cnf-customer-iam-role-manual.yml \
  --stack-name CloudreachAWSComplianceRole-CNFStack \
  --region <CUSTOMER_REGION>
```

#### Step 2: Create EventBridge Rule in cr-opsdev account
1. Copy `event_rule_mock_customer_dev.tf` to a new file in the repo root. Use naming convention:
```
event_rule_<CUSTOMER_NAME>_<ENV_NAME>.tf
```

2. Customize the module input block:
```
module "CUSTOMER_NAME" {
  source               = "./module-eventbridge"               # <-- DO NOT CHANGE THIS
  lambda_arn           = aws_lambda_function.audit_lambda.arn # <-- DO NOT CHANGE THIS
  eventbridge_role_arn = aws_iam_role.iam_for_eventbridge.arn # <-- DO NOT CHANGE THIS

  event_rule_name = "event_rule_CUATOMER_NAME_ENV"
  cron            = "cron(00 12 * * ? *)"           # <-- Replace cron schedule
  account_id      = "xxxxxxxxxx"                    # <-- Replace with Customer AWS account ID
  regions         = ["eu-west-1", "ap-northeast-3"] # <-- Specify the regions to analyze

  # Enable the checks customers want to run. Set to true to enable the check, false to disable it
  enable_gp2_check        = false
  enable_encryption_check = true
  enable_sg_check         = false

  # Optional, exclude specific volumes or security group rules from the checks
  exclude_gp2_volumes         = ["vol-xxxxx", "vol-xxxxx"] 
  exclude_unencrypted_volumes = ["vol-yyyyy", "vol-yyyyy"] 
  exclude_sg_rules            = ["sgr-zzzzz", "sgr-zzzzz"] 
}
```
3. For initial setup, leave exclusions part empty. These can be updated later based on customer feedback.
```
  exclude_gp2_volumes         = [] 
  exclude_unencrypted_volumes = [] 
  exclude_sg_rules            = [] 
```

4. Deploy the new rule to the cr-opsdev account
  ```
  terraform init
  terraform apply
  ```


<!-- BEGIN_TF_DOCS -->
## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | >= 1.3.0 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 6.0 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_archive"></a> [archive](#provider\_archive) | 2.7.1 |
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.6.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_mock_customer"></a> [mock\_customer](#module\_mock\_customer) | ./module-eventbridge | n/a |

## Resources

| Name | Type |
|------|------|
| [aws_iam_role.iam_for_eventbridge](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role.lambda_exec](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.eventbridge_inline](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy.lambda_inline](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy_attachment.lambda_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_lambda_function.audit_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [archive_file.python_script_file](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_ses_email_identity.ses](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ses_email_identity) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_email_recipients"></a> [email\_recipients](#input\_email\_recipients) | List of email addresses to receive notifications | `list(string)` | n/a | yes |
| <a name="input_lambda_function_name"></a> [lambda\_function\_name](#input\_lambda\_function\_name) | Name of the Lambda function | `string` | `"aws_compliance_notifier"` | no |
| <a name="input_region"></a> [region](#input\_region) | AWS region where the resources will be deployed | `string` | n/a | yes |

## Outputs

No outputs.
<!-- END_TF_DOCS -->