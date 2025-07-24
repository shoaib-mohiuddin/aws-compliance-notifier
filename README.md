# EBS Compliance Notifier

An automated AWS Lambda-based solution to identify non-compliant Amazon EBS volumes across multiple regions. It performs two key audits:

  - Unencrypted EBS Volumes
  - EBS Volumes using gp2 storage type

The Lambda function analyzes EBS volumes, generates CSV reports, and emails stakeholders with detailed findings, which helps align with best practices for security and cost optimization.

**Note:** The AWS account must have a SES verified sender email

## Project Structure
`.
├── backend.tf
├── iam_role.tf
├── lambda.tf
├── provider.tf
├── python
│   ├── __init__.py
│   ├── ebs_compliance_notifier.py
│   └── library
│       ├── __init__.py
│       ├── ebs
│       │   ├── __init__.py
│       │   ├── ebs_gp2_analyzer.py
│       │   └── ebs_unencrypted_volumes_analyzer.py
│       └── helpers
│           ├── __init__.py
│           └── send_email.py
├── README.md
└── variables.tf`

### Environment Variables

These should be passed to the Lambda function:
| Variable |	Description |
| -------- | ------------ |
| `EMAIL_FROM_ADDRESS` |	Verified email in SES to send reports |
| `DEFAULT_EMAIL_RECIPIENTS` |	JSON list of recipient emails (e.g., ["email@example.com"]) |

<!-- BEGIN_TF_DOCS -->
## Requirements

No requirements.

## Providers

| Name | Version |
|------|---------|
| <a name="provider_archive"></a> [archive](#provider\_archive) | 2.7.1 |
| <a name="provider_aws"></a> [aws](#provider\_aws) | 6.4.0 |

## Modules

No modules.

## Resources

| Name | Type |
|------|------|
| [aws_cloudwatch_event_rule.lambda_event_rule](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule) | resource |
| [aws_cloudwatch_event_target.lambda_target](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target) | resource |
| [aws_iam_role.lambda_exec](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role) | resource |
| [aws_iam_role_policy.iam_cleanup_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy) | resource |
| [aws_iam_role_policy_attachment.lambda_policy](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/iam_role_policy_attachment) | resource |
| [aws_lambda_function.audit_lambda](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function) | resource |
| [aws_lambda_permission.allow_cloudwatch_event](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission) | resource |
| [archive_file.python_script_file](https://registry.terraform.io/providers/hashicorp/archive/latest/docs/data-sources/file) | data source |
| [aws_ses_email_identity.ses](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ses_email_identity) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_lambda_function_name"></a> [lambda\_function\_name](#input\_lambda\_function\_name) | Name of the Lambda function | `string` | `"ebs-compliance-notifier"` | no |

## Outputs

No outputs.
<!-- END_TF_DOCS -->