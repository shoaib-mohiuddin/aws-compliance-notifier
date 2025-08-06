"""
This module provides a function to assume an IAM role in a specified AWS account.
It returns a new boto3 session with temporary credentials for the assumed role.
"""

import boto3
from botocore.exceptions import ClientError


def assume_role(account_id, role_name="CloudreachAWSComplianceRole", session_name="CloudreachAWSComplianceRoleSession"):
    """
    Assumes a role in the target account and returns a new boto3 session.

    Args:
        account_id (str): AWS Account ID of the target account.
        role_name (str): Name of the IAM role to assume in the target account.
        session_name (str): Session name for the STS assume role call.

    Returns:
        boto3.Session: A new session object for the assumed role.
    """
    sts_client = boto3.client("sts")

    role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"

    try:
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )

        credentials = response["Credentials"]

        # Return a session using temporary credentials
        return boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"]
        )

    except ClientError as e:
        print(f"Failed to assume role {role_arn}: {e}")
        raise
