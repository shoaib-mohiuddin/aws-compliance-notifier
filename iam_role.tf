resource "aws_iam_role" "lambda_exec" {
  name = "lambda_iam_role_cleanup"

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
  name = "IAMCleanupPolicy"
  role = aws_iam_role.lambda_exec.id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Sid" : "EC2InstanceManagement",
        "Effect" : "Allow",
        "Action" : [
          "ec2:DescribeInstances",
          "ec2:DescribeInstanceStatus"
        ],
        "Resource" : "*"
      },
      {
        "Sid" : "EBSVolumeOperations",
        "Effect" : "Allow",
        "Action" : [
          "ec2:DescribeVolumes",
          "ec2:DescribeVolumeStatus",
          "ec2:DescribeVolumeAttribute"
        ],
        "Resource" : "*"
      },
      {
        "Sid" : "TagOperations",
        "Effect" : "Allow",
        "Action" : [
          "ec2:DescribeTags"
        ],
        "Resource" : "*"
      },
      {
        "Sid" : "SES",
        "Effect" : "Allow",
        "Action" : [
          "ses:*"
        ],
        "Resource" : "*"
      }
    ]
  })
}