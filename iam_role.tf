# IAM Role for Lambda Function
resource "aws_iam_role" "lambda_exec" {
  name = "${var.lambda_function_name}-lambda-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "lambda_inline" {
  name = "${var.lambda_function_name}-lambda-inline"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "SESSendEmail",
        "Effect" : "Allow",
        "Action" : [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ],
        "Resource" : "arn:aws:ses:${var.region}:${data.aws_caller_identity.current.account_id}:identity/${data.aws_ses_email_identity.ses.id}" # <-- SES verified email address
      },
      {
        "Sid" : "AssumeRoleInCustomerAccount",
        "Effect" : "Allow",
        "Action" : [
          "sts:AssumeRole"
        ],
        "Resource" : "arn:aws:iam::*:role/CloudreachAWSComplianceRole"
      }
    ]
  })
}

# IAM Role for Eventbridge
resource "aws_iam_role" "iam_for_eventbridge" {
  name = "aws-compliance-notifier-eventbridge-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "events.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "eventbridge_inline" {
  name = "aws-compliance-notifier-eventbridge-inline"
  role = aws_iam_role.iam_for_eventbridge.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "arn:aws:lambda:${var.region}:${data.aws_caller_identity.current.account_id}:function:${var.lambda_function_name}"
      }
    ]
  })
}