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

resource "aws_iam_role_policy" "iam_cleanup_policy" {
  name = "${var.lambda_function_name}-lambda-inline"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "EC2VolumesAndSecurityGroups",
        "Effect" : "Allow",
        "Action" : [
          "ec2:DescribeVolumes",
          # "ec2:DescribeVolumeStatus",
          # "ec2:DescribeVolumeAttribute",
          "ec2:DescribeSecurityGroups",
          # "ec2:DescribeInstances",
          "ec2:DescribeSecurityGroupRules"

        ],
        "Resource" : "*"
      },
      {
        "Sid" : "SESSendEmail",
        "Effect" : "Allow",
        "Action" : [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ],
        "Resource" : "arn:aws:ses:${var.region}:${data.aws_caller_identity.current.account_id}:identity/${data.aws_ses_email_identity.ses.id}" # <-- SES verified email address
      }
    ]
  })
}